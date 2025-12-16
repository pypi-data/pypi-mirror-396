# SPDX-FileCopyrightText: 2021 Dalibo
#
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

import configparser
import contextlib
import datetime
import json
import os
import re
from collections.abc import AsyncIterator, Iterator
from functools import partial
from pathlib import Path, PurePath
from typing import Any

import attrs
import pgtoolkit.conf as pgconf
from dateutil.tz import gettz

from .. import conf, deps, exceptions, postgresql, types, util
from ..models import Instance, PostgreSQLInstance, interface
from ..postgresql import pq
from ..settings import Settings, _pgbackrest
from ..system import Command, FileSystem
from ..task import task
from .models import interface as i
from .models import system as s

logger = util.get_logger(__name__)


@util.cache
def template(*args: str) -> str:
    logger.debug("loading %s template", util.joinpath(*args))
    return util.template("pgbackrest", *args)


def available(settings: Settings) -> _pgbackrest.Settings | None:
    return settings.pgbackrest


def get_settings(settings: Settings) -> _pgbackrest.Settings:
    """Return settings for pgbackrest

    Same as `available` but assert that settings are not None.
    Should be used in a context where settings for the plugin are surely
    set (for example in hookimpl).
    """
    assert settings.pgbackrest is not None
    return settings.pgbackrest


def rolename(settings: Settings) -> str:
    return settings.postgresql.backuprole.name


def role(settings: Settings, service: i.Service) -> interface.Role | None:
    name = rolename(settings)
    extra = {}
    if settings.postgresql.auth.passfile is not None:
        extra["pgpass"] = settings.postgresql.backuprole.pgpass
    return interface.Role(
        name=name, password=service.password, login=True, superuser=True, **extra
    )


def enabled(instance: PostgreSQLInstance, settings: _pgbackrest.Settings) -> bool:
    return system_lookup(instance.datadir, settings) is not None


def base_configpath(settings: _pgbackrest.Settings) -> Path:
    return settings.configpath / "pgbackrest.conf"


def config_directory(settings: _pgbackrest.Settings) -> Path:
    return settings.configpath / "conf.d"


@deps.use
def create_include_directory(
    settings: _pgbackrest.Settings, *, fs: FileSystem = deps.Auto
) -> None:
    if not fs.exists(d := config_directory(settings)):
        logger.info("creating pgBackRest include directory")
        fs.mkdir(d, mode=0o750, exist_ok=True, parents=True)


@deps.use
def delete_include_directory(
    settings: _pgbackrest.Settings, *, fs: FileSystem = deps.Auto
) -> None:
    if fs.exists(d := config_directory(settings)):
        logger.info("deleting pgBackRest include directory")
        util.rmdir(d)


def make_cmd(stanza: str, settings: _pgbackrest.Settings, *args: str) -> list[str]:
    return [
        str(settings.execpath),
        f"--config-path={settings.configpath}",
        "--log-level-stderr=info",
        f"--stanza={stanza}",
    ] + list(args)


parser = partial(configparser.ConfigParser, strict=True)

pgpath_rgx = re.compile(r"pg(\d+)-path")


def next_index(cp: configparser.ConfigParser, stanza: str) -> int:
    """Return the next index of pgN- options in parser.

    >>> cp = parser()
    >>> next_index(cp, "st")
    Traceback (most recent call last):
        ...
    configparser.NoSectionError: No section: 'st'
    >>> cp.add_section("st")
    >>> next_index(cp, "st")
    1
    >>> cp["st"]["pg1-path"] = "/pgsql/main"
    >>> next_index(cp, "st")
    2
    """
    idxs = {0}
    for opt in cp.options(stanza):
        if m := pgpath_rgx.match(opt):
            idxs.add(int(m.group(1)))
    return max(idxs) + 1


@deps.use
def system_lookup(
    datadir: Path, settings: _pgbackrest.Settings, *, fs: FileSystem = deps.Auto
) -> s.Service | None:
    d = config_directory(settings)
    for p in fs.glob(d, "*.conf"):
        cp = parser()
        with fs.open(p) as f:
            cp.read_file(f)
        for stanza in cp.sections():
            for key, value in cp.items(stanza):
                if (m := pgpath_rgx.match(key)) and value == str(datadir):
                    return s.Service(
                        stanza=stanza, path=p, datadir=datadir, index=int(m.group(1))
                    )
    logger.debug(
        "no pgBackRest configuration file matching PGDATA=%s found in %s", datadir, d
    )
    return None


@deps.use
def stanza_pgpaths(
    path: Path, stanza: str, *, fs: FileSystem = deps.Auto
) -> Iterator[tuple[int, Path]]:
    cp = parser()
    with fs.open(path) as f:
        cp.read_file(f)
    for key, value in cp.items(stanza):
        if m := pgpath_rgx.match(key):
            yield int(m.group(1)), Path(value)


@deps.use
def get_service(
    instance: PostgreSQLInstance,
    manifest: i.Service,
    settings: _pgbackrest.Settings,
    upgrading_from: interface.PostgreSQLInstanceRef | None,
    *,
    fs: FileSystem = deps.Auto,
) -> s.Service:
    """Retrieve a Service object.

    In case of an upgrade, if a service exists on original 'upgrading_from'
    instance, return it but bound to 'instance.datadir'.

    Otherwise, lookup for a service bound to 'instance' and return it if
    found.

    Fall back to building a new service object from scratch.
    """
    if upgrading_from:
        if svc := system_lookup(upgrading_from.datadir, settings):
            return attrs.evolve(svc, datadir=instance.datadir)
    if svc := system_lookup(instance.datadir, settings):
        if manifest.stanza != svc.stanza:
            raise exceptions.InstanceStateError(
                f"instance {instance} is already bound to pgbackrest stanza {svc.stanza!r} (path={svc.path})"
            )
        return svc
    stanza = manifest.stanza
    index = 1
    path = config_directory(settings) / f"{stanza}.conf"
    # Use the next pgN index when the path exists but configured instance is
    # not attached to its stanza. This would typically happen for standby
    # instances, when created on the same host as the primary.
    if fs.exists(path):
        cp = parser()
        with fs.open(path) as f:
            cp.read_file(f)
        index = next_index(cp, stanza)
    return s.Service(stanza=stanza, path=path, datadir=instance.datadir, index=index)


@deps.use
async def backup_info(
    service: s.Service,
    settings: _pgbackrest.Settings,
    *,
    backup_set: str | None = None,
    cmd: Command = deps.Auto,
) -> dict[str, Any]:
    """Call pgbackrest info command to obtain information about backups.

    Ref.: https://pgbackrest.org/command.html#command-info
    """
    args = []
    if backup_set is not None:
        args.append(f"--set={backup_set}")
    args.extend(["--output=json", "info"])
    r = await cmd.run(make_cmd(service.stanza, settings, *args), check=True)
    infos = json.loads(r.stdout)
    try:
        return next(i for i in infos if i["name"] == service.stanza)
    except StopIteration:
        return {}


def setup(
    instance: PostgreSQLInstance,
    service: i.Service,
    config: pgconf.Configuration,
    changes: types.ConfigChanges,
    creating: bool,
    upgrading_from: interface.PostgreSQLInstanceRef | None,
) -> s.Service:
    """Build and return a Service value while configuring respective pgBackRest stanza."""
    settings = instance._settings
    s = get_settings(settings)
    svc = get_service(instance, service, s, upgrading_from)
    setup_stanza(
        svc,
        s,
        config,
        changes,
        creating,
        settings.postgresql.backuprole.name,
    )
    return svc


@task
@deps.use
def setup_stanza(
    service: s.Service,
    settings: _pgbackrest.Settings,
    instance_config: pgconf.Configuration,
    changes: types.ConfigChanges,
    creating: bool,
    backuprole: str,
    *,
    fs: FileSystem = deps.Auto,
) -> None:
    """Setup pgBackRest"""
    if not creating and not any(
        s in changes for s in ("port", "unix_socket_directories")
    ):
        return

    base_config_path = base_configpath(settings)
    if not fs.exists(base_config_path):
        raise exceptions.SystemError(
            f"Missing base config file {base_config_path} for pgbackrest. "
            "Did you forget to run 'pglift site-configure'?"
        )

    stanza = service.stanza
    stanza_confpath = service.path
    pg = f"pg{service.index}"
    cp = parser()
    if fs.exists(stanza_confpath):
        with fs.open(stanza_confpath) as f:
            cp.read_file(f)

    logger.info(
        "configuring pgBackRest stanza '%s' for pg%d-path=%s",
        stanza,
        service.index,
        service.datadir,
    )
    # Always use string values so that this would match with actual config (on
    # disk) that's parsed later on.
    config = {
        stanza: {
            f"{pg}-path": str(service.datadir),
            f"{pg}-port": str(conf.get_port(instance_config)),
            f"{pg}-user": backuprole,
        },
    }
    if unix_socket_directories := instance_config.get("unix_socket_directories"):
        config[stanza][f"{pg}-socket-path"] = str(unix_socket_directories)
    cp.read_dict(config)
    with fs.open(stanza_confpath, "w") as configfile:
        cp.write(configfile)


def postgresql_configuration(
    stanza: str, settings: _pgbackrest.Settings, version: str, datadir: PurePath
) -> pgconf.Configuration:
    pgconfig = postgresql.template(version, "pgbackrest.conf").format(
        execpath=settings.execpath,
        configpath=settings.configpath,
        stanza=stanza,
        datadir=datadir,
    )
    config = pgconf.Configuration()
    list(config.parse(pgconfig.splitlines()))
    return config


@setup_stanza.revert
@deps.use
def revert_setup_stanza(
    service: s.Service, settings: _pgbackrest.Settings, *, fs: FileSystem = deps.Auto
) -> None:
    """Un-setup pgBackRest.

    Remove options from 'stanza' section referencing instance's datadir, then
    possibly remove the configuration file if empty, and finally remove
    stanza's log files.
    """
    stanza = service.stanza
    logger.info("deconfiguring pgBackRest stanza '%s'", stanza)
    stanza_confpath = service.path
    if fs.exists(stanza_confpath):
        cp = parser()
        with fs.open(stanza_confpath) as f:
            cp.read_file(f)
        for opt in cp.options(stanza):
            if opt.startswith(f"pg{service.index}-"):
                cp.remove_option(stanza, opt)
        with fs.open(stanza_confpath, "w") as f:
            cp.write(f)
        if not cp.options(stanza):
            fs.unlink(stanza_confpath, missing_ok=True)
    if not fs.exists(stanza_confpath):
        for logf in fs.glob(settings.logpath, f"{stanza}-*.log"):
            fs.unlink(logf, missing_ok=True)


@task(title="checking pgBackRest configuration for stanza {service.stanza!r}")
@deps.use
async def check(
    instance: PostgreSQLInstance,
    service: s.Service,
    settings: _pgbackrest.Settings,
    password: str | None,
    *,
    cmd: Command = deps.Auto,
) -> None:
    env = os.environ.copy()
    if password is not None:
        env["PGPASSWORD"] = password
    postgresql_settings = instance._settings.postgresql
    env = pq.environ(instance, postgresql_settings.backuprole.name, base=env)
    await cmd.run(make_cmd(service.stanza, settings, "check"), check=True, env=env)


@deps.use
async def start(
    stanza: str, settings: _pgbackrest.Settings, *, cmd: Command = deps.Auto
) -> None:
    logger.debug("starting pgBackRest processes for stanza %s", stanza)
    await cmd.run(make_cmd(stanza, settings, "start"), check=True)


@deps.use
async def stop(
    stanza: str, settings: _pgbackrest.Settings, *, cmd: Command = deps.Auto
) -> None:
    logger.debug("stopping pgBackRest processes for stanza %s", stanza)
    await cmd.run(make_cmd(stanza, settings, "stop"), check=True)


async def iter_backups(
    instance: Instance, settings: _pgbackrest.Settings
) -> AsyncIterator[i.Backup]:
    """Yield information about backups on an instance."""
    try:
        service = instance.service(s.Service)
    except ValueError:
        raise exceptions.InstanceStateError(
            f"pgBackRest service is not configured for instance {instance}"
        ) from None

    backups = (await backup_info(service, settings))["backup"]

    def started_at(entry: Any) -> float:
        return entry["timestamp"]["start"]  # type: ignore[no-any-return]

    for backup in sorted(backups, key=started_at, reverse=True):
        info_set = await backup_info(service, settings, backup_set=backup["label"])
        databases = [db["name"] for db in info_set["backup"][0]["database-ref"]]
        dtstart = datetime.datetime.fromtimestamp(backup["timestamp"]["start"])
        dtstop = datetime.datetime.fromtimestamp(backup["timestamp"]["stop"])
        yield i.Backup(
            label=backup["label"],
            size=backup["info"]["size"],
            # For a "block incremental backup", the size is not returned.
            repo_size=backup["info"]["repository"].get("size"),
            date_start=dtstart.replace(tzinfo=gettz()),
            date_stop=dtstop.replace(tzinfo=gettz()),
            type=backup["type"],
            databases=databases,
        )


def restore_command(
    service: s.Service,
    settings: _pgbackrest.Settings,
    *,
    date: datetime.datetime | None = None,
    backup_set: str | None = None,
) -> list[str]:
    """Return the pgbackrest restore command for ``service``.

    Ref.: https://pgbackrest.org/command.html#command-restore
    """
    args = [
        # The delta option allows pgBackRest to handle instance data/wal
        # directories itself, without the need to clean them up beforehand.
        "--delta",
        "--link-all",
    ]
    if date is not None and backup_set is not None:
        raise exceptions.UnsupportedError(
            "date and backup_set are not expected to be both specified"
        )
    elif date is not None:
        target = date.strftime("%Y-%m-%d %H:%M:%S.%f%z")
        args += ["--target-action=promote", "--type=time", f"--target={target}"]
    elif backup_set is not None:
        args += ["--target-action=promote", "--type=immediate", f"--set={backup_set}"]
    args.append("restore")
    return make_cmd(service.stanza, settings, *args)


@deps.use
async def restore(
    instance: Instance,
    settings: _pgbackrest.Settings,
    *,
    label: str | None = None,
    date: datetime.datetime | None = None,
    cmd: Command = deps.Auto,
) -> None:
    """Restore an instance, possibly only including specified databases.

    The instance must not be running.

    Ref.: https://pgbackrest.org/command.html#command-restore
    """
    pg_instance = instance.postgresql
    if pg_instance.standby:
        raise exceptions.InstanceReadOnlyError(pg_instance)

    try:
        service = instance.service(s.Service)
    except ValueError:
        raise exceptions.InstanceStateError(
            f"pgBackRest service is not configured for instance {instance}"
        ) from None

    logger.info("restoring instance %s with pgBackRest", instance)
    cmd_args = restore_command(service, settings, date=date, backup_set=label)
    await cmd.run(cmd_args, check=True)


def env_for(service: s.Service, settings: _pgbackrest.Settings) -> dict[str, str]:
    return {
        "PGBACKREST_CONFIG_PATH": str(settings.configpath),
        "PGBACKREST_STANZA": service.stanza,
    }


@deps.use
def site_configure_install(
    settings: Settings, config: configparser.ConfigParser, *, fs: FileSystem = deps.Auto
) -> None:
    s = get_settings(settings)
    if not fs.exists(global_configpath := base_configpath(s)):
        util.check_or_create_directory(
            global_configpath.parent, "base pgBackRest configuration"
        )
        logger.info("installing base pgBackRest configuration")
        with fs.open(global_configpath, "w") as f:
            config.write(f)
    create_include_directory(s)


@deps.use
def site_configure_uninstall(settings: Settings, *, fs: FileSystem = deps.Auto) -> None:
    s = get_settings(settings)
    delete_include_directory(s)
    if fs.exists(global_configpath := base_configpath(s)):
        logger.info("uninstalling base pgBackRest configuration")
        fs.unlink(global_configpath, missing_ok=True)


@deps.use
def site_configure_check(
    settings: Settings, log: bool, *, fs: FileSystem = deps.Auto
) -> Iterator[bool]:
    s = get_settings(settings)
    for p in (config_directory(s), base_configpath(s)):
        if not fs.exists(p):
            if log:
                logger.error("pgBackRest configuration path %s missing", p)
            yield False
        else:
            yield True


def site_configure_list(settings: Settings) -> Iterator[Path]:
    s = get_settings(settings)
    yield config_directory(s)
    yield base_configpath(s)


@contextlib.contextmanager
def instance_dropped(instance: Instance) -> Iterator[s.Service | None]:
    try:
        service = instance.service(s.Service)
    except ValueError:
        yield None
        return
    yield service
    revert_setup_stanza(service, get_settings(instance._settings))

# SPDX-FileCopyrightText: 2021 Dalibo
#
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

import contextlib
import io
import os
import re
import subprocess
import tempfile
import warnings
from collections.abc import AsyncIterator, Iterator, Sequence
from pathlib import Path
from re import Pattern
from typing import IO, Any, Literal, NoReturn

import pgtoolkit.conf as pgconf

from .. import (
    async_hook,
    conf,
    deps,
    exceptions,
    execpath,
    h,
    hookimpl,
    hooks,
    systemd,
    util,
)
from ..models import Instance, PostgreSQLInstance, interface
from ..settings import Settings, _postgresql, postgresql_waldir
from ..system import Command, FileSystem, db
from ..types import ConfigChanges, PostgreSQLStopMode, Status
from .ctl import WAIT_TIMEOUT as WAIT_TIMEOUT
from .ctl import bindir as bindir
from .ctl import check_status as check_status
from .ctl import is_ready as is_ready
from .ctl import is_running as is_running
from .ctl import logfile as logfile
from .ctl import logs as logs
from .ctl import pg_ctl
from .ctl import replication_lag as replication_lag
from .ctl import status as status
from .ctl import wait_ready as wait_ready
from .ctl import wal_replay_pause_state as wal_replay_pause_state
from .ctl import wal_sender_state as wal_sender_state
from .models import Initdb
from .models import RewindSource as RewindSource
from .models import Standby as Standby

logger = util.get_logger(__name__)

POSTGRESQL_SERVICE_NAME = "pglift-postgresql@.service"
HBA_HEADERS_PATTERN = re.compile(r"#.*TYPE.*DATABASE.*USER.*ADDRESS.*METHOD")
IDENT_HEADERS_PATTERN = re.compile(r"#.*MAPNAME.*SYSTEM-USERNAME.*PG-USERNAME")


@hookimpl
async def site_configure_install(settings: Settings) -> None:
    if settings.postgresql.logpath is not None:
        util.check_or_create_directory(
            settings.postgresql.logpath, "PostgreSQL log", mode=0o740
        )


@hookimpl
async def site_configure_uninstall(settings: Settings) -> None:
    _uninstall(settings.postgresql)


@deps.use
def _uninstall(settings: _postgresql.Settings, *, fs: FileSystem = deps.Auto) -> None:
    if settings.logpath is not None and fs.exists(settings.logpath):
        logger.info("deleting PostgreSQL log directory")
        fs.rmtree(settings.logpath)
    if fs.exists(settings.socket_directory):
        logger.info("deleting PostgreSQL socket directory")
        fs.rmtree(settings.socket_directory)


@hookimpl
def site_configure_check(settings: Settings, log: bool) -> Iterator[bool]:
    yield _check(settings.postgresql, log)


@deps.use
def _check(
    settings: _postgresql.Settings, log: bool, *, fs: FileSystem = deps.Auto
) -> bool:
    if settings.logpath is not None and not fs.exists(settings.logpath):
        if log:
            logger.error("PostgreSQL log directory '%s' missing", settings.logpath)
        return False
    return True


@hookimpl
def site_configure_list(settings: Settings) -> Iterator[Path]:
    if settings.postgresql.logpath is not None:
        yield settings.postgresql.logpath


@hookimpl(trylast=True)
def postgresql_service_name() -> str:
    return "postgresql"


@hookimpl(trylast=True)
async def standby_model(
    instance: PostgreSQLInstance, standby: Standby, running: bool
) -> Standby:
    values: dict[str, Any] = {
        "primary_conninfo": standby.primary_conninfo,
        "slot": standby.slot,
        "password": standby.password,
    }
    if running:
        values["replication_lag"] = await replication_lag(instance)
        values["wal_replay_pause_state"] = await wal_replay_pause_state(instance)
    values["wal_sender_state"] = await wal_sender_state(instance)
    return Standby.model_validate(values)


async def postgresql_editable_conf(
    instance: PostgreSQLInstance,
) -> pgconf.Configuration:
    return instance.configuration(managed_only=True)


async def postgresql_conf(instance: PostgreSQLInstance) -> pgconf.Configuration:
    return instance.configuration()


@deps.use
async def init_replication(
    instance: PostgreSQLInstance, standby: Standby, *, cmd: Command = deps.Auto
) -> None:
    cmd_args = [
        str(bindir(instance) / "pg_basebackup"),
        "--pgdata",
        str(instance.datadir),
        "--write-recovery-conf",
        "--checkpoint=fast",
        "--no-password",
        "--progress",
        "--verbose",
        "--dbname",
        standby.primary_conninfo,
        "--waldir",
        str(instance.waldir),
    ]

    if standby.slot:
        cmd_args += ["--slot", standby.slot]

    env = None
    if standby.password:
        env = os.environ.copy()
        env["PGPASSWORD"] = standby.password.get_secret_value()
    await cmd.run(cmd_args, check=True, env=env)


async def initdb(
    manifest: interface.PostgreSQLInstance, instance: PostgreSQLInstance
) -> None:
    """Initialize the PostgreSQL database cluster with plain initdb."""
    pgctl = await pg_ctl(bindir(instance))

    settings = instance._settings
    auth_opts = auth_options(manifest.auth, settings.postgresql.auth).model_dump(
        exclude={"hostssl"}
    )
    opts = {f"auth_{m}": v for m, v in auth_opts.items()} | initdb_options(
        manifest, settings.postgresql
    ).model_dump(mode="json", exclude_none=True)

    surole = manifest.surole(settings)
    if surole.password:
        with tempfile.NamedTemporaryFile("w") as pwfile:
            pwfile.write(surole.password.get_secret_value())
            pwfile.flush()
            await pgctl.init(instance.datadir, pwfile=pwfile.name, **opts)
    else:
        await pgctl.init(instance.datadir, **opts)


async def init_postgresql(
    manifest: interface.Instance, instance: PostgreSQLInstance
) -> None:
    if (
        await async_hook(
            instance._settings,
            h.restore_postgresql,
            instance=instance,
            manifest=manifest,
        )
        is None
    ):
        if manifest.standby:
            await init_replication(instance=instance, standby=manifest.standby)
        else:
            await initdb(manifest, instance)


async def deinit_postgresql(instance: PostgreSQLInstance) -> None:
    if await is_running(instance):
        await stop_postgresql(instance, mode="fast", wait=True)
    delete_postgresql_data(instance)


@deps.use
def delete_postgresql_data(
    instance: PostgreSQLInstance, *, fs: FileSystem = deps.Auto
) -> None:
    logger.info("deleting PostgreSQL data and WAL directories")
    for path in (instance.datadir, instance.waldir):
        if fs.exists(path):
            util.rmtree(path)


def initdb_options(
    manifest: interface.PostgreSQLInstance, settings: _postgresql.Settings, /
) -> Initdb:
    base = settings.initdb
    data_checksums: Literal[True] | None = {
        True: True,
        False: None,
        None: base.data_checksums or None,
    }[manifest.data_checksums]
    return Initdb(
        locale=manifest.locale or base.locale,
        encoding=manifest.encoding or base.encoding,
        data_checksums=data_checksums,
        username=settings.surole.name,
        waldir=postgresql_waldir(
            settings, version=manifest.version, name=manifest.name
        ),
        allow_group_access=base.allow_group_access,
    )


def auth_options(
    value: interface.Auth | None, /, settings: _postgresql.AuthSettings
) -> interface.Auth:
    local, host, hostssl = settings.local, settings.host, settings.hostssl
    if value:
        local = value.local or local
        host = value.host or host
        hostssl = value.hostssl or hostssl
    return interface.Auth(local=local, host=host, hostssl=hostssl)


def pg_hba(manifest: interface.PostgreSQLInstance, /, settings: Settings) -> str:
    surole_name = settings.postgresql.surole.name
    replrole_name = settings.postgresql.replrole
    auth = auth_options(manifest.auth, settings.postgresql.auth)
    return template(manifest.version, "pg_hba.conf").format(
        auth=auth,
        surole=surole_name,
        backuprole=settings.postgresql.backuprole.name,
        replrole=replrole_name,
    )


def pg_ident(manifest: interface.PostgreSQLInstance, /, settings: Settings) -> str:
    surole_name = settings.postgresql.surole.name
    replrole_name = settings.postgresql.replrole
    return template(manifest.version, "pg_ident.conf").format(
        surole=surole_name,
        backuprole=settings.postgresql.backuprole.name,
        replrole=replrole_name,
        sysuser=settings.sysuser[0],
    )


def configuration(
    manifest: interface.Instance, settings: Settings, *, _template: str | None = None
) -> pgconf.Configuration:
    """Return the PostgreSQL configuration built from manifest and
    'postgresql.conf' site template (the former taking precedence over the
    latter).

    'shared_buffers' and 'effective_cache_size' setting, if defined and set to
    a percent-value, will be converted to proper memory value relative to the
    total memory available on the system.
    """
    if _template is None:
        _template = template(manifest.version, "postgresql.conf")
    # Load base configuration from site settings.
    try:
        confitems = pgconf.parse_string(_template).as_dict()
    except pgconf.ParseError as e:
        raise exceptions.SettingsError(f"invalid postgresql.conf template: {e}") from e

    # Transform initdb options as configuration parameters.
    if locale := initdb_options(manifest, settings.postgresql).locale:
        for key in ("lc_messages", "lc_monetary", "lc_numeric", "lc_time"):
            confitems.setdefault(key, locale)

    if manifest.port is not None:
        confitems["port"] = manifest.port
    confitems.update(manifest.settings)

    spl = confitems.get("shared_preload_libraries", "")
    if not isinstance(spl, str):
        raise exceptions.InstanceStateError(
            f"expecting a string value for 'shared_preload_libraries' setting: {spl!r}"
        )

    for plugin, r in hooks(
        settings, h.instance_settings, manifest=manifest, settings=settings
    ):
        for k, v in r.entries.items():
            plugin_conf = v.value
            if k in confitems and plugin_conf != confitems[k]:
                logger.info(
                    "parameter %r is overwritten by %r configuration, %r will be used instead of %r",
                    k,
                    plugin,
                    plugin_conf,
                    confitems[k],
                )
            if k == "shared_preload_libraries":
                assert isinstance(plugin_conf, str), (
                    f"expecting a string, got {plugin_conf!r}"
                )
                spl = conf.merge_lists(spl, plugin_conf)
            else:
                confitems[k] = plugin_conf

    if spl:
        confitems["shared_preload_libraries"] = spl

    conf.format_values(confitems, manifest.name, manifest.version, settings.postgresql)

    return conf.make(**confitems)


async def configure(
    instance: PostgreSQLInstance, manifest: interface.Instance
) -> ConfigChanges:
    logger.info("configuring PostgreSQL")
    config = configuration(manifest, instance._settings)
    return await configure_postgresql(config, instance, manifest)


async def configure_postgresql(
    configuration: pgconf.Configuration,
    instance: PostgreSQLInstance,
    manifest: interface.Instance,  # noqa: ARG001
) -> ConfigChanges:
    postgresql_conf = conf.read(instance.datadir, managed_only=True)
    config_before = postgresql_conf.as_dict()
    if instance.standby:
        # For standby instances we want to keep the parameters set in the primary
        # and only override the new values.
        # This is specifically the case for max_connections which must be
        # greater than or equal to the value set on the primary.
        conf.merge(postgresql_conf, **configuration.as_dict())
    else:
        # Capture UseWarning from pgtoolkit.conf.edit()
        # TODO: from Python 3.11, use:
        #       warnings.catch_warnings(record=True, action="default", category=UserWarning)
        with warnings.catch_warnings(record=True) as ws:
            warnings.filterwarnings("default", category=UserWarning)
            conf.update(postgresql_conf, **configuration.as_dict())
        for w in ws:
            logger.warning(str(w.message))
    config_after = postgresql_conf.as_dict()
    changes = conf.changes(config_before, config_after)

    if changes:
        conf.save(instance.datadir, postgresql_conf)

    return changes


def hba_path(instance: PostgreSQLInstance) -> Path:
    return instance.datadir / "pg_hba.conf"


def conf_headers(file: IO[str], pattern: Pattern[str]) -> str:
    """Read and return all lines that appear before the last occurrence of
    the given pattern in a file-like object.

    If the pattern is not found, return empty string.

    >>> from io import StringIO
    >>> import re
    >>> content = "Hello World!\\nPattern\\nSomething\\nPattern\\nElse"
    >>> f = StringIO(content)
    >>> conf_headers(f, re.compile(r"Pattern"))
    'Hello World!\\nPattern\\nSomething\\nPattern\\n'
    >>> f = StringIO(content)
    >>> conf_headers(f, re.compile(r"Notinfile"))
    ''
    """
    lines = file.readlines()
    last_index = 0

    for i, line in enumerate(lines):
        if pattern.search(line):
            last_index = i + 1
    return "".join(lines[:last_index])


def configure_auth(
    instance: PostgreSQLInstance, manifest: interface.PostgreSQLInstance
) -> Literal[True]:
    """Configure authentication for the PostgreSQL instance."""
    logger.info("configuring PostgreSQL authentication")
    hba = pg_hba(manifest, instance._settings)
    _write_hba(instance, hba, configuring=True)
    ident = pg_ident(manifest, instance._settings)
    _write_ident(instance, ident)
    return True


async def pg_hba_config(instance: PostgreSQLInstance) -> list[str]:
    return _read_hba(instance)


async def configure_pg_hba(instance: PostgreSQLInstance, hba: list[str]) -> None:
    _write_hba(instance, "\n".join(hba))


@deps.use
def _read_hba(instance: PostgreSQLInstance, *, fs: FileSystem = deps.Auto) -> list[str]:
    with fs.open(hba_path(instance)) as f:
        return f.readlines()


@deps.use
def _write_hba(
    instance: PostgreSQLInstance,
    content: str,
    configuring: bool = False,
    *,
    fs: FileSystem = deps.Auto,
) -> None:
    path = hba_path(instance)
    if configuring:
        with fs.open(path) as f:
            content = conf_headers(f, HBA_HEADERS_PATTERN) + content
    fs.write_text(path, content)


@deps.use
def _write_ident(
    instance: PostgreSQLInstance, content: str, *, fs: FileSystem = deps.Auto
) -> None:
    path = instance.datadir / "pg_ident.conf"
    with fs.open(path) as f:
        headers = conf_headers(f, IDENT_HEADERS_PATTERN)
    fs.write_text(path, headers + content)


def ensure_socket_directory(s: Settings, /) -> None:
    """Ensure socket directory is present if no alternative tmpfiles manager
    (e.g. systemd-tmpfiles) is selected.
    """
    if s.tmpfiles_manager is not None:
        return
    util.check_or_create_directory(
        s.postgresql.socket_directory, "PostgreSQL socket directory"
    )


async def start_postgresql(
    instance: PostgreSQLInstance,
    foreground: bool,
    wait: bool,
    *,
    timeout: int = WAIT_TIMEOUT,
    run_hooks: bool = True,
    **runtime_parameters: str,
) -> None:
    settings = instance._settings
    ensure_socket_directory(settings)
    logger.info("starting PostgreSQL %s", instance)
    if not foreground and run_hooks:
        if await async_hook(
            settings,
            h.start_service,
            settings=settings,
            service=postgresql_service_name(),
            name=instance.qualname,
        ):
            if wait:
                await wait_ready(instance, timeout=timeout)
            return

    options: list[str] = []
    for name, value in runtime_parameters.items():
        options.extend(["-c", f"{name}={value}"])
    if foreground:
        _start_with_postgres(instance, options)
    else:
        await _start_with_pgctl(instance, options, wait, timeout)


@deps.use
def _start_with_postgres(
    instance: PostgreSQLInstance, options: Sequence[str], *, cmd: Command = deps.Auto
) -> NoReturn:
    """Start PostgreSQL with 'postgres'."""
    command = [str(bindir(instance) / "postgres"), "-D", str(instance.datadir)]
    cmd.execute_program(command + list(options))


@deps.use
async def _start_with_pgctl(
    instance: PostgreSQLInstance,
    options: Sequence[str],
    wait: bool,
    timeout: int,
    *,
    cmd: Command = deps.Auto,
    fs: FileSystem = deps.Auto,
) -> None:
    """Start PostgreSQL with 'pg_ctl start', handling log redirection the best we can."""
    pgctl = await pg_ctl(bindir(instance))
    command = [str(pgctl.pg_ctl), "start", "-D", str(instance.datadir)]
    if options:
        command.extend(["-o", " ".join(options)])
    if wait:
        command.extend(["--wait", f"--timeout={timeout}"])
    # When starting the server, pg_ctl captures its stdout/stderr and
    # redirects them to its own stdout (not stderr) unless the -l option
    # is used. So without the -l option, the pg_ctl process will get its
    # stdout filled as long as the underlying server is running. If we
    # capture this stream to a pipe, we will not be able to continue and
    # ultimately exit pglift as the pipe will keep being used. If we don't
    # capture it, it'd go to parent's process stdout and pollute the
    # output.
    # So we have two options:
    if logdir := instance._settings.postgresql.logpath:
        # 1. We have a place to put the log file, let's use -l option.
        logpath = logdir / f"{instance.qualname}-start.log"
        # Note: if the logging collector is not enabled, log messages from
        # the server will keep coming in this file.
        command.extend(["-l", str(logpath)])
        fs.touch(logpath)
        with fs.open(logpath) as f:
            f.seek(0, io.SEEK_END)
            try:
                await cmd.run(command, log_stdout=True, check=True)
            except exceptions.CommandError:
                for line in f:
                    logger.warning("%s: %s", pgctl.pg_ctl, line.rstrip())
                raise
    else:
        # 2. We don't, redirect to /dev/null and lose messages.
        logger.debug(
            "not capturing 'pg_ctl start' output as postgresql.logpath setting is disabled"
        )
        await cmd.run(
            command,
            capture_output=False,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=True,
        )
    if wait:
        await wait_ready(instance)


async def stop_postgresql(
    instance: PostgreSQLInstance,
    mode: PostgreSQLStopMode,
    wait: bool,
    deleting: bool = False,  # noqa: ARG001
    run_hooks: bool = True,
) -> None:
    logger.info("stopping PostgreSQL %s", instance)

    if run_hooks:
        settings = instance._settings
        if await async_hook(
            settings,
            h.stop_service,
            settings=settings,
            service=postgresql_service_name(),
            name=instance.qualname,
        ):
            return

    pgctl = await pg_ctl(bindir(instance))
    await pgctl.stop(instance.datadir, mode=mode, wait=wait)


async def restart_postgresql(
    instance: PostgreSQLInstance, mode: PostgreSQLStopMode, wait: bool
) -> None:
    logger.info("restarting PostgreSQL")
    await stop_postgresql(instance, mode=mode, wait=wait)
    await start_postgresql(instance, foreground=False, wait=wait)


async def reload_postgresql(instance: PostgreSQLInstance) -> None:
    logger.info(f"reloading PostgreSQL configuration for {instance}")
    async with db.connect(instance) as cnx:
        await db.execute(cnx, "SELECT pg_reload_conf()")


async def promote_postgresql(instance: PostgreSQLInstance) -> None:
    await promote(instance)


@deps.use
async def promote(instance: PostgreSQLInstance, *, cmd: Command = deps.Auto) -> None:
    logger.info("promoting PostgreSQL instance")
    pgctl = await pg_ctl(bindir(instance))
    await cmd.run(
        [str(pgctl.pg_ctl), "promote", "-D", str(instance.datadir)],
        check=True,
    )


async def demote_postgresql(
    instance: PostgreSQLInstance,
    source: RewindSource,
    *,
    rewind_opts: Sequence[str] = (),
) -> None:
    logger.info("demoting PostgreSQL instance")
    await rewind(instance, source, extra_opts=rewind_opts)


async def pause_wal_replay(instance: PostgreSQLInstance) -> None:
    if not instance.standby:
        raise exceptions.InstanceStateError(f"{instance} is not a standby")
    async with db.connect(instance) as cnx:
        logger.info("pausing WAL replay")
        await db.execute(cnx, "SELECT pg_wal_replay_pause()")


async def resume_wal_replay(instance: PostgreSQLInstance) -> None:
    if not instance.standby:
        raise exceptions.InstanceStateError(f"{instance} is not a standby")
    async with db.connect(instance) as cnx:
        logger.info("resuming WAL replay")
        await db.execute(cnx, "SELECT pg_wal_replay_resume()")


@deps.use
async def rewind(
    instance: PostgreSQLInstance,
    source: RewindSource,
    *,
    extra_opts: Sequence[str] = (),
    cmd: Command = deps.Auto,
) -> None:
    """Rewind 'instance' from 'source' server as standby (through
    --write-recovery-conf).
    """
    pg_rewind = bindir(instance) / "pg_rewind"
    cmd_args = [
        str(pg_rewind),
        "-D",
        str(instance.datadir),
        "--source-server",
        source.conninfo,
        "--write-recovery-conf",
    ]
    cmd_args.extend(extra_opts)
    env = None
    if source.password is not None:
        env = os.environ.copy()
        env["PGPASSWORD"] = source.password.get_secret_value()
    await cmd.run(cmd_args, check=True, env=env)


@util.cache
def template(version: str, *args: str) -> str:
    r"""Return the content of a PostgreSQL configuration file (in a postgresql/
    directory in site configuration or distribution data), first looking into
    'postgresql/<version>' base directory.

    >>> print(template("16", "psqlrc"))
    \set PROMPT1 '[{instance}] %n@%~%R%x%# '
    \set PROMPT2 ' %R%x%# '
    <BLANKLINE>
    """
    bases = (("postgresql", version), "postgresql")
    logger.debug("loading %s template", util.joinpath(*args))
    return util.template(bases, *args)


@contextlib.asynccontextmanager
async def running(
    instance: PostgreSQLInstance, *, timeout: int = WAIT_TIMEOUT
) -> AsyncIterator[None]:
    """Context manager to temporarily start a PostgreSQL instance."""
    if await is_running(instance):
        yield
        return

    await start_postgresql(
        instance,
        foreground=False,
        wait=True,
        timeout=timeout,
        run_hooks=False,
        # Keep logs to stderr, uncollected, to get meaningful errors on our side.
        logging_collector="off",
        log_destination="stderr",
    )
    try:
        yield
    finally:
        await stop_postgresql(instance, mode="fast", wait=True, run_hooks=False)


@hookimpl
def systemd_units() -> list[str]:
    return [POSTGRESQL_SERVICE_NAME]


@hookimpl
def systemd_unit_templates(settings: Settings) -> Iterator[tuple[str, str]]:
    yield (
        POSTGRESQL_SERVICE_NAME,
        systemd.template(POSTGRESQL_SERVICE_NAME).format(
            executeas=systemd.executeas(settings),
            execpath=execpath,
            environment=systemd.environment(util.environ()),
        ),
    )


@hookimpl
def systemd_tmpfilesd_managed_dir(settings: Settings) -> Iterator[tuple[str, Path]]:
    yield "postgresql", settings.postgresql.socket_directory


@hookimpl
def logrotate_config(settings: Settings) -> str | None:
    if settings.postgresql.logpath is None:
        logger.warning(
            "postgresql.logpath setting is unset; logrotate will not handle PostgreSQL logs"
        )
        return None
    return util.template("postgresql", "logrotate.conf").format(
        logpath=settings.postgresql.logpath
    )


@hookimpl
def rsyslog_config(settings: Settings) -> str | None:
    if settings.postgresql.logpath is None:
        logger.warning(
            "postgresql.logpath setting is unset; rsyslog will not handle PostgreSQL logs"
        )
        return None
    user, group = settings.sysuser
    return util.template("postgresql", "rsyslog.conf").format(
        logpath=settings.postgresql.logpath, user=user, group=group
    )


@hookimpl
async def instance_status(instance: Instance) -> tuple[Status, str]:
    return (await status(instance.postgresql), "PostgreSQL")

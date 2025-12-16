# SPDX-FileCopyrightText: 2021 Dalibo
#
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

import configparser
from collections.abc import Iterator
from pathlib import Path

import pgtoolkit.conf as pgconf

from .. import deps, exceptions, hookimpl, postgresql, types, ui, util
from ..models import Instance, PostgreSQLInstance, interface
from ..settings import Settings, _pgbackrest
from ..system import Command, FileSystem
from ..task import task
from ..types import DEFAULT_BACKUP_TYPE, BackupType, CompletedProcess
from . import base
from . import register_if as base_register_if
from .base import get_settings
from .models import interface as i
from .models import system as s

logger = util.get_logger(__name__)

PathRepository = _pgbackrest.PathRepository


def register_if(settings: Settings) -> bool:
    if not base_register_if(settings):
        return False
    s = get_settings(settings)
    return isinstance(s.repository, PathRepository)


@hookimpl
async def site_configure_install(settings: Settings) -> None:
    s = get_settings(settings)
    base.site_configure_install(settings, base_config(s))
    util.check_or_create_directory(
        repository_settings(s).path, "pgBackRest repository backups and archive"
    )


@hookimpl
async def site_configure_uninstall(settings: Settings) -> None:
    base.site_configure_uninstall(settings)
    s = get_settings(settings)
    uninstall(s)


@deps.use
def uninstall(settings: _pgbackrest.Settings, *, fs: FileSystem = deps.Auto) -> None:
    # XXX isn't this the responsibility of base.site_configure_uninstall()?
    util.rmdir(settings.configpath)
    if fs.exists(repo_path := repository_settings(settings).path):
        if ui.confirm(f"Delete pgbackrest repository path {repo_path}?", False):
            fs.rmtree(repo_path)
            logger.info("deleted pgBackRest repository path")


@hookimpl
def site_configure_check(settings: Settings, log: bool) -> Iterator[bool]:
    yield from base.site_configure_check(settings, log)
    s = get_settings(settings)
    yield check(s, log)


@deps.use
def check(
    settings: _pgbackrest.Settings, log: bool, *, fs: FileSystem = deps.Auto
) -> bool:
    if not fs.exists(repo_path := repository_settings(settings).path):
        if log:
            logger.error("pgBackRest repository path %s missing", repo_path)
        return False
    return True


@hookimpl
def site_configure_list(settings: Settings) -> Iterator[Path]:
    yield from base.site_configure_list(settings)
    s = get_settings(settings)
    yield repository_settings(s).path


@hookimpl
async def postgresql_configured(
    instance: PostgreSQLInstance,
    manifest: interface.Instance,
    config: pgconf.Configuration,
    changes: types.ConfigChanges,
) -> None:
    try:
        service = manifest.service(i.Service)
    except ValueError:
        return
    svc = base.setup(
        instance, service, config, changes, manifest.creating, manifest.upgrading_from
    )
    settings = instance._settings
    s = get_settings(settings)

    if manifest.upgrading_from is not None:
        await upgrade(svc, s)
    elif manifest.creating:
        await init(svc, s)

    if manifest.creating and await postgresql.is_running(instance):
        password = None
        backup_role = base.role(instance._settings, service)
        assert backup_role is not None
        if backup_role.password is not None:
            password = backup_role.password.get_secret_value()
        if instance.standby:
            logger.warning("not checking pgBackRest configuration on a standby")
        else:
            await base.check(instance, svc, s, password)


@hookimpl
async def instance_dropped(instance: Instance) -> None:
    with base.instance_dropped(instance) as service:
        if not service:
            return
        settings = get_settings(instance._settings)
        if not (
            nb_backups := len((await base.backup_info(service, settings))["backup"])
        ) or (
            can_delete_stanza(service)
            and ui.confirm(
                f"Confirm deletion of {nb_backups} backup(s) for stanza {service.stanza!r}?",
                False,
            )
        ):
            await delete_stanza(service, settings)


def repository_settings(settings: _pgbackrest.Settings) -> PathRepository:
    assert isinstance(settings.repository, PathRepository)
    return settings.repository


def base_config(settings: _pgbackrest.Settings) -> configparser.ConfigParser:
    cp = base.parser()
    cp.read_string(base.template("pgbackrest.conf").format(**dict(settings)))
    s = repository_settings(settings)
    cp["global"]["repo1-path"] = str(s.path)
    for opt, value in s.retention:
        cp["global"][f"repo1-retention-{opt}"] = str(value)
    return cp


@task(title="creating pgBackRest stanza {service.stanza!r}")
@deps.use
async def init(
    service: s.Service, settings: _pgbackrest.Settings, *, cmd: Command = deps.Auto
) -> None:
    await cmd.run(
        base.make_cmd(service.stanza, settings, "stanza-create", "--no-online"),
        check=True,
    )


@init.revert
async def revert_init(service: s.Service, settings: _pgbackrest.Settings) -> None:
    if not can_delete_stanza(service):
        logger.debug(
            "not deleting stanza '%s', still used by another instance", service.stanza
        )
        return
    await delete_stanza(service, settings)


def can_delete_stanza(service: s.Service) -> bool:
    for idx, path in base.stanza_pgpaths(service.path, service.stanza):
        if (idx, path) != (service.index, service.datadir):
            return False
    return True


@deps.use
async def delete_stanza(
    service: s.Service, settings: _pgbackrest.Settings, *, cmd: Command = deps.Auto
) -> None:
    stanza = service.stanza
    logger.info("deleting pgBackRest stanza '%s'", stanza)
    await base.stop(stanza, settings)
    await cmd.run(
        base.make_cmd(
            stanza,
            settings,
            "stanza-delete",
            "--pg1-path",
            str(service.datadir),
            "--force",
        ),
        check=True,
    )


@deps.use
async def upgrade(
    service: s.Service, settings: _pgbackrest.Settings, *, cmd: Command = deps.Auto
) -> None:
    """Upgrade stanza"""
    stanza = service.stanza
    logger.info("upgrading pgBackRest stanza '%s'", stanza)
    await cmd.run(
        base.make_cmd(stanza, settings, "stanza-upgrade", "--no-online"), check=True
    )


def backup_command(
    service: s.Service,
    settings: _pgbackrest.Settings,
    *,
    type: BackupType = DEFAULT_BACKUP_TYPE,
    start_fast: bool = True,
    backup_standby: bool = False,
) -> list[str]:
    """Return the full pgbackrest command to perform a backup for ``instance``.

    :param type: backup type (one of 'full', 'incr', 'diff').

    Ref.: https://pgbackrest.org/command.html#command-backup
    """
    args = [f"--type={type}", "backup"]
    if start_fast:
        args.insert(-1, "--start-fast")
    if backup_standby:
        args.insert(-1, "--backup-standby")
    return base.make_cmd(service.stanza, settings, *args)


@deps.use
async def backup(
    instance: Instance,
    settings: _pgbackrest.Settings,
    *,
    type: BackupType = DEFAULT_BACKUP_TYPE,
    cmd: Command = deps.Auto,
) -> CompletedProcess:
    """Perform a backup of ``instance``.

    :param type: backup type (one of 'full', 'incr', 'diff').

    Ref.: https://pgbackrest.org/command.html#command-backup
    """
    try:
        svc = instance.service(s.Service)
    except ValueError:
        raise exceptions.InstanceStateError(
            f"pgBackRest service is not configured for instance {instance}"
        ) from None

    logger.info("backing up instance %s with pgBackRest", instance)
    pg_instance = instance.postgresql
    cmd_args = backup_command(
        svc, settings, type=type, backup_standby=pg_instance.standby is not None
    )
    postgresql_settings = instance._settings.postgresql
    env = postgresql.pq.environ(pg_instance, postgresql_settings.backuprole.name)
    return await cmd.run(cmd_args, check=True, env=env)

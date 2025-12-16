# SPDX-FileCopyrightText: 2021 Dalibo
#
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

import shlex
from collections.abc import Iterator
from pathlib import Path
from typing import Annotated, Any, Final, Literal

import pgtoolkit.conf as pgconf
from pydantic import Field, ValidationError, ValidationInfo, field_validator

from .. import deps, exceptions, hookimpl, types, ui, util
from ..models import Instance, PostgreSQLInstance, interface
from ..settings import Settings, _pgbackrest, postgresql_datadir
from ..system import Command, FileSystem
from . import base
from .base import available as available
from .base import backup_info as backup_info
from .base import check as check
from .base import enabled as enabled
from .base import get_settings as get_settings
from .base import iter_backups as iter_backups
from .base import make_cmd as make_cmd
from .base import restore as restore
from .base import start as start
from .base import stop as stop
from .models import interface as i
from .models import system as s

__all__ = ["available", "backup", "iter_backups", "restore"]

logger = util.get_logger(__name__)


def register_if(settings: Settings) -> bool:
    return available(settings) is not None


def dirs(settings: _pgbackrest.Settings) -> list[tuple[Path, str]]:
    return [(settings.logpath, "log"), (settings.spoolpath, "spool")]


@hookimpl
async def site_configure_install(settings: Settings) -> None:
    s = get_settings(settings)
    for d, purpose in dirs(s):
        util.check_or_create_directory(d, f"pgBackRest {purpose}")


@hookimpl
async def site_configure_uninstall(settings: Settings) -> None:
    s = get_settings(settings)
    uninstall(s)


@deps.use
def uninstall(settings: _pgbackrest.Settings, *, fs: FileSystem = deps.Auto) -> None:
    for d, purpose in dirs(settings):
        if fs.exists(d):
            logger.info("deleting pgBackRest %s directory", purpose)
            util.rmdir(d)


@hookimpl
def site_configure_check(settings: Settings, log: bool) -> Iterator[bool]:
    s = get_settings(settings)
    yield from _system_configure_check(s, log)


@deps.use
def _system_configure_check(
    settings: _pgbackrest.Settings, log: bool, *, fs: FileSystem = deps.Auto
) -> Iterator[bool]:
    for d, purpose in dirs(settings):
        if not fs.exists(d):
            if log:
                logger.error("pgBackRest %s directory '%s' not found", purpose, d)
            yield False
        else:
            yield True


@hookimpl
def site_configure_list(settings: Settings) -> Iterator[Path]:
    s = get_settings(settings)
    for d, _ in dirs(s):
        yield d


@hookimpl
def system_lookup(instance: PostgreSQLInstance) -> s.Service | None:
    settings = get_settings(instance._settings)
    return base.system_lookup(instance.datadir, settings)


@hookimpl
async def get(instance: Instance) -> i.Service | None:
    try:
        svc = instance.service(s.Service)
    except ValueError:
        return None
    else:
        return i.Service(stanza=svc.stanza)


@hookimpl
def instance_settings(
    manifest: interface.Instance, settings: Settings
) -> tuple[str, pgconf.Configuration]:
    try:
        service_manifest = manifest.service(i.Service)
    except ValueError:
        return "pgbackrest", pgconf.Configuration()
    s = get_settings(settings)
    datadir = postgresql_datadir(
        settings.postgresql, version=manifest.version, name=manifest.name
    )
    return "pgbackrest", base.postgresql_configuration(
        service_manifest.stanza, s, manifest.version, datadir
    )


@deps.use
def check_stanza_not_bound(
    value: str, info: ValidationInfo, *, fs: FileSystem = deps.Auto
) -> None:
    """Check that the stanza is not already bound to an other instance."""

    if not info.context or info.context.get("operation") != "create":
        return

    if info.data.get("upgrading_from"):
        return

    # 'standby' key missing on info.data means that there was a validation
    # error on this field, so we don't try to validate here.
    if "standby" not in info.data or info.data["standby"]:
        return

    settings = info.context["settings"]

    assert settings.pgbackrest
    d = base.config_directory(settings.pgbackrest)
    # info.data may be missing some keys to format the datadir which means
    # that there was a validation error.
    try:
        version, name = info.data["version"], info.data["name"]
    except KeyError:
        return
    datadir = postgresql_datadir(settings.postgresql, version=version, name=name)
    for p in fs.glob(d, "*.conf"):
        cp = base.parser()
        with fs.open(p) as f:
            cp.read_file(f)
        if value not in cp.sections():
            continue
        for k, v in cp.items(value):
            if base.pgpath_rgx.match(k) and v != str(datadir):
                raise ValidationError.from_exception_data(
                    title="Invalid pgBackRest stanza",
                    line_errors=[
                        {
                            "type": "value_error",
                            "loc": ("stanza",),
                            "input": value,
                            "ctx": {
                                "error": f"Stanza {value!r} already bound to another instance (datadir={v})"
                            },
                        }
                    ],
                )


def validate_service(
    cls: Any,  # noqa: ARG001
    value: i.Service | None,
    info: ValidationInfo,
) -> i.Service | None:
    if value is not None:
        check_stanza_not_bound(value.stanza, info)
    return value


@hookimpl
def instance_model() -> types.ComponentModel:
    return types.ComponentModel(
        i.Service.__service__,
        (
            Annotated[
                i.Service | None,
                Field(
                    description="Configuration for the pgBackRest service, if enabled in site settings.",
                    json_schema_extra={"readOnly": True},
                ),
            ],
            None,
        ),
        field_validator(i.Service.__service__)(validate_service),
    )


async def initdb_restore_command(
    instance: PostgreSQLInstance, manifest: interface.Instance
) -> list[str] | None:
    settings = get_settings(instance._settings)
    try:
        service = manifest.service(i.Service)
    except ValueError:
        return None
    svc = base.get_service(instance, service, settings, None)
    if not (await backup_info(svc, settings))["backup"]:
        return None
    return new_from_restore_command(service, settings, instance, manifest)


def new_from_restore_command(
    service_manifest: i.Service,
    settings: _pgbackrest.Settings,
    instance: PostgreSQLInstance,
    manifest: interface.PostgreSQLInstance,
) -> list[str]:
    """Return arguments for 'pgbackrest restore' command to create a new
    instance from a backup; 'instance' represents the new instance.
    """
    cmd_args = [
        str(settings.execpath),
        "--log-level-file=off",
        "--log-level-stderr=info",
        "--config-path",
        str(settings.configpath),
        "--stanza",
        service_manifest.stanza,
        "--pg1-path",
        str(instance.datadir),
    ]
    if instance.waldir != instance.datadir / "pg_wal":
        cmd_args.extend(["--link-map", f"pg_wal={instance.waldir}"])
    if manifest.standby:
        cmd_args.append("--type=standby")
        # Double quote if needed (e.g. to escape white spaces in value).
        value = manifest.standby.full_primary_conninfo.replace("'", "''")
        cmd_args.extend(["--recovery-option", f"primary_conninfo={value}"])
        if manifest.standby.slot:
            cmd_args.extend(
                ["--recovery-option", f"primary_slot_name={manifest.standby.slot}"]
            )
    cmd_args.append("restore")
    return cmd_args


@hookimpl
def patroni_create_replica_method(
    manifest: interface.Instance, instance: PostgreSQLInstance
) -> tuple[str, dict[str, Any]] | None:
    settings = get_settings(instance._settings)
    try:
        service_manifest = manifest.service(i.Service)
    except ValueError:
        return None
    args = new_from_restore_command(service_manifest, settings, instance, manifest)
    return "pgbackrest", {
        "command": shlex.join(args),
        "keep_data": True,
        "no_params": True,
    }


@hookimpl
async def restore_postgresql(
    instance: PostgreSQLInstance, manifest: interface.Instance
) -> Literal[True] | None:
    if manifest.upgrading_from:
        return None
    return await maybe_restore(instance, manifest)


@deps.use
async def maybe_restore(
    instance: PostgreSQLInstance,
    manifest: interface.Instance,
    *,
    cmd: Command = deps.Auto,
) -> Literal[True] | None:
    if (args := await initdb_restore_command(instance, manifest)) is None:
        return None
    if not manifest.standby and not ui.confirm(
        "Confirm creation of instance from pgBackRest backup", True
    ):
        raise exceptions.Cancelled(f"creation of instance {instance} cancelled")
    logger.info("restoring from a pgBackRest backup")
    await cmd.run(args, check=True)
    return True


CHECK_ON_PROMOTE: Final = True


@hookimpl
async def instance_promoted(instance: Instance) -> None:
    if service := await get(instance):
        settings = get_settings(instance._settings)
        pg_instance = instance.postgresql
        svc = base.get_service(pg_instance, service, settings, None)
        if ui.confirm(
            "Check pgBackRest configuration and WAL archival?", CHECK_ON_PROMOTE
        ):
            await check(pg_instance, svc, settings, None)


@hookimpl
def instance_env(instance: Instance) -> dict[str, str]:
    pgbackrest_settings = base.get_settings(instance._settings)
    try:
        service = instance.service(s.Service)
    except ValueError:
        return {}
    return base.env_for(service, pgbackrest_settings)


@hookimpl
def rolename(settings: Settings) -> str:
    return base.rolename(settings)


@hookimpl
def role(settings: Settings, manifest: interface.Instance) -> interface.Role | None:
    try:
        service = manifest.service(i.Service)
    except ValueError:
        return None
    return base.role(settings, service)


@hookimpl
def logrotate_config(settings: Settings) -> str:
    assert settings.logrotate is not None
    s = get_settings(settings)
    return base.template("logrotate.conf").format(logpath=s.logpath)

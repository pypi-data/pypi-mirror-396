# SPDX-FileCopyrightText: 2021 Dalibo
#
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

from collections.abc import Iterator
from pathlib import Path
from typing import Annotated

from pgtoolkit.conf import Configuration
from pydantic import Field

from .. import deps, hookimpl, systemd, types, util
from ..models import Instance, PostgreSQLInstance, interface
from ..settings import Settings
from ..system import FileSystem, svc
from ..types import Status
from . import impl
from .impl import available as available
from .impl import get_settings
from .models import interface as i
from .models import system as s

logger = util.get_logger(__name__)


def register_if(settings: Settings) -> bool:
    return available(settings) is not None


@hookimpl
async def site_configure_install(settings: Settings) -> None:
    s = get_settings(settings)
    util.check_or_create_directory(s.logpath, "temBoard log", mode=0o740)


@hookimpl
async def site_configure_uninstall(settings: Settings) -> None:
    uninstall(settings)


@deps.use
def uninstall(settings: Settings, *, fs: FileSystem = deps.Auto) -> None:
    s = get_settings(settings)
    if fs.exists(s.logpath):
        logger.info("deleting temBoard log directory")
        fs.rmtree(s.logpath)


@hookimpl
def site_configure_check(settings: Settings, log: bool) -> Iterator[bool]:
    yield check(settings, log)


@deps.use
def check(settings: Settings, log: bool, *, fs: FileSystem = deps.Auto) -> bool:
    s = get_settings(settings)
    if not fs.exists(s.logpath):
        if log:
            logger.error("temBoard log directory '%s' missing", s.logpath)
        return False
    return True


@hookimpl
def site_configure_list(settings: Settings) -> Iterator[Path]:
    s = get_settings(settings)
    yield s.logpath


@hookimpl
def system_lookup(instance: PostgreSQLInstance) -> s.Service | None:
    settings = get_settings(instance._settings)
    return impl.system_lookup(instance.qualname, settings)


@hookimpl
def instance_model() -> types.ComponentModel:
    return types.ComponentModel(
        i.Service.__service__,
        (
            Annotated[
                i.Service,
                Field(
                    description="Configuration for the temBoard service, if enabled in site settings.",
                    validate_default=True,
                ),
            ],
            i.Service(),
        ),
    )


@hookimpl
async def get(instance: Instance) -> i.Service | None:
    try:
        svc = instance.service(s.Service)
    except ValueError:
        return None
    else:
        return i.Service(port=svc.port, password=svc.password)


SYSTEMD_SERVICE_NAME = "pglift-temboard_agent@.service"


@hookimpl
def systemd_units() -> list[str]:
    return [SYSTEMD_SERVICE_NAME]


@hookimpl
def systemd_unit_templates(settings: Settings) -> Iterator[tuple[str, str]]:
    s = get_settings(settings)
    configpath = str(s.configpath).replace("{name}", "%i")
    yield (
        SYSTEMD_SERVICE_NAME,
        systemd.template(SYSTEMD_SERVICE_NAME).format(
            executeas=systemd.executeas(settings),
            configpath=configpath,
            execpath=s.execpath,
        ),
    )


@hookimpl
def systemd_tmpfilesd_managed_dir(settings: Settings) -> Iterator[tuple[str, Path]]:
    s = get_settings(settings)
    yield "temboard", s.pid_file.parent


@hookimpl
async def postgresql_configured(
    instance: PostgreSQLInstance,
    manifest: interface.Instance,
    config: Configuration,
) -> None:
    """Install temboard agent for an instance when it gets configured."""
    settings = get_settings(instance._settings)
    try:
        service = manifest.service(i.Service)
    except ValueError:
        return
    await impl.setup(instance, service, settings, config)


@hookimpl
async def instance_started(instance: Instance) -> None:
    """Start temboard agent service."""
    try:
        service = instance.service(s.Service)
    except ValueError:
        return
    await impl.start(instance._settings, service)


@hookimpl
async def instance_stopped(instance: Instance) -> None:
    """Stop temboard agent service."""
    try:
        service = instance.service(s.Service)
    except ValueError:
        return
    await impl.stop(instance._settings, service)


@hookimpl
async def instance_dropped(instance: Instance) -> None:
    """Uninstall temboard from an instance being dropped."""
    try:
        instance.service(s.Service)
    except ValueError:
        return
    await impl.revert_setup(instance.postgresql, get_settings(instance._settings))


@hookimpl
def rolename(settings: Settings) -> str:
    assert settings.temboard
    return settings.temboard.role


@hookimpl
def role(settings: Settings, manifest: interface.Instance) -> interface.Role | None:
    name = rolename(settings)
    try:
        service_manifest = manifest.service(i.Service)
    except ValueError:
        return None
    return interface.Role(
        name=name, password=service_manifest.password, login=True, superuser=True
    )


@hookimpl
async def instance_status(instance: Instance) -> tuple[Status, str] | None:
    try:
        service = instance.service(s.Service)
    except ValueError:
        return None
    return (await svc.status(instance._settings, service), "temBoard")

# SPDX-FileCopyrightText: 2021 Dalibo
#
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

from collections.abc import Iterator
from typing import Annotated

from pgtoolkit.conf import Configuration
from pydantic import Field

from .. import hookimpl, systemd, types, util
from ..models import Instance, PostgreSQLInstance, interface
from ..settings import Settings
from ..system import svc
from ..types import Status
from . import impl
from .impl import apply as apply
from .impl import available as available
from .impl import get_settings as get_settings
from .impl import start as start
from .impl import stop as stop
from .models import interface as i
from .models import system as s
from .models.interface import PostgresExporter as PostgresExporter

__all__ = ["PostgresExporter", "apply", "available", "start", "stop"]

logger = util.get_logger(__name__)


def register_if(settings: Settings) -> bool:
    return available(settings) is not None


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
                    description="Configuration for the Prometheus service, if enabled in site settings.",
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


SYSTEMD_SERVICE_NAME = "pglift-postgres_exporter@.service"


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
async def postgresql_configured(
    instance: PostgreSQLInstance,
    manifest: interface.Instance,
    config: Configuration,
) -> None:
    """Install postgres_exporter for an instance when it gets configured."""
    try:
        service = manifest.service(i.Service)
    except ValueError:
        return
    settings = get_settings(instance._settings)
    await impl.setup_local(instance, service, settings, config)


@hookimpl
async def instance_started(instance: Instance) -> None:
    """Start postgres_exporter service."""
    try:
        service = instance.service(s.Service)
    except ValueError:
        return
    await impl.start(instance._settings, service)


@hookimpl
async def instance_stopped(instance: Instance) -> None:
    """Stop postgres_exporter service."""
    try:
        service = instance.service(s.Service)
    except ValueError:
        return
    await impl.stop(instance._settings, service)


@hookimpl
async def instance_dropped(instance: Instance) -> None:
    """Uninstall postgres_exporter from an instance being dropped."""
    settings = instance._settings
    prometheus_settings = get_settings(settings)
    await impl.revert_setup(instance.qualname, settings, prometheus_settings)


@hookimpl
def role(settings: Settings, manifest: interface.Instance) -> interface.Role | None:
    try:
        service_manifest = manifest.service(i.Service)
    except ValueError:
        return None
    s = get_settings(settings)
    return interface.Role(
        name=s.role,
        password=service_manifest.password,
        login=True,
        memberships=["pg_monitor"],
    )


@hookimpl
async def instance_status(instance: Instance) -> tuple[Status, str] | None:
    try:
        service = instance.service(s.Service)
    except ValueError:
        return None
    return (await svc.status(instance._settings, service), "prometheus")

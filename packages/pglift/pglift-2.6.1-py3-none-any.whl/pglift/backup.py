# SPDX-FileCopyrightText: 2021 Dalibo
#
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

from collections.abc import Iterator

from . import async_hook, execpath, hookimpl, systemd, util
from . import hookspecs as h
from .models import Instance, PostgreSQLInstance, interface
from .pgbackrest import repo_path
from .settings import Settings

logger = util.get_logger(__name__)

service_name = "backup"
BACKUP_SERVICE_NAME = "pglift-backup@.service"
BACKUP_TIMER_NAME = "pglift-backup@.timer"


def register_if(settings: Settings) -> bool:
    return (
        settings.service_manager == "systemd"
        and settings.scheduler == "systemd"
        and settings.pgbackrest is not None
        and repo_path.register_if(settings)
    )


@hookimpl
def systemd_units() -> list[str]:
    return [BACKUP_SERVICE_NAME, BACKUP_TIMER_NAME]


@hookimpl
def systemd_unit_templates(settings: Settings) -> Iterator[tuple[str, str]]:
    yield (
        BACKUP_SERVICE_NAME,
        systemd.template(BACKUP_SERVICE_NAME).format(
            executeas=systemd.executeas(settings),
            environment=systemd.environment(util.environ()),
            execpath=execpath,
        ),
    )
    yield BACKUP_TIMER_NAME, systemd.template(BACKUP_TIMER_NAME)


@hookimpl
async def postgresql_configured(
    instance: PostgreSQLInstance, manifest: interface.Instance
) -> None:
    """Enable scheduled backup job for configured instance."""
    if not manifest.creating:
        return
    s = instance._settings
    await async_hook(
        s,
        h.schedule_service,
        settings=s,
        service=service_name,
        name=instance.qualname,
    )


@hookimpl
async def instance_dropped(instance: Instance) -> None:
    """Disable scheduled backup job when instance is being dropped."""
    s = instance._settings
    await async_hook(
        s,
        h.unschedule_service,
        settings=s,
        service=service_name,
        name=instance.qualname,
        now=True,
    )


@hookimpl
async def instance_started(instance: Instance) -> None:
    """Start schedule backup job at instance startup."""
    s = instance._settings
    await async_hook(
        s,
        h.start_timer,
        settings=s,
        service=service_name,
        name=instance.qualname,
    )


@hookimpl
async def instance_stopped(instance: Instance) -> None:
    """Stop schedule backup job when instance is stopping."""
    s = instance._settings
    await async_hook(
        s,
        h.stop_timer,
        settings=s,
        service=service_name,
        name=instance.qualname,
    )

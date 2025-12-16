# SPDX-FileCopyrightText: 2021 Dalibo
#
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

from .. import async_hook, deps, h, util
from ..settings import Settings
from ..types import Runnable, Status
from .command import Command

logger = util.get_logger(__name__)


@deps.use
async def start(
    settings: Settings,
    service: Runnable,
    *,
    foreground: bool,
    cmd: Command = deps.Auto,
) -> None:
    """Start a service.

    This will use any service manager plugin, if enabled, and fall back to
    a direct subprocess otherwise.

    If foreground=True, the service is started directly through a subprocess.
    """
    if foreground:
        cmd.execute_program(service.args(), env=service.env())
        return
    if await async_hook(
        settings,
        h.start_service,
        settings=settings,
        service=service.__service_name__,
        name=service.name,
    ):
        return
    pidfile = service.pidfile()
    if cmd.status_program(pidfile) == Status.running:
        logger.debug("service '%s' is already running", service)
        return
    cmd.start_program(
        service.args(), pidfile=pidfile, logfile=service.logfile(), env=service.env()
    )


@deps.use
async def stop(
    settings: Settings, service: Runnable, *, cmd: Command = deps.Auto
) -> None:
    """Stop a service.

    This will use any service manager plugin, if enabled, and fall back to
    a direct program termination (through service's pidfile) otherwise.
    """
    if await async_hook(
        settings,
        h.stop_service,
        settings=settings,
        service=service.__service_name__,
        name=service.name,
    ):
        return
    pidfile = service.pidfile()
    if cmd.status_program(pidfile) == Status.not_running:
        logger.debug("service '%s' is already stopped", service)
        return
    cmd.terminate_program(pidfile)


async def restart(settings: Settings, service: Runnable) -> None:
    """Restart a service.

    This will use any service manager plugin, if enabled, and fall back to
    stop and start method otherwise.
    """
    if await async_hook(
        settings,
        h.restart_service,
        settings=settings,
        service=service.__service_name__,
        name=service.name,
    ):
        return
    await stop(settings, service)
    await start(settings, service, foreground=False)


@deps.use
async def status(
    settings: Settings, service: Runnable, *, cmd: Command = deps.Auto
) -> Status:
    service_status = await async_hook(
        settings,
        h.service_status,
        settings=settings,
        service=service.__service_name__,
        name=service.name,
    )
    if service_status is None:
        pidfile = service.pidfile()
        logger.debug(
            "looking for '%s' service status by its PID at %s", service, pidfile
        )
        return cmd.status_program(pidfile)
    return service_status

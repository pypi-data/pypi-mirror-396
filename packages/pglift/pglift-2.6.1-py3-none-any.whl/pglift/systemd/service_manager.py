# SPDX-FileCopyrightText: 2021 Dalibo
#
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

from collections.abc import Iterator
from pathlib import Path
from typing import Literal

from .. import h, hookimpl, hooks, util
from ..settings import Settings
from ..types import Status
from . import (
    daemon_reload,
    disable,
    enable,
    get_property,
    install,
    installed,
    restart,
    start,
    stop,
    uninstall,
    unit_path,
)
from . import get_settings as s

logger = util.get_logger(__name__)


def register_if(settings: Settings) -> bool:
    return settings.service_manager == "systemd"


def unit(service: str, qualname: str | None) -> str:
    if qualname is not None:
        return f"pglift-{service}@{qualname}.service"
    else:
        return f"pglift-{service}.service"


@hookimpl
async def enable_service(
    settings: Settings, service: str, name: str | None
) -> Literal[True]:
    await enable(s(settings), unit(service, name))
    return True


@hookimpl
async def disable_service(
    settings: Settings, service: str, name: str | None, now: bool | None
) -> Literal[True]:
    kwargs = {}
    if now is not None:
        kwargs["now"] = now
    await disable(s(settings), unit(service, name), **kwargs)
    return True


@hookimpl
async def start_service(
    settings: Settings, service: str, name: str | None
) -> Literal[True]:
    await start(s(settings), unit(service, name))
    return True


@hookimpl
async def stop_service(
    settings: Settings, service: str, name: str | None
) -> Literal[True]:
    await stop(s(settings), unit(service, name))
    return True


@hookimpl
async def restart_service(
    settings: Settings, service: str, name: str | None
) -> Literal[True]:
    await restart(s(settings), unit(service, name))
    return True


@hookimpl
async def service_status(settings: Settings, service: str, name: str | None) -> Status:
    prop = await get_property(s(settings), unit(service, name), "ActiveState")
    _, status = prop.split("=", 1)
    status = status.strip()
    return Status.running if status == "active" else Status.not_running


@hookimpl
async def site_configure_install(settings: Settings, header: str) -> None:
    systemd_settings = settings.systemd
    assert systemd_settings is not None
    changed = False
    for outcome in hooks(settings, h.systemd_unit_templates, settings=settings):
        for name, content in outcome:
            if install(name, util.with_header(content, header), systemd_settings):
                changed = True
    if changed:
        await daemon_reload(systemd_settings)


@hookimpl
async def site_configure_uninstall(settings: Settings) -> None:
    systemd_settings = settings.systemd
    assert systemd_settings is not None
    changed = False
    for outcome in hooks(settings, h.systemd_units):
        for name in outcome:
            if uninstall(name, systemd_settings):
                changed = True
    if changed:
        await daemon_reload(systemd_settings)


@hookimpl
def site_configure_check(settings: Settings, log: bool) -> Iterator[bool]:
    systemd_settings = settings.systemd
    assert systemd_settings is not None
    for outcome in hooks(settings, h.systemd_units):
        for name in outcome:
            if not installed(name, systemd_settings):
                if log:
                    logger.error("missing systemd unit '%s'", name)
                yield False
            else:
                yield True


@hookimpl
def site_configure_list(settings: Settings) -> Iterator[Path]:
    systemd_settings = settings.systemd
    assert systemd_settings is not None
    for outcome in hooks(settings, h.systemd_units):
        for name in outcome:
            yield unit_path(name, systemd_settings)

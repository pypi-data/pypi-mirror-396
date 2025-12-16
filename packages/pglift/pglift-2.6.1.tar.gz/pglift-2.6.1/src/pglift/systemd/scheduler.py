# SPDX-FileCopyrightText: 2021 Dalibo
#
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

from typing import Literal

from .. import hookimpl
from ..settings import Settings
from . import disable, enable, start, stop
from . import get_settings as s


def register_if(settings: Settings) -> bool:
    return settings.scheduler == "systemd"


def unit(service: str, qualname: str) -> str:
    return f"pglift-{service}@{qualname}.timer"


@hookimpl
async def schedule_service(
    settings: Settings, service: str, name: str
) -> Literal[True]:
    await enable(s(settings), unit(service, name))
    return True


@hookimpl
async def unschedule_service(
    settings: Settings, service: str, name: str, now: bool | None
) -> Literal[True]:
    kwargs = {}
    if now is not None:
        kwargs["now"] = now
    await disable(s(settings), unit(service, name), **kwargs)
    return True


@hookimpl
async def start_timer(settings: Settings, service: str, name: str) -> Literal[True]:
    await start(s(settings), unit(service, name))
    return True


@hookimpl
async def stop_timer(settings: Settings, service: str, name: str) -> Literal[True]:
    await stop(s(settings), unit(service, name))
    return True

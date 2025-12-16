# SPDX-FileCopyrightText: 2021 Dalibo
#
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

from pathlib import Path

from .. import async_hooks, h, hooks
from ..settings import Settings


async def do(settings: Settings, header: str = "") -> None:
    await async_hooks(
        settings, h.site_configure_install, settings=settings, header=header
    )
    await async_hooks(settings, h.site_configure_start, settings=settings)


async def undo(settings: Settings) -> None:
    await async_hooks(settings, h.site_configure_stop, settings=settings)
    await async_hooks(settings, h.site_configure_uninstall, settings=settings)


def check(settings: Settings, *, partial: bool = False) -> bool:
    """Check the installation.

    Return True if the installation is complete (or partial, if partial=True).
    """
    results = (
        status
        for outcome in hooks(
            settings, h.site_configure_check, settings=settings, log=not partial
        )
        for status in outcome
    )
    if partial:
        return any(results)
    return all(results)


def ls(settings: Settings) -> list[Path]:
    """Return the list of managed files during installation."""
    return sum(
        (
            list(outcome)
            for outcome in hooks(settings, h.site_configure_list, settings=settings)
        ),
        start=[],
    )

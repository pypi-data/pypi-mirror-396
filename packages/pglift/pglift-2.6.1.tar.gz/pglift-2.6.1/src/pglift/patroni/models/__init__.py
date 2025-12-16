# SPDX-FileCopyrightText: 2021 Dalibo
#
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

from ...settings import _patroni
from .build import Patroni
from .system import Service

__all__ = [
    "Patroni",
    "Service",
]


def patroni(qualname: str, /, settings: _patroni.Settings) -> Patroni | None:
    try:
        return Patroni.get(qualname, settings)
    except FileNotFoundError:
        return None


def service(name: str, p: Patroni, /, settings: _patroni.Settings) -> Service:
    return Service(name=name, patroni=p, settings=settings)

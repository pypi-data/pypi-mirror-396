# SPDX-FileCopyrightText: 2021 Dalibo
#
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

from pathlib import Path
from typing import ClassVar

from attrs import field, frozen

from ...settings._patroni import Settings
from .. import impl
from .build import Patroni


@frozen
class Service:
    """A Patroni service bound to a PostgreSQL instance."""

    __service_name__: ClassVar = "patroni"
    name: str
    patroni: Patroni = field(repr=False)
    settings: Settings = field(repr=False)

    @property
    def cluster(self) -> str:
        return self.patroni.scope

    @property
    def node(self) -> str:
        return self.patroni.name

    def __str__(self) -> str:
        return f"{self.__service_name__}@{self.name}"

    def args(self) -> list[str]:
        configpath = impl._configpath(self.name, self.settings)
        return [str(self.settings.execpath), str(configpath)]

    def pidfile(self) -> Path:
        return Path(str(self.settings.pid_file).format(name=self.name))

    def logfile(self) -> Path:
        return impl.logfile(self.name, self.settings)

    def env(self) -> None:
        return None

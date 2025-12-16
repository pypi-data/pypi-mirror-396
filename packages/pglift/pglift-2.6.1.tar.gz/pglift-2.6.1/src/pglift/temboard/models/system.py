# SPDX-FileCopyrightText: 2021 Dalibo
#
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

from pathlib import Path
from typing import ClassVar, Final

from attrs import field, frozen
from pydantic import SecretStr

from ...settings._temboard import Settings
from .. import impl

service_name: Final = "temboard_agent"


@frozen
class Service:
    """A temboard-agent service bound to a PostgreSQL instance."""

    __service_name__: ClassVar[str] = service_name

    name: str
    """Identifier for the service, usually the instance qualname."""

    settings: Settings = field(repr=False)

    port: int
    """TCP port for the temboard-agent API."""

    password: SecretStr | None

    def __str__(self) -> str:
        return f"{self.__service_name__}@{self.name}"

    def args(self) -> list[str]:
        configpath = impl._configpath(self.name, self.settings)
        return impl._args(self.settings.execpath, configpath)

    def pidfile(self) -> Path:
        return impl._pidfile(self.name, self.settings)

    def logfile(self) -> Path:
        return impl._logfile(self.name, self.settings)

    def env(self) -> None:
        return None

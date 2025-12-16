# SPDX-FileCopyrightText: 2021 Dalibo
#
# SPDX-License-Identifier: GPL-3.0-or-later

from collections.abc import Mapping
from pathlib import Path
from typing import ClassVar, Final

from attrs import field, frozen
from pydantic import SecretStr

from ... import exceptions
from ...settings._prometheus import Settings
from .. import impl

service_name: Final = "postgres_exporter"


@frozen
class Config:
    values: Mapping[str, str]
    path: Path

    def __getitem__(self, key: str) -> str:
        try:
            return self.values[key]
        except KeyError as e:
            raise exceptions.ConfigurationError(self.path, f"{key} not found") from e


@frozen
class Service:
    """A Prometheus postgres_exporter service bound to a PostgreSQL instance."""

    __service_name__: ClassVar[str] = service_name

    name: str
    """Identifier for the service, usually the instance qualname."""

    settings: Settings = field(repr=False)

    port: int
    """TCP port for the web interface and telemetry."""

    password: SecretStr | None

    def __str__(self) -> str:
        return f"{self.__service_name__}@{self.name}"

    def args(self) -> list[str]:
        config = impl._config(impl._configpath(self.name, self.settings))
        return impl._args(self.settings.execpath, config)

    def pidfile(self) -> Path:
        return impl._pidfile(self.name, self.settings)

    def logfile(self) -> None:
        # postgres_exporter can only log to stderr.
        return None

    def env(self) -> dict[str, str]:
        config = impl._config(impl._configpath(self.name, self.settings))
        return impl._env(config)

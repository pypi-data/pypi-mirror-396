# SPDX-FileCopyrightText: 2025 Dalibo
#
# SPDX-License-Identifier: GPL-3.0-or-later
from __future__ import annotations

from collections.abc import Iterator
from contextlib import contextmanager
from contextvars import ContextVar
from typing import Annotated, Protocol

import pgtoolkit.conf as pgconf

from ..deps import Dependency
from ..models import PostgreSQLInstance, interface
from ..types import ConfigChanges


class AbstractConfigurationManager(Protocol):
    async def configure_postgresql(
        self,
        configuration: pgconf.Configuration,
        instance: PostgreSQLInstance,
        manifest: interface.Instance,
    ) -> ConfigChanges | None: ...

    async def postgresql_editable_conf(
        self, instance: PostgreSQLInstance
    ) -> pgconf.Configuration: ...

    async def postgresql_conf(
        self, instance: PostgreSQLInstance
    ) -> pgconf.Configuration: ...

    def configure_auth(
        self, instance: PostgreSQLInstance, manifest: interface.Instance
    ) -> bool: ...


VAR = ContextVar[AbstractConfigurationManager]("ConfigurationManager")

ConfigurationManager = Annotated[AbstractConfigurationManager, Dependency(VAR)]


@contextmanager
def use(manager: AbstractConfigurationManager) -> Iterator[None]:
    """Set the contextvar dedicated to the configuration manager to a specific
    implementation (patroni or postgresql).
    """
    token = VAR.set(manager)
    try:
        yield
    finally:
        VAR.reset(token)

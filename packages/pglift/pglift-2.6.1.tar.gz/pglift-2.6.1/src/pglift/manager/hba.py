# SPDX-FileCopyrightText: 2025 Dalibo
#
# SPDX-License-Identifier: GPL-3.0-or-later
from __future__ import annotations

from collections.abc import Iterator
from contextlib import contextmanager
from contextvars import ContextVar
from typing import Annotated, Protocol

from ..deps import Dependency
from ..models import PostgreSQLInstance


class AbstractHbaManager(Protocol):
    """Interface for HBA manager, define operations to manipulate HBA
    configuration.
    """

    async def configure_pg_hba(
        self, instance: PostgreSQLInstance, hba: list[str]
    ) -> None: ...

    async def pg_hba_config(self, instance: PostgreSQLInstance) -> list[str]: ...


VAR = ContextVar[AbstractHbaManager]("HbaManager")

HbaManager = Annotated[AbstractHbaManager, Dependency(VAR)]


@contextmanager
def use(manager: AbstractHbaManager) -> Iterator[None]:
    """Alter the contextvar for the HBA manager."""
    token = VAR.set(manager)
    try:
        yield
    finally:
        VAR.reset(token)

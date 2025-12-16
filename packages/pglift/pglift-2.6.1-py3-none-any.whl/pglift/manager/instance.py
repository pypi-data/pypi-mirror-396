# SPDX-FileCopyrightText: 2025 Dalibo
#
# SPDX-License-Identifier: GPL-3.0-or-later
from __future__ import annotations

from collections.abc import Iterator, Sequence
from contextlib import contextmanager
from contextvars import ContextVar
from typing import Annotated, Protocol

from .. import postgresql
from ..deps import Dependency
from ..models import PostgreSQLInstance, interface
from ..types import PostgreSQLStopMode


class AbstractInstanceManager(Protocol):
    """Interface for instance manager, define operations available to manage
    an instance.
    """

    async def init_postgresql(
        self, manifest: interface.Instance, instance: PostgreSQLInstance
    ) -> None: ...

    async def deinit_postgresql(self, instance: PostgreSQLInstance) -> None: ...

    async def start_postgresql(
        self,
        instance: PostgreSQLInstance,
        foreground: bool,
        *,
        wait: bool,
        timeout: int = ...,
        run_hooks: bool = True,
        **runtime_parameters: str,
    ) -> None: ...

    async def stop_postgresql(
        self,
        instance: PostgreSQLInstance,
        mode: PostgreSQLStopMode,
        wait: bool,
        deleting: bool = False,
        run_hooks: bool = True,
    ) -> None: ...

    async def restart_postgresql(
        self, instance: PostgreSQLInstance, mode: PostgreSQLStopMode, wait: bool
    ) -> None: ...

    async def reload_postgresql(self, instance: PostgreSQLInstance) -> None: ...

    async def promote_postgresql(self, instance: PostgreSQLInstance) -> None: ...

    async def demote_postgresql(
        self,
        instance: PostgreSQLInstance,
        source: postgresql.RewindSource,
        *,
        rewind_opts: Sequence[str] = (),
    ) -> None: ...

    async def pause_wal_replay(self, instance: PostgreSQLInstance) -> None: ...

    async def resume_wal_replay(self, instance: PostgreSQLInstance) -> None: ...


VAR = ContextVar[AbstractInstanceManager]("InstanceManager")

InstanceManager = Annotated[AbstractInstanceManager, Dependency(VAR)]


@contextmanager
def use(manager: AbstractInstanceManager) -> Iterator[None]:
    """Alter the contextvar to manager (patroni or postgresql) to use for mananing
    the instances.
    """
    token = VAR.set(manager)
    try:
        yield
    finally:
        VAR.reset(token)

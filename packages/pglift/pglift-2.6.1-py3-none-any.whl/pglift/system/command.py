# SPDX-FileCopyrightText: 2024 Dalibo
#
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

import shlex
import subprocess
from collections.abc import Mapping, Sequence
from contextvars import ContextVar
from pathlib import Path
from typing import Annotated, Any, NoReturn, Protocol

from .. import deps, types
from ..deps import Dependency
from . import cmd as cmd_mod
from .fs import FileSystem


class CommandType(Protocol):
    async def run(
        self,
        args: Sequence[str],
        *,
        input: str | None = None,
        capture_output: bool = True,
        timeout: float | None = None,
        check: bool = False,
        log_stdout: bool = False,
        **kwargs: Any,
    ) -> types.CompletedProcess: ...

    def start_program(
        self,
        cmd: Sequence[str],
        *,
        pidfile: Path | None,
        logfile: Path | None,
        timeout: float = 1,
        env: Mapping[str, str] | None = None,
        fs: FileSystem = deps.Auto,
    ) -> subprocess.Popen[bytes]: ...

    def execute_program(
        self, cmd: Sequence[str], *, env: Mapping[str, str] | None = None
    ) -> NoReturn: ...

    def status_program(
        self, pidfile: Path, *, fs: FileSystem = deps.Auto
    ) -> types.Status: ...

    def terminate_program(
        self, pidfile: Path, *, fs: FileSystem = deps.Auto
    ) -> None: ...


class NoOpProcess(subprocess.Popen[bytes]):
    def __init__(self, args: Sequence[str]):
        pass


class NoOpCommand:
    async def run(
        self, args: Sequence[str], capture_output: bool = True, **kwargs: Any
    ) -> types.CompletedProcess:
        cmds = shlex.join(args)
        cmd_mod.logger.debug(cmds)
        return subprocess.CompletedProcess(
            args,
            returncode=0,
            stderr="No op" if capture_output else None,
            stdout="" if capture_output else None,
        )

    def start_program(
        self, cmd: Sequence[str], *args: Any, **kwargs: Any
    ) -> subprocess.Popen[bytes]:
        # return a Popen that doesn't do anything
        cmd_mod.logger.debug("starting program '%s'", shlex.join(cmd))
        return NoOpProcess(cmd)

    def execute_program(
        self, cmd: Sequence[str], *, env: Mapping[str, str] | None = None
    ) -> NoReturn:
        # This should never return
        raise NotImplementedError

    def status_program(self, *args: Any, **kwargs: Any) -> types.Status:
        return types.Status.running

    def terminate_program(self, pidfile: Path, *, fs: FileSystem = deps.Auto) -> None:
        pass


VAR = ContextVar[CommandType]("Command", default=cmd_mod)

Command = Annotated[CommandType, Dependency(VAR)]


get = VAR.get
set = VAR.set
reset = VAR.reset

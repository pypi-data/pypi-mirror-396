# SPDX-FileCopyrightText: 2025 Dalibo
#
# SPDX-License-Identifier: GPL-3.0-or-later

"""Implementation of the Command protocol for functional tests."""

from __future__ import annotations

import logging
import subprocess
from collections.abc import Mapping, Sequence
from pathlib import Path

from pglift import deps
from pglift.system import FileSystem
from pglift.system.cmd import execute_program as execute_program
from pglift.system.cmd import run as run
from pglift.system.cmd import start_program as _start_program
from pglift.system.cmd import status_program as status_program
from pglift.system.cmd import terminate_program as terminate_program

logger = logging.getLogger("pglift-tests")

procs: list[tuple[subprocess.Popen[bytes], list[str]]] = []


@deps.use
def start_program(
    cmd: Sequence[str],
    *,
    pidfile: Path | None,
    logfile: Path | None,
    timeout: float = 1,
    env: Mapping[str, str] | None = None,
    fs: FileSystem = deps.Auto,
) -> subprocess.Popen[bytes]:
    proc = _start_program(
        cmd, pidfile=pidfile, logfile=logfile, timeout=timeout, env=env, fs=fs
    )
    logger.debug("supervising process %d: %s", proc.pid, cmd)
    procs.append((proc, list(cmd)))
    return proc

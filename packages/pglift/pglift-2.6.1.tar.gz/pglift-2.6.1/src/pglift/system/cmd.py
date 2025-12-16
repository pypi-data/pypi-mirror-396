# SPDX-FileCopyrightText: 2021 Dalibo
#
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

import asyncio
import logging
import os
import shlex
import subprocess
from asyncio import create_task
from asyncio.subprocess import Process, SubprocessStreamProtocol
from collections.abc import AsyncIterator, Iterator, Mapping, Sequence
from contextlib import asynccontextmanager, contextmanager
from functools import partial
from pathlib import Path, PurePath
from subprocess import PIPE, TimeoutExpired
from typing import IO, Any, NoReturn

import psutil

from .. import deps, exceptions
from ..types import CompletedProcess, Status
from .fs import FileSystem

logger = logging.getLogger(__name__)


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
    """Start program described by 'cmd', in the background, and possibly store
    its PID in 'pidfile'.

    :raises ~exceptions.SystemError: if the program is already running.
    :raises ~exceptions.CommandError: in case program unexpectedly terminates
        before `timeout`.
    """
    program = cmd[0]
    if pidfile is not None:
        _check_pidfile(pidfile, program)

    logpos = 0
    if logfile is not None:
        # Possibly store the current end-of-file before starting the process, in
        # order to tail logfile upon premature exit.
        try:
            with fs.open(logfile) as f:
                logpos = f.seek(0, os.SEEK_END)
        except FileNotFoundError:
            pass

    logger.debug("starting program '%s'", shlex.join(cmd))
    proc = subprocess.Popen(  # nosec
        cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, env=env
    )
    try:
        proc.wait(timeout)
    except subprocess.TimeoutExpired:
        if pidfile is not None:
            fs.mkdir(pidfile.parent, parents=True, exist_ok=True)
            fs.write_text(pidfile, str(proc.pid))
        return proc
    else:
        if logfile is not None:
            try:
                with fs.open(logfile) as f:
                    f.seek(logpos)
                    for line in f:
                        logger.debug("%s: %s", program, line.rstrip())
            except FileNotFoundError:
                pass
        assert proc.returncode is not None
        assert proc.returncode != 0, f"{program} terminated with exit code 0"
        raise exceptions.CommandError(proc.returncode, cmd)


@contextmanager
def handle_errors(args: Sequence[str]) -> Iterator[None]:
    """Context manager handling logging and common errors to suprocess run."""
    cmds = shlex.join(args)
    logger.debug(cmds)
    try:
        yield
    except FileNotFoundError as e:
        raise exceptions.FileNotFoundError(
            f"program from command {cmds!r} not found"
        ) from e
    except OSError as e:
        logger.debug("failed to start child process", exc_info=True)
        raise exceptions.SystemError(
            f"failed to start child process from command {cmds!r}"
        ) from e


async def run(
    args: Sequence[str],
    *,
    input: str | None = None,
    capture_output: bool = True,
    timeout: float | None = None,
    check: bool = False,
    log_stdout: bool = False,
    **kwargs: Any,
) -> CompletedProcess:
    if not args:
        raise ValueError("empty arguments sequence")

    if input is not None:
        if "stdin" in kwargs:
            raise ValueError("stdin and input arguments may not both be used")
        kwargs["stdin"] = PIPE

    if capture_output:
        if kwargs.get("stdout") is not None or kwargs.get("stderr") is not None:
            raise ValueError(
                "stdout and stderr arguments may not be used with capture_output."
            )
        kwargs["stdout"] = kwargs["stderr"] = subprocess.PIPE

    with handle_errors(args):
        async with logged_subprocess_exec(
            *args, log_stdout=log_stdout, **kwargs
        ) as proc:
            aw = proc.communicate(input.encode("utf-8") if input is not None else None)
            if timeout is None:
                out, err = await aw
            else:
                try:
                    out, err = await asyncio.wait_for(aw, timeout)
                except asyncio.TimeoutError:
                    proc.kill()
                    await proc.wait()
                    raise TimeoutExpired(args, timeout) from None

    assert proc.returncode is not None
    stdout = out.decode("utf-8") if out is not None else None
    stderr = err.decode("utf-8") if err is not None else None

    r = CompletedProcess(args, proc.returncode, stdout, stderr)
    if check:
        try:
            r.check_returncode()
        except subprocess.CalledProcessError as e:
            raise exceptions.CommandError(
                r.returncode, r.args, stdout=r.stdout, stderr=r.stderr
            ) from e
    return r


class _CloneStdStreamsProtocol(SubprocessStreamProtocol):
    """Subprocess protocol extending the default one to handle clones of
    standard streams.
    """

    def __init__(
        self,
        stderr_reader: asyncio.StreamReader | None,
        stdout_reader: asyncio.StreamReader | None,
        *,
        limit: int,
        loop: asyncio.events.AbstractEventLoop,
    ) -> None:
        super().__init__(limit=limit, loop=loop)
        self._readers = {
            fd: reader
            for fd, reader in [(1, stdout_reader), (2, stderr_reader)]
            if reader is not None
        }

    def __repr__(self) -> str:
        base = super().__repr__()[1:-1]
        for fd, reader in sorted(self._readers.items()):
            base += f" cloned fd={fd} using {reader}"
        return f"<{base}>"

    def pipe_data_received(self, fd: int, data: bytes | str) -> None:
        super().pipe_data_received(fd, data)
        try:
            reader = self._readers[fd]
        except KeyError:
            pass
        else:
            assert isinstance(data, bytes)
            reader.feed_data(data)

    def pipe_connection_lost(self, fd: int, exc: Exception | None) -> None:
        super().pipe_connection_lost(fd, exc)
        try:
            reader = self._readers[fd]
        except KeyError:
            pass
        else:
            if exc:
                reader.set_exception(exc)
            else:
                reader.feed_eof()


async def log_stream(program: str | PurePath, stream: asyncio.StreamReader) -> None:
    """Log 'stream' from a Process running 'program' as DEBUG messages."""
    try:
        async for line in stream:
            logger.debug("%s: %s", program, line.decode("utf-8").rstrip())
    except asyncio.CancelledError:
        pass


@asynccontextmanager
async def logged_subprocess_exec(
    program: str,
    *args: str,
    stdin: int | IO[Any] | None = None,
    stdout: int | IO[Any] | None = None,
    stderr: int | IO[Any] | None = None,
    log_stdout: bool = False,
    **kwds: Any,
) -> AsyncIterator[Process]:
    """Context manager starting an asyncio Process while possibly forwarding
    its stderr to our logger.

    This is similar quite to asyncio.subprocess.create_subprocess_exec() but
    with a custom protocol to install a cloned stream for stderr.
    """
    loop = asyncio.get_event_loop()
    tasks = []
    cloned_stderr = cloned_stdout = None
    if stderr is not None:
        cloned_stderr = asyncio.StreamReader()
        tasks.append(
            create_task(log_stream(program, cloned_stderr), name="stderr logger")
        )
    if log_stdout:
        assert stdout is not None, "cannot use log_stdout is stdout is None"
        cloned_stdout = asyncio.StreamReader()
        tasks.append(
            create_task(log_stream(program, cloned_stdout), name="stdout logger")
        )

    protocol_factory = partial(
        _CloneStdStreamsProtocol,
        cloned_stderr,
        cloned_stdout,
        limit=2**16,  # asyncio.streams._DEFAULT_LIMIT
        loop=loop,
    )
    try:
        transport, protocol = await loop.subprocess_exec(
            protocol_factory,
            program,
            *args,
            stdin=stdin,
            stdout=stdout,
            stderr=stderr,
            **kwds,
        )
        yield Process(transport, protocol, loop)
    finally:
        for task in tasks:
            if task and not task.done():
                task.cancel()


def execute_program(
    cmd: Sequence[str], *, env: Mapping[str, str] | None = None
) -> NoReturn:
    """Execute program described by 'cmd', replacing the current process.

    :raises ValueError: if program path is not absolute.
    """
    program = cmd[0]
    if not PurePath(program).is_absolute():
        raise ValueError(f"expecting an absolute program path {program}")
    logger.debug("executing program '%s'", shlex.join(cmd))
    if env is not None:
        os.execve(program, list(cmd), env)  # nosec
    else:
        os.execv(program, list(cmd))  # nosec


@deps.use
def status_program(pidfile: Path, *, fs: FileSystem = deps.Auto) -> Status:
    """Return the status of a program which PID is in 'pidfile'.

    :raises ~exceptions.SystemError: if the program is already running.
    :raises ~exceptions.CommandError: in case program execution terminates
        after `timeout`.
    """
    if fs.exists(pidfile):
        with fs.open(pidfile) as f:
            pid = f.readline().rstrip()
        if fs.exists(Path("/proc") / pid):
            return Status.running
    return Status.not_running


@deps.use
def _check_pidfile(pidfile: Path, program: str, *, fs: FileSystem = deps.Auto) -> None:
    """Use specified pidfile, when not None, to check if the program is
    already running.
    """
    if (status := status_program(pidfile)) is Status.running:
        with fs.open(pidfile) as f:
            pid = f.readline().strip()
        if status == Status.running:
            raise exceptions.SystemError(
                f"program {program} seems to be running already with PID {pid}"
            )
    elif fs.exists(pidfile):
        with fs.open(pidfile) as f:
            pid = f.readline().strip()
        logger.warning(
            "program %s is supposed to be running with PID %s but "
            "it's apparently not; starting anyway",
            program,
            pid,
        )
        fs.unlink(pidfile)


def _terminate_process(pid: int, timeout: float = 5) -> None:
    logger.debug("terminating process %d", pid)
    try:
        process = psutil.Process(pid)
    except psutil.NoSuchProcess as e:
        logger.warning("process %d doesn't exist: %s", pid, e)
        return

    process.terminate()

    try:
        process.wait(timeout=timeout)
    except psutil.TimeoutExpired:
        logger.warning("process %d did not terminate on time, forcing kill.", pid)
        process.kill()
        process.wait(timeout=timeout)


@deps.use
def terminate_program(pidfile: Path, *, fs: FileSystem = deps.Auto) -> None:
    """Terminate program matching PID in 'pidfile'.

    Upon successful termination, the 'pidfile' is removed.
    No-op if no process matching PID from 'pidfile' is running.
    """
    if status_program(pidfile) == Status.not_running:
        logger.warning("program from %s not running", pidfile)
        if fs.exists(pidfile):
            logger.debug("removing dangling PID file %s", pidfile)
            fs.unlink(pidfile)
        return

    with fs.open(pidfile) as f:
        pid = int(f.readline().rstrip())
    _terminate_process(pid)

    fs.unlink(pidfile)


def _main() -> None:  # pragma: nocover
    import argparse
    import logging
    import sys

    logger.setLevel(logging.DEBUG)
    handler = logging.StreamHandler(sys.stderr)
    handler.setFormatter(
        logging.Formatter(fmt="%(asctime)s - %(message)s", datefmt="[%Xs]")
    )
    logger.addHandler(handler)

    parser = argparse.ArgumentParser(
        __name__,
        description="Run, start or terminate programs while logging their stderr",
    )

    subparsers = parser.add_subparsers(title="Commands")

    run_parser = subparsers.add_parser(
        "run",
        description="Run PROGRAM with positional ARGuments.",
        epilog=f"Example: {__name__} run initdb /tmp/pgdata --debug",
    )
    run_parser.add_argument("program", metavar="PROGRAM")
    run_parser.add_argument("arguments", metavar="ARG", nargs="*")

    def run_func(args: argparse.Namespace, remaining: Sequence[str]) -> None:
        cmd = [args.program] + args.arguments + list(remaining)
        asyncio.run(run(cmd, check=True))

    run_parser.set_defaults(func=run_func)

    start_parser = subparsers.add_parser(
        "start",
        description="Start PROGRAM with positional ARGuments.",
        epilog=f"Example: {__name__} start postgres -D /tmp/pgdata -k /tmp",
    )
    start_parser.add_argument("program", metavar="PROGRAM")
    start_parser.add_argument("arguments", metavar="ARG", nargs="*")
    start_parser.add_argument(
        "-p",
        "--pidfile",
        type=Path,
        help="Path to file where PID will be stored.",
    )
    start_parser.add_argument(
        "--logfile",
        type=Path,
        help="Path to file program logs are written.",
    )
    start_parser.add_argument(
        "--timeout", type=float, default=1, help="Liveliness timeout."
    )

    def start_func(args: argparse.Namespace, remaining: Sequence[str]) -> None:
        cmd = [args.program] + args.arguments + list(remaining)

        proc = start_program(
            cmd, pidfile=args.pidfile, logfile=args.logfile, timeout=args.timeout
        )
        print(f"Program {args.program} running with PID {proc.pid}")

    start_parser.set_defaults(func=start_func)

    terminate_parser = subparsers.add_parser(
        "terminate",
        description="Terminate process from PIDFILE.",
        epilog=f"Example: {__name__} terminate /tmp/pgdata/postmaster.pid",
    )
    terminate_parser.add_argument("pidfile", metavar="PIDFILE", type=Path)

    def terminate_func(args: argparse.Namespace, _remaining: Sequence[str]) -> None:
        terminate_program(args.pidfile)

    terminate_parser.set_defaults(func=terminate_func)

    ns, remaining = parser.parse_known_args()

    ns.func(ns, remaining)


if __name__ == "__main__":  # pragma: nocover
    _main()

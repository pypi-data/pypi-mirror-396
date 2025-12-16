# SPDX-FileCopyrightText: 2021 Dalibo
#
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

import logging
import subprocess
import sys
import time
from pathlib import Path
from unittest.mock import patch

import psutil
import pytest

from pglift import exceptions
from pglift.exceptions import CommandError, SystemError
from pglift.system import cmd
from pglift.types import Status


@pytest.mark.anyio
async def test_run(tmp_path: Path, caplog: pytest.LogCaptureFixture) -> None:
    caplog.clear()
    with caplog.at_level(logging.DEBUG, logger=cmd.__name__):
        r = await cmd.run(["true"], input="a")
    assert r.returncode == 0
    assert not r.stderr and not r.stdout
    assert caplog.messages == ["true"]

    caplog.clear()
    with caplog.at_level(logging.DEBUG, logger=cmd.__name__):
        assert (await cmd.run(["echo", "ahah"])).stdout == "ahah\n"
    assert caplog.messages == ["echo ahah"]

    caplog.clear()
    with caplog.at_level(logging.DEBUG, logger=cmd.__name__):
        r = await cmd.run(["cat", "nosuchfile"], env={"LANG": "C"}, cwd=tmp_path)
    assert r.stderr == "cat: nosuchfile: No such file or directory\n"
    assert caplog.messages == [
        "cat nosuchfile",
        "cat: cat: nosuchfile: No such file or directory",
    ]

    caplog.clear()
    with (
        caplog.at_level(logging.DEBUG, logger=cmd.__name__),
        pytest.raises(
            exceptions.CommandError,
            match=r"Command .* returned non-zero exit status 1",
        ),
    ):
        await cmd.run(["cat", "doesnotexist"], check=True, cwd=tmp_path)
    assert caplog.messages == [
        "cat doesnotexist",
        "cat: cat: doesnotexist: No such file or directory",
    ]

    caplog.clear()
    with caplog.at_level(logging.DEBUG, logger=cmd.__name__):
        with pytest.raises(subprocess.TimeoutExpired):
            await cmd.run(["sleep", "0.1"], timeout=0.01)
    assert caplog.messages == ["sleep 0.1"]

    caplog.clear()
    with (
        caplog.at_level(logging.DEBUG, logger=cmd.__name__),
        pytest.raises(
            exceptions.FileNotFoundError, match=r"program from command 'nosuchcommand"
        ),
    ):
        await cmd.run(["nosuchcommand", "x", "y", "-v"])
    assert caplog.messages == ["nosuchcommand x y -v"]


@pytest.mark.anyio
@pytest.mark.parametrize("log_stdout", [True, False])
async def test_run_log_stdout(
    caplog: pytest.LogCaptureFixture, log_stdout: bool
) -> None:
    with caplog.at_level(logging.DEBUG, logger=cmd.__name__):
        args = [sys.executable, "-c", "import sys; print('err as out'); sys.exit(1)"]
        await cmd.run(args, log_stdout=log_stdout)
    assert f"{sys.executable} -c" in caplog.messages[0]
    if log_stdout:
        assert caplog.messages[1:] == [f"{sys.executable}: err as out"]
    else:
        assert not caplog.messages[1:]


def test_execute_program(caplog: pytest.LogCaptureFixture) -> None:
    command = ["/c", "m", "d"]
    with (
        patch("os.execve", autospec=True) as execve,
        patch("os.execv", autospec=True) as execv,
    ):
        cmd.execute_program(command, env={"X": "Y"})
        execve.assert_called_once_with("/c", command, {"X": "Y"})
        assert not execv.called
    with (
        patch("os.execve", autospec=True) as execve,
        patch("os.execv", autospec=True) as execv,
        caplog.at_level(logging.DEBUG, logger="pglift.cmd"),
    ):
        cmd.execute_program(command)
        execv.assert_called_once_with("/c", command)
        assert not execve.called
    assert "executing program '/c m d'" in caplog.records[0].message


def test_terminate_process(caplog: pytest.LogCaptureFixture, tmp_path: Path) -> None:
    with (
        caplog.at_level(logging.DEBUG, logger="pglift.cmd"),
        subprocess.Popen(["sleep", "1"]) as proc,
    ):
        pid = proc.pid
        time.sleep(0.1)  # ensure process starts
        assert psutil.pid_exists(pid)
        cmd._terminate_process(pid)
        assert not psutil.pid_exists(pid)
    assert f"terminating process {pid}" in caplog.records[0].message

    caplog.clear()

    # non existing pid
    pid = 999999
    with caplog.at_level(logging.WARNING, logger="pglift.cmd"):
        cmd._terminate_process(pid)
    assert f"process {pid} doesn't exist" in caplog.records[0].message

    caplog.clear()

    # process already terminated
    with (
        caplog.at_level(logging.WARNING, logger="pglift.cmd"),
        subprocess.Popen(["sleep", "1"]) as proc,
    ):
        pid = proc.pid
        time.sleep(0.1)  # ensure process starts
        proc.terminate()  # manually terminate
        proc.wait()  # ensure termination

        assert not psutil.pid_exists(pid)
        cmd._terminate_process(pid)  # No error raised
    assert f"process {pid} doesn't exist" in caplog.records[0].message

    caplog.clear()

    # process that ignores SIGTERM and requires SIGKILL
    with (
        caplog.at_level(logging.DEBUG, logger="pglift.cmd"),
        subprocess.Popen(["bash", "-c", "trap '' TERM; sleep 30"]) as proc,
    ):
        pid = proc.pid
        time.sleep(0.1)  # ensure process starts
        assert psutil.pid_exists(pid)
        cmd._terminate_process(pid, timeout=0.2)
        assert not psutil.pid_exists(pid)
    assert f"terminating process {pid}" in caplog.records[0].message
    assert (
        f"process {pid} did not terminate on time, forcing kill"
        in caplog.records[1].message
    )


def test_start_program_terminate_program_status_program(
    caplog: pytest.LogCaptureFixture, tmp_path: Path
) -> None:
    pidfile = tmp_path / "sleep" / "pid"
    proc = cmd.start_program(
        ["sleep", "10"],
        pidfile=pidfile,
        logfile=None,
        timeout=0.01,
        env={"X_DEBUG": "1"},
    )
    with pidfile.open() as f:
        pid = f.read()
    assert proc.pid == int(pid)

    procdir = Path("/proc") / pid
    assert procdir.exists()
    assert "sleep\x0010\x00" in (procdir / "cmdline").read_text()
    assert "X_DEBUG" in (procdir / "environ").read_text()

    assert cmd.status_program(pidfile) == Status.running

    with pidfile.open("a") as f:
        f.write("\nextra\ninformation\nignored")
    assert cmd.status_program(pidfile) == Status.running

    with pytest.raises(SystemError, match="running already"):
        cmd.start_program(["sleep", "10"], pidfile=pidfile, logfile=None)

    cmd.terminate_program(pidfile)
    r = subprocess.run(["pgrep", pid], check=False)
    assert r.returncode == 1
    proc.communicate()
    assert proc.returncode == 0

    assert not pidfile.exists()
    assert cmd.status_program(pidfile) == Status.not_running

    pidfile = tmp_path / "invalid.pid"
    pidfile.write_text("innnnvaaaaaaaaaaliiiiiiiiiiid")
    assert cmd.status_program(pidfile) == Status.not_running

    caplog.clear()
    logfile = tmp_path / "log"
    pyprog = tmp_path / "pyprog"
    pyprog.touch(mode=0o755)
    pyprog.write_text(
        "\n".join(
            [
                "import sys",
                f"with open('{logfile}', 'w') as f:",
                "  f.write('test test')",
                "sys.exit(1)",
            ]
        )
    )
    with (
        pytest.raises(CommandError),
        caplog.at_level(logging.DEBUG, logger=__name__),
    ):
        cmd.start_program(
            [sys.executable, str(pyprog)], pidfile=pidfile, logfile=logfile
        )
    assert not pidfile.exists()
    assert f"{sys.executable} is supposed to be running" in caplog.records[0].message
    assert f"{sys.executable}: test test" in caplog.records[2].message

    pidfile = tmp_path / "notfound"
    caplog.clear()
    with caplog.at_level(logging.WARNING, logger="pglift.cmd"):
        cmd.terminate_program(pidfile)
    assert f"program from {pidfile} not running" in caplog.records[0].message

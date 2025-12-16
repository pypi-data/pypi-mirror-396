# SPDX-FileCopyrightText: 2021 Dalibo
#
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

import functools
import os
import pwd
import subprocess
from collections.abc import Callable, Coroutine
from pathlib import Path
from typing import Any, Literal, TypeAlias

from .. import deps, exceptions, util
from ..settings import Settings, _systemd
from ..system import Command, FileSystem
from ..types import CompletedProcess

logger = util.get_logger(__name__)


def get_settings(settings: Settings) -> _systemd.Settings:
    assert settings.systemd is not None
    return settings.systemd


@util.cache
def template(*args: str) -> str:
    logger.debug("loading %s template", util.joinpath(*args))
    return util.template("systemd", *args)


def executeas(settings: Settings) -> str:
    """Return User/Group options for systemd unit depending on settings."""
    if get_settings(settings).user:
        return ""
    user, group = settings.sysuser
    return "\n".join([f"User={user}", f"Group={group}"])


def environment(value: dict[str, Any]) -> str:
    """Format Environment options to be inserted in a systemd unit.

    >>> print(environment({"foo": "bar", "active": 1}))
    Environment="active=1"
    Environment="foo=bar"
    >>> environment({})
    ''
    """
    return "\n".join([f'Environment="{k}={v}"' for k, v in sorted(value.items())])


Action: TypeAlias = Literal[
    "daemon-reload",
    "disable",
    "enable",
    "is-active",
    "is-enabled",
    "reload",
    "restart",
    "show",
    "show-environment",
    "start",
    "status",
    "stop",
]


def systemctl_cmd(
    settings: _systemd.Settings, action: Action, *options: str, unit: str | None
) -> list[str]:
    sflag = "--user" if settings.user else "--system"
    cmd_args = [str(settings.systemctl), sflag] + list(options) + [action]
    if unit is not None:
        cmd_args.append(unit)
    if settings.sudo:
        cmd_args.insert(0, "sudo")
    return cmd_args


@functools.cache
def systemctl_env(settings: _systemd.Settings) -> dict[str, str]:
    """Return additional environment variables suitable to run systemctl --user commands.

    To run systemctl --user there must be login session for the current user
    and both XDG_RUNTIME_DIR and DBUS_SESSION_BUS_ADDRESS must be set.
    In some cases like using sudo through ansible, we might not have access to
    required environment variables.

    First check session exists and get XDG_RUNTIME_DIR using `loginctl show-user`. If this is not a
    lingering session display a warning message

    Then if DBUS_SESSION_BUS_ADDRESS is not set, get it by running `systemctl
    --user show-environment`.
    """
    if not settings.user:
        return {}
    user = pwd.getpwuid(os.getuid()).pw_name
    proc = subprocess.run(  # nosec
        [
            "loginctl",
            "show-user",
            user,
            "--value",
            "--property",
            "RuntimePath",
            "--property",
            "Linger",
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    env = {}
    rpath, linger = proc.stdout.splitlines()
    if linger == "no":
        logger.warning(
            "systemd lingering for user %s is not enabled, "
            "pglift services won't start automatically at boot",
            user,
        )
    if "XDG_RUNTIME_DIR" not in os.environ:
        env["XDG_RUNTIME_DIR"] = rpath
    if "DBUS_SESSION_BUS_ADDRESS" not in os.environ:
        proc = subprocess.run(  # nosec
            ["systemctl", "--user", "show-environment"],
            env=os.environ | env,
            check=True,
            capture_output=True,
            text=True,
        )
        for line in proc.stdout.splitlines():
            if line.startswith("DBUS_SESSION_BUS_ADDRESS="):
                env["DBUS_SESSION_BUS_ADDRESS"] = line.split("=", 1)[1]
                break
        else:
            raise exceptions.SystemError(
                "could not find expected DBUS_SESSION_BUS_ADDRESS "
                "in `systemctl --user show-environment` output"
            )
    return env


@deps.use
async def systemctl(
    settings: _systemd.Settings,
    action: Action,
    *options: str,
    unit: str | None,
    check: bool = True,
    cmd: Command = deps.Auto,
) -> CompletedProcess:
    env = systemctl_env(settings)
    return await cmd.run(
        systemctl_cmd(settings, action, *options, unit=unit),
        env=os.environ | env,
        check=check,
    )


def unit_path(name: str, settings: _systemd.Settings) -> Path:
    return settings.unit_path / name


@deps.use
def install(
    name: str, content: str, settings: _systemd.Settings, *, fs: FileSystem = deps.Auto
) -> bool:
    if fs.exists(path := unit_path(name, settings)):
        return False
    fs.mkdir(path.parent, parents=True, exist_ok=True)
    fs.write_text(path, content)
    logger.info("installed %s systemd unit at %s", name, path)
    return True


@deps.use
def uninstall(
    name: str, settings: _systemd.Settings, *, fs: FileSystem = deps.Auto
) -> bool:
    if not fs.exists(path := settings.unit_path / name):
        return False
    logger.info("removing %s systemd unit (%s)", name, path)
    fs.unlink(path, missing_ok=True)
    return True


@deps.use
def installed(
    name: str, settings: _systemd.Settings, *, fs: FileSystem = deps.Auto
) -> bool:
    return fs.exists(settings.unit_path / name)


async def daemon_reload(settings: _systemd.Settings) -> None:
    logger.info("reloading systemd manager configuration")
    await systemctl(settings, "daemon-reload", unit=None)


async def is_enabled(settings: _systemd.Settings, unit: str) -> bool:
    r = await systemctl(settings, "is-enabled", unit=unit, check=False)
    logger.debug("systemd unit %s: %s", unit, r.stdout.rstrip())
    return r.returncode == 0


async def enable(settings: _systemd.Settings, unit: str) -> None:
    if await is_enabled(settings, unit):
        logger.debug("systemd unit %s already enabled, 'enable' action skipped", unit)
        return
    logger.info("enabling systemd unit %s", unit)
    await systemctl(settings, "enable", unit=unit)


async def disable(settings: _systemd.Settings, unit: str, *, now: bool = True) -> None:
    if not await is_enabled(settings, unit):
        logger.debug("systemd unit %s not enabled, 'disable' action skipped", unit)
        return
    logger.info("disabling systemd unit %s", unit)
    await systemctl(settings, "disable", *(("--now",) if now else ()), unit=unit)


F = Callable[[_systemd.Settings, str], Coroutine[None, None, None]]


def log_status(fn: F) -> F:
    @functools.wraps(fn)
    async def wrapper(settings: _systemd.Settings, unit: str) -> None:
        try:
            return await fn(settings, unit)
        except (subprocess.CalledProcessError, SystemExit):
            # Ansible runner would call sys.exit(1), hence SystemExit.
            logger.error(await status(settings, unit))
            raise

    return wrapper


async def status(settings: _systemd.Settings, unit: str) -> str:
    proc = await systemctl(
        settings,
        "status",
        "--full",
        "--lines=100",
        unit=unit,
        check=False,
    )
    # https://www.freedesktop.org/software/systemd/man/systemctl.html#Exit%20status
    if proc.returncode not in (0, 1, 2, 3, 4):
        raise exceptions.CommandError(
            proc.returncode, proc.args, proc.stdout, proc.stderr
        )
    return proc.stdout


@log_status
async def start(settings: _systemd.Settings, unit: str) -> None:
    logger.info("starting systemd unit %s", unit)
    await systemctl(settings, "start", unit=unit)


@log_status
async def stop(settings: _systemd.Settings, unit: str) -> None:
    logger.info("stopping systemd unit %s", unit)
    await systemctl(settings, "stop", unit=unit)


@log_status
async def reload(settings: _systemd.Settings, unit: str) -> None:
    logger.info("reloading systemd unit %s", unit)
    await systemctl(settings, "reload", unit=unit)


@log_status
async def restart(settings: _systemd.Settings, unit: str) -> None:
    logger.info("restarting systemd unit %s", unit)
    await systemctl(settings, "restart", unit=unit)


async def is_active(settings: _systemd.Settings, unit: str) -> bool:
    r = await systemctl(
        settings, "is-active", "--quiet", "--user", unit=unit, check=False
    )
    return r.returncode == 0


async def get_property(settings: _systemd.Settings, unit: str, property: str) -> str:
    r = await systemctl(settings, "show", "--user", "--property", property, unit=unit)
    return r.stdout

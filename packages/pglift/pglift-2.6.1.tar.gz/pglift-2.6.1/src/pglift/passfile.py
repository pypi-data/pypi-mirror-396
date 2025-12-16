# SPDX-FileCopyrightText: 2021 Dalibo
#
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

from collections.abc import Iterator
from contextlib import contextmanager
from copy import copy
from pathlib import Path
from typing import Annotated, Literal, TypedDict

from pgtoolkit import pgpass
from pgtoolkit.conf import Configuration
from pydantic import Field

from . import conf, deps, hookimpl, types, util
from .models import Instance, PostgreSQLInstance, interface
from .settings import Settings
from .system import FileSystem

logger = util.get_logger(__name__)


def register_if(settings: Settings) -> bool:
    return settings.postgresql.auth.passfile is not None


@contextmanager
@deps.use
def passfile(
    settings: Settings, mode: Literal["r", "w"] = "r", *, fs: FileSystem = deps.Auto
) -> Iterator[tuple[pgpass.PassFile, Path]]:
    path = settings.postgresql.auth.passfile
    assert path is not None  # per registration
    if mode == "r":
        with fs.open(path) as f:
            yield pgpass.parse(f), path
    elif mode == "w":
        exists = True
        try:
            with fs.open(path) as f:
                pf = pgpass.parse(f)
        except FileNotFoundError:
            pf = pgpass.PassFile()
            exists = False

        yield pf, path

        if not pf.lines:
            if exists:
                logger.info(
                    "removing now empty %(passfile)s",
                    {"passfile": path},
                )
                fs.unlink(path)
            return

        if not exists:
            fs.touch(path, mode=0o600)

        with fs.open(path, "w") as f:
            pf.save(f)


@hookimpl
def role_model() -> types.ComponentModel:
    return types.ComponentModel(
        "pgpass",
        (
            Annotated[
                bool,
                Field(
                    description="Whether to add an entry in password file for this role.",
                ),
            ],
            False,
        ),
    )


@hookimpl
async def postgresql_configured(
    instance: PostgreSQLInstance,
    manifest: interface.Instance,
    config: Configuration,
    changes: types.ConfigChanges,
) -> None:
    """Update passfile entry for PostgreSQL roles upon instance
    re-configuration (port change).
    """
    if manifest.creating or "port" not in changes:
        return
    old_port, port = changes["port"]
    if port is None:
        port = conf.get_port(config)
    if old_port is None:
        old_port = 5432
    assert isinstance(old_port, int)
    assert isinstance(port, int), port
    if port == old_port:
        return

    with passfile(instance._settings, "w") as (f, path):
        for entry in f:
            if entry.matches(port=old_port):
                entry.port = port
                logger.info(
                    "updating entry for '%(username)s' in %(passfile)s (port changed: %(old_port)d->%(port)d)",
                    {
                        "username": entry.username,
                        "passfile": path,
                        "old_port": old_port,
                        "port": port,
                    },
                )


@hookimpl
async def instance_dropped(instance: Instance) -> None:
    """Remove password file (pgpass) entries for the instance being dropped."""
    with passfile(instance._settings, "w") as (f, path):
        port = instance.postgresql.port
        logger.info(
            "removing entries matching port=%(port)s from %(passfile)s",
            {"port": port, "passfile": path},
        )
        f.remove(port=port)


@hookimpl
async def instance_upgraded(old: PostgreSQLInstance, new: PostgreSQLInstance) -> None:
    """Add pgpass entries matching 'old' instance for the 'new' one."""
    old_port = old.port
    new_port = new.port
    if new_port == old_port:
        return
    with passfile(old._settings, "w") as (f, path):
        for entry in list(f):
            if entry.matches(port=old_port):
                new_entry = copy(entry)
                new_entry.port = new_port
                f.lines.append(new_entry)
                logger.info("added entry %s in %s", new_entry, path)


@hookimpl
async def role_change(
    role: interface.BaseRole, instance: PostgreSQLInstance
) -> tuple[bool, bool]:
    """Create / update or delete passfile entry matching ('role', 'instance')."""
    port = instance.port
    username = role.name
    password = None
    if role.password:
        password = role.password.get_secret_value()
    in_pgpass = getattr(role, "pgpass", False)
    with passfile(instance._settings, "w") as (f, path):
        for entry in f:
            if entry.matches(username=username, port=port):
                if role.state == "absent" or not in_pgpass:
                    logger.info(
                        "removing entry for '%(username)s' in %(passfile)s (port=%(port)d)",
                        {"username": username, "passfile": path, "port": port},
                    )
                    f.lines.remove(entry)
                    return True, False
                elif password is not None and entry.password != password:
                    logger.info(
                        "updating password for '%(username)s' in %(passfile)s (port=%(port)d)",
                        {"username": username, "passfile": path, "port": port},
                    )
                    entry.password = password
                    return True, False
                return False, False
        else:
            if in_pgpass and password is not None:
                logger.info(
                    "adding an entry for '%(username)s' in %(passfile)s (port=%(port)d)",
                    {"username": username, "passfile": path, "port": port},
                )
                entry = pgpass.PassEntry("*", port, "*", username, password)
                f.lines.append(entry)
                f.sort()
                return True, False
            return False, False


class RoleInspect(TypedDict):
    pgpass: bool


@hookimpl
async def role_inspect(instance: PostgreSQLInstance, name: str) -> RoleInspect:
    try:
        with passfile(instance._settings, "r") as (f, _):
            return {
                "pgpass": any(e.matches(username=name, port=instance.port) for e in f)
            }
    except FileNotFoundError:
        return {"pgpass": False}

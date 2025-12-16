# SPDX-FileCopyrightText: 2021 Dalibo
#
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

from collections.abc import AsyncIterator, Callable
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any, Literal, TypeAlias, overload
from unittest.mock import patch

import httpx
import psycopg
import pytest
import tenacity

from pglift import instances, postgresql, types
from pglift.models import interface, system
from pglift.postgresql import pq
from pglift.settings import Settings
from pglift.types import Role

PostgresLogger: TypeAlias = Callable[[system.PostgreSQLInstance], None]

AuthType = Literal["peer", "password_command", "pgpass"]


@asynccontextmanager
async def running_instance(instance: system.Instance) -> AsyncIterator[None]:
    """Context manager to temporarily start an instance and run hooks."""
    if await postgresql.is_running(instance.postgresql):
        yield
        return

    await instances.start(instance)
    try:
        yield
    finally:
        await instances.stop(instance)


@asynccontextmanager
async def postgresql_stopped(
    instance: system.PostgreSQLInstance,
) -> AsyncIterator[None]:
    """Context manager to temporarily stop a PostgreSQL instance."""
    if not await postgresql.is_running(instance):
        yield
        return

    await postgresql.stop_postgresql(instance, mode="fast", wait=True)
    try:
        yield
    finally:
        await postgresql.start_postgresql(instance, foreground=False, wait=True)


def dsn(
    instance: system.PostgreSQLInstance, role: Role | None = None, **connargs: Any
) -> types.ConnectionString:
    assert "user" not in connargs
    if role is not None:
        connargs["user"] = role.name
        if role.password:
            assert "password" not in connargs
            connargs["password"] = role.password.get_secret_value()
    else:
        settings = instance._settings.postgresql
        connargs["user"] = settings.surole.name
        if "password" not in connargs:
            connargs["password"] = postgresql.pq.environ(
                instance, connargs["user"]
            ).get("PGPASSWORD")
    return pq.dsn(instance, **connargs)


def connect(
    instance: system.PostgreSQLInstance, role: Role | None = None, **connargs: Any
) -> psycopg.Connection[psycopg.rows.DictRow]:
    conninfo = dsn(instance, role=role, **connargs)
    return psycopg.connect(conninfo, autocommit=True, row_factory=psycopg.rows.dict_row)


async def async_connect(
    instance: system.PostgreSQLInstance, role: Role | None = None, **connargs: Any
) -> psycopg.AsyncConnection[psycopg.rows.DictRow]:
    conninfo = dsn(instance, role=role, **connargs)
    conn = await psycopg.AsyncConnection.connect(
        conninfo, row_factory=psycopg.rows.dict_row
    )
    await conn.set_autocommit(True)
    return conn


@overload
def execute(
    instance: system.PostgreSQLInstance,
    *queries: str,
    fetch: Literal[True],
    role: Role | None = None,
    **connargs: Any,
) -> list[Any]: ...


@overload
def execute(
    instance: system.PostgreSQLInstance,
    *queries: str,
    fetch: bool = False,
    role: Role | None = None,
    **connargs: Any,
) -> list[Any]: ...


def execute(
    instance: system.PostgreSQLInstance,
    *queries: str,
    fetch: bool = True,
    role: Role | None = None,
    **connargs: Any,
) -> list[Any] | None:
    if fetch and len(queries) > 1:
        raise ValueError("cannot use fetch=True with multiple queries")
    with connect(instance, role, **connargs) as conn:
        cur = conn.execute("; ".join(queries))
        if fetch:
            return cur.fetchall()
    return None


def check_connect(
    settings: Settings,
    postgresql_auth: AuthType,
    surole_name: str,
    instance_manifest: interface.Instance,
    instance: system.PostgreSQLInstance,
) -> None:
    surole = instance_manifest.surole(settings)
    pg_config = instance.configuration()
    port = pg_config.port
    connargs = {
        "host": str(pg_config.unix_socket_directories),
        "port": port,
        "user": surole.name,
    }
    if postgresql_auth == "peer":
        pass
    elif postgresql_auth == "pgpass":
        connargs["passfile"] = str(settings.postgresql.auth.passfile)
    else:
        with pytest.raises(
            psycopg.OperationalError, match="no password supplied"
        ) as exc_info:
            with patch.dict("os.environ", clear=True):
                psycopg.connect(**connargs).close()  # type: ignore[arg-type]
        assert exc_info.value.pgconn
        assert exc_info.value.pgconn.needs_password
        assert surole.password is not None
        connargs["password"] = surole.password.get_secret_value()
    if surole_name != "postgres":
        connargs["dbname"] = "postgres"
    with psycopg.connect(**connargs) as conn:  # type: ignore[arg-type]
        if postgresql_auth == "peer":
            assert not conn.pgconn.used_password
        else:
            assert conn.pgconn.used_password


def role_in_pgpass(
    passfile: Path,
    role: Role,
    *,
    port: int | str | None = None,
) -> bool:
    if not passfile.exists():
        return False
    password = ""
    if role.password:
        password = role.password.get_secret_value()
    parts = [role.name, password]
    if port is not None:
        parts = [str(port), "*"] + parts
    pattern = ":".join(parts)
    with passfile.open() as f:
        for line in f:
            if pattern in line:
                return True
    return False


@tenacity.retry(
    reraise=True,
    wait=tenacity.wait_fixed(2),
    stop=tenacity.stop_after_attempt(5),
    retry=tenacity.retry_if_exception_type(httpx.RequestError),
)
def http_get(*args: Any, **kwargs: Any) -> httpx.Response:
    return httpx.get(*args, **kwargs)


def passfile_entries(passfile: Path, *, role: str = "postgres") -> list[str]:
    return [line for line in passfile.read_text().splitlines() if f":{role}:" in line]


def config_dict(configpath: Path) -> dict[str, str]:
    config = {}
    for line in configpath.read_text().splitlines():
        key, value = line.split("=", 1)
        config[key] = value.strip()
    return config

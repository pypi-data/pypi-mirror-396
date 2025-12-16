# SPDX-FileCopyrightText: 2021 Dalibo
#
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

import functools
import sys
from collections.abc import AsyncIterator, Callable
from contextlib import AbstractAsyncContextManager, asynccontextmanager
from typing import Any, TypeAlias, overload

import psycopg.conninfo
import psycopg.errors
import psycopg.rows
from psycopg.abc import Params, QueryNoTemplate

from .. import ui, util
from ..models import PostgreSQLInstance, Standby
from ..postgresql import pq
from . import dryrun

logger = util.get_logger(__name__)

Connection: TypeAlias = psycopg.AsyncConnection[psycopg.rows.DictRow] | None


async def connect_dsn(conninfo: str) -> AbstractAsyncContextManager[Connection]:
    logger.debug(
        "connecting to PostgreSQL instance with: %s",
        pq.obfuscate_conninfo(conninfo),
    )
    return await psycopg.AsyncConnection.connect(
        conninfo, autocommit=True, row_factory=psycopg.rows.dict_row
    )


@asynccontextmanager
async def connect(
    instance: PostgreSQLInstance,
    *,
    user: str | None = None,
    password: str | None = None,
    dbname: str | None = None,
    **kwargs: Any,
) -> AsyncIterator[Connection]:
    postgresql_settings = instance._settings.postgresql
    if user is None:
        user = postgresql_settings.surole.name
    if password is None:
        password = pq.environ(instance, user).get("PGPASSWORD")

    if dbname is not None:
        kwargs["dbname"] = dbname
    build_conninfo = functools.partial(pq.dsn, instance, user=user, **kwargs)

    conninfo = build_conninfo(password=password)
    try:
        async with await connect_dsn(conninfo) as cnx:
            yield cnx
    except psycopg.OperationalError as e:
        # Don't try to connect to non-default in dry-run mode
        if dryrun.enabled() and dbname not in ["postgres", "template0", "template1"]:
            yield None
            return

        if not e.pgconn:
            raise
        if e.pgconn.needs_password:
            password = ui.prompt(f"Password for user {user}", hide_input=True)
        elif e.pgconn.used_password:
            password = ui.prompt(
                f"Password for user {user} is incorrect, re-enter a valid one",
                hide_input=True,
            )
        if not password:
            raise
        conninfo = build_conninfo(password=password)
        async with await connect_dsn(conninfo) as cnx:
            yield cnx


async def primary_connect(standby: Standby) -> AbstractAsyncContextManager[Connection]:
    """Connect to the primary of standby."""
    kwargs = {}
    if standby.password:
        kwargs["password"] = standby.password.get_secret_value()
    conninfo = psycopg.conninfo.make_conninfo(
        standby.primary_conninfo, dbname="template1", **kwargs
    )
    return await connect_dsn(conninfo)


@asynccontextmanager
async def transaction(cnx: Connection, /) -> AsyncIterator[None]:
    assert cnx is not None
    async with cnx.transaction():
        yield None


async def execute(
    cnx: Connection, query: QueryNoTemplate, params: Params | None = None, /
) -> None:
    if not dryrun.enabled() and cnx:
        await cnx.execute(query, params)


async def exec_fetch(
    cnx: Connection, query: QueryNoTemplate, params: Params | None = None, /
) -> tuple[str | None, list[psycopg.rows.DictRow] | None]:
    """Execute a query and return its results or None along with the status message."""
    assert cnx is not None
    cur = await cnx.execute(query, params)
    return cur.statusmessage, await cur.fetchall() if cur.description else None


@overload
async def fetchone(
    cnx: Connection,
    query: QueryNoTemplate,
    params: Params | None = None,
    /,
    *,
    row_factory: None = ...,
) -> psycopg.rows.DictRow | None: ...


@overload
async def fetchone(
    cnx: Connection,
    query: QueryNoTemplate,
    params: Params | None = None,
    /,
    *,
    row_factory: psycopg.rows.AsyncRowFactory[psycopg.rows.Row],
) -> psycopg.rows.Row | None: ...


async def fetchone(
    cnx: Connection,
    query: QueryNoTemplate,
    params: Params | None = None,
    /,
    *,
    row_factory: psycopg.rows.AsyncRowFactory[psycopg.rows.Row] | None = None,
) -> psycopg.rows.DictRow | psycopg.rows.Row | None:
    assert cnx is not None
    cur = cnx.cursor(row_factory=row_factory) if row_factory else cnx.cursor()
    async with cur:
        await cur.execute(query, params)
        return await cur.fetchone()


@overload
async def one(
    cnx: Connection,
    query: QueryNoTemplate,
    params: Params | None = None,
    /,
    *,
    row_factory: None = ...,
) -> psycopg.rows.DictRow: ...


@overload
async def one(
    cnx: Connection,
    query: QueryNoTemplate,
    params: Params | None = None,
    /,
    *,
    row_factory: psycopg.rows.AsyncRowFactory[psycopg.rows.Row],
) -> psycopg.rows.Row: ...


async def one(
    cnx: Connection,
    query: QueryNoTemplate,
    params: Params | None = None,
    /,
    *,
    row_factory: psycopg.rows.AsyncRowFactory[psycopg.rows.Row] | None = None,
) -> psycopg.rows.DictRow | psycopg.rows.Row:
    assert cnx is not None
    r = await fetchone(cnx, query, params, row_factory=row_factory)
    assert r is not None, f"{query!r} did not return any row"
    return r


@overload
async def fetchall(
    cnx: Connection,
    query: QueryNoTemplate,
    params: Params | None = None,
    /,
    *,
    row_factory: None = ...,
) -> list[psycopg.rows.DictRow]: ...


@overload
async def fetchall(
    cnx: Connection,
    query: QueryNoTemplate,
    params: Params | None = None,
    /,
    *,
    row_factory: psycopg.rows.AsyncRowFactory[psycopg.rows.Row],
) -> list[psycopg.rows.Row]: ...


async def fetchall(
    cnx: Connection,
    query: QueryNoTemplate,
    params: Params | None = None,
    /,
    *,
    row_factory: psycopg.rows.AsyncRowFactory[psycopg.rows.Row] | None = None,
) -> list[psycopg.rows.DictRow] | list[psycopg.rows.Row]:
    if not cnx:
        return []
    cur = cnx.cursor(row_factory=row_factory) if row_factory else cnx.cursor()
    async with cur:
        await cur.execute(query, params)
        return await cur.fetchall()


def encrypt_password(cnx: Connection, /, passwd: str, user: str) -> str:
    assert cnx is not None
    encoding = cnx.info.encoding
    return cnx.pgconn.encrypt_password(
        passwd.encode(encoding), user.encode(encoding)
    ).decode(encoding)


def add_notice_handler(cnx: Connection, callback: Callable[[Any], None], /) -> None:
    assert cnx is not None
    cnx.add_notice_handler(callback)


def default_notice_handler(diag: psycopg.errors.Diagnostic) -> None:
    if diag.message_primary is not None:
        sys.stderr.write(diag.message_primary + "\n")


def connection_password(cnx: Connection) -> str | None:
    return cnx.info.password if cnx else None


@asynccontextmanager
async def maybe_reconnect(
    cnx: Connection, instance: PostgreSQLInstance
) -> AsyncIterator[Connection]:
    if cnx is not None and cnx.closed:
        async with connect(instance) as cnx:
            yield cnx
    else:
        yield cnx

# SPDX-FileCopyrightText: 2021 Dalibo
#
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

from unittest.mock import patch

import psycopg.rows
import pytest

from pglift.models import PostgreSQLInstance
from pglift.settings import Settings
from pglift.system import db


@pytest.mark.anyio
async def test_connect_dsn() -> None:
    with patch("psycopg.AsyncConnection.connect", autospec=True) as connect:
        async with await db.connect_dsn("port=1234"):
            pass
    connect.assert_awaited_once_with(
        "port=1234", autocommit=True, row_factory=psycopg.rows.dict_row
    )


@pytest.mark.anyio
async def test_connect_instance(
    pg_instance: PostgreSQLInstance, settings: Settings
) -> None:
    with patch("psycopg.AsyncConnection.connect", autospec=True) as connect:
        cnx = db.connect(pg_instance, user="dba")
        connect.assert_not_awaited()
        async with cnx:
            pass
    passfile = settings.postgresql.auth.passfile
    assert passfile is not None and passfile.exists()
    connect.assert_awaited_once_with(
        f"user=dba port=999 host=/socks passfile={passfile} dbname=postgres",
        autocommit=True,
        row_factory=psycopg.rows.dict_row,
    )


@pytest.mark.anyio
async def test_primary_connect(standby_pg_instance: PostgreSQLInstance) -> None:
    standby = standby_pg_instance.standby
    assert standby
    with patch("psycopg.AsyncConnection.connect", autospec=True) as connect:
        async with await db.primary_connect(standby):
            pass
    connect.assert_awaited_once_with(
        "user=pg host=/tmp port=4242 dbname=template1",
        autocommit=True,
        row_factory=psycopg.rows.dict_row,
    )

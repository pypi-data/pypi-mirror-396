# SPDX-FileCopyrightText: 2021 Dalibo
#
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

import pytest

from pglift import databases, postgresql, privileges
from pglift.models import system
from pglift.models.interface import DefaultPrivilege, Privilege

from . import execute
from .conftest import DatabaseFactory, RoleFactory

pytestmark = pytest.mark.anyio


@pytest.fixture(scope="module", autouse=True)
async def _postgresql_running(pg_instance: system.PostgreSQLInstance) -> None:
    if not await postgresql.is_running(pg_instance):
        pytest.fail("instance is not running")


@pytest.fixture(autouse=True)
def roles_and_privileges(
    pg_instance: system.PostgreSQLInstance,
    role_factory: RoleFactory,
    database_factory: DatabaseFactory,
) -> None:
    role_factory("rol1")
    role_factory("rol2")
    database_factory("db1")
    database_factory("db2")
    execute(
        pg_instance,
        "ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO rol1",
        fetch=False,
        dbname="db1",
    )
    execute(
        pg_instance,
        "ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON FUNCTIONS TO rol2",
        fetch=False,
        dbname="db2",
    )


async def test_get_default(pg_instance: system.PostgreSQLInstance) -> None:
    expected = [
        DefaultPrivilege(  # type: ignore[call-arg]
            database="db1",
            schema="public",
            role="rol1",
            object_type="TABLE",
            privileges=[
                "DELETE",
                "REFERENCES",
                "INSERT",
                "SELECT",
                "TRUNCATE",
                "TRIGGER",
                "UPDATE",
            ]
            + (["MAINTAIN"] if pg_instance.version >= "17" else []),
        ),
        DefaultPrivilege(  # type: ignore[call-arg]
            database="db2",
            schema="public",
            role="rol2",
            object_type="FUNCTION",
            privileges=["EXECUTE"],
        ),
    ]
    prvlgs = await privileges.get(pg_instance, defaults=True)
    assert prvlgs == expected
    assert (
        await privileges.get(
            pg_instance, databases=["db1"], roles=["rol2"], defaults=True
        )
        == []
    )
    assert (
        await privileges.get(
            pg_instance, databases=["db2"], roles=["rol2"], defaults=True
        )
        == expected[-1:]
    )


async def test_get_general(
    pg_instance: system.PostgreSQLInstance, surole_name: str
) -> None:
    await databases.run(
        pg_instance,
        "CREATE TABLE table1 (x int, y varchar)",
        dbnames=["db1", "db2"],
    )
    await databases.run(
        pg_instance,
        "CREATE SCHEMA schema1",
        dbnames=["db2"],
    )
    await databases.run(
        pg_instance,
        "CREATE TABLE schema1.table3 (u int)",
        dbnames=["db2"],
    )
    await databases.run(
        pg_instance,
        "GRANT UPDATE ON table1 TO rol2; GRANT SELECT (x) ON table1 TO rol2; GRANT SELECT,INSERT ON schema1.table3 TO rol1",
        dbnames=["db2"],
    )
    def_priv = [
        "DELETE",
        "INSERT",
        "REFERENCES",
        "SELECT",
        "TRIGGER",
        "TRUNCATE",
        "UPDATE",
    ]
    if pg_instance.version >= "17":
        def_priv.append("MAINTAIN")
    expected = [
        Privilege(  # type: ignore[call-arg]
            database="db1",
            schema="public",
            object_type="TABLE",
            role=surole_name,
            privileges=def_priv,
            object_name="table1",
            column_privileges={},
        ),
        Privilege(  # type: ignore[call-arg]
            database="db1",
            schema="public",
            object_type="TABLE",
            role="rol1",
            privileges=def_priv,
            object_name="table1",
            column_privileges={},
        ),
        Privilege(  # type: ignore[call-arg]
            database="db2",
            schema="public",
            object_type="TABLE",
            role=surole_name,
            privileges=def_priv,
            object_name="table1",
            column_privileges={},
        ),
        Privilege(  # type: ignore[call-arg]
            database="db2",
            schema="public",
            object_type="TABLE",
            role="rol2",
            privileges=["UPDATE"],
            object_name="table1",
            column_privileges={"x": ["SELECT"]},
        ),
        Privilege(  # type: ignore[call-arg]
            database="db2",
            schema="schema1",
            object_type="TABLE",
            role=surole_name,
            privileges=def_priv,
            object_name="table3",
            column_privileges={},
        ),
        Privilege(  # type: ignore[call-arg]
            database="db2",
            schema="schema1",
            object_type="TABLE",
            role="rol1",
            privileges=["INSERT", "SELECT"],
            object_name="table3",
            column_privileges={},
        ),
    ]
    prvlgs = [
        p
        for p in await privileges.get(pg_instance, defaults=False)
        if p.database != "powa"
    ]

    def sort_key(p: DefaultPrivilege) -> str:
        return p.database + p.schema_ + p.role

    assert sorted(prvlgs, key=sort_key) == sorted(expected, key=sort_key)
    assert (
        await privileges.get(pg_instance, databases=["db1"], defaults=False)
        == sorted(expected, key=sort_key)[:2]
    )
    assert (
        await privileges.get(pg_instance, databases=["db2"], defaults=False)
        == sorted(expected, key=sort_key)[2:]
    )

# SPDX-FileCopyrightText: 2024 Dalibo
#
# SPDX-License-Identifier: GPL-3.0-or-later
from __future__ import annotations

import functools

import psycopg
import pytest

from pglift import profiles, roles, schemas
from pglift.models import interface, system

from . import dsn, execute
from .conftest import DatabaseFactory, RoleFactory

pytestmark = pytest.mark.anyio


async def test_profiles(
    pg_instance: system.PostgreSQLInstance,
    database_factory: DatabaseFactory,
    role_factory: RoleFactory,
) -> None:
    dbname = "profile_test1"
    database_factory(name=dbname)
    password = "George1984"
    role_options = "LOGIN", f"PASSWORD {password!r}"
    role_factory("customer1", *role_options, owns_objects_in=[dbname])
    role_factory("customer2", *role_options, owns_objects_in=[dbname])
    role1 = await roles.get(pg_instance, "customer1")
    role2 = await roles.get(pg_instance, "customer2")
    role_execute = functools.partial(
        execute, pg_instance, fetch=False, password=password, dbname=dbname
    )
    for schema_names, kind in [
        (["public", "schema_ro"], "read-only"),
        (["schema_rw"], "read-write"),
    ]:
        for s in schema_names:
            execute(
                pg_instance,
                f"CREATE SCHEMA {s}" if s != "public" else "",
                f"CREATE TABLE {s}.x1 (s TEXT)",
                f"CREATE SEQUENCE {s}.sr START 200",
                fetch=False,
                dbname=dbname,
            )
        for r in [role1, role2]:
            await profiles.set_for_role(
                pg_instance,
                r.name,
                interface.RoleProfile(kind=kind, schemas=schema_names, database=dbname),
            )

    for r in [role1, role2]:
        # Tests on schema with ro limited access
        for s in ["public", "schema_ro"]:
            with pytest.raises(psycopg.errors.InsufficientPrivilege):
                role_execute(f"INSERT INTO {s}.x1(s) VALUES ('a1')", role=r)
            with pytest.raises(psycopg.errors.InsufficientPrivilege):
                role_execute(f"DELETE FROM {s}.x1", role=r)
            with pytest.raises(psycopg.errors.InsufficientPrivilege):
                role_execute(f"SELECT nextval('{s}.sr')", role=r)
            assert role_execute(
                f"SELECT count(*) as c FROM {s}.x1", fetch=True, role=r
            ) == [{"c": 0}]
            assert role_execute(
                f"SELECT last_value FROM {s}.sr", fetch=True, role=r
            ) == [{"last_value": 200}]
        # tests on schema with rw access
        # Insert into table on schema with rw access (both role should be allowed)
        role_execute(
            "INSERT INTO schema_rw.x1(s) VALUES ('a1')",
            "SELECT nextval('schema_rw.sr'), nextval('schema_rw.sr')",
            role=r,
        )
    # Read data from rw schema should work
    assert role_execute(
        "SELECT count(*) as c from schema_rw.x1 where s ='a1'", fetch=True, role=role1
    ) == [{"c": 2}]
    assert role_execute(
        "SELECT last_value FROM schema_rw.sr", fetch=True, role=role1
    ) == [{"last_value": 203}]
    # Delete data into table with rw access
    assert role_execute(
        "WITH del as (DELETE from schema_rw.x1 RETURNING *)"
        "SELECT count(*) as count_del FROM DEL",
        fetch=True,
        role=role2,
    ) == [{"count_del": 2}]


def default_privileges(
    pg_instance: system.PostgreSQLInstance, dbname: str
) -> list[dict[str, str]]:
    r"""Return default privileges, similarly as \ddp in psql."""
    qs = """\
    SELECT pg_catalog.pg_get_userbyid(d.defaclrole) AS owner,
           n.nspname AS "schema",
           CASE d.defaclobjtype
                WHEN 'r' THEN 'table'
                WHEN 'S' THEN 'sequence'
                WHEN 'f' THEN 'function'
                WHEN 'T' THEN 'type'
                WHEN 'n' THEN 'schema' END AS type,
           pg_catalog.array_to_string(d.defaclacl, E',') AS privileges
    FROM pg_catalog.pg_default_acl d LEFT JOIN pg_catalog.pg_namespace n ON n.oid = d.defaclnamespace
    ORDER BY 1, 2, 3
    """
    return execute(pg_instance, qs, fetch=True, dbname=dbname)


@pytest.mark.parametrize("change_public_schema_owner", [False, True])
async def test_privileges_public_schema(
    pg_instance: system.PostgreSQLInstance,
    role_factory: RoleFactory,
    database_factory: DatabaseFactory,
    change_public_schema_owner: bool,
) -> None:
    dbname = "dbp"
    role_factory("dba")
    database_factory(dbname, owner="dba")

    if change_public_schema_owner:
        role_factory("otherdba")
        execute(
            pg_instance,
            "ALTER SCHEMA public OWNER TO otherdba",
            dbname=dbname,
            fetch=False,
        )
        async with await psycopg.AsyncConnection.connect(
            dsn(pg_instance, dbname=dbname), row_factory=psycopg.rows.dict_row
        ) as cnx:
            public_schema = next(s for s in await schemas.ls(cnx) if s.name == "public")
        assert public_schema.owner == "otherdba"
        schema_owner = "otherdba"
    else:
        schema_owner = "dba"

    await profiles.set_for_role(
        pg_instance,
        "dba",
        interface.RoleProfile(kind="read-only", database=dbname),
    )
    results = default_privileges(pg_instance, dbname=dbname)
    assert results == [
        {
            "privileges": f"dba=X/{schema_owner}",
            "owner": f"{schema_owner}",
            "schema": "public",
            "type": "function",
        },
        {
            "privileges": f"dba=r/{schema_owner}",
            "owner": f"{schema_owner}",
            "schema": "public",
            "type": "sequence",
        },
        {
            "privileges": f"dba=r/{schema_owner}",
            "owner": f"{schema_owner}",
            "schema": "public",
            "type": "table",
        },
        {
            "privileges": f"dba=U/{schema_owner}",
            "owner": f"{schema_owner}",
            "schema": "public",
            "type": "type",
        },
    ]


async def test_privileges(
    pg_instance: system.PostgreSQLInstance,
    database_factory: DatabaseFactory,
    role_factory: RoleFactory,
) -> None:
    dbname = "profile_test2"
    database_factory(dbname)
    password = "George1984"
    role_options = "LOGIN", f"PASSWORD {password!r}"
    role_factory("the_owner", *role_options, owns_objects_in=[dbname])
    owner = await roles.get(pg_instance, "the_owner")
    execute(
        pg_instance,
        "CREATE SCHEMA writable AUTHORIZATION the_owner;",
        fetch=False,
        dbname=dbname,
    )
    execute(
        pg_instance,
        "CREATE TABLE writable.b1 (s TEXT);",
        fetch=False,
        role=owner,
        password=password,
        dbname=dbname,
    )
    for role, kind in [
        ("read", "read-only"),
        ("write", "read-write"),
    ]:
        role_factory(role, *role_options, owns_objects_in=[dbname])
        await profiles.set_for_role(
            pg_instance,
            role,
            interface.RoleProfile(kind=kind, schemas=["writable"], database=dbname),
        )

    assert default_privileges(pg_instance, dbname=dbname) == [
        {
            "schema": "writable",
            "owner": "the_owner",
            "privileges": "read=X/the_owner,write=X/the_owner",
            "type": "function",
        },
        {
            "schema": "writable",
            "owner": "the_owner",
            "privileges": "read=r/the_owner,write=rw/the_owner",
            "type": "sequence",
        },
        {
            "schema": "writable",
            "owner": "the_owner",
            "privileges": "read=r/the_owner,write=arwdDx/the_owner",
            "type": "table",
        },
        {
            "schema": "writable",
            "owner": "the_owner",
            "privileges": "read=U/the_owner,write=U/the_owner",
            "type": "type",
        },
    ]

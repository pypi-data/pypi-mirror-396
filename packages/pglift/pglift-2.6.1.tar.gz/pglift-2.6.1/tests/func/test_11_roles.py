# SPDX-FileCopyrightText: 2021 Dalibo
#
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

import datetime
import functools

import psycopg
import pytest
from pydantic import SecretStr

from pglift import databases, exceptions, postgresql, roles, types
from pglift.models import interface, system
from pglift.settings import Settings
from pglift.testutil import model_copy_validate

from . import AuthType, connect, execute, role_in_pgpass
from .conftest import DatabaseFactory, RoleFactory

pytestmark = pytest.mark.anyio


@pytest.fixture(scope="module", autouse=True)
async def _postgresql_running(pg_instance: system.PostgreSQLInstance) -> None:
    if not await postgresql.is_running(pg_instance):
        pytest.fail("instance is not running")


async def test_exists(
    pg_instance: system.PostgreSQLInstance, role_factory: RoleFactory
) -> None:
    assert not await roles.exists(pg_instance, "absent")
    role_factory("present")
    assert await roles.exists(pg_instance, "present")


async def test_apply(
    settings: Settings,
    postgresql_auth: AuthType,
    instance_manifest: interface.Instance,
    pg_instance: system.PostgreSQLInstance,
) -> None:
    rolname = "applyme"
    passfile = settings.postgresql.auth.passfile

    def _role_in_pgpass(role: types.Role, *, port: int | str | None = None) -> bool:
        if postgresql_auth != "pgpass":
            return False
        assert passfile is not None
        return role_in_pgpass(passfile, role, port=port)

    role = interface.Role(name=rolname)
    assert not await roles.exists(pg_instance, role.name)
    r = await roles.apply(pg_instance, role)
    assert r.change_state == "created"
    assert await roles.exists(pg_instance, role.name)
    assert not role.has_password
    assert passfile is None or not _role_in_pgpass(role)
    assert (await roles.apply(pg_instance, role)).change_state is None  # no-op

    role = interface.Role(name=rolname, state="absent")
    assert await roles.exists(pg_instance, role.name)
    r = await roles.apply(pg_instance, role)
    assert r.change_state == "dropped"
    assert not await roles.exists(pg_instance, role.name)

    valid_until = datetime.datetime(2050, 1, 2, tzinfo=datetime.timezone.utc)
    role = interface.Role(
        name=rolname,
        password="passw0rd",
        connection_limit=3,
        valid_until=valid_until,
    )
    r = await roles.apply(pg_instance, role)
    assert r.change_state == "created"
    assert role.has_password
    (row,) = execute(
        pg_instance,
        f"select rolpassword from pg_authid where rolname = {role.name!r}",
    )
    if pg_instance.version >= "14":
        assert row["rolpassword"].startswith("SCRAM-SHA-256$4096:")
    else:
        assert row["rolpassword"].startswith("md5")
    assert passfile is None or not _role_in_pgpass(role)
    with pytest.raises(psycopg.OperationalError, match="is not permitted to log in"):
        execute(pg_instance, "select 1", dbname="template1", role=role)
    (record,) = execute(
        pg_instance,
        f"select rolvaliduntil, rolconnlimit from pg_roles where rolname = {role.name!r}",
    )
    assert record["rolvaliduntil"] == valid_until
    assert record["rolconnlimit"] == 3

    role = interface.Role(
        name=rolname,
        login=True,
        password="passw0rd",
        memberships=["pg_monitor"],
        pgpass=True,
    )
    r = await roles.apply(pg_instance, role)
    assert r.change_state == "changed"
    assert role.has_password
    assert passfile is None or _role_in_pgpass(role)
    with connect(pg_instance, role, dbname="template1"):
        pass
    rows = execute(
        pg_instance,
        """
        SELECT
            r.rolname AS role,
            ARRAY_AGG(m.rolname) AS member_of
        FROM
            pg_auth_members
            JOIN pg_authid m ON pg_auth_members.roleid = m.oid
            JOIN pg_authid r ON pg_auth_members.member = r.oid
        GROUP BY
            r.rolname
        """,
    )
    assert {"role": rolname, "member_of": ["pg_monitor"]} in rows

    pwchanged_role = model_copy_validate(role, {"password": "changed"})
    r = await roles.apply(pg_instance, pwchanged_role)
    if passfile is not None:
        assert r.change_state == "changed"
    else:
        # Password changes in the database are not detected.
        assert r.change_state is None

    nopw_role = model_copy_validate(role, {"password": None})
    r = await roles.apply(pg_instance, nopw_role)
    assert r.change_state is None

    memberships_changed_role = model_copy_validate(
        role,
        {
            "memberships": [
                {"role": "pg_monitor", "state": "absent"},
                {"role": "pg_read_all_stats", "state": "absent"},
            ]
        },
    )
    r = await roles.apply(pg_instance, memberships_changed_role)
    assert r.change_state == "changed"
    rows = execute(
        pg_instance,
        "SELECT member::regrole AS role FROM pg_auth_members",
    )
    assert {"role": rolname} not in rows

    role = interface.Role(
        name=rolname,
        login=True,
        password="passw0rd_changed",
        connection_limit=5,
        pgpass=True,
    )
    r = await roles.apply(pg_instance, role)
    assert r.change_state == "changed"
    assert role.has_password
    assert passfile is None or _role_in_pgpass(role)
    assert (await roles.get(pg_instance, rolname)).connection_limit == 5
    with connect(pg_instance, role, dbname="template1"):
        pass

    role = interface.Role(name=rolname, login=False, pgpass=False)
    r = await roles.apply(pg_instance, role)
    assert r.change_state == "changed"
    with pytest.raises(psycopg.OperationalError, match="is not permitted to log in"):
        execute(
            pg_instance,
            "select 1",
            dbname="template1",
            role=role,
            password="passw0rd_changed",
        )
    assert not role.has_password
    assert passfile is None or not _role_in_pgpass(role)
    assert (await roles.get(pg_instance, rolname)).connection_limit is None

    role = interface.Role(
        name=rolname,
        hba_records=[
            {
                "connection": {"address": "192.168.0.0/16"},
                "database": "db",
                "method": "trust",
            },
            {
                "connection": {
                    "address": "127.0.0.1",
                    "netmask": "255.255.255.255",
                },
                "database": "db",
                "method": "trust",
            },
        ],
    )
    await roles.apply(pg_instance, role)
    hba_path = pg_instance.datadir / "pg_hba.conf"
    auth_instance = instance_manifest.auth
    assert auth_instance
    hba = hba_path.read_text().splitlines()
    assert (
        f"host    db              {rolname}         192.168.0.0/16          trust"
        in hba
    )
    assert (
        f"host    db              {rolname}         127.0.0.1       255.255.255.255 trust"
        in hba
    )

    hbachanged_role = model_copy_validate(
        role,
        update={
            "hba_records": [
                {
                    "connection": {"address": "192.168.0.0/16"},
                    "database": "db",
                    "state": "absent",
                    "method": "trust",
                },
                {
                    "connection": {
                        "address": "127.0.0.1",
                        "netmask": "255.255.255.255",
                    },
                    "database": "db",
                    "method": "trust",
                },
            ],
        },
    )
    await roles.apply(pg_instance, hbachanged_role)
    hba = hba_path.read_text().splitlines()
    assert (
        f"host    db              {rolname}         192.168.0.0/16          trust"
        not in hba
    )
    assert (
        f"host    db              {rolname}         127.0.0.1       255.255.255.255 trust"
        in hba
    )

    role = interface.Role(name=rolname, state="absent")
    await roles.apply(pg_instance, hbachanged_role)
    hba = hba_path.read_text().splitlines()
    assert rolname not in hba


async def test_encrypted_password(pg_instance: system.PostgreSQLInstance) -> None:
    # Already encrypted password should be stored "as is"
    already_encrypted_password = (
        # This is encrypted "scret"
        "SCRAM-SHA-256$4096:kilIxOG9m0wvjkJtBVw+dg==$o2jKTC2nw+"
        "POUAVt5YARHuekubQ+LUeVH1cdCS4bKnw=:6y1eBzBUXITZPEiCb1H"
        "k6AscBq/gmgB5AnFz/57zI/g="
    )
    already_encrypted = interface.Role(
        name="already_encrypted",
        encrypted_password=already_encrypted_password,
        login=True,
    )
    assert (await roles.apply(pg_instance, already_encrypted)).change_state == "created"
    rows = execute(
        pg_instance,
        "select rolpassword from pg_authid where rolname = 'already_encrypted'",
    )
    assert rows == [{"rolpassword": already_encrypted_password}]

    # We cannot login with an already encrypted password
    with pytest.raises(
        psycopg.OperationalError, match="password authentication failed"
    ):
        execute(
            pg_instance,
            "select 1",
            dbname="template1",
            role=interface.Role(
                name="already_encrypted", password=already_encrypted_password
            ),
        )
    assert execute(
        pg_instance,
        "select 1 as v",
        dbname="template1",
        role=interface.Role(name="already_encrypted", password="scret"),
    ) == [{"v": 1}]


async def test_alter_surole_password(
    settings: Settings,
    instance_manifest: interface.Instance,
    pg_instance: system.PostgreSQLInstance,
    postgresql_auth: AuthType,
    surole_name: str,
    caplog: pytest.LogCaptureFixture,
) -> None:
    if postgresql_auth == "peer":
        pytest.skip(f"not applicable for auth:{postgresql_auth}")

    check_connect = functools.partial(connect, pg_instance)
    surole = await roles.get(pg_instance, surole_name)
    surole = model_copy_validate(
        surole,
        update={
            "password": instance_manifest.surole(settings).password,
            "state": "present",
        },
    )
    role = model_copy_validate(
        surole, update={"password": SecretStr("passw0rd_changed"), "state": "present"}
    )
    caplog.clear()
    r = await roles.apply(pg_instance, role)
    if postgresql_auth == "pgpass":
        assert r.change_state == "changed"
    else:
        assert r.change_state is None
    try:
        with check_connect(password="passw0rd_changed"):
            pass
    finally:
        with pytest.MonkeyPatch.context() as mp:
            mp.setenv("PGPASSWORD", "passw0rd_changed")
            r = await roles.apply(pg_instance, surole)
        if postgresql_auth == "pgpass":
            assert r.change_state == "changed"
        else:
            assert r.change_state is None
        with pytest.raises(
            psycopg.OperationalError, match="password authentication failed"
        ):
            with check_connect(password="passw0rd_changed"):
                pass
        with connect(pg_instance):
            pass


async def test_get(
    settings: Settings,
    instance_manifest: interface.Instance,
    pg_instance: system.PostgreSQLInstance,
    role_factory: RoleFactory,
    surole_name: str,
) -> None:
    with pytest.raises(exceptions.RoleNotFound, match="absent"):
        await roles.get(pg_instance, "absent")

    role = await roles.get(pg_instance, surole_name)
    assert role is not None
    surole = instance_manifest.surole(settings)
    assert role.name == surole_name
    if surole.password:
        assert role.has_password
        if settings.postgresql.surole.pgpass:
            assert role.model_dump(include={"pgpass"}) == {"pgpass": True}
        assert (
            await roles.get(pg_instance, surole_name, password=False)
        ).password is None
    assert role.login
    assert role.superuser
    assert role.replication

    role_factory(
        "r1",
        "LOGIN",
        "NOINHERIT",
        "CREATEROLE",
        "VALID UNTIL '2051-07-29T00:00+00:00'",
        "IN ROLE pg_monitor",
        "CONNECTION LIMIT 10",
    )
    r1 = await roles.get(pg_instance, "r1")
    assert r1.password is None
    assert not r1.inherit
    assert r1.login
    assert not r1.superuser
    assert not r1.replication
    assert not r1.createdb
    assert r1.createrole
    assert r1.connection_limit == 10
    assert len(r1.memberships) == 1
    assert r1.memberships[0].role == "pg_monitor"
    assert r1.valid_until == datetime.datetime(
        2051, 7, 29, tzinfo=datetime.timezone.utc
    )


async def test_ls(
    pg_instance: system.PostgreSQLInstance, role_factory: RoleFactory
) -> None:
    await roles.apply(
        pg_instance,
        interface.Role.model_validate({"name": "r1", "password": "secret"}),
    )
    role_factory(
        "r2",
        "LOGIN",
        "NOINHERIT",
        "CREATEDB",
        "VALID UNTIL '2051-07-29T00:00+00:00'",
        "IN ROLE pg_monitor",
        "CONNECTION LIMIT 10",
    )
    rls = await roles.ls(pg_instance)
    await roles.drop(pg_instance, interface.RoleDropped(name="r1"))
    assert {"r1", "r2"} & {r.name for r in rls}
    r1 = next(r for r in rls if r.name == "r1").model_dump(include={"has_password"})
    r2 = next(r for r in rls if r.name == "r2").model_dump(exclude={"pgpass"})
    assert r1 == {"has_password": True}
    assert r2 == {
        "connection_limit": 10,
        "has_password": False,
        "memberships": [{"role": "pg_monitor"}],
        "inherit": False,
        "login": True,
        "name": "r2",
        "replication": False,
        "superuser": False,
        "createdb": True,
        "createrole": False,
        "hba_records": [],
        "valid_until": datetime.datetime(
            2051, 7, 29, 0, 0, tzinfo=datetime.timezone.utc
        ),
        "validity": datetime.datetime(2051, 7, 29, 0, 0, tzinfo=datetime.timezone.utc),
    }


async def test_drop(
    pg_instance: system.PostgreSQLInstance, role_factory: RoleFactory
) -> None:
    with pytest.raises(exceptions.RoleNotFound, match="dropping_absent"):
        await roles.drop(pg_instance, interface.Role(name="dropping_absent"))
    role_factory("dropme")
    await roles.drop(pg_instance, interface.Role(name="dropme"))
    assert not await roles.exists(pg_instance, "dropme")


async def test_drop_reassign_owned(
    pg_instance: system.PostgreSQLInstance, database_factory: DatabaseFactory
) -> None:
    role1 = interface.Role(name="owner1", password="password", login=True)
    assert (await roles.apply(pg_instance, role1)).change_state == "created"
    assert await roles.exists(pg_instance, role1.name)

    role2 = interface.Role(name="owner2", password="password", login=True)
    assert (await roles.apply(pg_instance, role2)).change_state == "created"
    assert await roles.exists(pg_instance, role2.name)

    schema = "myschema"
    execute(pg_instance, f"CREATE SCHEMA {schema}", fetch=False, dbname="postgres")
    execute(
        pg_instance,
        f"GRANT ALL ON SCHEMA {schema} TO PUBLIC",
        fetch=False,
        dbname="postgres",
    )

    tablename = "myapp"
    execute(
        pg_instance,
        f"CREATE TABLE {schema}.{tablename} (id INT)",
        fetch=False,
        dbname="postgres",
        role=role1,
    )
    r = execute(
        pg_instance,
        f"SELECT tableowner FROM pg_catalog.pg_tables WHERE tablename = {tablename!r}",
        dbname="postgres",
        role=role1,
    )
    assert {"tableowner": role1.name} in r
    with pytest.raises(
        exceptions.DependencyError,
        match=r'role "owner1" cannot be dropped .* \(detail: owner of table myschema.myapp\)',
    ):
        await roles.drop(pg_instance, role1)

    role1 = model_copy_validate(
        role1, update={"reassign_owned": role2.name, "state": "absent"}
    )
    await roles.apply(pg_instance, role1)
    assert not await roles.exists(pg_instance, role1.name)
    r = execute(
        pg_instance,
        f"SELECT tableowner FROM pg_catalog.pg_tables WHERE tablename = {tablename!r}",
    )
    assert {"tableowner": role2.name} in r

    database_factory("db_owned", owner=role2.name)

    role2 = model_copy_validate(role2, update={"drop_owned": True, "state": "absent"})
    await roles.apply(pg_instance, role2)
    assert not await roles.exists(pg_instance, role2.name)
    r = execute(
        pg_instance,
        f"SELECT EXISTS (SELECT FROM pg_tables WHERE tablename = {tablename!r})",
    )
    assert {"exists": False} in r
    assert not await databases.exists(pg_instance, "db_owned")

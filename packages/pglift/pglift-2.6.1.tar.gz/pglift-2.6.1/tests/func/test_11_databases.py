# SPDX-FileCopyrightText: 2021 Dalibo
#
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

import datetime
import logging
import re
from collections.abc import AsyncIterator
from functools import partial
from pathlib import Path

import psycopg
import pytest
import tenacity

from pglift import databases, exceptions, instances, postgresql, task
from pglift.models import interface, system
from pglift.postgresql import pq
from pglift.settings import PostgreSQLVersion, Settings

from . import async_connect, connect, execute
from .conftest import DatabaseFactory, InstanceFactory, RoleFactory, TablespaceFactory

pytestmark = pytest.mark.anyio


@pytest.fixture(scope="module", autouse=True)
async def _postgresql_running(pg_instance: system.PostgreSQLInstance) -> None:
    if not await postgresql.is_running(pg_instance):
        pytest.fail("instance is not running")


@pytest.fixture
async def standby_instance_stopped(
    standby_instance: system.Instance,
) -> AsyncIterator[None]:
    await instances.stop(standby_instance)
    try:
        yield
    finally:
        await instances.start(standby_instance)


@pytest.fixture
def pg_database_owner(pg_version: PostgreSQLVersion, surole_name: str) -> str:
    return "pg_database_owner" if pg_version >= "15" else surole_name


async def test_exists(
    pg_instance: system.PostgreSQLInstance, database_factory: DatabaseFactory
) -> None:
    assert not await databases.exists(pg_instance, "absent")
    database_factory("present")
    assert await databases.exists(pg_instance, "present")


async def test_apply(
    pg_instance: system.PostgreSQLInstance, pg_database_owner: str, surole_name: str
) -> None:
    r = execute(
        pg_instance,
        "SELECT default_version FROM pg_available_extensions WHERE name='hstore'",
    )
    assert r is not None
    default_version = r[0]["default_version"]

    dbname = "applyme"
    database = interface.Database(
        name=dbname,
        settings={"work_mem": "1MB"},
        extensions=[{"name": "hstore", "version": default_version}],
        schemas=[{"name": "myapp"}, {"name": "my_schema"}],
        tablespace="pg_default",
        locale="en_US.utf8",
    )
    assert not await databases.exists(pg_instance, database.name)

    assert (await databases.apply(pg_instance, database)).change_state == "created"

    db = await databases.get(pg_instance, dbname)
    assert db.settings == {"work_mem": "1MB"}

    assert db.schemas == [
        interface.Schema(name="my_schema", owner=surole_name),
        interface.Schema(name="myapp", owner=surole_name),
        interface.Schema(name="public", owner=pg_database_owner),
    ]

    assert db.extensions == [
        interface.Extension(name="hstore", schema="public", version=default_version),  # type: ignore[call-arg]
    ]

    assert db.locale == "en_US.utf8"

    assert (await databases.apply(pg_instance, database)).change_state is None  # no-op

    database = interface.Database(
        name=dbname,
        owner=surole_name,
        settings={"work_mem": "1MB"},
        schemas=[
            interface.Schema(name="my_schema", owner=surole_name),
            interface.Schema(name="myapp", owner=surole_name),
            interface.Schema(name="public", owner=pg_database_owner),
        ],
        extensions=[
            {"name": "hstore", "schema": "my_schema", "version": default_version},
        ],
        tablespace="pg_default",
        locale="en_US.utf8",
    )
    assert (await databases.apply(pg_instance, database)).change_state == "changed"
    assert await databases.get(pg_instance, dbname) == database

    database = interface.Database(name=dbname, state="absent")
    assert await databases.exists(pg_instance, dbname)
    assert (await databases.apply(pg_instance, database)).change_state == "dropped"
    assert not await databases.exists(pg_instance, dbname)


async def test_apply_change_owner(
    pg_instance: system.PostgreSQLInstance,
    database_factory: DatabaseFactory,
    role_factory: RoleFactory,
    pg_database_owner: str,
    surole_name: str,
) -> None:
    database_factory("apply")
    database = interface.Database(name="apply")
    assert (await databases.apply(pg_instance, database)).change_state is None  # no-op
    assert (await databases.get(pg_instance, "apply")).owner == surole_name

    role_factory("dbapply")
    database = interface.Database(
        name="apply",
        owner="dbapply",
        schemas=[interface.Schema(name="public", owner=pg_database_owner)],
        tablespace="pg_default",
        locale="C",
    )
    assert (await databases.apply(pg_instance, database)).change_state == "changed"
    try:
        assert await databases.get(pg_instance, "apply") == database
    finally:
        await databases.drop(pg_instance, interface.DatabaseDropped(name="apply"))


async def test_apply_change_tablespace(
    standby_instance_stopped: system.Instance,
    pg_instance: system.PostgreSQLInstance,
    tablespace_factory: TablespaceFactory,
    database_factory: DatabaseFactory,
    pg_database_owner: str,
    surole_name: str,
) -> None:
    database_factory("apply")
    database = interface.Database(name="apply")
    assert (await databases.apply(pg_instance, database)).change_state is None  # no-op

    tablespace_factory("dbs2")
    database = interface.Database(
        name="apply",
        owner=surole_name,
        tablespace="dbs2",
        schemas=[interface.Schema(name="public", owner=pg_database_owner)],
        locale="C",
    )
    assert (await databases.apply(pg_instance, database)).change_state == "changed"
    assert await databases.get(pg_instance, "apply") == database


async def test_apply_update_schemas(
    pg_instance: system.PostgreSQLInstance,
    database_factory: DatabaseFactory,
    role_factory: RoleFactory,
    pg_database_owner: str,
    surole_name: str,
) -> None:
    database_factory("db3")
    execute(pg_instance, "CREATE SCHEMA my_schema", fetch=False, dbname="db3")

    assert (await databases.get(pg_instance, "db3")).schemas == [
        interface.Schema(name="my_schema", owner=surole_name),
        interface.Schema(name="public", owner=pg_database_owner),
    ]

    role_factory("schemauser")
    database = interface.Database(
        name="db3",
        schemas=[
            interface.Schema(name="my_schema", owner="schemauser"),
        ],
    )
    assert (await databases.apply(pg_instance, database)).change_state == "changed"
    assert (await databases.get(pg_instance, "db3")).schemas == [
        interface.Schema(name="my_schema", owner="schemauser"),
        interface.Schema(name="public", owner=pg_database_owner),
    ]

    database = interface.Database(
        name="db3",
        schemas=[
            interface.Schema(name="my_schema", state="absent", owner=surole_name),
        ],
    )
    assert (await databases.apply(pg_instance, database)).change_state == "changed"

    assert (await databases.get(pg_instance, "db3")).schemas == [
        interface.Schema(name="public", owner=pg_database_owner)
    ]


async def test_apply_update_extensions(
    pg_instance: system.PostgreSQLInstance, database_factory: DatabaseFactory
) -> None:
    database_factory("db4")
    execute(
        pg_instance,
        "CREATE SCHEMA my_schema",
        "CREATE SCHEMA second_schema",
        "CREATE EXTENSION unaccent WITH SCHEMA my_schema",
        "CREATE EXTENSION hstore WITH VERSION '1.4'",
        fetch=False,
        dbname="db4",
    )
    r = execute(
        pg_instance,
        "SELECT name, default_version FROM pg_available_extensions",
    )
    assert r is not None
    extversions = {e["name"]: e["default_version"] for e in r}
    unaccent_version = extversions["unaccent"]
    pgss_version = extversions["pg_stat_statements"]
    hstore_version = extversions["hstore"]
    intarray_version = extversions["intarray"]

    assert (await databases.get(pg_instance, "db4")).extensions == [
        interface.Extension(name="hstore", schema="public", version="1.4"),  # type: ignore[call-arg]
        interface.Extension(  # type: ignore[call-arg]
            name="unaccent", schema="my_schema", version=unaccent_version
        ),
    ]

    database = interface.Database(
        name="db4",
        extensions=[
            {"name": "pg_stat_statements", "schema": "my_schema"},
            {"name": "unaccent"},
            {"name": "hstore"},
            {"name": "intarray", "version": intarray_version},
        ],
    )
    assert (await databases.apply(pg_instance, database)).change_state == "changed"
    assert (await databases.get(pg_instance, "db4")).extensions == [
        interface.Extension(name="hstore", schema="public", version=hstore_version),  # type: ignore[call-arg]
        interface.Extension(name="intarray", schema="public", version=intarray_version),  # type: ignore[call-arg]
        interface.Extension(  # type: ignore[call-arg]
            name="pg_stat_statements", schema="my_schema", version=pgss_version
        ),
        interface.Extension(name="unaccent", schema="public", version=unaccent_version),  # type: ignore[call-arg]
    ]

    database = interface.Database(
        name="db4",
        extensions=[
            {"name": "hstore", "state": "absent"},
            {"name": "pg_stat_statements", "state": "absent"},
            {"name": "unaccent", "state": "absent"},
        ],
    )
    assert (await databases.apply(pg_instance, database)).change_state == "changed"
    assert [
        e.model_dump(by_alias=True)
        for e in (await databases.get(pg_instance, "db4")).extensions
    ] == [{"name": "intarray", "schema": "public", "version": intarray_version}]

    assert (await databases.apply(pg_instance, database)).change_state is None


async def test_apply_transaction(pg_instance: system.PostgreSQLInstance) -> None:
    dbname = "unknownext"
    database = interface.Database(
        name=dbname, extensions=[{"name": "unknownextension"}]
    )
    with pytest.raises(psycopg.errors.DatabaseError, match="unknownextension.control"):
        async with task.async_transaction():
            await databases.apply(pg_instance, database)
    assert not await databases.exists(pg_instance, dbname)


async def test_publications(
    pg_instance: system.PostgreSQLInstance,
    database_factory: DatabaseFactory,
    pg_database_owner: str,
    surole_name: str,
) -> None:
    database_factory("publisher")
    execute(
        pg_instance,
        "CREATE TABLE things (u int)",
        "CREATE TABLE users (s int)",
        "CREATE TABLE departments (n text)",
        "CREATE PUBLICATION test FOR TABLE users, departments",
        dbname="publisher",
        fetch=False,
    )
    db = await databases.get(pg_instance, "publisher")
    assert db.model_dump() == {
        "extensions": [],
        "locale": "C",
        "name": "publisher",
        "owner": surole_name,
        "publications": [{"name": "test"}],
        "schemas": [{"name": "public", "owner": pg_database_owner}],
        "settings": None,
        "subscriptions": [],
        "tablespace": "pg_default",
    }

    database = interface.Database(
        name="publisher",
        publications=[{"name": "mypub"}],
    )
    assert (await databases.apply(pg_instance, database)).change_state == "changed"

    (row,) = execute(
        pg_instance,
        "SELECT puballtables FROM pg_publication WHERE pubname = 'mypub'",
        dbname="publisher",
    )
    assert row["puballtables"] is True

    db = await databases.get(pg_instance, "publisher")
    assert db.model_dump() == {
        "extensions": [],
        "locale": "C",
        "name": "publisher",
        "owner": surole_name,
        "publications": [
            {"name": "mypub"},
            {"name": "test"},
        ],
        "schemas": [{"name": "public", "owner": pg_database_owner}],
        "settings": None,
        "subscriptions": [],
        "tablespace": "pg_default",
    }

    database = interface.Database(
        name="publisher",
        publications=[{"name": "test", "state": "absent"}],
    )
    assert (await databases.apply(pg_instance, database)).change_state == "changed"
    db = await databases.get(pg_instance, "publisher")
    assert db.model_dump()["publications"] == [
        {"name": "mypub"},
    ]

    assert (await databases.apply(pg_instance, database)).change_state is None


@pytest.fixture
def publisher_role() -> interface.Role:
    return interface.Role.model_validate(
        {"name": "app", "login": True, "password": "secret", "replication": True}
    )


@pytest.fixture
def published_dbname() -> str:
    return "app"


@pytest.fixture
def publication_name() -> str:
    return "pub"


@pytest.fixture
async def publisher_instance(
    settings: Settings,
    publisher_role: interface.Role,
    published_dbname: str,
    publication_name: str,
    surole_password: str | None,
    instance_factory: InstanceFactory,
    logger: logging.Logger,
) -> system.PostgreSQLInstance:
    _, instance = await instance_factory(
        settings.model_copy(
            update={
                "pgbackrest": None,
                "powa": None,
                "prometheus": None,
                "temboard": None,
            },
            deep=True,
        ),
        name="publisher",
        settings={
            "wal_level": "logical",
            "synchronous_commit": "remote_apply",
            "log_line_prefix": "",
        },
        # Either use surole_password which would be in password_command or set
        # a dummy password only needed at instance creation in order to get
        # --auth-local=md5 working.
        surole_password=surole_password or "super",
        auth={
            "local": "md5",
            "host": "md5",
        },
        state="started",
        roles=[publisher_role],
        databases=[
            {
                "name": published_dbname,
                "owner": publisher_role.name,
                "publications": [
                    {"name": publication_name},
                ],
            },
        ],
    )
    pg_instance = instance.postgresql
    assert pg_instance.configuration()["wal_level"] == "logical"
    execute(
        pg_instance,
        "CREATE TABLE t (s int)",
        dbname=published_dbname,
        role=publisher_role,
        fetch=False,
    )
    try:
        for line in postgresql.logs(pg_instance, timeout=0):
            logger.debug("publisher instance: %s", line.rstrip())
    except TimeoutError:
        pass
    return pg_instance


async def test_subscriptions(
    publisher_role: interface.Role,
    published_dbname: str,
    publication_name: str,
    publisher_instance: system.PostgreSQLInstance,
    role_factory: RoleFactory,
    pg_instance: system.PostgreSQLInstance,
    logger: logging.Logger,
    pg_database_owner: str,
) -> None:
    assert publisher_role.password is not None
    publisher_password = publisher_role.password.get_secret_value()
    connection = interface.ConnectionString(
        conninfo=pq.dsn(
            publisher_instance, user=publisher_role.name, dbname=published_dbname
        ),
        password=publisher_password,
    )
    with psycopg.connect(connection.full_conninfo):
        # Make sure the connection string to be used for subscription is usable.
        pass
    subname = "subs"
    subscription = {
        "name": subname,
        "connection": connection,
        "publications": [publication_name],
        "enabled": True,
    }
    dbname = "subscriber"
    role_factory(publisher_role.name)
    target = {
        "name": dbname,
        "owner": publisher_role.name,
        "clone": {
            "dsn": f"postgresql://{publisher_role.name}:{publisher_password}@127.0.0.1:{publisher_instance.port}/{published_dbname}",
            "schema_only": True,
        },
        "subscriptions": [subscription],
    }

    @tenacity.retry(
        reraise=True, wait=tenacity.wait_fixed(1), stop=tenacity.stop_after_attempt(5)
    )
    def check_replication(expected: int) -> None:
        try:
            for line in postgresql.logs(pg_instance, timeout=0):
                logger.debug("subscriber instance: %s", line.rstrip())
        except TimeoutError:
            pass
        for _ in range(3):
            execute(pg_instance, "SELECT pg_sleep(1)", dbname=dbname, fetch=False)
            (row,) = execute(pg_instance, "SELECT MAX(s) AS m FROM t", dbname=dbname)
            if (m := row["m"]) == expected:
                break
        else:
            pytest.fail(f"not replicated: {m} != {expected}")

    try:
        assert (
            await databases.apply(
                pg_instance, interface.Database.model_validate(target)
            )
        ).change_state == "created"
        actual = await databases.get(pg_instance, dbname)
        assert actual.model_dump() == {
            "locale": "C",
            "name": dbname,
            "owner": publisher_role.name,
            "settings": None,
            "schemas": [{"name": "public", "owner": pg_database_owner}],
            "extensions": [],
            "publications": [{"name": publication_name}],
            "subscriptions": [
                {
                    "name": "subs",
                    "connection": connection.model_dump(),
                    "publications": [publication_name],
                    "enabled": True,
                }
            ],
            "tablespace": "pg_default",
        }

        execute(
            publisher_instance,
            "INSERT INTO t VALUES (1), (2)",
            dbname=published_dbname,
            fetch=False,
        )
        check_replication(2)

        subscription["enabled"] = False
        assert (
            await databases.apply(
                pg_instance, interface.Database.model_validate(target)
            )
        ).change_state == "changed"
        actual = await databases.get(pg_instance, dbname)
        assert actual.model_dump() == {
            "locale": "C",
            "name": dbname,
            "owner": publisher_role.name,
            "settings": None,
            "schemas": [{"name": "public", "owner": pg_database_owner}],
            "extensions": [],
            "publications": [{"name": publication_name}],
            "subscriptions": [
                {
                    "name": "subs",
                    "connection": connection.model_dump(),
                    "publications": [publication_name],
                    "enabled": False,
                }
            ],
            "tablespace": "pg_default",
        }

        execute(
            publisher_instance,
            "INSERT INTO t VALUES (10)",
            dbname=published_dbname,
            fetch=False,
        )
        check_replication(2)

    finally:
        if await databases.exists(pg_instance, dbname):
            subscription["state"] = "absent"
            assert (
                await databases.apply(
                    pg_instance, interface.Database.model_validate(target)
                )
            ).change_state == "changed"
            actual = await databases.get(pg_instance, dbname)
            assert actual.model_dump()["subscriptions"] == []

            assert (
                await databases.apply(
                    pg_instance, interface.Database.model_validate(target)
                )
            ).change_state is None

            await databases.drop(pg_instance, interface.DatabaseDropped(name=dbname))


@pytest.fixture
async def clonable_database(
    role_factory: RoleFactory,
    database_factory: DatabaseFactory,
    pg_instance: system.PostgreSQLInstance,
) -> str:
    role_factory("cloner", "LOGIN")
    database_factory("db1", owner="cloner")
    await databases.run(
        pg_instance,
        "CREATE TABLE values AS SELECT * FROM generate_series(0, 100000, 2) AS v",
        dbnames=["db1"],
    )
    await databases.run(
        pg_instance, "ALTER TABLE values OWNER TO cloner", dbnames=["db1"]
    )
    return f"postgresql://cloner@127.0.0.1:{pg_instance.port}/db1"


async def test_clone(
    surole_name: str,
    clonable_database: str,
    pg_instance: system.PostgreSQLInstance,
    caplog: pytest.LogCaptureFixture,
) -> None:
    database = interface.Database.model_validate(
        {"name": "cloned_db", "clone": {"dsn": clonable_database}}
    )
    assert not await databases.exists(pg_instance, database.name)
    try:
        assert (await databases.apply(pg_instance, database)).change_state == "created"
        result = execute(
            pg_instance, "SELECT COUNT(*) AS count FROM values", dbname="cloned_db"
        )
        assert result == [{"count": 50001}]
    finally:
        await databases.drop(pg_instance, interface.DatabaseDropped(name="cloned_db"))

    database = interface.Database.model_validate(
        {
            "name": "cloned_schema",
            "clone": {"dsn": clonable_database, "schema_only": True},
        }
    )
    assert database.clone and database.clone.schema_only
    assert not await databases.exists(pg_instance, database.name)
    try:
        assert (await databases.apply(pg_instance, database)).change_state == "created"
        result = execute(
            pg_instance, "SELECT * FROM values LIMIT 1", dbname="cloned_schema"
        )
        assert result == []
    finally:
        await databases.drop(
            pg_instance, interface.DatabaseDropped(name="cloned_schema")
        )

    # DSN which target is a non existing database
    options = interface.CloneOptions(
        dsn=f"postgresql://{surole_name}@127.0.0.1:{pg_instance.port}/nosuchdb"
    )
    with (
        pytest.raises(exceptions.CommandError) as cm,
        caplog.at_level(logging.DEBUG, logger="pglift.database"),
    ):
        await databases.clone("cloned", options, pg_instance)
    expected = [
        r'pg_dump: error: .* database "nosuchdb" does not exist',
        r"pg_restore: error: input file is too short",
    ]
    for msg in caplog.messages:
        for idx, pattern in enumerate(expected[:]):
            if re.search(pattern, msg):
                del expected[idx]
                break
    if expected:
        pytest.fail(f"expected log message(s) not found: {expected}")

    assert cm.value.cmd[0] == str(postgresql.bindir(pg_instance) / "pg_dump")
    assert not await databases.exists(pg_instance, "cloned")

    # DSN which target is a non existing user
    options = interface.CloneOptions(
        dsn=f"postgresql://nosuchuser@127.0.0.1:{pg_instance.port}/postgres"
    )
    with pytest.raises(exceptions.CommandError) as cm:
        await databases.clone("cloned", options, pg_instance)
    assert cm.value.cmd[0] == str(postgresql.bindir(pg_instance) / "pg_dump")
    assert not await databases.exists(pg_instance, "cloned")

    # Target database does not exist
    with pytest.raises(exceptions.CommandError) as cm:
        await databases.clone("nosuchdb", database.clone, pg_instance)
    assert cm.value.cmd[0] == str(postgresql.bindir(pg_instance) / "pg_restore")
    assert not await databases.exists(pg_instance, "nosuchdb")


async def test_get(
    pg_instance: system.PostgreSQLInstance,
    database_factory: DatabaseFactory,
    pg_database_owner: str,
    surole_name: str,
) -> None:
    with pytest.raises(exceptions.DatabaseNotFound, match="absent"):
        await databases.get(pg_instance, "absent")

    database_factory("describeme")
    execute(pg_instance, "ALTER DATABASE describeme SET work_mem TO '3MB'", fetch=False)
    execute(
        pg_instance,
        "CREATE SCHEMA my_schema",
        "CREATE EXTENSION unaccent WITH SCHEMA my_schema",
        fetch=False,
        dbname="describeme",
    )
    database = await databases.get(pg_instance, "describeme")
    assert database.name == "describeme"
    assert database.settings == {"work_mem": "3MB"}
    assert database.schemas == [
        interface.Schema(name="my_schema", owner=surole_name),
        interface.Schema(name="public", owner=pg_database_owner),
    ]
    r = execute(
        pg_instance,
        "SELECT default_version FROM pg_available_extensions WHERE name='unaccent'",
    )
    assert r is not None
    default_version = r[0]["default_version"]
    assert database.extensions == [
        interface.Extension(  # type: ignore[call-arg]
            name="unaccent", schema="my_schema", version=default_version
        )
    ]


async def test_encoding(pg_instance: system.PostgreSQLInstance) -> None:
    async with await async_connect(pg_instance) as conn:
        assert await databases.encoding(conn) == "UTF8"


async def test_ls(
    pg_instance: system.PostgreSQLInstance,
    database_factory: DatabaseFactory,
    surole_name: str,
) -> None:
    database_factory("db1")
    database_factory("db2")
    dbs = await databases.ls(pg_instance)
    dbnames = [d.name for d in dbs]
    assert "db2" in dbnames
    dbs = await databases.ls(pg_instance, exclude_dbnames=("db2",))
    dbnames = [d.name for d in dbs]
    assert "db2" not in dbnames
    dbs = await databases.ls(pg_instance, dbnames=("db1",))
    dbnames = [d.name for d in dbs]
    assert "db2" not in dbnames
    assert len(dbs) == 1
    db1 = next(d for d in dbs).model_dump()
    db1.pop("size")
    db1["tablespace"].pop("size")
    assert db1 == {
        "acls": [],
        "collation": "C",
        "ctype": "C",
        "description": None,
        "encoding": "UTF8",
        "name": "db1",
        "owner": surole_name,
        "tablespace": {"location": "", "name": "pg_default"},
    }


async def test_drop(
    pg_instance: system.PostgreSQLInstance, database_factory: DatabaseFactory
) -> None:
    with pytest.raises(exceptions.DatabaseNotFound, match="absent"):
        await databases.drop(pg_instance, interface.DatabaseDropped(name="absent"))

    database_factory("dropme")
    await databases.drop(pg_instance, interface.DatabaseDropped(name="dropme"))
    assert not await databases.exists(pg_instance, "dropme")


async def test_drop_force(
    pg_version: PostgreSQLVersion,
    pg_instance: system.PostgreSQLInstance,
    database_factory: DatabaseFactory,
) -> None:
    database_factory("dropme")

    if pg_version >= "13":
        with connect(pg_instance, dbname="dropme"):
            with pytest.raises(psycopg.errors.ObjectInUse):
                await databases.drop(
                    pg_instance, interface.DatabaseDropped(name="dropme")
                )
            await databases.drop(
                pg_instance, interface.DatabaseDropped(name="dropme", force_drop=True)
            )
        assert not await databases.exists(pg_instance, "dropme")
    else:
        with pytest.raises(
            exceptions.UnsupportedError,
            match=r"^Force drop option can't be used with PostgreSQL < 13$",
        ):
            await databases.drop(
                pg_instance, interface.DatabaseDropped(name="dropme", force_drop=True)
            )


async def test_run(
    pg_instance: system.PostgreSQLInstance,
    database_factory: DatabaseFactory,
    caplog: pytest.LogCaptureFixture,
) -> None:
    database_factory("test")
    caplog.clear()
    with caplog.at_level(logging.INFO, logger="pglift"):
        result_run = await databases.run(
            pg_instance,
            "CREATE TABLE persons AS (SELECT 'bob' AS name)",
            dbnames=["test"],
        )
    expected = [
        "CREATE TABLE persons AS",
        "SELECT 1",
    ]
    for msg in caplog.messages:
        if re.search(expected[0], msg):
            del expected[0]
        if not expected:
            break
    else:
        pytest.fail(f"expected log message(s) not found: {expected}")
    assert not result_run
    result = execute(pg_instance, "SELECT * FROM persons", dbname="test")
    assert result == [{"name": "bob"}]
    result_run = await databases.run(
        pg_instance,
        "SELECT * from persons",
        dbnames=["test"],
    )
    assert result_run == {"test": [{"name": "bob"}]}


async def test_run_analyze(
    pg_instance: system.PostgreSQLInstance, database_factory: DatabaseFactory
) -> None:
    database_factory("test")

    @tenacity.retry(
        reraise=True,
        retry=tenacity.retry_if_exception_type(AssertionError),
        stop=tenacity.stop_after_attempt(5),
        wait=tenacity.wait_fixed(1),
    )
    def last_analyze() -> datetime.datetime:
        result = execute(
            pg_instance,
            "SELECT MIN(last_analyze) m FROM pg_stat_all_tables WHERE last_analyze IS NOT NULL",
            dbname="test",
        )[0]["m"]
        assert isinstance(result, datetime.datetime), result
        return result

    retrying = partial(
        tenacity.Retrying,
        retry=tenacity.retry_if_exception_type(AssertionError),
        stop=tenacity.stop_after_attempt(5),
        wait=tenacity.wait_fixed(0.2),
        reraise=True,
    )

    await databases.run(pg_instance, "ANALYZE")
    previous = last_analyze()
    await databases.run(pg_instance, "ANALYZE")
    for attempt in retrying():
        now = last_analyze()
        with attempt:
            assert now > previous
    await databases.run(pg_instance, "ANALYZE", exclude_dbnames=["test"])
    for attempt in retrying():
        with attempt:
            assert last_analyze() == now


async def test_run_output_notices(
    pg_instance: system.PostgreSQLInstance, capsys: pytest.CaptureFixture[str]
) -> None:
    await databases.run(
        pg_instance, "DO $$ BEGIN RAISE NOTICE 'foo'; END $$", dbnames=["postgres"]
    )
    captured = capsys.readouterr()
    assert captured.out == ""
    assert captured.err == "foo\n"


async def test_dump_error(pg_instance: system.PostgreSQLInstance) -> None:
    with pytest.raises(
        psycopg.OperationalError, match='database "absent" does not exist'
    ):
        await databases.dump(pg_instance, "absent")


@pytest.fixture
async def dumped_database(
    pg_instance: system.PostgreSQLInstance,
    database_factory: DatabaseFactory,
    pg_back_execpath: Path | None,
    surole_name: str,
    caplog: pytest.LogCaptureFixture,
) -> str:
    dbname = "dbtodump"
    database_factory(dbname)
    execute(
        pg_instance, "CREATE TABLE t AS (SELECT 1 AS c)", fetch=False, dbname=dbname
    )
    caplog.clear()
    with caplog.at_level(logging.DEBUG, logger="pglift.system"):
        await databases.dump(pg_instance, dbname)
    assert (
        f"backing up database {dbname!r} on instance {pg_instance}" in caplog.messages
    )
    cmd_messages = [r.message for r in caplog.records if r.name == "pglift.system.cmd"]
    dsn = f"dbname={dbname} user={surole_name} port={pg_instance.port} host={pg_instance.socket_directory}"
    if pg_instance._settings.postgresql.auth.passfile is not None:
        dsn += f" passfile={pg_instance._settings.postgresql.auth.passfile}"
    bindir = postgresql.bindir(pg_instance)
    if pg_back_execpath is not None:
        assert (
            cmd_messages[0]
            == f"{pg_back_execpath} -B {bindir} -b {pg_instance.dumps_directory} -d {dsn!r} {dbname} -K 7 -P 7"
        )
        assert "purging old dumps" in cmd_messages[-1]
    else:
        assert (
            f"{bindir / 'pg_dump'} -Fc -f {pg_instance.dumps_directory}"
            in cmd_messages[0]
        )
        assert dsn in cmd_messages[0]
    return dbname


async def test_dump(
    pg_instance: system.PostgreSQLInstance, dumped_database: str
) -> None:
    directory = pg_instance.dumps_directory
    assert directory.exists()
    assert list(directory.glob(f"{dumped_database}_*.dump"))


async def test_dumps(
    pg_instance: system.PostgreSQLInstance, dumped_database: str
) -> None:
    # Files with invalid name format should not be listed
    # File name doesn't contain "_"
    dump_file = pg_instance.dumps_directory / "dummy.dump"
    dump_file.touch()
    # Date is invalid
    dump_file = pg_instance.dumps_directory / "dummy_2024-13-32T00:00:00.dump"
    dump_file.touch()
    # Dump file name is valid
    dump_file = pg_instance.dumps_directory / "dummy_db_2024-12-10T00:00:00.dump"
    dump_file.touch()

    dumps = databases.dumps(pg_instance)
    dbnames = [d.dbname async for d in dumps]
    assert dumped_database in dbnames
    assert "dummy_db" in dbnames
    assert len(set(dbnames)) == 2

    dumps = databases.dumps(pg_instance, dbnames=(dumped_database,))
    dbnames = [d.dbname async for d in dumps]
    assert dumped_database in dbnames
    assert "dummy_db" not in dbnames
    assert len(set(dbnames)) == 1

    with pytest.raises(StopAsyncIteration):
        await databases.dumps(pg_instance, dbnames=("otherdb",)).__anext__()


async def test_restore(
    database_factory: DatabaseFactory,
    pg_instance: system.PostgreSQLInstance,
    dumped_database: str,
    caplog: pytest.LogCaptureFixture,
) -> None:
    async for _dump in databases.dumps(pg_instance, dbnames=(dumped_database,)):
        break
    else:
        pytest.fail(f"no dump found for {dumped_database}")

    target_dbname = f"{dumped_database}_restored"
    database_factory(target_dbname)
    caplog.clear()
    with caplog.at_level(logging.DEBUG, logger="pglift"):
        await databases.restore(pg_instance, _dump.id, target_dbname)
    assert (
        caplog.messages[0]
        == f"restoring dump for {dumped_database!r} on instance {pg_instance} into {target_dbname!r}"
    )
    r = execute(pg_instance, "TABLE t", fetch=True, dbname=target_dbname)
    assert r == [{"c": 1}]


async def test_locale(
    pg_instance: system.PostgreSQLInstance, caplog: pytest.LogCaptureFixture
) -> None:
    assert await postgresql.is_running(pg_instance)
    async with await async_connect(pg_instance) as conn:
        assert await databases.locale(conn, dbname="template1") == "C"

    execute(
        pg_instance,
        "CREATE DATABASE db_other_locales LC_COLLATE 'en_US.utf8' LC_CTYPE 'C' TEMPLATE template0",
        fetch=False,
    )
    caplog.clear()
    with caplog.at_level(logging.DEBUG, logger="pglift"):
        async with await async_connect(pg_instance) as conn:
            assert await databases.locale(conn, dbname="db_other_locales") is None
    assert any("cannot determine database locale" in s for s in caplog.messages)

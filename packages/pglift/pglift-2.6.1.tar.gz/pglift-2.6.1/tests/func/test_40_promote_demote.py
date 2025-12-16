# SPDX-FileCopyrightText: 2021 Dalibo
#
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

from pathlib import Path

import psycopg
import psycopg.errors
import pytest
import tenacity

from pglift import instances, pgbackrest, postgresql, roles
from pglift.models import interface, system
from pglift.settings import PostgreSQLVersion, Settings, _pgbackrest

from . import AuthType, async_connect, execute, postgresql_stopped

pytestmark = [pytest.mark.anyio, pytest.mark.standby]


@pytest.fixture(scope="module", autouse=True)
async def rewind_dbname(pg_instance: system.PostgreSQLInstance) -> str:
    """The database name used for the rewind connection.

    This is also the database in which GRANT EXECUTE statements needed for
    pg_rewind must be run.

    The fixture is in autouse because it needs to be executed before the standby
    gets promoted.
    """
    name = "rwdb"
    assert await postgresql.is_running(pg_instance)
    execute(pg_instance, f"CREATE DATABASE {name}", fetch=False)
    return name


@pytest.fixture(scope="module", autouse=True)
async def rewind_user(
    pg_instance: system.PostgreSQLInstance,
    rewind_dbname: str,
    pg_version: PostgreSQLVersion,
) -> interface.Role:
    """PostgreSQL "rewind" user, created on the source server to rewind from.

    The fixture is in autouse because it needs to be executed before the standby
    gets promoted.
    """
    name = "rewinder"
    method = "scram-sha-256" if pg_version >= "15" else "md5"
    role = interface.Role(
        name=name,
        password="dn!w3r^7@9",
        login=True,
        replication=True,
        hba_records=[
            interface.HbaRecordForRole(method=method, database=rewind_dbname),
            interface.HbaRecordForRole(method=method, database="replication"),
        ],
    )
    assert await postgresql.is_running(pg_instance)
    assert (await roles.apply(pg_instance, role)).change_state == "created"
    execute(
        pg_instance,
        f"GRANT EXECUTE ON function pg_catalog.pg_ls_dir(text, boolean, boolean) TO {name}",
        f"GRANT EXECUTE ON function pg_catalog.pg_stat_file(text, boolean) TO {name}",
        f"GRANT EXECUTE ON function pg_catalog.pg_read_binary_file(text) TO {name}",
        f"GRANT EXECUTE ON function pg_catalog.pg_read_binary_file(text, bigint, bigint, boolean) TO {name}",
        f"ALTER DATABASE {rewind_dbname} OWNER TO {name}",
        dbname=rewind_dbname,
        fetch=False,
    )
    return role


@pytest.fixture(scope="module")
async def promoted_instance(
    standby_instance: system.Instance,
) -> system.PostgreSQLInstance:
    assert await postgresql.is_running(standby_instance.postgresql)
    with pytest.MonkeyPatch.context() as mp:
        mp.setattr(pgbackrest, "CHECK_ON_PROMOTE", False)
        await instances.promote(standby_instance)
    return standby_instance.postgresql


async def test_promoted(
    promoted_instance: system.PostgreSQLInstance, instance_manifest: interface.Instance
) -> None:
    assert not promoted_instance.standby
    settings = promoted_instance._settings
    replrole = instance_manifest.replrole(settings)
    assert execute(
        promoted_instance,
        "SELECT * FROM pg_is_in_recovery()",
        role=replrole,
        dbname="template1",
    ) == [{"pg_is_in_recovery": False}]


async def test_connect(
    promoted_instance: system.PostgreSQLInstance,
    postgresql_auth: AuthType,
    surole_password: str | None,
) -> None:
    """Check that we can connect to the promoted instance."""
    settings = promoted_instance._settings
    pg_config = promoted_instance.configuration()
    connargs = {
        "host": str(pg_config.unix_socket_directories),
        "port": promoted_instance.port,
        "user": settings.postgresql.surole.name,
        "dbname": "postgres",
    }
    if postgresql_auth != "peer":
        connargs["password"] = surole_password
    with psycopg.connect(**connargs) as conn:  # type: ignore[arg-type]
        if postgresql_auth == "peer":
            assert not conn.pgconn.used_password
        else:
            assert conn.pgconn.used_password


@pytest.fixture(scope="module")
async def rewind_source(
    pg_instance: system.PostgreSQLInstance,
    rewind_user: interface.Role,
    rewind_dbname: str,
) -> postgresql.RewindSource:
    """The RewindSource used to demote the instance."""
    assert (host := pg_instance.socket_directory) is not None
    conninfo = psycopg.conninfo.make_conninfo(
        host=host, port=pg_instance.port, user=rewind_user.name, dbname=rewind_dbname
    )
    return postgresql.RewindSource(conninfo=conninfo, password=rewind_user.password)


@pytest.fixture(scope="module")
def before_demote_tablename() -> str:
    return "before_demote"


@pytest.fixture(scope="module")
async def demoted_instance(
    promoted_instance: system.PostgreSQLInstance,
    rewind_source: postgresql.RewindSource,
    pg_instance: system.PostgreSQLInstance,
    before_demote_tablename: str,
    settings: Settings,
) -> system.Instance:
    """The demoted 'instance', previously promoted, now back as a standby of the 'main' instance."""
    if pgbackrest_settings := settings.pgbackrest:
        await pgbackrest.stop("mystanza-test", pgbackrest_settings)
    execute(
        promoted_instance,
        f"CREATE TABLE {before_demote_tablename} AS (VALUES ('will be lost', true))",
        fetch=False,
    )

    async with postgresql_stopped(promoted_instance):
        await postgresql.ctl.set_data_checksums(promoted_instance, True)
        assert await postgresql.is_running(pg_instance)
        i = system.Instance.from_postgresql(promoted_instance)
        demoted = await instances.demote(i, rewind_source, rewind_opts=["--progress"])
    if pgbackrest_settings:
        await pgbackrest.start("mystanza-test", pgbackrest_settings)
    return demoted


async def test_demoted_pgpass(
    passfile: Path,
    demoted_instance: system.Instance,
    pg_instance: system.PostgreSQLInstance,
    surole_name: str,
) -> None:
    """The passfile contains entries for the demoted instance (as well as the primary one)."""
    content = passfile.read_text()
    assert f"*:{demoted_instance.postgresql.port}:*:{surole_name}:" in content
    assert f"*:{pg_instance.port}:*:{surole_name}:" in content


async def test_demoted_rewound(
    demoted_instance: system.Instance, before_demote_tablename: str
) -> None:
    """Demoted instance has lost data from the divergence to the source server."""
    async with await async_connect(demoted_instance.postgresql) as conn:
        with pytest.raises(psycopg.errors.UndefinedTable):
            await conn.execute(f"TABLE {before_demote_tablename}")


async def test_demoted_standby_setup(
    demoted_instance: system.Instance,
    rewind_user: interface.Role,
) -> None:
    """Standby is set up on the demoted instance."""
    stdby = demoted_instance.postgresql.standby
    assert (
        stdby is not None
        and stdby.user == rewind_user.name
        and stdby.password == rewind_user.password
    )
    async with await async_connect(demoted_instance.postgresql) as conn:
        assert await instances.is_in_recovery(conn)


@tenacity.retry(
    retry=tenacity.retry_if_exception_type(psycopg.errors.UndefinedTable),
    wait=tenacity.wait_fixed(0.5),
    stop=tenacity.stop_after_attempt(20),
)
async def get_replicated_table(
    conn: psycopg.AsyncConnection[dict[str, int]], name: str
) -> list[dict[str, int]]:
    return await (await conn.execute(f"TABLE {name}")).fetchall()


async def test_demoted_replication(
    pg_instance: system.PostgreSQLInstance,
    demoted_instance: system.Instance,
) -> None:
    """Replication on the demoted instance is functional."""
    assert (await postgresql.replication_lag(demoted_instance.postgresql)) == 0
    tablename = "after_demote"
    execute(
        pg_instance,
        f"CREATE TABLE {tablename} AS (VALUES (1, 2, 3))",
        fetch=False,
    )
    async with await async_connect(demoted_instance.postgresql) as conn:
        rows = await get_replicated_table(conn, tablename)
    assert rows == [{"column1": 1, "column2": 2, "column3": 3}]


async def test_demoted_pgbackrest(
    pgbackrest_settings: _pgbackrest.Settings,
    demoted_instance: system.Instance,
    pgbackrest_password: str | None,
) -> None:
    """pgBackRest configuration and WAL archival check on the demoted instance."""
    svc = demoted_instance.service(pgbackrest.models.Service)
    await pgbackrest.check(
        demoted_instance.postgresql, svc, pgbackrest_settings, pgbackrest_password
    )

# SPDX-FileCopyrightText: 2021 Dalibo
#
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

from pathlib import Path

import psycopg
import pytest
import tenacity

from pglift import exceptions, instances, postgresql
from pglift.models import interface, system
from pglift.postgresql import Standby, wal_replay_pause_state
from pglift.settings import PostgreSQLVersion, Settings
from pglift.types import Status

from . import async_connect, execute
from .conftest import DatabaseFactory

pytestmark = pytest.mark.anyio


async def test_password(
    standby_pg_instance: system.PostgreSQLInstance, replrole_password: str
) -> None:
    assert standby_pg_instance.standby
    assert (
        standby_pg_instance.standby.password
        and standby_pg_instance.standby.password.get_secret_value() == replrole_password
    )


async def test_primary_conninfo(standby_pg_instance: system.PostgreSQLInstance) -> None:
    assert standby_pg_instance.standby
    assert standby_pg_instance.standby.primary_conninfo


async def test_slot(
    pg_instance: system.PostgreSQLInstance,
    standby_manifest: interface.Instance,
    standby_pg_instance: system.PostgreSQLInstance,
) -> None:
    assert standby_manifest.standby
    slotname = standby_manifest.standby.slot
    assert standby_pg_instance.standby
    assert standby_pg_instance.standby.slot == slotname
    rows = execute(pg_instance, "SELECT slot_name FROM pg_replication_slots")
    assert [r["slot_name"] for r in rows] == [slotname]


async def test_pgpass(
    settings: Settings,
    passfile: Path,
    standby_pg_instance: system.PostgreSQLInstance,
    surole_name: str,
    pgbackrest_available: bool,
) -> None:
    content = passfile.read_text()
    if not pgbackrest_available:
        assert str(standby_pg_instance.port) not in content
    else:
        assert f"*:{standby_pg_instance.port}:*:{surole_name}:" in content
        backup = settings.postgresql.backuprole.name
        assert f"*:{standby_pg_instance.port}:*:{backup}:" in content


async def test_is_in_recovery(
    standby_pg_instance: system.PostgreSQLInstance, surole_password: str | None
) -> None:
    async with await async_connect(
        standby_pg_instance, password=surole_password
    ) as conn:
        assert await instances.is_in_recovery(conn)


async def test_wait_recovery_finished(
    standby_pg_instance: system.PostgreSQLInstance, surole_password: str | None
) -> None:
    async with await async_connect(
        standby_pg_instance, password=surole_password
    ) as conn:
        with pytest.raises(exceptions.InstanceStateError, match="still in recovery"):
            await instances.wait_recovery_finished(conn, timeout=1)


async def test_wal_replay_is_paused(
    standby_pg_instance: system.PostgreSQLInstance,
) -> None:
    assert await wal_replay_pause_state(standby_pg_instance) == "not paused"
    execute(standby_pg_instance, "SELECT pg_wal_replay_pause()")
    assert await wal_replay_pause_state(standby_pg_instance) == "paused"
    execute(standby_pg_instance, "SELECT pg_wal_replay_resume()")
    assert await wal_replay_pause_state(standby_pg_instance) == "not paused"


async def test_replication(
    settings: Settings,
    pg_version: PostgreSQLVersion,
    pg_instance: system.PostgreSQLInstance,
    instance_manifest: interface.Instance,
    database_factory: DatabaseFactory,
    standby_instance: system.Instance,
    standby_pg_instance: system.PostgreSQLInstance,
) -> None:
    assert standby_pg_instance.standby

    replrole = instance_manifest.replrole(settings)
    assert replrole

    async def get_stdby() -> Standby | None:
        return (await instances._get(standby_instance, Status.running)).standby

    class OutOfSync(AssertionError):
        pass

    @tenacity.retry(
        retry=tenacity.retry_if_exception_type(psycopg.OperationalError),
        wait=tenacity.wait_fixed(2),
        stop=tenacity.stop_after_attempt(5),
    )
    def assert_db_replicated() -> None:
        rows = execute(
            standby_pg_instance,
            "SELECT * FROM t",
            role=replrole,
            dbname="test",
        )
        if rows[0]["i"] != 1:
            pytest.fail(f"table 't' not replicated; rows: {rows}")

    @tenacity.retry(
        retry=tenacity.retry_if_exception_type(OutOfSync),
        wait=tenacity.wait_fixed(2),
        stop=tenacity.stop_after_attempt(5),
    )
    async def assert_replicated(expected: int) -> None:
        rlag = await postgresql.replication_lag(standby_pg_instance)
        assert rlag is not None
        row = execute(
            standby_pg_instance,
            "SELECT * FROM t",
            role=replrole,
            dbname="test",
        )
        if row[0]["i"] != expected:
            assert rlag > 0
            raise OutOfSync
        if rlag > 0:
            raise OutOfSync
        if rlag != 0:
            pytest.fail(f"non-zero replication lag: {rlag}")

    assert await postgresql.is_running(pg_instance)
    assert await postgresql.is_running(standby_pg_instance)

    database_factory("test", owner=replrole.name)
    execute(
        pg_instance,
        "CREATE TABLE t AS (SELECT 1 AS i)",
        dbname="test",
        fetch=False,
        role=replrole,
    )
    stdby = await get_stdby()
    assert stdby is not None
    assert psycopg.conninfo.conninfo_to_dict(
        stdby.primary_conninfo
    ) == psycopg.conninfo.conninfo_to_dict(standby_pg_instance.standby.primary_conninfo)
    assert stdby.password == replrole.password
    assert stdby.slot == standby_pg_instance.standby.slot
    assert stdby.replication_lag is not None
    assert stdby.wal_replay_pause_state == "not paused"
    if pg_version >= "12":
        assert str(stdby.wal_sender_state) == "streaming"

    assert execute(
        standby_pg_instance,
        "SELECT * FROM pg_is_in_recovery()",
        role=replrole,
        dbname="template1",
    ) == [{"pg_is_in_recovery": True}]

    assert_db_replicated()

    execute(
        pg_instance,
        "UPDATE t SET i = 42",
        dbname="test",
        role=replrole,
        fetch=False,
    )

    await assert_replicated(42)

    stdby = await get_stdby()
    assert stdby is not None
    assert stdby.replication_lag == 0
    if pg_version >= "12":
        assert str(stdby.wal_sender_state) == "streaming"

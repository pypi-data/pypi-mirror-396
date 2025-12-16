# SPDX-FileCopyrightText: 2024 Dalibo
#
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

from collections.abc import AsyncIterator

import pytest

from pglift import replication_slots
from pglift.models import interface, system

from . import async_connect

pytestmark = pytest.mark.anyio


@pytest.fixture
async def temp_slot(
    pg_instance: system.PostgreSQLInstance,
) -> AsyncIterator[interface.ReplicationSlot]:
    slot = interface.ReplicationSlot(name="aslot")
    async with await async_connect(pg_instance) as conn:
        r = await replication_slots.apply(conn, slot)
        assert r.change_state == "created"
        yield slot
        slot = slot.model_copy(update={"state": "absent"})
        r = await replication_slots.apply(conn, slot)
        assert r.change_state == "dropped"
        assert not await replication_slots.exists(conn, slot.name)


async def test_apply_no_op(
    pg_instance: system.PostgreSQLInstance, temp_slot: interface.ReplicationSlot
) -> None:
    async with await async_connect(pg_instance) as conn:
        r = await replication_slots.apply(conn, temp_slot)
        assert r.change_state is None


async def test_ls(
    pg_instance: system.PostgreSQLInstance,
    replication_slot: interface.ReplicationSlot,
    temp_slot: str,
) -> None:
    async with await async_connect(pg_instance) as conn:
        assert await replication_slots.ls(conn) == [
            temp_slot,
            interface.ReplicationSlot(name=replication_slot),
        ]

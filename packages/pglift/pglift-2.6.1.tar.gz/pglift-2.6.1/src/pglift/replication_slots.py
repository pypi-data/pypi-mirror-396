# SPDX-FileCopyrightText: 2024 Dalibo
#
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

import psycopg.rows

from . import sql, util
from .models import interface
from .system import db

logger = util.get_logger(__name__)


async def ls(cnx: db.Connection) -> list[interface.ReplicationSlot]:
    return await db.fetchall(
        cnx,
        sql.query("replication_slots"),
        row_factory=psycopg.rows.class_row(interface.ReplicationSlot),
    )


async def exists(cnx: db.Connection, name: str) -> bool:
    row = await db.fetchone(
        cnx, "SELECT true FROM pg_replication_slots WHERE slot_name = %s", (name,)
    )
    return row is not None


async def apply(
    cnx: db.Connection, slot: interface.ReplicationSlot
) -> interface.ApplyResult:
    name = slot.name
    if not await exists(cnx, name) and slot.state == "present":
        logger.info("creating replication slot '%s'", name)
        await db.execute(cnx, "SELECT pg_create_physical_replication_slot(%s)", (name,))
        return interface.ApplyResult(change_state="created")
    elif slot.state == "absent":
        logger.info("dropping replication slot '%s'", name)
        await db.execute(cnx, "SELECT pg_drop_replication_slot(%s)", (name,))
        return interface.ApplyResult(change_state="dropped")
    return interface.ApplyResult(change_state=None)

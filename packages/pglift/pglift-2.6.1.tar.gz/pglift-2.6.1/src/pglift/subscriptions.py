# SPDX-FileCopyrightText: 2021 Dalibo
#
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

import psycopg.rows

from . import sql, util
from .models import interface
from .system import db

logger = util.get_logger(__name__)


async def ls(cnx: db.Connection, dbname: str) -> list[interface.Subscription]:
    return await db.fetchall(
        cnx,
        sql.query("subscriptions"),
        {"datname": dbname},
        row_factory=psycopg.rows.kwargs_row(interface.Subscription.from_row),
    )


async def apply(
    cnx: db.Connection, subscription: interface.Subscription, dbname: str
) -> bool:
    absent = subscription.state == "absent"
    existing = {p.name: p for p in await ls(cnx, dbname)}
    actual = existing.get(subscription.name, None)
    name = sql.Identifier(subscription.name)
    if not absent:
        publications = ", ".join(p for p in subscription.publications)
        if actual is None:
            logger.info(
                "creating subscription %s in database %s", subscription.name, dbname
            )
            conninfo = subscription.connection.full_conninfo
            await db.execute(
                cnx,
                sql.SQL(
                    f"CREATE SUBSCRIPTION {{name}} CONNECTION {conninfo!r} PUBLICATION {publications} WITH (enabled = {{enabled}})"
                ).format(name=name, enabled=sql.Literal(subscription.enabled)),
            )
        else:
            logger.info(
                "altering subscription %s of database %s", subscription.name, dbname
            )
            await db.execute(
                cnx,
                sql.SQL(
                    f"ALTER SUBSCRIPTION {{name}} SET PUBLICATION {publications}"
                ).format(name=name),
            )
            if actual.enabled != subscription.enabled:
                await db.execute(
                    cnx,
                    sql.SQL(
                        f"ALTER SUBSCRIPTION {{name}} {'ENABLE' if subscription.enabled else 'DISABLE'}"
                    ).format(name=name),
                )
        return True
    elif actual is not None:
        logger.info(
            "dropping subscription %s from database %s", subscription.name, dbname
        )
        await db.execute(
            cnx, sql.SQL("DROP SUBSCRIPTION IF EXISTS {name}").format(name=name)
        )
        return True
    return False

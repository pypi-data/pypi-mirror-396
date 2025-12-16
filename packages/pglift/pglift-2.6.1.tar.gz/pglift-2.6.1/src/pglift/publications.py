# SPDX-FileCopyrightText: 2021 Dalibo
#
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

import psycopg.rows

from . import sql, util
from .models import interface
from .system import db

logger = util.get_logger(__name__)


async def ls(cnx: db.Connection) -> list[interface.Publication]:
    return await db.fetchall(
        cnx,
        sql.query("publications"),
        row_factory=psycopg.rows.class_row(interface.Publication),
    )


async def apply(
    cnx: db.Connection, publication: interface.Publication, dbname: str
) -> bool:
    absent = publication.state == "absent"
    exists = publication.name in {p.name for p in await ls(cnx)}
    if not absent and not exists:
        logger.info("creating publication %s in database %s", publication.name, dbname)
        await db.execute(
            cnx,
            sql.SQL("CREATE PUBLICATION {name} FOR ALL TABLES").format(
                name=sql.Identifier(publication.name)
            ),
        )
        return True
    elif absent and exists:
        logger.info(
            "dropping publication %s from database %s", publication.name, dbname
        )
        await db.execute(
            cnx,
            sql.SQL("DROP PUBLICATION IF EXISTS {name}").format(
                name=sql.Identifier(publication.name)
            ),
        )
        return True
    return False

# SPDX-FileCopyrightText: 2021 Dalibo
#
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

import psycopg.rows

from . import sql, util
from .models import interface
from .system import db

logger = util.get_logger(__name__)


async def ls(cnx: db.Connection) -> list[interface.Extension]:
    """Return list of extensions created in connected database using CREATE EXTENSION"""
    return await db.fetchall(
        cnx,
        sql.query("list_extensions"),
        row_factory=psycopg.rows.class_row(interface.Extension),
    )


async def create(
    cnx: db.Connection, extension: interface.Extension, dbname: str
) -> None:
    msg, args = "creating extension '%(name)s'", {"name": extension.name}
    query = sql.SQL("CREATE EXTENSION IF NOT EXISTS {}").format(
        sql.Identifier(extension.name)
    )
    if extension.schema_:
        query += sql.SQL(" SCHEMA {}").format(sql.Identifier(extension.schema_))
        msg += " in schema '%(schema)s'"
        args["schema"] = extension.schema_
    if extension.version:
        query += sql.SQL(" VERSION {}").format(sql.Identifier(extension.version))
        msg += " with version %(version)s"
        args["version"] = extension.version
    query += sql.SQL(" CASCADE")
    msg += " in database %(dbname)s"
    args["dbname"] = dbname
    logger.info(msg, args)
    await db.execute(cnx, query)


async def alter_schema(cnx: db.Connection, name: str, schema: str) -> None:
    opts = sql.SQL("SET SCHEMA {}").format(sql.Identifier(schema))
    logger.info("setting '%s' extension schema to '%s'", name, schema)
    await db.execute(
        cnx, sql.query("alter_extension", extension=sql.Identifier(name), opts=opts)
    )


async def alter_version(cnx: db.Connection, name: str, version: str) -> None:
    opts = sql.SQL("UPDATE TO {}").format(sql.Identifier(version))
    logger.info("updating '%s' extension version to '%s'", name, version)
    await db.execute(
        cnx, sql.query("alter_extension", extension=sql.Identifier(name), opts=opts)
    )


async def drop(cnx: db.Connection, name: str) -> None:
    logger.info("dropping extension '%s'", name)
    await db.execute(cnx, sql.query("drop_extension", extension=sql.Identifier(name)))


async def current_schema(cnx: db.Connection) -> str:
    return await db.one(
        cnx, "SELECT current_schema()", row_factory=psycopg.rows.scalar_row
    )


async def apply(
    cnx: db.Connection, extension: interface.Extension, dbname: str
) -> bool:
    """Apply the state defined by 'extension' in connected database and return
    True if something changed.
    """
    for existing in await ls(cnx):
        if extension.name == existing.name:
            if extension.state == "absent":
                await drop(cnx, extension.name)
                return True

            changed = False
            new_schema = extension.schema_ or await current_schema(cnx)
            if new_schema != existing.schema_:
                await alter_schema(cnx, extension.name, new_schema)
                changed = True

            default_version = await db.one(
                cnx,
                sql.query("extension_default_version"),
                {"extension_name": extension.name},
                row_factory=psycopg.rows.scalar_row,
            )
            new_version = extension.version or default_version
            if new_version != existing.version:
                await alter_version(cnx, extension.name, new_version)
                changed = True
            return changed

    if extension.state != "absent":
        await create(cnx, extension, dbname)
        return True

    return False

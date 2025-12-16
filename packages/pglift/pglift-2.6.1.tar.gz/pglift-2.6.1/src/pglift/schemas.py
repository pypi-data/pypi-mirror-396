# SPDX-FileCopyrightText: 2021 Dalibo
#
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

import psycopg.rows

from . import exceptions, sql, util
from .models import interface
from .system import db

logger = util.get_logger(__name__)


async def ls(cnx: db.Connection) -> list[interface.Schema]:
    """Return list of schemas of database."""
    return await db.fetchall(
        cnx,
        sql.query("list_schemas"),
        row_factory=psycopg.rows.class_row(interface.Schema),
    )


async def owner(cnx: db.Connection, schema: str) -> str:
    """Return the owner of a schema.

    :raises ~pglift.exceptions.SchemaNotFound: if specified 'schema' does not exist.
    """
    if r := await db.fetchone(
        cnx,
        sql.query("schema_owner"),
        {"name": schema},
        row_factory=psycopg.rows.args_row(str),
    ):
        return r
    raise exceptions.SchemaNotFound(schema)


async def current_role(cnx: db.Connection) -> str:
    return await db.one(cnx, "SELECT CURRENT_ROLE", row_factory=psycopg.rows.scalar_row)


async def alter_owner(cnx: db.Connection, name: str, owner: str) -> None:
    opts = sql.SQL("OWNER TO {}").format(sql.Identifier(owner))
    logger.info("setting '%s' schema owner to '%s'", name, owner)
    await db.execute(
        cnx, sql.query("alter_schema", schema=sql.Identifier(name), opts=opts)
    )


async def apply(cnx: db.Connection, schema: interface.Schema, dbname: str) -> bool:
    """Apply the state defined by 'schema' in connected database and return
    True if something changed.
    """
    for existing in await ls(cnx):
        if schema.name == existing.name:
            if schema.state == "absent":
                logger.info("dropping schema %s from database %s", schema.name, dbname)
                await db.execute(
                    cnx, sql.query("drop_schema", schema=sql.Identifier(schema.name))
                )
                return True

            new_owner = schema.owner or await current_role(cnx)
            if new_owner != existing.owner:
                await alter_owner(cnx, schema.name, new_owner)
                return True
            return False

    if schema.state != "absent":
        await create(cnx, schema, dbname)
        return True
    return False


async def create(cnx: db.Connection, schema: interface.Schema, dbname: str) -> None:
    msg, args = (
        "creating schema '%(name)s' in database %(dbname)s",
        {
            "name": schema.name,
            "dbname": dbname,
        },
    )
    opts = []
    if schema.owner is not None:
        opts.append(sql.SQL("AUTHORIZATION {}").format(sql.Identifier(schema.owner)))
        msg += " with owner '%(owner)s'"
        args["owner"] = schema.owner

    logger.info(msg, args)
    await db.execute(
        cnx,
        sql.query(
            "create_schema",
            schema=sql.Identifier(schema.name),
            options=sql.SQL(" ").join(opts),
        ),
    )

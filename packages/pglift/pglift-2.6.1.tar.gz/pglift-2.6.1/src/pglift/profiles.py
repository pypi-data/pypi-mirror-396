# SPDX-FileCopyrightText: 2024 Dalibo
#
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

from . import databases, schemas, sql, util
from .models import PostgreSQLInstance, interface
from .settings import PostgreSQLVersion
from .system import db

logger = util.get_logger(__name__)


async def _define_grantor(
    cnx: db.Connection,
    database: str,
    schema: str,
    *,
    pg_version: PostgreSQLVersion,
    surole: str,
) -> str:
    """Return grantor role used in FOR ROLE clause when defining default
    privileges.

    The result is based on schema owner or database owner if the schema is owned
    by the pre-defined role pg_database_owner (default value for the public
    schema on PostgreSQL>14). For PostgreSQL version <= 14 and the public
    schema, always use the database owner unless the schema is not owned by
    the superuser.
    """
    schema_owner = await schemas.owner(cnx, schema=schema)
    if (pg_version > "14" and schema_owner != "pg_database_owner") or (
        pg_version <= "14" and (schema != "public" or schema_owner != surole)
    ):
        return schema_owner
    db_owner = (await databases._get(cnx, database)).owner
    assert db_owner
    return db_owner


async def revoke(
    cnx: db.Connection, *, role: str, database: str, schema: str, grantor: str
) -> None:
    """Revoke all privileges for a PostgreSQL role for a specific database and
    schema.
    """
    for stmt in sql.queries(
        "profile_reset",
        dbname=sql.Identifier(database),
        username=sql.Identifier(role),
        grantor=sql.Identifier(grantor),
        schemaname=sql.Identifier(schema),
    ):
        await db.execute(cnx, stmt)


async def set_for_role(
    instance: PostgreSQLInstance, role: str, profile: interface.RoleProfile
) -> None:
    """Alter privileges to ensure a role has profile based privileges.

    First removes / revokes all privileges for the role (database and schema)
    and then applies the PostgreSQL commands (mainly GRANT and ALTER DEFAULT
    PRIVILEGES) based on the profile definition.
    """
    async with (
        db.connect(instance, dbname=profile.database) as cnx,
        db.transaction(cnx),
    ):
        surole = instance._settings.postgresql.surole.name
        for s in profile.schemas:
            grantor = await _define_grantor(
                cnx, profile.database, s, pg_version=instance.version, surole=surole
            )
            async with db.transaction(cnx):
                await revoke(
                    cnx, role=role, database=profile.database, schema=s, grantor=grantor
                )
                logger.info(
                    "setting profile '%(profile)s' for role '%(role)s' on schema '%(schema)s' in database '%(database)s'",
                    {
                        "profile": profile.kind,
                        "role": role,
                        "schema": s,
                        "database": profile.database,
                    },
                )
                for stmt in sql.queries(
                    f"profile_{profile.kind}",
                    schemaname=sql.Identifier(s),
                    grantor=sql.Identifier(grantor),
                    username=sql.Identifier(role),
                ):
                    await db.execute(cnx, stmt)

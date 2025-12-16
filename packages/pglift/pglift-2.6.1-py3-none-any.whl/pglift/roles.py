# SPDX-FileCopyrightText: 2021 Dalibo
#
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

import psycopg.pq
import psycopg.rows

from . import async_hooks, databases, deps, exceptions, h, sql, util
from .manager import InstanceManager
from .models import PostgreSQLInstance, interface
from .system import db
from .types import Role

logger = util.get_logger(__name__)


@deps.use
async def apply(
    instance: PostgreSQLInstance,
    role: interface.Role,
    manager: InstanceManager = deps.Auto,
) -> interface.ApplyResult:
    """Apply state described by specified interface model as a PostgreSQL role.

    In case it's not possible to inspect changed role, possibly due to the super-user
    password being modified, change_state attribute within the returned object
    is set to interface.ApplyResult.changed with a warning logged.

    The instance should be running and not a standby.

    :raises ~pglift.exceptions.DependencyError: if the role cannot be dropped due some database dependency.
    """
    if instance.standby:
        raise exceptions.InstanceReadOnlyError(instance)

    async with db.connect(instance) as cnx:
        result = await _apply(cnx, role, instance)
        if result.pending_reload:
            await manager.reload_postgresql(instance)
        return result


async def _apply(
    cnx: db.Connection, role: interface.Role, instance: PostgreSQLInstance
) -> interface.RoleApplyResult:
    name = role.name
    if role.state == "absent":
        dropped = False
        if await _exists(cnx, name):
            await _drop(cnx, role, instance=instance)
            dropped = True
        return interface.RoleApplyResult(change_state="dropped" if dropped else None)

    settings = instance._settings
    if not await _exists(cnx, name):
        await _create(cnx, role)
        role_change_results = await async_hooks(
            settings, h.role_change, role=role, instance=instance
        )
        pending_reload = any(r[1] for r in role_change_results)
        return interface.RoleApplyResult(
            change_state="created", pending_reload=pending_reload
        )
    else:
        actual = await _get(cnx, name, instance=instance, password=False)
        await _alter(cnx, role)
        role_change_results = await async_hooks(
            settings, h.role_change, role=role, instance=instance
        )
        role_changed, pending_reload = map(any, zip(*role_change_results, strict=False))
        if role_changed:
            return interface.RoleApplyResult(
                change_state="changed", pending_reload=pending_reload
            )
        changed = await _get(cnx, name, instance=instance, password=False) != actual
        return interface.RoleApplyResult(
            change_state="changed" if changed else None, pending_reload=pending_reload
        )


async def get(
    instance: PostgreSQLInstance, name: str, *, password: bool = True
) -> interface.Role:
    """Return the role object with specified name.

    :raises ~pglift.exceptions.RoleNotFound: if no role with specified 'name' exists.
    """
    async with db.connect(instance) as cnx:
        return await _get(cnx, name, instance=instance, password=password)


async def _get(
    cnx: db.Connection,
    name: str,
    *,
    instance: PostgreSQLInstance,
    password: bool = True,
) -> interface.Role:
    values = await db.fetchone(cnx, sql.query("role_inspect"), {"username": name})
    if values is None:
        raise exceptions.RoleNotFound(name)
    if not password:
        values["password"] = None
    for extra in await async_hooks(
        instance._settings, h.role_inspect, instance=instance, name=name
    ):
        conflicts = set(values) & set(extra)
        assert not conflicts, (
            f"conflicting keys returned by role_inspect() hook: {', '.join(conflicts)}"
        )
        values.update(extra)
    return interface.Role(**values)


async def ls(instance: PostgreSQLInstance) -> list[interface.Role]:
    """Return the list of roles for an instance."""
    async with db.connect(instance) as cnx:
        return await db.fetchall(
            cnx,
            sql.query("role_list"),
            row_factory=psycopg.rows.class_row(interface.Role),
        )


async def drop(
    instance: PostgreSQLInstance,
    role: interface.RoleDropped,
) -> None:
    """Drop a role from instance.

    :raises ~pglift.exceptions.RoleNotFound: if no role with specified 'role.name' exists.
    :raises ~pglift.exceptions.RoleNotFound: if no role with specified 'role.reassign_owned' exists.
    :raises ~pglift.exceptions.DependencyError: if the role cannot be dropped due some database dependency.
    """
    if instance.standby:
        raise exceptions.InstanceReadOnlyError(instance)
    async with db.connect(instance) as cnx:
        if not await _exists(cnx, role.name):
            raise exceptions.RoleNotFound(role.name)
        await _drop(cnx, role, instance=instance)


async def _drop(
    cnx: db.Connection,
    role: interface.RoleDropped,
    *,
    instance: PostgreSQLInstance,
) -> None:
    if role.reassign_owned and not await _exists(cnx, role.reassign_owned):
        raise exceptions.RoleNotFound(role.reassign_owned)
    logger.info("dropping role '%s'", role.name)
    dbs_to_drop: list[str] = []
    if role.drop_owned or role.reassign_owned:
        for database in await databases._list(cnx):
            if role.drop_owned and database.owner == role.name:
                dbs_to_drop.append(database.name)
            else:
                if role.drop_owned:
                    query = sql.query(
                        "role_drop_owned", username=sql.Identifier(role.name)
                    )
                elif role.reassign_owned:
                    query = sql.query(
                        "role_drop_reassign",
                        oldowner=sql.Identifier(role.name),
                        newowner=sql.Identifier(role.reassign_owned),
                    )
                async with db.connect(instance, dbname=database.name) as db_cnx:
                    await db.execute(db_cnx, query)

    for dbname in dbs_to_drop:
        await db.execute(
            cnx,
            sql.query(
                "database_drop",
                database=sql.Identifier(dbname),
                options=sql.SQL(""),
            ),
        )
    try:
        await db.execute(
            cnx, sql.query("role_drop", username=sql.Identifier(role.name))
        )
    except psycopg.errors.DependentObjectsStillExist as e:
        assert not role.drop_owned and not role.reassign_owned, (
            f"unexpected {e!r} while dropping {role}"
        )
        raise exceptions.DependencyError(
            f"{e.diag.message_primary} (detail: {e.diag.message_detail})"
        ) from e

    await async_hooks(instance._settings, h.role_change, role=role, instance=instance)


async def exists(instance: PostgreSQLInstance, name: str) -> bool:
    """Return True if named role exists in 'instance'.

    The instance should be running.
    """
    async with db.connect(instance) as cnx:
        return await _exists(cnx, name)


async def _exists(cnx: db.Connection, name: str) -> bool:
    return await db.one(
        cnx,
        sql.query("role_exists"),
        {"username": name},
        row_factory=psycopg.rows.args_row(bool),
    )


def encrypt_password(cnx: db.Connection, role: Role) -> str:
    if role.encrypted_password is not None:
        return role.encrypted_password.get_secret_value()
    assert role.password is not None, "role has no password to encrypt"
    return db.encrypt_password(cnx, role.password.get_secret_value(), role.name)


def options(
    cnx: db.Connection,
    role: interface.Role,
) -> list[sql.Composable]:
    """Return the "options" parts of CREATE ROLE or ALTER ROLE SQL commands
    based on 'role' model.
    """
    opts: list[sql.Composable] = [
        sql.SQL("INHERIT" if role.inherit else "NOINHERIT"),
        sql.SQL("LOGIN" if role.login else "NOLOGIN"),
        sql.SQL("SUPERUSER" if role.superuser else "NOSUPERUSER"),
        sql.SQL("REPLICATION" if role.replication else "NOREPLICATION"),
        sql.SQL("CREATEDB" if role.createdb else "NOCREATEDB"),
        sql.SQL("CREATEROLE" if role.createrole else "NOCREATEROLE"),
    ]
    if role.password or role.encrypted_password:
        opts.append(sql.SQL("PASSWORD {}").format(encrypt_password(cnx, role)))
    if role.valid_until is not None:
        opts.append(sql.SQL("VALID UNTIL {}").format(role.valid_until.isoformat()))
    opts.append(
        sql.SQL(
            f"CONNECTION LIMIT {role.connection_limit if role.connection_limit is not None else -1}"
        )
    )
    return opts


def in_role_option(names: list[str]) -> list[sql.Composable]:
    """Return the "IN ROLE" part of CREATE ROLE SQL command."""
    if not names:
        return []
    return [
        sql.SQL("IN ROLE"),
        sql.SQL(", ").join(sql.Identifier(name) for name in names),
    ]


async def _create(cnx: db.Connection, role: interface.Role) -> None:
    logger.info("creating role '%s'", role.name)
    memberships = [r.role for r in role.memberships if r.state == "present"]
    opts = sql.SQL(" ").join(options(cnx, role) + in_role_option(memberships))
    await db.execute(
        cnx, sql.query("role_create", username=sql.Identifier(role.name), options=opts)
    )


async def _alter(cnx: db.Connection, role: interface.Role) -> None:
    logger.info("altering role '%s'", role.name)
    actions = {
        "grant": {m.role for m in role.memberships if m.state == "present"},
        "revoke": {m.role for m in role.memberships if m.state == "absent"},
    }
    async with db.transaction(cnx):
        opts = sql.SQL(" ").join(options(cnx, role))
        await db.execute(
            cnx,
            sql.query("role_alter", username=sql.Identifier(role.name), options=opts),
        )
        for action, values in actions.items():
            if values:
                await db.execute(
                    cnx,
                    sql.query(
                        f"role_{action}",
                        rolname=sql.SQL(", ").join(sql.Identifier(r) for r in values),
                        rolspec=sql.Identifier(role.name),
                    ),
                )

# SPDX-FileCopyrightText: 2021 Dalibo
#
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

import contextlib
import logging
import os
import re
import shutil
import tempfile
import time
from collections.abc import AsyncIterator, Iterator, Sequence
from dataclasses import dataclass
from functools import singledispatch
from pathlib import Path, PurePath
from typing import Any

import pgtoolkit.conf as pgconf
import psycopg.rows
import psycopg.sql
import tenacity
from pgtoolkit import pgpass

from . import (
    async_hook,
    async_hooks,
    databases,
    deps,
    exceptions,
    h,
    hooks,
    plugin_manager,
    postgresql,
    replication_slots,
    roles,
    ui,
    util,
)
from .manager import ConfigurationManager, InstanceManager, from_instance
from .models import Instance, PGSetting, PostgreSQLInstance, interface
from .postgresql import pq
from .postgresql.ctl import get_data_checksums, set_data_checksums
from .postgresql.ctl import log as postgresql_log
from .settings import PostgreSQLVersion, Settings, default_postgresql_version
from .system import Command, FileSystem, db
from .task import task
from .types import ConfigChanges, PostgreSQLStopMode, Status, validation_context

logger = util.get_logger(__name__)


@task(title="initializing PostgreSQL")
@deps.use
async def init(
    instance: PostgreSQLInstance,
    manifest: interface.Instance,
    *,
    instance_manager: InstanceManager = deps.Auto,
    config_manager: ConfigurationManager = deps.Auto,
) -> bool:
    """Initialize a PostgreSQL cluster."""

    await instance_manager.init_postgresql(manifest, instance)

    is_running = await postgresql.is_running(instance)

    if config_manager.configure_auth(instance, manifest) and is_running:
        await instance_manager.restart_postgresql(instance, mode="fast", wait=True)

    await _post_init(instance)

    return is_running


@deps.use
async def _post_init(
    instance: PostgreSQLInstance, *, fs: FileSystem = deps.Auto
) -> None:
    psqlrc = postgresql.template(instance.version, "psqlrc")
    fs.write_text(instance.psqlrc, psqlrc.format(instance=instance))


def postgresql_service_names(instance: PostgreSQLInstance) -> Iterator[str]:
    return filter(
        None, hooks(instance._settings, h.postgresql_service_name, instance=instance)
    )


@task
async def setup_postgresql_service(instance: PostgreSQLInstance) -> None:
    settings = instance._settings
    service, *others = postgresql_service_names(instance)
    for other in others:
        await async_hook(
            settings,
            h.disable_service,
            settings=settings,
            service=other,
            name=instance.qualname,
            now=True,
        )
    await async_hook(
        settings,
        h.enable_service,
        settings=settings,
        service=service,
        name=instance.qualname,
    )


@setup_postgresql_service.revert
async def revert_setup_postgresql_service(instance: PostgreSQLInstance) -> None:
    await disable_postgresql_service(instance, now=True)


async def disable_postgresql_service(
    instance: PostgreSQLInstance, *, now: bool = False
) -> None:
    settings = instance._settings
    for service in postgresql_service_names(instance):
        await async_hook(
            settings,
            h.disable_service,
            settings=settings,
            service=service,
            name=instance.qualname,
            now=now,
        )


@init.revert
@deps.use
async def revert_init(
    instance: PostgreSQLInstance, *, manager: InstanceManager = deps.Auto
) -> None:
    """Un-initialize a PostgreSQL cluster."""
    await manager.deinit_postgresql(instance)


@dataclass
class ConfigureResult:
    changes: ConfigChanges
    restarted: bool = False


async def configure(
    instance: PostgreSQLInstance,
    manifest: interface.Instance,
    *,
    run_hooks: bool = True,
    _is_running: bool | None = None,
) -> ConfigureResult:
    """Configure PostgreSQL and satellite components of `instance` with respect
    to specified `manifest`.
    """
    async with configure_context(
        instance, manifest, run_hooks=run_hooks, is_running=_is_running
    ) as result:
        pass
    return result


@deps.use
async def configure_postgresql(
    instance: PostgreSQLInstance,
    manifest: interface.Instance,
    *,
    manager: ConfigurationManager = deps.Auto,
) -> tuple[pgconf.Configuration, ConfigChanges]:
    """Write instance's configuration in postgresql.conf."""
    logger.info("configuring PostgreSQL")
    config = postgresql.configuration(manifest, instance._settings)
    changes = await manager.configure_postgresql(config, instance, manifest)
    assert changes is not None
    return config, changes


@deps.use
async def postgresql_editable_conf(
    instance: PostgreSQLInstance, *, manager: ConfigurationManager = deps.Auto
) -> pgconf.Configuration:
    return await manager.postgresql_editable_conf(instance)


@deps.use
async def postgresql_conf(
    instance: PostgreSQLInstance, *, manager: ConfigurationManager = deps.Auto
) -> pgconf.Configuration:
    return await manager.postgresql_conf(instance)


@contextlib.asynccontextmanager
async def configure_context(
    instance: PostgreSQLInstance,
    manifest: interface.Instance,
    *,
    run_hooks: bool = True,
    is_running: bool | None = None,
) -> AsyncIterator[ConfigureResult]:
    """Context manager to write instance's configuration in postgresql.conf
    while pausing for further actions before calling 'instance_configured'
    hooks.

    Also compute changes to the overall PostgreSQL configuration and return it
    as a 'ConfigChanges' dictionary.

    When resuming to call instance_configured hooks, PostgreSQL messages are
    forwarded to our logger if the current log file exists.
    """
    config, changes = await configure_postgresql(instance, manifest)
    result = ConfigureResult(changes=changes)

    yield result

    if run_hooks:
        async with postgresql_log(instance):
            await async_hooks(
                instance._settings,
                h.postgresql_configured,
                instance=instance,
                manifest=manifest,
                config=config,
                changes=changes,
            )

    if is_running is None:
        is_running = await postgresql.is_running(instance)
    if not manifest.creating and is_running:
        result.restarted = await check_pending_actions(
            instance, changes, manifest.restart_on_changes
        )


@contextlib.asynccontextmanager
async def stopped(
    instance: Instance, *, timeout: int = postgresql.WAIT_TIMEOUT
) -> AsyncIterator[None]:
    """Context manager to temporarily stop an instance.

    :param timeout: delay to wait for instance stop.

    :raises ~exceptions.InstanceStateError: when the instance did stop after
        specified `timeout` (in seconds).
    """
    pg_instance = instance.postgresql
    if not await postgresql.is_running(pg_instance):
        yield
        return

    await stop(instance)
    for __ in range(timeout):
        time.sleep(1)
        if not await postgresql.is_running(pg_instance):
            break
    else:
        raise exceptions.InstanceStateError(f"{instance} not stopped after {timeout}s")
    try:
        yield
    finally:
        await start(instance)


async def start(
    instance: Instance,
    *,
    foreground: bool = False,
    wait: bool = True,
    _check: bool = True,
) -> None:
    """Start an instance.

    :param wait: possibly wait for PostgreSQL to get ready.
    :param foreground: start postgres in the foreground, replacing the current
        process.

    .. note:: When starting in "foreground", hooks will not be triggered and
        `wait` parameter have no effect.
    """
    await _start_postgresql(
        instance.postgresql, foreground=foreground, wait=wait, check=_check
    )
    if wait:
        if foreground:
            logger.debug("not running hooks for a foreground start")
        else:
            await async_hooks(instance._settings, h.instance_started, instance=instance)


@deps.use
async def _start_postgresql(
    instance: PostgreSQLInstance,
    *,
    foreground: bool = False,
    wait: bool = True,
    check: bool = True,
    manager: InstanceManager = deps.Auto,
) -> None:
    if check and await postgresql.is_running(instance):
        logger.warning("instance %s is already started", instance)
        return
    await manager.start_postgresql(instance, foreground=foreground, wait=wait)


@deps.use
async def stop(
    instance: Instance,
    *,
    mode: PostgreSQLStopMode = "fast",
    wait: bool = True,
    deleting: bool = False,
    manager: InstanceManager = deps.Auto,
) -> None:
    """Stop an instance."""
    s = instance._settings
    pg_instance = instance.postgresql
    if not await postgresql.is_running(pg_instance):
        logger.warning("instance %s is already stopped", instance)
    else:
        await manager.stop_postgresql(
            instance.postgresql, mode=mode, wait=wait, deleting=deleting
        )

    if wait:
        await async_hooks(s, h.instance_stopped, instance=instance)


async def restart(
    instance: Instance,
    *,
    mode: PostgreSQLStopMode = "fast",
    wait: bool = True,
) -> None:
    """Restart an instance."""
    logger.info("restarting instance %s", instance)
    s = instance._settings
    await async_hooks(s, h.instance_stopped, instance=instance)
    await restart_postgresql(instance.postgresql, mode=mode, wait=wait)
    await async_hooks(s, h.instance_started, instance=instance)


@deps.use
async def restart_postgresql(
    instance: PostgreSQLInstance,
    *,
    mode: PostgreSQLStopMode = "fast",
    wait: bool = True,
    manager: InstanceManager = deps.Auto,
) -> None:
    s = instance._settings
    service = next(postgresql_service_names(instance))
    if await async_hook(
        s,
        h.restart_service,
        settings=s,
        service=service,
        name=instance.qualname,
    ):
        await postgresql.wait_ready(instance)
    else:
        await manager.restart_postgresql(instance, mode=mode, wait=wait)


@deps.use
async def reload(
    instance: PostgreSQLInstance, *, manager: InstanceManager = deps.Auto
) -> None:
    """Reload an instance."""
    async with postgresql_log(instance):
        await manager.reload_postgresql(instance)


@deps.use
async def promote(instance: Instance, *, manager: InstanceManager = deps.Auto) -> None:
    """Promote a standby instance"""
    pg_instance = instance.postgresql
    if not pg_instance.standby:
        raise exceptions.InstanceStateError(f"{instance} is not a standby")
    s = instance._settings
    async with postgresql_log(pg_instance):
        await manager.promote_postgresql(pg_instance)
        await async_hooks(s, h.instance_promoted, instance=instance)


@deps.use
async def demote(
    instance: Instance,
    source: postgresql.RewindSource,
    *,
    rewind_opts: Sequence[str] = (),
    manager: InstanceManager = deps.Auto,
) -> Instance:
    """Demote an instance as standby.

    The target instance is rewound from specified source (thus becoming an
    exact copy of the source server) and then re-configured so that its
    original definition is restored as it was before rewind.

    The logic for re-configuration is adapted from :func:`configure`.
    """
    pg_instance, settings = instance.postgresql, instance._settings
    await postgresql.check_status(pg_instance, Status.not_running)
    manifest = await _get(instance, Status.not_running)
    await manager.demote_postgresql(pg_instance, source, rewind_opts=rewind_opts)
    # Drop previous standby setup as the demoted instance will use the rewind
    # connection for streaming replication.
    manifest.settings.pop("primary_conninfo", None)
    manifest.settings.pop("primary_slot_name", None)
    # First configure only PostgreSQL, restoring the original instance
    # configuration before demote (e.g. port, etc.).
    config, _ = await configure_postgresql(pg_instance, manifest)
    # Then re-configure through hooks (e.g. pgpass) but ignoring "changes"
    # from the previous operation as they essentially result from the original
    # state being re-applied..
    await async_hooks(
        settings,
        h.postgresql_configured,
        instance=pg_instance,
        manifest=manifest,
        config=config,
        changes={},
    )
    return Instance.system_lookup(instance.name, instance.postgresql.version, settings)


@deps.use
async def pause_wal_replay(
    instance: PostgreSQLInstance, *, manager: InstanceManager = deps.Auto
) -> None:
    """Pause WAL replay on standby instance"""
    await manager.pause_wal_replay(instance)


@deps.use
async def resume_wal_replay(
    instance: PostgreSQLInstance, *, manager: InstanceManager = deps.Auto
) -> None:
    """Resume WAL replay on standby instance"""
    await manager.resume_wal_replay(instance)


@deps.use
async def upgrade(
    instance: Instance,
    *,
    version: PostgreSQLVersion | None = None,
    name: str | None = None,
    port: int | None = None,
    extra_opts: tuple[str, ...] = (),
    fs: FileSystem = deps.Auto,
    _instance_model: type[interface.Instance] | None = None,
) -> Instance:
    """Upgrade a primary instance using pg_upgrade"""
    settings = instance._settings
    postgresql_settings = settings.postgresql
    if version is None:
        version = default_postgresql_version(postgresql_settings)
    pg_instance = instance.postgresql
    if pg_instance.standby:
        raise exceptions.InstanceReadOnlyError(pg_instance)
    if pg_instance.version > version:
        raise exceptions.InvalidVersion(
            f"Could not upgrade {instance} from {pg_instance.version} to {version}"
        )
    if (name is None or name == pg_instance.name) and version == pg_instance.version:
        raise exceptions.InvalidVersion(
            f"Could not upgrade {instance} using same name and same version"
        )
    # check if target name/version already exists
    if exists((pg_instance.name if name is None else name), version, settings):
        raise exceptions.InstanceAlreadyExists(
            f"Could not upgrade {instance}: target name/version instance already exists"
        )

    surole_name = postgresql_settings.surole.name
    surole_password = pq.environ(instance.postgresql, surole_name).get("PGPASSWORD")
    if (
        not surole_password
        and postgresql_settings.auth.passfile
        and fs.exists(postgresql_settings.auth.passfile)
    ):
        with fs.open(postgresql_settings.auth.passfile) as f:
            passfile = pgpass.parse(f)
        for entry in passfile:
            if entry.matches(port=pg_instance.port, username=surole_name):
                surole_password = entry.password
    surole = interface.Role(name=surole_name, password=surole_password)

    if _instance_model is None:
        pm = plugin_manager(settings)
        _instance_model = interface.Instance.composite(pm)

    old_manifest = await _get(instance, Status.not_running)
    data = dict(
        old_manifest,
        name=name or pg_instance.name,
        version=version,
        port=port or pg_instance.port,
        state="stopped",
        surole_password=surole.password,
        upgrading_from={
            "name": pg_instance.name,
            "version": pg_instance.version,
            "port": pg_instance.port,
            "datadir": pg_instance.datadir,
        },
    )
    with validation_context(operation="create", settings=settings):
        new_manifest = _instance_model.model_validate(data)

    if not ui.confirm(
        f"Confirm upgrade of instance {instance} to version {version}?", True
    ):
        raise exceptions.Cancelled(f"upgrade of instance {instance} cancelled")

    with PostgreSQLInstance.creating(
        new_manifest.name, new_manifest.version, settings
    ) as new_pg_instance:
        await _upgrade(
            pg_instance, new_pg_instance, new_manifest, surole, extra_opts=extra_opts
        )
    return Instance.from_postgresql(new_pg_instance)


@task(title="upgrading instance {instance} as {new_instance}")
@deps.use
async def _upgrade(
    instance: PostgreSQLInstance,
    new_instance: PostgreSQLInstance,
    new_manifest: interface.Instance,
    surole: interface.Role,
    *,
    extra_opts: tuple[str, ...] = (),
    cmd: Command = deps.Auto,
) -> None:
    logger.info("initializing PostgreSQL")
    await postgresql.initdb(new_manifest, new_instance)
    postgresql.configure_auth(new_instance, new_manifest)
    await _post_init(new_instance)

    # At this point, just install a minimal configuration, though including
    # shared_preload_libraries and port settings. A more complete
    # configuration will be installed in apply() call below.
    await postgresql.configure(new_instance, new_manifest)

    old_bindir = postgresql.bindir(instance)
    new_bindir = postgresql.bindir(new_instance)
    pg_upgrade = str(new_bindir / "pg_upgrade")
    cmd_args = [
        pg_upgrade,
        f"--old-bindir={old_bindir}",
        f"--new-bindir={new_bindir}",
        f"--old-datadir={instance.datadir}",
        f"--new-datadir={new_instance.datadir}",
        f"--username={surole.name}",
    ]
    cmd_args.extend(extra_opts)
    env = pq.environ(instance, surole.name)
    if surole.password:
        env.setdefault("PGPASSWORD", surole.password.get_secret_value())
    logger.info("upgrading instance with pg_upgrade")
    with tempfile.TemporaryDirectory() as tmpdir:
        await cmd.run(cmd_args, check=True, cwd=tmpdir, env=env)
    settings = new_instance._settings
    await async_hooks(settings, h.instance_upgraded, old=instance, new=new_instance)
    await apply(settings, new_manifest)


@_upgrade.revert
@deps.use
async def revert__upgrade(
    new_instance: PostgreSQLInstance, *, fs: FileSystem = deps.Auto
) -> None:
    if fs.exists(new_instance.datadir):
        to_drop = Instance.from_postgresql(new_instance)
        logger.info("dropping partially upgraded instance %s", to_drop)
        await drop(to_drop)


async def get_locale(cnx: db.Connection) -> str | None:
    """Return the value of instance locale.

    If locale subcategories are set to distinct values, return None.
    """
    locales = {
        s.name: s.setting for s in await settings(cnx) if s.name.startswith("lc_")
    }
    values = set(locales.values())
    if len(values) == 1:
        return values.pop()
    else:
        logger.debug(
            "cannot determine instance locale, settings are heterogeneous: %s",
            ", ".join(f"{n}: {s}" for n, s in sorted(locales.items())),
        )
        return None


async def apply(
    settings: Settings, instance: interface.Instance, *, _is_running: bool | None = None
) -> interface.InstanceApplyResult:
    """Apply state described by interface model as a PostgreSQL instance.

    Depending on the previous state and existence of the target instance, the
    instance may be created or updated or dropped.

    If configuration changes are detected and the instance was previously
    running, the server will be reloaded automatically; if a restart is
    needed, the user will be prompted in case of interactive usage or this
    will be performed automatically if 'restart_on_changes' is set to True.
    """
    if (state := instance.state) == "absent":
        try:
            i = Instance.system_lookup(instance.name, instance.version, settings)
        except exceptions.InstanceNotFound:
            return interface.InstanceApplyResult(change_state=None)
        await drop(i)
        return interface.InstanceApplyResult(change_state="dropped")

    changed = False
    try:
        pg_instance = PostgreSQLInstance.system_lookup(
            instance.name, instance.version, settings
        )
    except exceptions.InstanceNotFound:
        pg_instance = None
    if pg_instance is None:
        with PostgreSQLInstance.creating(
            instance.name, instance.version, settings
        ) as pg_instance:
            _is_running = await init(pg_instance, instance)
        instance = instance.model_copy(update={"creating": True})
        changed = True

    if _is_running is None:
        _is_running = await postgresql.is_running(pg_instance)

    surole = instance.surole(settings)

    @contextlib.asynccontextmanager
    async def superuser_connect() -> AsyncIterator[db.Connection]:
        await postgresql.wait_ready(pg_instance)
        password = (
            surole.password.get_secret_value() if surole.password is not None else None
        )
        async with db.connect(pg_instance, user=surole.name, password=password) as cnx:
            yield cnx

    async with configure_context(
        pg_instance, instance, is_running=_is_running
    ) as configure_result:
        await setup_postgresql_service(pg_instance)
        if state in ("started", "restarted") and not _is_running:
            await _start_postgresql(pg_instance, check=False)
            _is_running = True
        if instance.creating:
            # Now that PostgreSQL configuration is done, call hooks for
            # super-user role creation (handled by initdb), e.g. to create the
            # .pgpass entry.
            instance_roles = filter(
                None, hooks(settings, h.role, settings=settings, manifest=instance)
            )
            await async_hooks(
                settings, h.role_change, role=surole, instance=pg_instance
            )
            if pg_instance.standby or instance.upgrading_from:
                # Just apply role changes here (e.g. .pgpass entries).
                # This concerns standby instances, which are read-only, as
                # well as upgraded instances, in which objects (roles and
                # databases) would be migrated as is.
                for role in instance_roles:
                    await async_hooks(
                        settings, h.role_change, role=role, instance=pg_instance
                    )
            else:

                async def apply_databases_and_roles() -> bool:
                    changed = False
                    async with superuser_connect() as cnx:
                        await wait_recovery_finished(cnx)
                        replrole = instance.replrole(settings)
                        if replrole:
                            if (
                                await roles._apply(cnx, replrole, pg_instance)
                            ).change_state:
                                changed = True
                        for role in instance_roles:
                            if (
                                await roles._apply(cnx, role, pg_instance)
                            ).change_state:
                                changed = True
                        for database in hooks(
                            settings, h.database, settings=settings, manifest=instance
                        ):
                            if (
                                await databases._apply(cnx, database, pg_instance)
                            ).change_state:
                                changed = True
                    return changed

                if _is_running:
                    changed = await apply_databases_and_roles()
                else:
                    async with postgresql.running(pg_instance):
                        changed = await apply_databases_and_roles()

    changed = changed or bool(configure_result.changes)

    if instance.data_checksums is not None:
        actual_data_checksums = await get_data_checksums(pg_instance)
        if actual_data_checksums != instance.data_checksums:
            if instance.data_checksums:
                logger.info("enabling data checksums")
            else:
                logger.info("disabling data checksums")
            if _is_running:
                raise exceptions.InstanceStateError(
                    "cannot alter data_checksums on a running instance"
                )
            await set_data_checksums(pg_instance, instance.data_checksums)
            changed = True

    sys_instance = Instance.from_postgresql(pg_instance)

    if state == "stopped":
        if _is_running:
            await stop(sys_instance)
            changed = True
            _is_running = False
    elif state in ("started", "restarted"):
        if state == "started":
            if not _is_running:
                await start(sys_instance, _check=False)
            else:
                await async_hooks(settings, h.instance_started, instance=sys_instance)
        elif state == "restarted" and not configure_result.restarted:
            await restart(sys_instance)
        changed = True
        _is_running = True
    else:
        # TODO: use typing.assert_never() instead
        # https://typing.readthedocs.io/en/latest/source/unreachable.html
        assert False, f"unexpected state: {state}"  # noqa: B011  # pragma: nocover

    standby = instance.standby

    if standby and standby.status == "promoted" and pg_instance.standby is not None:
        await promote(sys_instance)

    if not pg_instance.standby and (
        instance.roles or instance.databases or instance.replication_slots
    ):
        async with postgresql.running(pg_instance), superuser_connect() as cnx:
            pending_reload = False
            for a_role in instance.roles:
                role_result = await roles._apply(cnx, a_role, pg_instance)
                changed = role_result.change_state in ("created", "changed") or changed
                pending_reload = role_result.pending_reload or pending_reload
            if pending_reload:
                await reload(pg_instance)

            for a_database in instance.databases:
                r = await databases._apply(cnx, a_database, pg_instance)
                changed = r.change_state in ("changed", "created") or changed
            for replication_slot in instance.replication_slots:
                r = await replication_slots.apply(cnx, replication_slot)
                changed = (r.change_state is not None) or changed
    change_state, p_restart = None, False
    if instance.creating:
        change_state = "created"
    elif changed:
        change_state = "changed"
        if _is_running:
            async with superuser_connect() as cnx:
                p_restart = await pending_restart(cnx)
    return interface.InstanceApplyResult(
        change_state=change_state, pending_restart=p_restart
    )


async def pending_restart(cnx: db.Connection) -> bool:
    """Return True if the instance is pending a restart to account for configuration changes."""
    return await db.one(
        cnx,
        "SELECT bool_or(pending_restart) FROM pg_settings",
        row_factory=psycopg.rows.scalar_row,
    )


async def check_pending_actions(
    instance: PostgreSQLInstance,
    changes: ConfigChanges,
    restart_on_changes: bool,
) -> bool:
    """Check if any of the changes require a reload or a restart and return
    True if a restart occurred.

    The instance is automatically reloaded if needed.
    The user is prompted for confirmation if a restart is needed.

    The instance MUST be running.
    """
    changes_ = changes.copy()
    port_change = (port := changes_.pop("port", None)) and set(port) != {None, 5432}
    if port_change:
        needs_restart = True
    else:
        needs_restart = False
        pending_restart = set()
        pending_reload = set()
        async with db.connect(instance) as cnx:
            for p in await settings(cnx):
                pname = p.name
                if pname not in changes_:
                    continue
                if p.context == "postmaster":
                    pending_restart.add(pname)
                else:
                    pending_reload.add(pname)

        if pending_reload:
            logger.info(
                "instance %s needs reload due to parameter changes: %s",
                instance,
                ", ".join(sorted(pending_reload)),
            )
            await reload(instance)

        if pending_restart:
            logger.warning(
                "instance %s needs restart due to parameter changes: %s",
                instance,
                ", ".join(sorted(pending_restart)),
            )
            needs_restart = True

    if needs_restart and ui.confirm(
        "PostgreSQL needs to be restarted; restart now?", restart_on_changes
    ):
        await restart_postgresql(instance)
        return True

    return False


@singledispatch
async def get(arg: tuple[str, str] | Instance, /, **kwargs: Any) -> interface.Instance:
    raise NotImplementedError


@get.register(tuple)
async def _(arg: tuple[str, str], /, *, settings: Settings) -> interface.Instance:
    """Return a interface Instance model from (name, version) value."""
    name, version = arg
    pg_instance = PostgreSQLInstance.system_lookup(name, version, settings)  # type: ignore[arg-type]
    instance = Instance.from_postgresql(pg_instance)
    return await get(instance)


@get.register
async def _(instance: Instance) -> interface.Instance:
    """Return a interface Instance model from a system Instance."""
    pg_instance = instance.postgresql
    status = await postgresql.status(pg_instance)
    if status != Status.running:
        missing_bits = [
            "locale",
            "encoding",
            "passwords",
            "pending_restart",
            "replication_slots",
        ]
        if pg_instance.standby is not None:
            missing_bits.append("replication lag")
        logger.warning(
            "instance %s is not running, information about %s may not be accurate",
            instance,
            f"{', '.join(missing_bits[:-1])} and {missing_bits[-1]}",
        )
    return await _get(instance, status)


async def _get(
    instance: Instance, status: Status, port_from_config: bool = False
) -> interface.Instance:
    settings = instance._settings
    pg_instance = instance.postgresql
    with from_instance(instance.postgresql):
        config = await postgresql_conf(instance.postgresql)
    managed_config = config.as_dict()
    port = managed_config.pop("port", None)
    state = interface.state_from_pg_status(status)
    instance_is_running = status == Status.running
    services = {
        s.__class__.__service__: s
        for s in await async_hooks(
            settings, h.get, instance=instance, running=instance_is_running
        )
        if s is not None
    }

    standby = None
    if pg_instance.standby:
        try:
            standby = await async_hook(
                settings,
                h.standby_model,
                instance=pg_instance,
                standby=pg_instance.standby,
                running=instance_is_running,
            )
        except ValueError:
            pass

    locale = None
    encoding = None
    data_checksums = None
    pending_rst = False
    slots = []
    if instance_is_running:
        async with db.connect(pg_instance, dbname="template1") as cnx:
            locale = await get_locale(cnx)
            encoding = await databases.encoding(cnx)
            pending_rst = await pending_restart(cnx)
            slots = await replication_slots.ls(cnx)
    data_checksums = await get_data_checksums(pg_instance)

    return interface.Instance(
        name=instance.name,
        version=pg_instance.version,
        port=port if port_from_config else pg_instance.port,
        state=state,
        pending_restart=pending_rst,
        settings=managed_config,
        locale=locale,
        encoding=encoding,
        data_checksums=data_checksums,
        standby=standby,
        replication_slots=slots,
        data_directory=pg_instance.datadir,
        wal_directory=pg_instance.waldir,
        **services,
    )


async def drop(instance: Instance) -> None:
    """Drop an instance."""
    logger.info("dropping instance %s", instance)
    if not ui.confirm(f"Confirm complete deletion of instance {instance}?", True):
        raise exceptions.Cancelled(f"deletion of instance {instance} cancelled")

    await stop(instance, mode="immediate", deleting=True)

    settings = instance._settings
    pg_instance = instance.postgresql
    await async_hooks(settings, h.instance_dropped, instance=instance)
    for rolename in hooks(settings, h.rolename, settings=settings):
        await async_hooks(
            settings,
            h.role_change,
            role=interface.Role(name=rolename, state="absent"),
            instance=pg_instance,
        )
    await disable_postgresql_service(instance.postgresql)
    await revert_init(instance.postgresql)


async def ls(
    settings: Settings, *, version: PostgreSQLVersion | None = None
) -> AsyncIterator[interface.InstanceListItem]:
    """Yield instances found by system lookup.

    :param version: filter instances matching a given version.

    :raises ~exceptions.InvalidVersion: if specified version is unknown.
    """
    for instance in system_list(settings, version=version):
        status = await postgresql.status(instance)
        yield interface.InstanceListItem(
            name=instance.name,
            datadir=instance.datadir,
            port=instance.port,
            status=status.name,
            version=instance.version,
        )


def system_list(
    settings: Settings, *, version: PostgreSQLVersion | None = None
) -> Iterator[PostgreSQLInstance]:
    if version is not None:
        versions = [version]
    else:
        versions = [v.version for v in settings.postgresql.versions]
    for ver in versions:
        for name in system_version_lookup(ver, settings.postgresql.datadir):
            try:
                yield PostgreSQLInstance.system_lookup(name, ver, settings)
            except exceptions.InstanceNotFound:
                pass


@deps.use
def system_version_lookup(
    version: str | None, datadir_template: Path, *, fs: FileSystem = deps.Auto
) -> Iterator[str]:
    # Search for directories matching datadir template globing on the part
    # containing {name}. Since the {version} part may come after or before
    # {name}, we first build a datadir for each known version and split it
    # on part containing {name} for further globbing.
    name_idx = next(
        i for i, item in enumerate(datadir_template.parts) if "{name}" in item
    )
    assert version is not None or "{version}" not in datadir_template.parts
    args = {"version": version} if version is not None else {}
    datadir = str(datadir_template)
    version_path = PurePath(datadir.format(name="*", **args))
    prefix = Path(*version_path.parts[:name_idx])
    suffix = PurePath(*version_path.parts[name_idx + 1 :])
    pattern = re.compile(datadir.format(name="(.*)", **args))
    for d in sorted(fs.glob(prefix, f"*/{suffix}")):
        if not fs.is_dir(d):
            continue
        matches = re.match(pattern, str(d))
        if not matches:
            continue
        name = matches.groups()[0]
        yield name


def env_for(instance: Instance, *, path: bool = False) -> dict[str, str]:
    """Return libpq environment variables suitable to connect to `instance`.

    If 'path' is True, also inject PostgreSQL binaries directory in PATH.
    """
    settings = instance._settings
    postgresql_settings = settings.postgresql
    pg_instance = instance.postgresql
    env = pq.environ(pg_instance, postgresql_settings.surole.name, base={})
    env.update(
        {
            "PGUSER": postgresql_settings.surole.name,
            "PGPORT": str(pg_instance.port),
            "PGDATA": str(pg_instance.datadir),
            "PSQLRC": str(pg_instance.psqlrc),
            "PSQL_HISTORY": str(pg_instance.psql_history),
        }
    )
    if sd := pg_instance.socket_directory:
        env["PGHOST"] = sd
    if path:
        env["PATH"] = ":".join(
            [str(postgresql.bindir(pg_instance))]
            + ([os.environ["PATH"]] if "PATH" in os.environ else [])
        )
    for env_vars in hooks(settings, h.instance_env, instance=instance):
        env.update(env_vars)
    return env


@deps.use
def exec(
    instance: Instance,
    command: tuple[str, ...],
    *,
    cmd: Command = deps.Auto,
    fs: FileSystem = deps.Auto,
) -> None:
    """Execute given PostgreSQL command in the libpq environment for `instance`.

    The command to be executed is looked up for in PostgreSQL binaries directory.
    """
    env = os.environ.copy()
    for key, value in env_for(instance).items():
        env.setdefault(key, value)
    progname, *args = command
    program = PurePath(progname)
    if not program.is_absolute():
        program = postgresql.bindir(instance.postgresql) / program
        if not fs.exists(program):
            ppath = shutil.which(progname)
            if ppath is None:
                raise exceptions.FileNotFoundError(progname)
            program = PurePath(ppath)
    try:
        cmd.execute_program([str(program)] + args, env=env)
    except FileNotFoundError as e:
        raise exceptions.FileNotFoundError(str(e)) from e


def env(instance: Instance) -> str:
    return "\n".join(
        [
            f"export {key}={value}"
            for key, value in sorted(env_for(instance, path=True).items())
        ]
    )


def exists(name: str, version: PostgreSQLVersion, settings: Settings) -> bool:
    """Return true when instance exists"""
    try:
        PostgreSQLInstance.system_lookup(name, version, settings)
    except exceptions.InstanceNotFound:
        return False
    return True


async def is_in_recovery(cnx: db.Connection) -> bool:
    """Return True if the instance is in recovery"""
    return await db.one(
        cnx, "SELECT pg_is_in_recovery()", row_factory=psycopg.rows.scalar_row
    )


async def wait_recovery_finished(cnx: db.Connection, *, timeout: int = 10) -> None:
    logger.debug("checking if PostgreSQL is in recovery")
    async for attempt in tenacity.AsyncRetrying(
        retry=tenacity.retry_if_exception_type(exceptions.InstanceStateError),
        wait=tenacity.wait_exponential(multiplier=1, min=1, max=timeout),
        stop=tenacity.stop_after_delay(timeout),
        before_sleep=tenacity.before_sleep_log(logger, logging.DEBUG),
        reraise=True,
    ):
        with attempt:
            if await is_in_recovery(cnx):
                raise exceptions.InstanceStateError("PostgreSQL still in recovery")


async def settings(cnx: db.Connection) -> list[PGSetting]:
    """Return the list of run-time parameters of the server, as available in
    pg_settings view.
    """
    return await db.fetchall(
        cnx, PGSetting.query, row_factory=psycopg.rows.class_row(PGSetting)
    )

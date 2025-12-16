# SPDX-FileCopyrightText: 2021 Dalibo
#
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

from collections.abc import Iterator
from pathlib import Path
from typing import TYPE_CHECKING, Any, Literal, TypeAlias

import pluggy
from pgtoolkit.conf import Configuration

from . import __name__ as pkgname

if TYPE_CHECKING:
    from . import postgresql
    from .models import Instance, PostgreSQLInstance, Standby, interface
    from .settings import Settings
    from .types import ComponentModel, ConfigChanges, Service, Status

hookspec = pluggy.HookspecMarker(pkgname)

FirstResult: TypeAlias = Literal[True]
#: At least one hook implementation is expected to return (True).
MaybeFirstResult: TypeAlias = Literal[True] | None
#: At most one hook implementation is expected to return (True), but the hook
#  is allowed to not return (e.g. if no returning hook implementation is
#  registered).


@hookspec
async def site_configure_install(settings: Settings, header: str) -> None:
    """Global site installation hook.

    This is typically used to install site-wise configuration files or create
    data directories.

    Respective implementation should be idempotent (possibly no-op, in case of
    re-configuration), and should avoid overwriting existing files.
    """
    raise NotImplementedError


@hookspec
async def site_configure_uninstall(settings: Settings) -> None:
    """Global site uninstallation hook.

    Respective implementation should be idempotent (possibly no-op, in case of
    already de-configured services).
    """
    raise NotImplementedError


@hookspec
def site_configure_check(settings: Settings, log: bool) -> Iterator[bool]:
    """Check installation in each plugin.

    Yield True values if installation is okay and False otherwise, most likely
    with an ERROR message logged (if 'log' is True).
    """
    raise NotImplementedError


@hookspec
def site_configure_list(settings: Settings) -> Iterator[Path]:
    """Yield paths managed during site-configure by the plugin."""
    raise NotImplementedError


@hookspec
async def site_configure_start(settings: Settings) -> None:
    """Start site-wise services upon site configuration."""
    raise NotImplementedError


@hookspec
async def site_configure_stop(settings: Settings) -> None:
    """Stop site-wise services upon site de-configuration."""
    raise NotImplementedError


@hookspec
def systemd_units() -> list[str]:
    """Systemd unit names used by each plugin."""
    raise NotImplementedError


@hookspec
def systemd_unit_templates(settings: Settings) -> Iterator[tuple[str, str]]:
    """Systemd unit templates used by each plugin."""
    raise NotImplementedError


@hookspec
def systemd_tmpfilesd_managed_dir(settings: Settings) -> Iterator[tuple[str, Path]]:
    """Directory managed with systemd-tmpfiles.d."""
    raise NotImplementedError


@hookspec
def system_lookup(instance: PostgreSQLInstance) -> Any | None:
    """Look up for the satellite service object on system that matches specified instance.

    If the service is unexpectedly misconfigured, a log message at WARNING level
    should be emitted by respective hook implementation.
    """
    raise NotImplementedError


@hookspec
async def get(instance: Instance, running: bool) -> Service | None:
    """Return the description the satellite service bound to specified instance."""
    raise NotImplementedError


@hookspec
def instance_model() -> ComponentModel:
    """Return the definition of an extra field to the Instance interface model
    provided by a plugin.
    """
    raise NotImplementedError


@hookspec
def instance_settings(
    manifest: interface.Instance, settings: Settings
) -> tuple[str, Configuration]:
    """Called before the PostgreSQL instance settings is written."""
    raise NotImplementedError


@hookspec(firstresult=True)
async def standby_model(
    instance: PostgreSQLInstance, standby: Standby, running: bool
) -> postgresql.Standby:
    """The interface model holding standby information, if 'instance' is a
    plain standby.

    Only one implementation should be invoked so call order and returned value
    matter.

    An implementation may raise a ValueError to interrupt hook execution.
    """
    raise NotImplementedError


@hookspec
async def postgresql_configured(
    instance: PostgreSQLInstance,
    manifest: interface.Instance,
    config: Configuration,
    changes: ConfigChanges,
) -> None:
    """Called when the PostgreSQL instance got (re-)configured."""
    raise NotImplementedError


@hookspec
async def instance_dropped(instance: Instance) -> None:
    """Called when the PostgreSQL instance got dropped."""
    raise NotImplementedError


@hookspec
async def instance_started(instance: Instance) -> None:
    """Called when the PostgreSQL instance got started."""
    raise NotImplementedError


@hookspec
async def instance_stopped(instance: Instance) -> None:
    """Called when the PostgreSQL instance got stopped."""
    raise NotImplementedError


@hookspec
async def instance_promoted(instance: Instance) -> None:
    """Called when the PostgreSQL instance got promoted."""
    raise NotImplementedError


@hookspec
def instance_env(instance: Instance) -> dict[str, str]:
    """Return environment variables for instance defined by the plugin."""
    raise NotImplementedError


@hookspec
async def instance_upgraded(old: PostgreSQLInstance, new: PostgreSQLInstance) -> None:
    """Called when 'old' PostgreSQL instance got upgraded as 'new'."""
    raise NotImplementedError


@hookspec
async def instance_status(instance: Instance) -> tuple[Status, str] | None:
    """Return instance status"""
    raise NotImplementedError


@hookspec
def role_model() -> ComponentModel:
    """Return the definition for an extra field to the Role interface model
    provided by a plugin.
    """
    raise NotImplementedError


@hookspec
async def role_change(
    role: interface.BaseRole, instance: PostgreSQLInstance
) -> tuple[bool, bool]:
    """Called when 'role' changed in 'instance' (be it a create, an update or a deletion).

    Return a tuple with 2 boolean values. The first one tells if any change happened
    during hook invocation. The second one if a configuration reload is required.
    """
    raise NotImplementedError


@hookspec
async def role_inspect(instance: PostgreSQLInstance, name: str) -> dict[str, Any]:
    """Return extra attributes for 'name' role from plugins."""
    raise NotImplementedError


@hookspec
def rolename(settings: Settings) -> str:
    """Return the name of role used by a plugin."""
    raise NotImplementedError


@hookspec
def role(settings: Settings, manifest: interface.Instance) -> interface.Role | None:
    """Return the role used by a plugin, to be created at instance creation."""
    raise NotImplementedError


@hookspec
def database(settings: Settings, manifest: interface.Instance) -> interface.Database:
    """Return the database used by a plugin, to be created at instance creation."""
    raise NotImplementedError


@hookspec(firstresult=True)
async def restore_postgresql(
    instance: PostgreSQLInstance, manifest: interface.Instance
) -> MaybeFirstResult:
    """Restore an instance from a backup."""
    raise NotImplementedError


@hookspec
def patroni_create_replica_method(
    manifest: interface.Instance, instance: PostgreSQLInstance
) -> tuple[str, dict[str, Any]] | None:
    raise NotImplementedError


@hookspec
def postgresql_service_name(instance: PostgreSQLInstance) -> str | None:
    """Return the system service name (e.g. 'postgresql')."""
    raise NotImplementedError


@hookspec(firstresult=True)
async def enable_service(
    settings: Settings, service: str, name: str | None
) -> FirstResult | None:
    """Enable a service

    Only one implementation should be invoked so call order and returned value
    matter.
    """
    raise NotImplementedError


@hookspec(firstresult=True)
async def disable_service(
    settings: Settings, service: str, name: str | None, now: bool | None
) -> FirstResult | None:
    """Disable a service

    Only one implementation should be invoked so call order and returned value
    matter.
    """
    raise NotImplementedError


@hookspec(firstresult=True)
async def start_service(
    settings: Settings, service: str, name: str | None
) -> MaybeFirstResult:
    """Start a service for a plugin

    Only one implementation should be invoked so call order and returned value
    matter.
    """
    raise NotImplementedError


@hookspec(firstresult=True)
async def stop_service(
    settings: Settings, service: str, name: str | None
) -> MaybeFirstResult:
    """Stop a service for a plugin

    Only one implementation should be invoked so call order and returned value
    matter.
    """
    raise NotImplementedError


@hookspec(firstresult=True)
async def restart_service(
    settings: Settings, service: str, name: str | None
) -> MaybeFirstResult:
    """Restart a service for a plugin

    Only one implementation should be invoked so call order and returned value
    matter.
    """
    raise NotImplementedError


@hookspec(firstresult=True)
async def service_status(settings: Settings, service: str, name: str | None) -> Status:
    """Return a service status for a plugin

    Only one implementation should be invoked so call order and returned value
    matter.
    """
    raise NotImplementedError


@hookspec(firstresult=True)
async def schedule_service(
    settings: Settings, service: str, name: str
) -> MaybeFirstResult:
    """Schedule a job through timer

    Only one implementation should be invoked so call order and returned value
    matter.
    """
    raise NotImplementedError


@hookspec(firstresult=True)
async def unschedule_service(
    settings: Settings, service: str, name: str, now: bool | None
) -> MaybeFirstResult:
    """Unchedule a job

    Only one implementation should be invoked so call order and returned value
    matter.
    """
    raise NotImplementedError


@hookspec(firstresult=True)
async def start_timer(settings: Settings, service: str, name: str) -> MaybeFirstResult:
    """Start a timer

    Only one implementation should be invoked so call order and returned value
    matter.
    """
    raise NotImplementedError


@hookspec(firstresult=True)
async def stop_timer(settings: Settings, service: str, name: str) -> FirstResult:
    """Stop a timer

    Only one implementation should be invoked so call order and returned value
    matter.
    """
    raise NotImplementedError


@hookspec
def logrotate_config(settings: Settings) -> str | None:
    """Return logrotate configuration for the plugin or None if no
    configuration should be installed.
    """
    raise NotImplementedError


@hookspec
def rsyslog_config(settings: Settings) -> str | None:
    """Return rsyslog configuration for the service or None if no
    configuration should be installed.
    """
    raise NotImplementedError

# SPDX-FileCopyrightText: 2021 Dalibo
#
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

import configparser

import pgtoolkit.conf as pgconf

from .. import hookimpl, types, util
from ..models import Instance, PostgreSQLInstance, interface
from ..settings import Settings, _pgbackrest
from . import base
from . import register_if as base_register_if
from .base import get_settings, parser
from .models import interface as i

logger = util.get_logger(__name__)

HostRepository = _pgbackrest.SSHHostRepository


def register_if(settings: Settings) -> bool:
    if not base_register_if(settings):
        return False
    s = get_settings(settings)
    return isinstance(s.repository, HostRepository)


@hookimpl
async def site_configure_install(settings: Settings) -> None:
    s = get_settings(settings)
    base.site_configure_install(settings, base_config(s))


@hookimpl
async def site_configure_uninstall(settings: Settings) -> None:
    base.site_configure_uninstall(settings)


@hookimpl
async def postgresql_configured(
    instance: PostgreSQLInstance,
    manifest: interface.Instance,
    config: pgconf.Configuration,
    changes: types.ConfigChanges,
) -> None:
    try:
        service = manifest.service(i.Service)
    except ValueError:
        return
    base.setup(
        instance, service, config, changes, manifest.creating, manifest.upgrading_from
    )


@hookimpl
async def instance_dropped(instance: Instance) -> None:
    with base.instance_dropped(instance):
        pass


def repository_settings(settings: _pgbackrest.Settings) -> HostRepository:
    assert isinstance(settings.repository, HostRepository)
    return settings.repository


def base_config(settings: _pgbackrest.Settings) -> configparser.ConfigParser:
    """Build the base configuration for pgbackrest clients on the database
    host.
    """
    cp = parser()
    cp.read_string(base.template("pgbackrest.conf").format(**dict(settings)))
    s = repository_settings(settings)
    rhost = {
        "repo1-host-type": "ssh",
        "repo1-host": s.host,
    }
    if s.host_port:
        rhost["repo1-host-port"] = str(s.host_port)
    if s.host_config:
        rhost["repo1-host-config"] = str(s.host_config)
    if s.host_user:
        rhost["repo1-host-user"] = s.host_user
    if s.cmd_ssh:
        rhost["cmd-ssh"] = str(s.cmd_ssh)
    cp["global"].update(rhost)
    return cp

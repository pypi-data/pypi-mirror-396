# SPDX-FileCopyrightText: 2025 Dalibo
#
# SPDX-License-Identifier: GPL-3.0-or-later
from __future__ import annotations

from typing import Any, Literal

import pgtoolkit.conf as pgconf

from .. import types
from ..models import PostgreSQLInstance, interface
from . import configure_context, impl
from .impl import available as available
from .impl import get_settings as get_settings
from .models import build


async def pg_hba_config(instance: PostgreSQLInstance) -> list[str]:
    settings = get_settings(instance._settings)
    patroni = build.Patroni.get(instance.qualname, settings)
    r = await impl.api_request(patroni, "GET", "config")
    hba = r.json().get("postgresql", {}).get("pg_hba", [])
    assert isinstance(hba, list)
    return hba


async def configure_pg_hba(instance: PostgreSQLInstance, hba: list[str]) -> None:
    settings = get_settings(instance._settings)
    patroni = build.Patroni.get(instance.qualname, settings)
    await impl.api_request(
        patroni, "PATCH", "config", json={"postgresql": {"pg_hba": hba}}
    )


def configure_auth(*args: Any, **kwargs: Any) -> Literal[False]:
    # no-op, since pg_hba.conf and pg_ident.conf are installed
    # through Patroni configuration.
    return False


async def postgresql_editable_conf(
    instance: PostgreSQLInstance,
) -> pgconf.Configuration:
    settings = get_settings(instance._settings)
    patroni = build.Patroni.get(instance.qualname, settings)
    conf = pgconf.Configuration()
    parameters = await _postgresql_parameters(patroni)
    with conf.edit() as entries:
        for k, v in parameters.items():
            entries.add(k, v)
    return conf


postgresql_conf = postgresql_editable_conf


async def _postgresql_parameters(patroni: build.Patroni) -> dict[str, Any]:
    r = await impl.api_request(patroni, "GET", "config")
    parameters = r.json().get("postgresql", {}).get("parameters", {})
    assert isinstance(parameters, dict)
    return parameters


async def configure_postgresql(
    configuration: pgconf.Configuration,
    instance: PostgreSQLInstance,
    manifest: interface.Instance,
) -> types.ConfigChanges | None:
    """Build and validate Patroni configuration,
    optionally send a PATCH request with DCS stored parameters,
    and return changes to PostgreSQL configuration.
    """

    async def _parameters(
        actual: build.Patroni | None, configuration: pgconf.Configuration
    ) -> tuple[dict[str, Any], dict[str, Any]]:
        if actual is None:
            return {}, build.parameters_managed(configuration, {})
        actual_params = await _postgresql_parameters(actual)
        return (
            actual_params,
            build.parameters_managed(configuration, actual_params, False),
        )

    settings = get_settings(instance._settings)
    async with configure_context(instance, manifest) as ctx:
        op, actual = ctx
        if op == "create":
            # Nothing should be done here. All operations have been performed
            # by Patroni after the Patroni configuration has been written when
            # running init_postgresql().
            return {}
        # In all other operations (upgrade, convert or update), we need to
        # write (or alter) the Patroni configuration file.
        patroni = impl._configure_postgresql(
            settings, configuration, instance, manifest, ctx
        )

    if op != "update":
        # Only updating ("alter") an instance should modify the configuration
        # stored on the DCS.
        return {}

    # When updating an instance, parameters will be stored into the DCS, this
    # will affect all instances in the Patroni cluster.
    assert patroni is not None
    actual_params, params = await _parameters(actual, configuration)
    await impl.api_request(
        patroni, "PATCH", "config", json={"postgresql": {"parameters": params}}
    )
    return impl.postgresql_changes(
        actual.postgresql if actual is not None else None,
        actual_params,
        patroni.postgresql,
        params,
    )

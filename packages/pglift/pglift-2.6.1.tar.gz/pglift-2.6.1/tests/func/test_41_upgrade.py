# SPDX-FileCopyrightText: 2021 Dalibo
#
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

from pathlib import Path

import pytest

from pglift import (
    databases,
    exceptions,
    instances,
    pgbackrest,
    plugin_manager,
    postgresql,
)
from pglift.models import interface, system
from pglift.pgbackrest.models import Service as pgBackRestService
from pglift.settings import PostgreSQLVersion, Settings, _pgbackrest

from . import passfile_entries

pytestmark = pytest.mark.anyio


async def test_upgrade(
    pg_version: PostgreSQLVersion, upgraded_instance: system.Instance
) -> None:
    assert upgraded_instance.name == "upgraded"
    pg_instance = upgraded_instance.postgresql
    assert pg_instance.version == pg_version
    assert not await postgresql.is_running(pg_instance)
    async with postgresql.running(pg_instance):
        assert await databases.exists(pg_instance, "postgres")


async def test_upgrade_pgpass(
    settings: Settings,
    passfile: Path,
    upgraded_instance: system.Instance,
    surole_password: str | None,
    pgbackrest_password: str | None,
) -> None:
    backuprole = settings.postgresql.backuprole.name
    port = upgraded_instance.postgresql.port
    assert f"*:{port}:*:postgres:{surole_password}" in passfile_entries(passfile)
    assert f"*:{port}:*:{backuprole}:{pgbackrest_password}" in passfile_entries(
        passfile, role=backuprole
    )


@pytest.fixture
def old_instance(
    upgraded_instance: system.Instance, to_be_upgraded_instance: system.Instance
) -> system.Instance:
    # Do a fresh system lookup to account for pgbackrest being deconfigured on
    # the old instance.
    i = system.Instance.from_postgresql(to_be_upgraded_instance.postgresql)
    with pytest.raises(ValueError):
        i.service(pgBackRestService)
    return i


async def test_pgbackrest_iter_backups(
    old_instance: system.Instance, pgbackrest_settings: _pgbackrest.Settings
) -> None:
    with pytest.raises(exceptions.InstanceStateError):
        await pgbackrest.iter_backups(old_instance, pgbackrest_settings).__anext__()


async def test_pgbackrest_restore(
    old_instance: system.Instance, pgbackrest_settings: _pgbackrest.Settings
) -> None:
    with pytest.raises(exceptions.InstanceStateError):
        await pgbackrest.restore(old_instance, pgbackrest_settings)


async def test_upgrade_again(
    pg_version: PostgreSQLVersion,
    settings: Settings,
    old_instance: system.Instance,
    free_tcp_port: int,
) -> None:
    """Upgrading the old instance works."""
    pm = plugin_manager(settings)
    instance = await instances.upgrade(
        old_instance,
        name="upgraded_again",
        version=pg_version,
        port=free_tcp_port,
        _instance_model=interface.Instance.composite(pm),
    )
    try:
        with pytest.raises(ValueError):
            instance.service(pgBackRestService)
    finally:
        await instances.drop(instance)

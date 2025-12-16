# SPDX-FileCopyrightText: 2021 Dalibo
#
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

from pathlib import Path

import httpx
import pytest
from pgtoolkit.conf import Configuration

import pglift.pgbackrest.models as pgbackrest_models
import pglift.prometheus.impl as prometheus
import pglift.prometheus.models as prometheus_models
from pglift import exceptions, pgbackrest, systemd
from pglift.models import interface, system
from pglift.settings import Settings, _pgbackrest, _systemd
from pglift.systemd import scheduler, service_manager

from .pgbackrest import PgbackrestRepoHost

pytestmark = pytest.mark.anyio


@pytest.mark.standby
async def test_standby_pgbackrest_teardown(
    instance: system.Instance,
    standby_instance: system.Instance,
    standby_pg_instance: system.PostgreSQLInstance,
    standby_instance_dropped: Configuration,
) -> None:
    pgbackrest_settings = pgbackrest.available(standby_pg_instance._settings)
    if not pgbackrest_settings:
        pytest.skip("pgbackrest not available")
    assert not pgbackrest.enabled(standby_pg_instance, pgbackrest_settings)
    assert pgbackrest.system_lookup(standby_pg_instance) is None
    standby_svc = standby_instance.service(pgbackrest_models.Service)  # still in memory
    config = standby_svc.path.read_text()
    assert f"pg{standby_svc.index}-path" not in config
    assert str(standby_pg_instance.datadir) not in config

    svc = instance.service(pgbackrest_models.Service)
    assert svc.path == standby_svc.path
    assert f"pg{svc.index}-path" in config
    assert str(instance.postgresql.datadir) in config


@pytest.mark.anyio
async def test_upgrade_pgbackrest_teardown(
    to_be_upgraded_instance: system.Instance,
    upgraded_instance: system.Instance,
    to_be_upgraded_instance_dropped: Configuration,
    upgraded_instance_dropped: Configuration,
) -> None:
    pgbackrest_settings = pgbackrest.available(to_be_upgraded_instance._settings)
    if not pgbackrest_settings:
        pytest.skip("pgbackrest not available")
    assert pgbackrest.available(upgraded_instance._settings) == pgbackrest_settings

    assert not pgbackrest.enabled(
        to_be_upgraded_instance.postgresql, pgbackrest_settings
    )
    assert pgbackrest.system_lookup(to_be_upgraded_instance.postgresql) is None
    svc = to_be_upgraded_instance.service(pgbackrest_models.Service)  # still in memory
    assert not svc.path.exists()

    assert not pgbackrest.enabled(upgraded_instance.postgresql, pgbackrest_settings)
    assert pgbackrest.system_lookup(upgraded_instance.postgresql) is None
    svc = upgraded_instance.service(pgbackrest_models.Service)  # still in memory
    assert not svc.path.exists()


@pytest.mark.standby
@pytest.mark.anyio
async def test_pgbackrest_teardown(
    instance: system.Instance,
    standby_instance_dropped: Configuration,
    instance_dropped: Configuration,
    pgbackrest_repo_host: PgbackrestRepoHost | None,
) -> None:
    pgbackrest_settings = pgbackrest.available(instance._settings)
    if not pgbackrest_settings:
        pytest.skip("pgbackrest not available")
    stanza = f"mystanza-{instance.name}"
    path_repository: _pgbackrest.PathRepository | None = None
    if pgbackrest_repo_host is None:
        assert isinstance(pgbackrest_settings.repository, _pgbackrest.PathRepository)
        path_repository = pgbackrest_settings.repository
    if path_repository:
        # Backups are kept (confirmation prompt defaults to 'no', in
        # instance_drop() hook).
        assert list(
            (path_repository.path / "archive").glob(f"{stanza}*"),
        )
        assert list(
            (path_repository.path / "backup").glob(f"{stanza}*"),
        )
    assert not (pgbackrest_settings.configpath / "conf.d" / f"{stanza}.conf").exists()
    # global directories and files are preserved
    assert (pgbackrest_settings.configpath / "pgbackrest.conf").exists()
    assert (pgbackrest_settings.configpath / "conf.d").exists()
    if path_repository:
        assert path_repository.path.exists()
    assert pgbackrest_settings.spoolpath.exists()
    assert pgbackrest_settings.logpath.exists()
    assert not list(pgbackrest_settings.logpath.glob(f"{stanza}*.log"))


async def test_pgpass(
    settings: Settings,
    passfile: Path,
    instance_manifest: interface.Instance,
    upgraded_instance_dropped: Configuration,
    to_be_upgraded_instance_dropped: Configuration,
    instance_dropped: Configuration,
) -> None:
    assert not passfile.exists()


@pytest.mark.usefixtures("require_systemd_scheduler")
async def test_systemd_backup_job(
    systemd_settings: _systemd.Settings,
    instance: system.Instance,
    instance_dropped: Configuration,
) -> None:
    unit = scheduler.unit("backup", instance.qualname)
    assert not await systemd.is_active(systemd_settings, unit)
    assert not await systemd.is_enabled(systemd_settings, unit)


async def test_prometheus_teardown(
    settings: Settings,
    instance: system.Instance,
    instance_dropped: Configuration,
) -> None:
    prometheus_settings = prometheus.available(settings)
    if not prometheus_settings:
        pytest.skip("prometheus not available")
    configpath = Path(
        str(prometheus_settings.configpath).format(name=instance.qualname)
    )
    assert not configpath.exists()
    if settings.service_manager == "systemd":
        assert settings.systemd is not None
        assert not await systemd.is_enabled(
            settings.systemd,
            service_manager.unit("postgres_exporter", instance.qualname),
        )
        service = instance.service(prometheus_models.Service)
        port = service.port
        with pytest.raises(httpx.ConnectError):
            httpx.get(f"http://0.0.0.0:{port}/metrics")


async def test_databases_teardown(
    pg_instance: system.PostgreSQLInstance,
    instance_dropped: Configuration,
) -> None:
    assert not pg_instance.dumps_directory.exists()


async def test_instance(
    pg_instance: system.PostgreSQLInstance, instance_dropped: Configuration
) -> None:
    with pytest.raises(exceptions.InstanceNotFound, match=str(pg_instance)):
        system.check_instance(pg_instance)

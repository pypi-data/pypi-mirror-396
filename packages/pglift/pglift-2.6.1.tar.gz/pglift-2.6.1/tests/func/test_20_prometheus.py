# SPDX-FileCopyrightText: 2021 Dalibo
#
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

import logging
import urllib.parse
from collections.abc import AsyncIterator
from pathlib import Path

import httpx
import pydantic
import pytest
from anyio.pytest_plugin import FreePortFactory

from pglift import exceptions, instances, postgresql, systemd
from pglift.models import interface, system
from pglift.prometheus import impl as prometheus
from pglift.prometheus import instance_status
from pglift.prometheus.models import Service
from pglift.prometheus.models.interface import PostgresExporter
from pglift.settings import Settings
from pglift.systemd import service_manager
from pglift.types import Status

from . import config_dict, http_get
from .conftest import DatabaseFactory, RoleFactory

METRICS_URL = "http://0.0.0.0:{}/metrics"

pytestmark = pytest.mark.anyio


@pytest.fixture(scope="session", autouse=True)
def _prometheus_available(prometheus_execpath: Path | None) -> None:
    if not prometheus_execpath:
        pytest.skip("prometheus is not available")


async def test_configure(
    settings: Settings, prometheus_password: str, instance: system.Instance
) -> None:
    service = instance.service(Service)
    assert (
        service.password and service.password.get_secret_value() == prometheus_password
    )
    name = instance.qualname
    prometheus_settings = prometheus.get_settings(settings)
    configpath = Path(str(prometheus_settings.configpath).format(name=name))
    assert configpath.exists()

    prometheus_config = config_dict(configpath)
    dsn = prometheus_config["DATA_SOURCE_NAME"]
    assert "postgresql://prometheus" in dsn
    pgport = instance.postgresql.port
    assert f"{urllib.parse.quote(prometheus_password)}@:{pgport}" in dsn
    port = service.port
    assert f":{port}" in prometheus_config["POSTGRES_EXPORTER_OPTS"]


@pytest.fixture
async def postgres_exporter(
    settings: Settings,
    prometheus_password: str,
    pg_instance: system.PostgreSQLInstance,
    free_tcp_port: int,
    role_factory: RoleFactory,
) -> AsyncIterator[Service]:
    """Setup a postgres_exporter service for 'instance' using another port."""
    port = free_tcp_port
    name = "123-fo-o"
    role = interface.Role(name="prometheus_tests", password=prometheus_password)
    unix_socket_directories = pg_instance.configuration()["unix_socket_directories"]
    assert isinstance(unix_socket_directories, str), unix_socket_directories
    host = unix_socket_directories.split(",", 1)[0]
    dsn = f"host={host} dbname=postgres port={pg_instance.port} user={role.name} sslmode=disable"
    prometheus_settings = prometheus.get_settings(settings)
    service = await prometheus.setup(
        name,
        settings,
        prometheus_settings,
        dsn=dsn,
        password=pydantic.SecretStr(prometheus_password),
        port=port,
    )
    configpath = Path(str(prometheus_settings.configpath).format(name=name))
    assert configpath.exists()

    role_factory(
        role.name, "LOGIN", f"PASSWORD {prometheus_password!r}", "IN ROLE pg_monitor"
    )

    yield service

    await prometheus.revert_setup(name, settings, prometheus_settings)
    assert not configpath.exists()


@pytest.mark.usefixtures("instance")
async def test_setup(
    settings: Settings,
    pg_instance: system.PostgreSQLInstance,
    postgres_exporter: Service,
) -> None:
    prometheus_settings = prometheus.get_settings(settings)
    configpath = Path(
        str(prometheus_settings.configpath).format(name=postgres_exporter.name)
    )
    prometheus_config = config_dict(configpath)
    assert f":{pg_instance.port}" in prometheus_config["DATA_SOURCE_NAME"]
    assert f":{postgres_exporter.port}" in prometheus_config["POSTGRES_EXPORTER_OPTS"]


async def test_start_stop(
    settings: Settings, instance: system.Instance, database_factory: DatabaseFactory
) -> None:
    service = instance.service(Service)
    port = service.port

    systemd_settings = settings.systemd
    if settings.service_manager == "systemd":
        assert systemd_settings
        assert await systemd.is_enabled(
            systemd_settings,
            service_manager.unit("postgres_exporter", instance.qualname),
        )

    database_factory("newdb")

    if settings.service_manager == "systemd":
        assert systemd_settings
        assert await systemd.is_active(
            systemd_settings,
            service_manager.unit("postgres_exporter", instance.qualname),
        )
    r = http_get(METRICS_URL.format(port))
    r.raise_for_status()
    output = r.text
    assert "pg_up 1" in output.splitlines()

    assert await instance_status(instance) == (Status.running, "prometheus")

    async with instances.stopped(instance):
        if settings.service_manager == "systemd":
            assert systemd_settings
            assert not await systemd.is_active(
                systemd_settings,
                service_manager.unit("postgres_exporter", instance.qualname),
            )
        with pytest.raises(httpx.ConnectError):
            httpx.get(METRICS_URL.format(port))

        assert await instance_status(instance) == (Status.not_running, "prometheus")


async def test_standby(
    settings: Settings,
    prometheus_password: str,
    standby_instance: system.Instance,
) -> None:
    name = standby_instance.qualname
    service = standby_instance.service(Service)
    port = service.port
    assert (
        service.password and service.password.get_secret_value() == prometheus_password
    )
    standby_prometheus_settings = prometheus.get_settings(settings)
    configpath = Path(str(standby_prometheus_settings.configpath).format(name=name))
    assert configpath.exists()

    assert await postgresql.is_running(standby_instance.postgresql)

    if settings.service_manager == "systemd":
        assert settings.systemd
        assert await systemd.is_active(
            settings.systemd, service_manager.unit("postgres_exporter", name)
        )
    r = http_get(METRICS_URL.format(port))
    r.raise_for_status()
    output = r.text
    assert "pg_up 1" in output.splitlines()


async def test_upgrade(
    prometheus_password: str, upgraded_instance: system.Instance
) -> None:
    service = upgraded_instance.service(Service)
    assert service.password
    name = upgraded_instance.qualname
    configpath = Path(str(service.settings.configpath).format(name=name))
    prometheus_config = config_dict(configpath)
    dsn = prometheus_config["DATA_SOURCE_NAME"]
    pgport = upgraded_instance.postgresql.port
    assert f"{urllib.parse.quote(prometheus_password)}@:{pgport}" in dsn


async def test_start_stop_nonlocal(
    settings: Settings,
    pg_instance: system.PostgreSQLInstance,
    postgres_exporter: Service,
) -> None:
    if settings.service_manager == "systemd":
        assert settings.systemd
        assert await systemd.is_enabled(
            settings.systemd,
            service_manager.unit("postgres_exporter", postgres_exporter.name),
        )

    assert await postgresql.is_running(pg_instance)
    await prometheus.start(settings, postgres_exporter)
    try:
        if settings.service_manager == "systemd":
            assert settings.systemd
            assert await systemd.is_active(
                settings.systemd,
                service_manager.unit("postgres_exporter", postgres_exporter.name),
            )
        r = http_get(METRICS_URL.format(postgres_exporter.port))
        r.raise_for_status()
        output = r.text
        assert "pg_up 1" in output.splitlines()
    finally:
        await prometheus.stop(settings, postgres_exporter)

    if settings.service_manager == "systemd":
        assert settings.systemd
        assert not await systemd.is_active(
            settings.systemd,
            service_manager.unit("postgres_exporter", postgres_exporter.name),
        )
    with pytest.raises(httpx.ConnectError):
        httpx.get(METRICS_URL.format(postgres_exporter.port))


async def test_apply(
    settings: Settings, free_tcp_port_factory: FreePortFactory
) -> None:
    port = free_tcp_port_factory()
    m = PostgresExporter(name="test", dsn="dbname=test", port=port)
    prometheus_settings = prometheus.get_settings(settings)
    r = await prometheus.apply(m, settings, prometheus_settings)
    assert r.change_state == "created"

    configpath = Path(str(prometheus_settings.configpath).format(name="test"))
    assert configpath.exists()

    prometheus_config = config_dict(configpath)
    assert f":{port}" in prometheus_config["POSTGRES_EXPORTER_OPTS"]

    port1 = free_tcp_port_factory()
    r = await prometheus.apply(
        m.model_copy(update={"port": port1}), settings, prometheus_settings
    )
    assert r.change_state == "changed"
    prometheus_config = config_dict(configpath)
    assert f":{port1}" in prometheus_config["POSTGRES_EXPORTER_OPTS"]

    r = await prometheus.apply(
        PostgresExporter(name="test", dsn="", port=port, state="absent"),
        settings,
        prometheus_settings,
    )
    assert r.change_state == "dropped"
    assert not configpath.exists()


async def test_drop_exists(
    settings: Settings,
    free_tcp_port: int,
    caplog: pytest.LogCaptureFixture,
) -> None:
    port = free_tcp_port
    prometheus_settings = prometheus.get_settings(settings)
    await prometheus.setup("dropme", settings, prometheus_settings, port=port)
    configpath = prometheus._configpath("dropme", prometheus_settings)
    config = prometheus._config(configpath)
    assert prometheus.port(config) == port
    await prometheus.drop(settings, "dropme")
    with pytest.raises(exceptions.FileNotFoundError, match="postgres_exporter config"):
        prometheus._config(configpath)
    caplog.clear()
    with caplog.at_level(logging.WARNING, logger="pglift"):
        await prometheus.drop(settings, "dropme")
    assert caplog.messages == [
        f"failed to read postgres_exporter configuration dropme: postgres_exporter configuration file {configpath} not found",
        "no postgres_exporter service 'dropme' found",
    ]

# SPDX-FileCopyrightText: 2021 Dalibo
#
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

import ssl
from pathlib import Path

import httpx
import pytest
import tenacity

from pglift import instances, postgresql, systemd
from pglift.models import system
from pglift.settings import Settings
from pglift.systemd import service_manager
from pglift.temboard import impl as temboard
from pglift.temboard import instance_status
from pglift.temboard.models import Service
from pglift.types import Status

from . import http_get

DISCOVER_URL = "https://0.0.0.0:{}/discover"

pytestmark = pytest.mark.anyio


@pytest.fixture(scope="session", autouse=True)
def _temboard_available(temboard_execpath: Path | None) -> None:
    if not temboard_execpath:
        pytest.skip("temboard not available")


@tenacity.retry(
    wait=tenacity.wait_fixed(1), stop=tenacity.stop_after_attempt(5), reraise=True
)
def check_discover(
    pg_instance: system.PostgreSQLInstance, service: Service, ca_cert: Path
) -> None:
    port = service.port
    ctx = ssl.create_default_context(cafile=str(ca_cert))
    r = http_get(DISCOVER_URL.format(port), verify=ctx)
    r.raise_for_status()
    assert r.json()["postgres"]["port"] == pg_instance.port


async def test_configure(
    settings: Settings, temboard_password: str, instance: system.Instance, ca_cert: Path
) -> None:
    temboard_settings = temboard.get_settings(settings)
    configpath = Path(str(temboard_settings.configpath).format(name=instance.qualname))
    assert configpath.exists()
    lines = configpath.read_text().splitlines()
    assert "user = temboardagent" in lines
    assert f"port = {instance.postgresql.port}" in lines
    assert f"password = {temboard_password}" in lines

    home_dir = Path(str(temboard_settings.home).format(name=instance.qualname))
    assert home_dir.exists()
    assert (
        temboard_settings.logpath / f"temboard_agent_{instance.qualname}.log"
    ).exists()

    service = instance.service(Service)
    check_discover(instance.postgresql, service, ca_cert)


async def test_start_stop(
    settings: Settings, instance: system.Instance, ca_cert: Path
) -> None:
    service = instance.service(Service)
    port = service.port
    if settings.service_manager == "systemd":
        assert settings.systemd
        assert await systemd.is_enabled(
            settings.systemd, service_manager.unit("temboard_agent", instance.qualname)
        )
        assert await systemd.is_active(
            settings.systemd, service_manager.unit("temboard_agent", instance.qualname)
        )
    check_discover(instance.postgresql, service, ca_cert)

    assert await instance_status(instance) == (Status.running, "temBoard")

    async with instances.stopped(instance):
        if settings.service_manager == "systemd":
            assert settings.systemd
            assert not await systemd.is_active(
                settings.systemd,
                service_manager.unit("temboard_agent", instance.qualname),
            )
        with pytest.raises(httpx.ConnectError):
            httpx.get(DISCOVER_URL.format(port), verify=False)
        assert await instance_status(instance) == (Status.not_running, "temBoard")


async def test_standby(
    settings: Settings,
    temboard_password: str,
    standby_instance: system.Instance,
    ca_cert: Path,
) -> None:
    temboard_settings = temboard.get_settings(settings)
    service = standby_instance.service(Service)
    assert service.password and service.password.get_secret_value() == temboard_password
    configpath = Path(
        str(temboard_settings.configpath).format(name=standby_instance.qualname)
    )
    assert configpath.exists()
    assert await postgresql.is_running(standby_instance.postgresql)

    if settings.service_manager == "systemd":
        assert settings.systemd
        assert await systemd.is_active(
            settings.systemd,
            service_manager.unit("temboard_agent", standby_instance.qualname),
        )
    check_discover(standby_instance.postgresql, service, ca_cert)

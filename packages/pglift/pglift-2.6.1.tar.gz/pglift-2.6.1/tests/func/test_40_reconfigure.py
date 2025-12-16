# SPDX-FileCopyrightText: 2021 Dalibo
#
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

import urllib.parse
from collections.abc import AsyncIterator
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import psutil
import pytest
from anyio.pytest_plugin import FreePortFactory

from pglift import instances, pgbackrest, postgresql, roles, systemd
from pglift.models import interface, system
from pglift.prometheus import impl as prometheus
from pglift.settings import Settings, _postgresql
from pglift.systemd import service_manager
from pglift.temboard import impl as temboard
from pglift.testutil import model_copy_validate

from . import AuthType, async_connect, config_dict, passfile_entries, role_in_pgpass

pytestmark = pytest.mark.anyio


async def get_last_start(settings: Settings, unit: str, pidfile: Path) -> float:
    if settings.service_manager == "systemd":
        assert settings.systemd
        _, value = (
            await systemd.get_property(
                settings.systemd, unit, "ActiveEnterTimestampMonotonic"
            )
        ).split("=", 1)
        return float(value.strip())
    else:
        with pidfile.open() as f:
            return psutil.Process(int(f.readline().strip())).create_time()


@dataclass
class Recorder:
    service: Any
    service_name: str

    async def record(self) -> None:
        pass

    def assert_restarted(self) -> None:
        pytest.skip(f"{self.service_name} is not available")


@dataclass
class RestartRecorder(Recorder):
    instance: system.Instance
    records: list[float] = field(default_factory=list)

    async def record(self) -> None:
        settings = self.instance._settings
        s = self.service.get_settings(settings)
        record = await get_last_start(
            settings,
            service_manager.unit(self.service_name, self.instance.qualname),
            self.service._pidfile(self.instance.qualname, s),
        )
        self.records.append(record)

    def assert_restarted(self) -> None:
        assert self.records[-2] != self.records[-1]


@pytest.fixture(scope="module")
def prometheus_restart_recorder(
    instance: system.Instance,
    prometheus_execpath: Path | None,
) -> Recorder:
    if prometheus_execpath:
        return RestartRecorder(prometheus, "postgres_exporter", instance)
    return Recorder(prometheus, "postgres_exporter")


@pytest.fixture(scope="module")
def temboard_restart_recorder(
    instance: system.Instance,
    temboard_execpath: Path | None,
) -> Recorder:
    if temboard_execpath:
        return RestartRecorder(temboard, "temboard_agent", instance)
    return Recorder(temboard, "temboard_agent")


role1, role2, role3 = (
    interface.Role(name="r1", password="1", pgpass=True),
    interface.Role(name="r2", password="2", pgpass=True),
    interface.Role(name="r3", pgpass=False),
)


@pytest.fixture(scope="module")
async def passfile_roles(
    settings: Settings,
    pg_instance: system.PostgreSQLInstance,
    instance_manifest: interface.Instance,
    postgresql_auth: AuthType,
    postgresql_settings: _postgresql.Settings,
) -> None:
    if postgresql_auth == "pgpass":
        surole = instance_manifest.surole(settings)
        assert settings.postgresql.surole.pgpass
        assert await postgresql.is_running(pg_instance)
        await roles.apply(pg_instance, role1)
        await roles.apply(pg_instance, role2)
        await roles.apply(pg_instance, role3)
        port = pg_instance.port
        passfile = postgresql_settings.auth.passfile
        assert passfile is not None
        assert role_in_pgpass(passfile, role1, port=port)
        assert role_in_pgpass(passfile, role2, port=port)
        assert not role_in_pgpass(passfile, role3)
        assert role_in_pgpass(passfile, surole, port=port)


@dataclass
class Reconfigured:
    instance: system.PostgreSQLInstance
    newport: int


@pytest.fixture(scope="module")
async def reconfigured(
    pg_instance: system.PostgreSQLInstance,
    instance_manifest: interface.Instance,
    prometheus_restart_recorder: Recorder,
    temboard_restart_recorder: Recorder,
    passfile_roles: None,
    free_tcp_port_factory: FreePortFactory,
) -> AsyncIterator[Reconfigured]:
    newport = free_tcp_port_factory()
    update = {
        "port": newport,
        "restart_on_changes": True,
        "settings": {"lc_numeric": ""},
    }
    await prometheus_restart_recorder.record()
    await temboard_restart_recorder.record()

    await instances.configure(
        pg_instance, model_copy_validate(instance_manifest, update)
    )
    await prometheus_restart_recorder.record()
    await temboard_restart_recorder.record()

    yield Reconfigured(pg_instance, newport)

    await instances.configure(pg_instance, instance_manifest)


async def test_pgpass(
    settings: Settings,
    passfile: Path,
    reconfigured: Reconfigured,
    surole_password: str,
    pgbackrest_password: str,
    pgbackrest_available: bool,
) -> None:
    newport = reconfigured.newport
    backuprole = settings.postgresql.backuprole.name
    assert f"*:{newport}:*:postgres:{surole_password}" in passfile_entries(passfile)
    if pgbackrest_available:
        assert f"*:{newport}:*:{backuprole}:{pgbackrest_password}" in passfile_entries(
            passfile, role=backuprole
        )


async def test_get_locale(reconfigured: Reconfigured) -> None:
    async with await async_connect(reconfigured.instance) as conn:
        assert await instances.get_locale(conn) is None


async def test_passfile(
    settings: Settings,
    reconfigured: Reconfigured,
    instance_manifest: interface.Instance,
    passfile: Path,
) -> None:
    newport = reconfigured.newport
    surole = instance_manifest.surole(settings)
    oldport = instance_manifest.port
    assert not role_in_pgpass(passfile, role1, port=oldport)
    assert role_in_pgpass(passfile, role1, port=newport)
    assert not role_in_pgpass(passfile, role2, port=oldport)
    assert role_in_pgpass(passfile, role2, port=newport)
    assert not role_in_pgpass(passfile, role3)
    assert not role_in_pgpass(passfile, surole, port=oldport)
    assert role_in_pgpass(passfile, surole, port=newport)


async def test_pgbackrest(
    settings: Settings,
    reconfigured: Reconfigured,
    pgbackrest_available: bool,
) -> None:
    instance, newport = reconfigured.instance, reconfigured.newport
    if not pgbackrest_available:
        pytest.skip("pgbackrest is not available")
    stanza = f"mystanza-{instance.name}"
    pgbackrest_settings = pgbackrest.get_settings(settings)
    stanza_configpath = pgbackrest_settings.configpath / "conf.d" / f"{stanza}.conf"
    config_after = stanza_configpath.read_text()
    assert f"pg1-port = {newport}" in config_after.splitlines()


async def test_prometheus(
    settings: Settings,
    reconfigured: Reconfigured,
    prometheus_password: str,
    prometheus_restart_recorder: Recorder,
) -> None:
    instance, newport = reconfigured.instance, reconfigured.newport
    prometheus_restart_recorder.assert_restarted()
    name = instance.qualname
    prometheus_settings = prometheus.get_settings(settings)
    configpath = Path(str(prometheus_settings.configpath).format(name=name))
    new_prometheus_config = config_dict(configpath)
    dsn = new_prometheus_config["DATA_SOURCE_NAME"]
    assert f"{urllib.parse.quote(prometheus_password)}@:{newport}" in dsn


async def test_temboard(
    settings: Settings,
    reconfigured: Reconfigured,
    temboard_restart_recorder: Recorder,
) -> None:
    instance, newport = reconfigured.instance, reconfigured.newport
    temboard_restart_recorder.assert_restarted()
    temboard_settings = temboard.get_settings(settings)
    configpath = Path(str(temboard_settings.configpath).format(name=instance.qualname))
    lines = configpath.read_text().splitlines()
    assert f"port = {newport}" in lines

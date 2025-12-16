# SPDX-FileCopyrightText: 2021 Dalibo
#
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

import logging
import re
import socket
import subprocess
from collections.abc import AsyncIterator, Iterator
from contextlib import asynccontextmanager
from functools import partial
from pathlib import Path
from typing import Any

import httpx
import pgtoolkit.conf as pgconf
import pytest
import tenacity
import yaml
from anyio.pytest_plugin import FreePortFactory

from pglift import (
    exceptions,
    hba,
    instances,
    manager,
    patroni,
    pgbackrest,
    plugin_manager,
    postgresql,
    roles,
    systemd,
)
from pglift.fixtures.etcd import Etcd
from pglift.fixtures.types import CertFactory
from pglift.models import interface, system
from pglift.patroni import impl, instance_status
from pglift.patroni.models import Patroni, Service
from pglift.patroni.models import interface as i
from pglift.patroni.models import patroni as patroni_get
from pglift.pgbackrest import repo_path
from pglift.pgbackrest.models import Service as PgBackRestService
from pglift.settings import PostgreSQLVersion, Settings, _patroni
from pglift.systemd import service_manager
from pglift.testutil import model_copy_validate
from pglift.types import ConfigChanges, Status, local_host
from pglift.util import deep_update

from . import AuthType, PostgresLogger, check_connect, execute, passfile_entries
from .conftest import InstanceFactory, ManifestFactory
from .pgbackrest import PgbackrestRepoHost

pytestmark = pytest.mark.anyio


@asynccontextmanager
async def reconfigure_instance(
    instance: system.PostgreSQLInstance,
    manifest: interface.Instance,
    **confitems: Any,
) -> AsyncIterator[ConfigChanges]:
    """Context manager to temporarily change instance settings.

    Upon enter, this applies provided settings (and possibly new port)
    and yields settings 'changes' dict.

    Upon exit, the previous settings is restored, and the 'changes' dict
    returned upon enter is updated to reflect this.
    """
    update: dict[str, Any] = {}
    if confitems:
        update["settings"] = dict(manifest.settings) | confitems
    assert update
    update |= {"restart_on_changes": True}
    m = model_copy_validate(manifest, update)
    r = await instances.configure(instance, m)
    changes = r.changes.copy()
    try:
        yield changes
    finally:
        r = await instances.configure(instance, manifest)
        changes.clear()
        changes.update(r.changes)


@pytest.fixture(scope="session", autouse=True)
def _patroni_available(
    patroni_execpaths: tuple[Path, Path] | None,
) -> None:
    if not patroni_execpaths:
        pytest.skip("Patroni is not available")


@pytest.fixture(scope="module")
def etcd_credentials() -> tuple[str, str]:
    return "patroni", "p@tr0n!"


@pytest.fixture(scope="module")
def restapi_credentials() -> tuple[str, str]:
    return "restapiuser", "restapiP4ss0ord!"


# Override default instance_managers fixture, still defined as async
# because mixing sync and async fixtures does not work pretty well
# with ContextVar, more information:
# https://github.com/agronholm/anyio/issues/614
@pytest.fixture(scope="module", autouse=True)
async def instance_managers() -> AsyncIterator[None]:
    # Set the manager to patroni for all operation in this module,
    # we still can change it if needed (eg: creating a standalone)
    with (
        manager.instance.use(patroni),
        manager.hba.use(patroni),
        manager.configuration.use(patroni),
    ):
        yield


@pytest.fixture(scope="module", autouse=True)
def _etcd_running(
    etcd_host: Etcd | None,
    etcd_credentials: tuple[str, str],
    cluster_name: str,
    upgrade_cluster_name: str,
    standalone_convert_cluster_name: str,
    dynamic_cluster_name: str,
) -> Iterator[None]:
    if etcd_host is None:
        pytest.skip("etcd executable not found")
    with etcd_host.running() as e:
        e.setup_auth(
            credentials=etcd_credentials,
            role="svc",
            prefixes=(
                f"/service/{cluster_name}",
                f"/service/{upgrade_cluster_name}",
                f"/service/{standalone_convert_cluster_name}",
                f"/service/{dynamic_cluster_name}",
            ),
        )
        yield None


@pytest.fixture(scope="module", autouse=True)
def http_logs() -> None:
    logging.getLogger("httpx").setLevel(logging.DEBUG)
    logging.getLogger("httpcore").setLevel(logging.INFO)


@pytest.fixture
def patroni_settings(settings: Settings) -> _patroni.Settings:
    return impl.get_settings(settings)


@pytest.fixture(scope="module")
def cluster_name(postgresql_auth: AuthType) -> str:
    # Since instances are kept running while moving from one postgresql_auth
    # value to another, we need distinct cluster name for each.
    return f"pglift-tests-{postgresql_auth}"


@pytest.fixture(scope="module")
def upgrade_cluster_name(postgresql_auth: AuthType) -> str:
    # Since instances are kept running while moving from one postgresql_auth
    # value to another, we need distinct cluster name for each.
    return f"pglift-upgrade-tests-{postgresql_auth}"


@pytest.fixture(scope="module")
def standalone_convert_cluster_name(postgresql_auth: AuthType) -> str:
    # Since instances are kept running while moving from one postgresql_auth
    # value to another, we need distinct cluster name for each.
    return f"pglift-standalone-convert-tests-{postgresql_auth}"


@asynccontextmanager
async def _make_instance(
    settings: Settings,
    manifest: interface.Instance,
    postgres_logger: PostgresLogger,
    pgbackrest_repo_host: PgbackrestRepoHost | None,
    pgbackrest_password: str | None,
) -> AsyncIterator[system.Instance]:
    assert await instances.apply(settings, manifest)
    instance = system.Instance.system_lookup(manifest.name, manifest.version, settings)
    pg_instance = instance.postgresql
    postgres_logger(pg_instance)
    # Define loop_wait to the lowest value possible to speed up our tests
    await impl.api_request(
        Patroni.get(instance.qualname, impl.get_settings(settings)),
        method="PATCH",
        path="config",
        json={"loop_wait": 1},
    )
    if settings.pgbackrest:
        if not pg_instance.standby:
            # make a pgbackrest backup so future standby could be initialized from
            # pgbackrest backup
            if pgbackrest_repo_host is not None:
                svc = instance.service(PgBackRestService)
                pgbackrest_repo_host.add_stanza(svc.stanza, pg_instance)
                await pgbackrest.check(
                    pg_instance, svc, settings.pgbackrest, pgbackrest_password
                )
                pgbackrest_repo_host.run(
                    "backup",
                    "--stanza",
                    svc.stanza,
                    "--type",
                    "full",
                )
            else:
                await repo_path.backup(instance, settings.pgbackrest)
        else:
            # ensure standby has been created from pgbackrest backup
            assert instance._settings.patroni is not None
            assert any(
                "replica has been created using pgbackrest" in line
                for line in impl.logs(instance.qualname, instance._settings.patroni)
            )

    if settings.systemd:
        assert settings.service_manager == "systemd"
        assert await systemd.is_enabled(
            settings.systemd, service_manager.unit("patroni", instance.qualname)
        )

    yield instance

    if instances.exists(pg_instance.name, pg_instance.version, instance._settings):
        # Rebuild the Instance in order to get the list of services refreshed.
        instance = system.Instance.from_postgresql(pg_instance)
        await instances.drop(instance)

        if settings.systemd:
            assert not await systemd.is_enabled(
                settings.systemd, service_manager.unit("patroni", instance.qualname)
            )


@pytest.fixture(scope="module")
def instance1_manifest(
    settings: Settings,
    instance_manifest_factory: ManifestFactory,
    cluster_name: str,
    free_tcp_port_factory: FreePortFactory,
    ca_cert: Path,
    cert_factory: CertFactory,
    etcd_credentials: tuple[str, str],
    restapi_credentials: tuple[str, str],
) -> interface.Instance:
    name = "test1"
    hostname = socket.gethostname()
    host = local_host()
    extras = {}
    if settings.pgbackrest:
        extras = {"pgbackrest": {"stanza": "patroni"}}
    server_cert = cert_factory(host, common_name=hostname)
    return instance_manifest_factory(
        settings,
        name,
        state="started",
        patroni={
            "cluster": cluster_name,
            "node": name,
            "etcd": {
                "username": etcd_credentials[0],
                "password": etcd_credentials[1],
            },
            "restapi": {
                "connect_address": f"{host}:{free_tcp_port_factory()}",
                "authentication": {
                    "username": restapi_credentials[0],
                    "password": restapi_credentials[1],
                },
            },
        },
        auth={"host": "password"},
        settings={
            "listen_addresses": "*",
            "work_mem": "8MB",
            "ssl": True,
            "ssl_ca_file": ca_cert,
            "ssl_cert_file": server_cert.path,
            "ssl_key_file": server_cert.private_key,
            "log_connections": True,
        },
        **extras,
    )


@pytest.fixture(scope="module")
async def instance1(
    settings: Settings,
    instance1_manifest: interface.Instance,
    postgres_logger: PostgresLogger,
    pgbackrest_repo_host: PgbackrestRepoHost | None,
    pgbackrest_password: str | None,
) -> AsyncIterator[system.Instance]:
    async with _make_instance(
        settings,
        instance1_manifest,
        postgres_logger,
        pgbackrest_repo_host,
        pgbackrest_password,
    ) as i:
        yield i


def _p(instance: system.Instance, patroni_settings: _patroni.Settings) -> Patroni:
    p = patroni_get(instance.qualname, patroni_settings)
    assert p
    return p


@pytest.fixture
def patroni1(
    instance1: system.Instance, patroni_settings: _patroni.Settings
) -> Patroni:
    return _p(instance1, patroni_settings)


@pytest.fixture
def patroni2(
    instance2: system.Instance, patroni_settings: _patroni.Settings
) -> Patroni:
    return _p(instance2, patroni_settings)


@pytest.fixture(scope="module")
async def instance2_manifest(
    settings: Settings,
    instance_manifest_factory: ManifestFactory,
    cluster_name: str,
    free_tcp_port_factory: FreePortFactory,
    cert_factory: CertFactory,
    etcd_credentials: tuple[str, str],
) -> interface.Instance:
    name = "test2"
    extras = {}
    if settings.pgbackrest:
        extras = {"pgbackrest": {"stanza": "patroni"}}
    replication_cert = cert_factory(common_name="replication")
    return instance_manifest_factory(
        settings,
        name,
        state="started",
        patroni={
            "cluster": cluster_name,
            "node": name,
            "postgresql": {
                "replication": {
                    "ssl": {
                        "cert": replication_cert.path,
                        "key": replication_cert.private_key,
                    },
                },
            },
            "etcd": {
                "username": etcd_credentials[0],
                "password": etcd_credentials[1],
            },
            "restapi": {"connect_address": f"{local_host()}:{free_tcp_port_factory()}"},
        },
        auth={"host": "password"},
        settings={
            "listen_addresses": "*",
            "work_mem": "8MB",
        },
        **extras,
    )


@pytest.fixture(scope="module")
async def instance2(
    settings: Settings,
    instance2_manifest: interface.Instance,
    postgres_logger: PostgresLogger,
    pgbackrest_repo_host: PgbackrestRepoHost | None,
    pgbackrest_password: str | None,
) -> AsyncIterator[system.Instance]:
    async with _make_instance(
        settings,
        instance2_manifest,
        postgres_logger,
        pgbackrest_repo_host,
        pgbackrest_password,
    ) as i:
        yield i


@pytest.fixture
async def primary_standby(
    instance1: system.Instance, instance2: system.Instance
) -> tuple[system.PostgreSQLInstance, system.PostgreSQLInstance]:
    if instance1.postgresql.standby:
        assert not instance2.postgresql.standby
        return instance2.postgresql, instance1.postgresql
    else:
        assert instance2.postgresql.standby
        return instance1.postgresql, instance2.postgresql


@pytest.fixture
def primary(
    primary_standby: tuple[system.PostgreSQLInstance, system.PostgreSQLInstance],
) -> system.PostgreSQLInstance:
    return primary_standby[0]


@pytest.fixture
def standby(
    primary_standby: tuple[system.PostgreSQLInstance, system.PostgreSQLInstance],
) -> system.PostgreSQLInstance:
    return primary_standby[1]


async def test_waldir(instance1: system.Instance, instance2: system.Instance) -> None:
    pg_wal1 = instance1.postgresql.datadir / "pg_wal"
    assert pg_wal1.is_symlink()
    assert pg_wal1.resolve() == instance1.postgresql.waldir

    pg_wal2 = instance2.postgresql.datadir / "pg_wal"
    assert pg_wal2.is_symlink()
    assert pg_wal2.resolve() == instance2.postgresql.waldir


async def test_service_and_config(
    patroni_settings: _patroni.Settings,
    instance1: system.Instance,
    instance1_manifest: interface.Instance,
    instance2: system.Instance,
    instance2_manifest: interface.Instance,
    cluster_name: str,
) -> None:
    for instance, manifest in (
        (instance1, instance1_manifest),
        (instance2, instance2_manifest),
    ):
        check_server_and_config(instance, manifest, patroni_settings, cluster_name)


async def test_pgpass(
    patroni_settings: _patroni.Settings,
    primary: system.PostgreSQLInstance,
    standby: system.PostgreSQLInstance,
    replrole_password: str,
) -> None:
    primary_patroni = Patroni.get(primary.qualname, patroni_settings)
    primary_pgpass = primary_patroni.postgresql.pgpass
    assert primary_pgpass and not primary_pgpass.exists()
    standby_patroni = Patroni.get(standby.qualname, patroni_settings)
    standby_pgpass = standby_patroni.postgresql.pgpass
    assert standby_pgpass and standby_pgpass.exists()
    (replication_entry,) = passfile_entries(standby_pgpass, role="replication")
    assert replication_entry.endswith(
        f":{primary.port}:*:replication:{replrole_password}"
    )


def check_server_and_config(
    instance: system.Instance,
    manifest: interface.Instance,
    settings: _patroni.Settings,
    cluster_name: str,
) -> None:
    s = instance.service(Service)
    assert s and s.cluster == cluster_name
    configpath = impl._configpath(instance.qualname, settings)
    with configpath.open() as f:
        config = yaml.safe_load(f)
    listen_addr = manifest.patroni.restapi.listen  # type: ignore[attr-defined]
    assert config["restapi"]["listen"] == listen_addr
    assert config["postgresql"]["listen"] == f"*:{instance.postgresql.port}"
    assert config["postgresql"]["parameters"]["work_mem"] == "8MB"
    assert config["ctl"]["certfile"]


async def test_postgresql_conf(instance1: system.Instance) -> None:
    with (instance1.postgresql.datadir / "postgresql.conf").open() as f:
        _pgconf = pgconf.parse(f)
    assert "lc_messages" in _pgconf.as_dict()
    assert "lc_monetary" in _pgconf.as_dict()


async def test_logpath(
    patroni_settings: _patroni.Settings, instance1: system.Instance
) -> None:
    logpath = patroni_settings.logpath / instance1.qualname
    assert logpath.exists()
    assert (logpath / "patroni.log").exists()


def logs(instance: system.Instance, settings: _patroni.Settings) -> list[str]:
    return [
        line.split("INFO: ", 1)[-1].strip()
        for line in impl.logs(instance.qualname, settings)
    ]


async def test_logs(
    patroni_settings: _patroni.Settings,
    instance1: system.Instance,
    instance2: system.Instance,
) -> None:
    logs1 = logs(instance1, patroni_settings)
    logs2 = logs(instance2, patroni_settings)
    leader = instance1.name
    secondary = instance2.name
    assert f"no action. I am ({leader}), the leader with the lock" in logs1
    assert (
        f"no action. I am ({secondary}), a secondary, and following a leader ({leader})"
        in logs2
    )


@pytest.mark.parametrize(
    "setting,expected",
    [
        ("work_mem", "8MB"),
        ("listen_addresses", "*"),
    ],
)
async def test_postgresql_config(
    instance1: system.Instance, setting: str, expected: Any
) -> None:
    _pgconf = instance1.postgresql.configuration()
    assert _pgconf[setting] == expected


async def test_configure_postgresql(
    patroni_settings: _patroni.Settings,
    instance1_manifest: interface.Instance,
    instance1: system.Instance,
) -> None:
    postgresql_conf = instance1.postgresql.datadir / "postgresql.conf"
    mtime = postgresql_conf.stat().st_mtime

    # Retry assertions on postgresql.conf, waiting for patroni reload (1s, per
    # loop_wait).
    @tenacity.retry(
        retry=(
            tenacity.retry_if_exception_type(ValueError)
            | tenacity.retry_if_exception_type(AttributeError)
        ),
        wait=tenacity.wait_fixed(0.5),
        stop=tenacity.stop_after_attempt(5),
        reraise=True,
    )
    def check_postgresql_config(work_mem: str, mtime: float) -> float:
        mtime_after = postgresql_conf.stat().st_mtime
        if mtime_after <= mtime:
            raise ValueError
        with postgresql_conf.open() as f:
            _pgconf = pgconf.parse(f)
        assert _pgconf.work_mem == work_mem
        return mtime_after

    async with reconfigure_instance(
        instance1.postgresql, instance1_manifest, work_mem="10MB"
    ) as changes:
        config = Patroni.get(instance1.qualname, patroni_settings)
        assert config.postgresql.parameters is not None
        assert config.postgresql.parameters["work_mem"] == "10MB"
        mtime = check_postgresql_config("10MB", mtime)
        assert changes == {"work_mem": ("8MB", "10MB")}

    assert changes == {"work_mem": ("10MB", "8MB")}
    config = Patroni.get(instance1.qualname, patroni_settings)
    assert config.postgresql.parameters is not None
    assert config.postgresql.parameters["work_mem"] == "8MB"
    check_postgresql_config("8MB", mtime)


async def test_instance_get(
    instance1: system.Instance, instance2: system.Instance, cluster_name: str
) -> None:
    for instance in (instance1, instance2):
        m = await instances.get(instance)
        p = m.service(i.Service)
        assert p is not None and p.cluster == cluster_name
        assert p.cluster == cluster_name
        assert not p.is_paused
        assert {m.name for m in p.cluster_members} == {"test1", "test2"}


async def test_check_api_status(patroni1: Patroni) -> None:
    assert await impl.check_api_status(patroni1)


async def test_instance_status(
    instance1: system.Instance, instance2: system.Instance
) -> None:
    assert await instance_status(instance1) == (Status.running, "Patroni API")
    assert await instance_status(instance2) == (Status.running, "Patroni API")


async def test_cluster_members(
    instance1: system.Instance,
    instance2: system.Instance,
    patroni1: Patroni,
) -> None:
    members = await impl.cluster_members(patroni1)
    assert len(members) == 2, members
    for m, instance in zip(members, (instance1, instance2), strict=True):
        assert m.port == instance.postgresql.port


async def test_cluster_leader(patroni1: Patroni, patroni2: Patroni) -> None:
    assert await impl.cluster_leader(patroni1) == "test1"
    assert await impl.cluster_leader(patroni2) == "test1"


async def test_replication_connection_uses_ssl_cert(
    instance1: system.Instance, instance2: system.Instance
) -> None:
    patterns = [
        r'connection authenticated: identity="CN=replication,.+" method=cert',
        rf"replication connection authorized: user=replication application_name={instance2.name} SSL enabled",
    ]
    try:
        for line in postgresql.logs(instance1.postgresql, timeout=0):
            p = patterns[0]
            if re.search(p, line.rstrip()):
                del patterns[0]
                if not patterns:
                    break
        else:
            pytest.fail(f"expected log lines not found: {patterns!r}")
    except TimeoutError:
        pass


async def test_connect(
    settings: Settings,
    postgresql_auth: AuthType,
    instance1_manifest: interface.Instance,
    instance1: system.Instance,
    instance2_manifest: interface.Instance,
    instance2: system.Instance,
    surole_name: str,
) -> None:
    check_connect(
        settings, postgresql_auth, surole_name, instance1_manifest, instance1.postgresql
    )
    check_connect(
        settings, postgresql_auth, surole_name, instance2_manifest, instance2.postgresql
    )


async def test_reload(instance1: system.Instance) -> None:
    await instances.reload(instance1.postgresql, manager=patroni)


async def test_start_restart_stop(
    settings: Settings,
    instance1: system.Instance,
    instance2: system.Instance,
    patroni1: Patroni,
    patroni2: Patroni,
) -> None:
    use_systemd = settings.service_manager == "systemd"

    assert await postgresql.is_running(instance1.postgresql)
    if use_systemd:
        assert settings.systemd
        assert await systemd.is_active(
            settings.systemd, service_manager.unit("patroni", instance1.qualname)
        )
    assert await impl.check_api_status(patroni1)

    # Stop instance2, then restart instance1, so that the latter remains
    # leader.
    async with instances.stopped(instance2):
        assert (await postgresql.status(instance2.postgresql)) == Status.not_running
        if use_systemd:
            assert settings.systemd
            assert not await systemd.is_active(
                settings.systemd, service_manager.unit("patroni", instance2.qualname)
            )
        assert not await impl.check_api_status(patroni2)

        with pytest.raises(
            exceptions.SystemError,
            match=r"REST API server for Patroni .+ is unreachable",
        ):
            await instances.reload(instance2.postgresql, manager=patroni)

        await instances.restart(instance1)
    assert await postgresql.is_running(instance1.postgresql)
    assert await impl.check_api_status(patroni1)

    # Starting instance2 can take a bit of time, so use a retry logic.
    async for attempt in tenacity.AsyncRetrying(
        retry=tenacity.retry_if_exception_type(httpx.HTTPError),
        wait=tenacity.wait_fixed(0.5),
        stop=tenacity.stop_after_attempt(5),
    ):
        with attempt:
            await impl.api_request(patroni2, "GET", "readiness")


async def test_ctl_version(
    primary: system.PostgreSQLInstance,
    patroni_settings: _patroni.Settings,
    cluster_name: str,
) -> None:
    # Test patronictl with command that uses a REST API endpoint
    configfile = impl._configpath(primary.qualname, patroni_settings)
    if not (patronictl := patroni_settings.execpath.parent / "patronictl").exists():
        pytest.skip("patronictl executable not found")
    r = subprocess.run(
        [patronictl, "--config-file", configfile, "version", cluster_name],
        check=True,
        capture_output=True,
        text=True,
    )
    patterns = [
        r"patronictl version .*",
        r"test1: Patroni .* PostgreSQL .*$",
        r"test2: Patroni .* PostgreSQL .*$",
    ]
    for line in r.stdout.splitlines():
        p = patterns[0]
        if re.search(p, line.rstrip()):
            del patterns[0]
            if not patterns:
                break
    else:
        pytest.fail(f"expected lines not found: {patterns!r}")


async def test_basicauth_protected(
    instance1: system.Instance,
    patroni_settings: _patroni.Settings,
    restapi_credentials: tuple[str, str],
) -> None:
    """Test Patroni managed instance protected by basicauth."""

    # check restapi basic authentication is configured
    configpath = impl._configpath(instance1.qualname, patroni_settings)
    with configpath.open() as f:
        config = yaml.safe_load(f)
        assert config["restapi"]["authentication"] == {
            "username": restapi_credentials[0],
            "password": restapi_credentials[1],
        }

    # test connection and alter config with valid credential (from YAML config file)
    api_r = partial(impl.api_request, path="config")
    p = _p(instance1, patroni_settings)
    r = await api_r(patroni=p, method="GET")
    assert r.status_code == 200
    r = await api_r(
        patroni=p,
        method="PATCH",
        json={"postgresql": {"parameters": {"max_connections": "101"}}},
    )
    assert r.status_code == 200

    # alter username & password then test connection (must fail)
    badauth = model_copy_validate(
        p,
        {"restapi": {"authentication": {"username": "wrong", "password": "alsowrong"}}},
    )
    with pytest.raises(
        exceptions.SystemError, match=r"REST API server for Patroni .+ is unreachable"
    ):
        await api_r(patroni=badauth, method="GET")
    with pytest.raises(
        exceptions.SystemError, match=r"REST API server for Patroni .+ is unreachable"
    ):
        await api_r(
            patroni=badauth,
            method="PATCH",
            json={"postgresql": {"parameters": {"max_connections": "101"}}},
        )

    # test without authentication
    noauth = model_copy_validate(
        p,
        {"restapi": {"authentication": None}},
    )
    with pytest.raises(
        exceptions.SystemError, match=r"REST API server for Patroni .+ is unreachable"
    ):
        await api_r(patroni=noauth, method="GET")


@pytest.fixture
def to_be_upgraded_manifest(
    settings: Settings,
    instance_manifest_factory: ManifestFactory,
    free_tcp_port: int,
    etcd_credentials: tuple[str, str],
    upgrade_cluster_name: str,
) -> interface.Instance:
    name = "upgrademe"
    extras = {}
    if settings.pgbackrest:
        extras = {"pgbackrest": {"stanza": "patroniup"}}
    return instance_manifest_factory(
        settings,
        name,
        state="started",
        patroni={
            "cluster": upgrade_cluster_name,
            "node": name,
            "etcd": {
                "username": etcd_credentials[0],
                "password": etcd_credentials[1],
            },
            "restapi": {"connect_address": f"{local_host()}:{free_tcp_port}"},
        },
        auth={"host": "password"},
        **extras,
    )


@pytest.fixture
async def to_be_upgraded(
    settings: Settings,
    to_be_upgraded_manifest: interface.Instance,
    postgres_logger: PostgresLogger,
    pgbackrest_repo_host: PgbackrestRepoHost | None,
    pgbackrest_password: str | None,
) -> AsyncIterator[system.Instance]:
    async with _make_instance(
        settings,
        to_be_upgraded_manifest,
        postgres_logger,
        pgbackrest_repo_host,
        pgbackrest_password,
    ) as i:
        yield i


@pytest.fixture
async def upgraded(
    settings: Settings,
    to_be_upgraded: system.Instance,
    free_tcp_port: int,
    pg_version: PostgreSQLVersion,
) -> AsyncIterator[system.Instance]:
    assert to_be_upgraded.postgresql.standby is None
    await instances.stop(to_be_upgraded, manager=patroni)
    port = free_tcp_port
    pm = plugin_manager(settings)
    upgraded = await instances.upgrade(
        to_be_upgraded,
        name="patroni_upgraded",
        version=pg_version,
        port=port,
        _instance_model=interface.Instance.composite(pm),
    )
    yield upgraded
    await instances.drop(upgraded)


async def test_upgrade(
    upgraded: system.Instance, patroni_settings: _patroni.Settings
) -> None:
    p = _p(upgraded, patroni_settings)
    await instances.start(upgraded)
    members = await impl.cluster_members(p)
    assert len(members) == 1, members


async def test_convert_standalone(
    settings: Settings,
    instance_factory: InstanceFactory,
    etcd_credentials: tuple[str, str],
    standalone_convert_cluster_name: str,
    free_tcp_port: int,
) -> None:
    name = "standalone"
    # temporarily set the manager to postgresql, as we want to build a
    # standalone instance we will convert.
    with (
        manager.instance.use(postgresql),
        manager.hba.use(postgresql),
        manager.configuration.use(postgresql),
    ):
        manifest, instance = await instance_factory(settings, name, state="started")
    with pytest.raises(ValueError):
        instance.service(Service)
    manifest = model_copy_validate(
        manifest,
        {
            "patroni": {
                "cluster": standalone_convert_cluster_name,
                "node": name,
                "etcd": {
                    "username": etcd_credentials[0],
                    "password": etcd_credentials[1],
                },
                "restapi": {"connect_address": f"{local_host()}:{free_tcp_port}"},
            }
        },
    )
    result = await instances.apply(settings, manifest)
    assert result.change_state == "changed"
    # Rebuild system.Instance to force satellite services lookup.
    instance = system.Instance.from_postgresql(instance.postgresql)
    s = instance.service(Service)
    assert s and s.cluster == standalone_convert_cluster_name


async def test_add_role_with_hba(
    patroni_settings: _patroni.Settings, instance1: system.Instance
) -> None:
    rolname = "dwho1960"

    @tenacity.retry(
        retry=tenacity.retry_if_exception_type(AssertionError),
        wait=tenacity.wait_fixed(0.5),
        stop=tenacity.stop_after_attempt(5),
        reraise=True,
    )
    def check_hba_rules(expected: Any) -> None:
        result = execute(
            instance1.postgresql,
            f"SELECT type, database, address, netmask, auth_method FROM pg_hba_file_rules WHERE '{rolname}' = ANY(user_name)",
            fetch=True,
        )
        assert result == expected

    role = interface.Role(
        name=rolname,
        hba_records=[
            {
                "connection": {"address": "192.168.0.0/16"},
                "database": "db",
                "method": "trust",
            },
            {
                "connection": {
                    "address": "127.0.0.1",
                    "netmask": "255.255.255.255",
                },
                "database": "db",
                "method": "trust",
            },
        ],
    )
    await roles.apply(instance1.postgresql, role)
    configpath = impl._configpath(instance1.qualname, patroni_settings)
    conf = yaml.safe_load(configpath.read_text())
    pg_hba = conf["postgresql"]["pg_hba"]
    assert (
        f"host    db              {rolname}        127.0.0.1       255.255.255.255 trust"
        in pg_hba
    )
    assert (
        f"host    db              {rolname}        192.168.0.0/16          trust"
        in pg_hba
    )
    await instances.reload(instance1.postgresql, manager=patroni)
    check_hba_rules(
        [
            {
                "type": "host",
                "database": ["db"],
                "address": "192.168.0.0",
                "netmask": "255.255.0.0",
                "auth_method": "trust",
            },
            {
                "type": "host",
                "database": ["db"],
                "address": "127.0.0.1",
                "netmask": "255.255.255.255",
                "auth_method": "trust",
            },
        ]
    )

    await roles.drop(instance1.postgresql, interface.RoleDropped(name=rolname))
    await instances.reload(instance1.postgresql)
    conf = yaml.safe_load(configpath.read_text())
    pg_hba = conf["postgresql"]["pg_hba"]
    assert rolname not in pg_hba
    check_hba_rules([])


async def test_update(
    settings: Settings,
    instance1_manifest: interface.Instance,
    instance1: system.Instance,
    free_tcp_port: int,
    cluster_name: str,
    patroni1: Patroni,
    caplog: pytest.LogCaptureFixture,
) -> None:
    # Update the restapi.listen of the Patroni model
    restapi_new = {"listen": f"{local_host()}:{free_tcp_port}"}
    manifest = model_copy_validate(
        instance1_manifest,
        update={
            "patroni": {
                "cluster": cluster_name,
                "restapi": restapi_new,
            },
        },
    )
    result = await instances.apply(settings, manifest)
    assert result.change_state == "changed"

    logger_name = f"{__name__}.test_update"
    logger = logging.getLogger(logger_name)

    retrying = partial(
        tenacity.AsyncRetrying,
        wait=tenacity.wait_fixed(0.5),
        stop=tenacity.stop_after_attempt(10),
    )

    # Request to the Patroni API with the old connect address should fail (after a few seconds)
    with caplog.at_level(logging.DEBUG):
        async for attempt in retrying(
            retry=tenacity.retry_if_result(lambda r: r is True)
        ):
            with attempt:
                if not (r := await impl.check_api_status(patroni1, logger=logger)):
                    logger.info("API is no longer listening")
            attempt.retry_state.set_result(r)
    messages = [r.message for r in caplog.records if r.name == logger_name]
    assert re.match(
        rf"checking status of REST API.*at {patroni1.restapi.listen}$", messages[0]
    )
    assert messages[-1] == "API is no longer listening"

    caplog.clear()

    # Make sure that we can connect to the REST API using the new address
    # We use deep_update to keep the other fields (certificates, etc.)
    patroni1_updated = model_copy_validate(
        patroni1,
        update={"restapi": deep_update(patroni1.restapi.model_dump(), restapi_new)},
    )
    with caplog.at_level(logging.DEBUG):
        async for attempt in retrying(
            retry=tenacity.retry_if_result(lambda r: r is False)
        ):
            with attempt:
                if r := await impl.check_api_status(patroni1_updated, logger=logger):
                    logger.info("API is now listening")
            attempt.retry_state.set_result(r)
    messages = [r.message for r in caplog.records if r.name == logger_name]
    assert re.match(
        rf"checking status of REST API.*at {restapi_new['listen']}$", messages[0]
    )
    assert messages[-1] == "API is now listening"
    assert await postgresql.is_running(instance1.postgresql)


async def test_postgresql_info_on_paused_mode(
    caplog: pytest.LogCaptureFixture,
    instance1: system.Instance,
    patroni1: Patroni,
    patroni_settings: _patroni.Settings,
) -> None:
    async def pause(enabled: bool = True) -> None:
        await impl.api_request(
            patroni1, method="PATCH", path="config", json={"pause": enabled}
        )
        async for attempt in tenacity.AsyncRetrying(
            retry=tenacity.retry_if_exception_type(AssertionError),
            wait=tenacity.wait_fixed(0.5),
            stop=tenacity.stop_after_attempt(5),
        ):
            with attempt:
                assert enabled == await impl.is_paused(patroni1)

    await pause()
    caplog.clear()
    await instances.stop(instance1)
    assert (
        f"Patroni '{instance1.qualname}' is in pause mode, PostgreSQL server will not be stopped"
        in caplog.messages
    )
    # _check set to False, because in maintenance mode PostgreSQL keeps
    # running even when we shut down Patroni
    await instances.start(instance1, _check=False)
    async for attempt in tenacity.AsyncRetrying(
        retry=tenacity.retry_if_exception_type(
            (exceptions.SystemError, httpx.HTTPStatusError)
        ),
        wait=tenacity.wait_fixed(0.5),
        stop=tenacity.stop_after_attempt(5),
    ):
        with attempt:
            await impl.api_request(patroni1, "GET", "readiness")
    await pause(False)


@pytest.fixture(scope="module")
def dynamic_settings(settings: Settings) -> Settings:
    s = settings.model_dump()
    s["patroni"]["configuration_mode"]["auth"] = "dynamic"
    s["patroni"]["configuration_mode"]["parameters"] = "dynamic"
    return Settings.model_validate(s)


@pytest.fixture
def dynamic_patroni_settings(dynamic_settings: Settings) -> _patroni.Settings:
    return impl.get_settings(dynamic_settings)


@pytest.fixture(scope="module")
def dynamic_cluster_name(postgresql_auth: AuthType) -> str:
    return f"pglift-dynamic-tests-{postgresql_auth}"


@pytest.fixture(scope="module")
def instance_dynamic_mode_manifest(
    dynamic_settings: Settings,
    instance_manifest_factory: ManifestFactory,
    dynamic_cluster_name: str,
    free_tcp_port_factory: FreePortFactory,
    ca_cert: Path,
    cert_factory: CertFactory,
    etcd_credentials: tuple[str, str],
    restapi_credentials: tuple[str, str],
) -> interface.Instance:
    name = "dynamic"
    host = local_host()
    extras = {}
    if dynamic_settings.pgbackrest:
        extras = {"pgbackrest": {"stanza": "patronidcs"}}
    return instance_manifest_factory(
        dynamic_settings,
        name,
        state="started",
        patroni={
            "cluster": dynamic_cluster_name,
            "node": name,
            "etcd": {
                "username": etcd_credentials[0],
                "password": etcd_credentials[1],
            },
            "restapi": {
                "connect_address": f"{host}:{free_tcp_port_factory()}",
                "authentication": {
                    "username": restapi_credentials[0],
                    "password": restapi_credentials[1],
                },
            },
        },
        auth={"host": "password"},
        settings={
            "listen_addresses": "*",
            "work_mem": "8MB",
            "log_connections": True,
        },
        **extras,
    )


@pytest.fixture(scope="module")
async def dynamic(
    dynamic_settings: Settings,
    instance_dynamic_mode_manifest: interface.Instance,
    postgres_logger: PostgresLogger,
    pgbackrest_repo_host: PgbackrestRepoHost | None,
    pgbackrest_password: str | None,
) -> AsyncIterator[system.Instance]:
    with manager.from_manifest(instance_dynamic_mode_manifest, dynamic_settings):
        async with _make_instance(
            dynamic_settings,
            instance_dynamic_mode_manifest,
            postgres_logger,
            pgbackrest_repo_host,
            pgbackrest_password,
        ) as i:
            yield i


@pytest.fixture
def patroni_dynamic(
    dynamic: system.Instance, dynamic_patroni_settings: _patroni.Settings
) -> Patroni:
    return _p(dynamic, dynamic_patroni_settings)


async def test_instance_dynamic_mode(
    dynamic_settings: Settings,
    instance_dynamic_mode_manifest: interface.Instance,
    dynamic: system.Instance,
    free_tcp_port: int,
    caplog: pytest.LogCaptureFixture,
) -> None:
    def assert_no_hba_and_parameters_in_patroni_conf() -> None:
        p = Patroni.get(dynamic.qualname, impl.get_settings(dynamic_settings))
        assert p.postgresql.parameters is None
        assert p.postgresql.pg_hba is None

    async def _dcs_config() -> dict[str, Any]:
        r = await impl.api_request(
            Patroni.get(dynamic.qualname, impl.get_settings(dynamic_settings)),
            method="GET",
            path="config",
        )
        res = r.json()
        assert isinstance(res, dict)
        return res

    # first check our instance is running
    assert await instance_status(dynamic) == (Status.running, "Patroni API")

    assert_no_hba_and_parameters_in_patroni_conf()

    dynamic_conf = await _dcs_config()
    assert "postgresql" in dynamic_conf
    assert dynamic_conf["postgresql"]["parameters"]["work_mem"] == "8MB"

    caplog.set_level("WARNING", logger="pglift.patroni")
    async with reconfigure_instance(
        dynamic.postgresql,
        instance_dynamic_mode_manifest,
        work_mem="10MB",
        max_worker_processes=2,
    ) as changes:
        assert changes == {
            "max_worker_processes": (None, 2),
            "work_mem": ("8MB", "10MB"),
        }
        cur_parameters = (await _dcs_config())["postgresql"]["parameters"]
        assert cur_parameters["work_mem"] == "10MB"
        assert cur_parameters["max_worker_processes"] == 2

    assert (
        "the following PostgreSQL parameter(s) cannot be changed for a Patroni-managed instance: max_worker_processes"
        not in caplog.messages
    )

    # verify pg_hba is modified / retrieved / stored into the DCS
    assert "pg_hba" in dynamic_conf["postgresql"]
    await hba.add(dynamic.postgresql, interface.HbaRecord(user="caesar", method="md5"))

    cur_hba = (await _dcs_config())["postgresql"]["pg_hba"]
    assert cur_hba
    assert_no_hba_and_parameters_in_patroni_conf()

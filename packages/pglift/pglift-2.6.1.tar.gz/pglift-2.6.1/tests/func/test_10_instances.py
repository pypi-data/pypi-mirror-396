# SPDX-FileCopyrightText: 2021 Dalibo
#
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

import logging
import re
import socket
from pathlib import Path

import pgtoolkit.conf as pgconf
import psycopg
import pytest

from pglift import databases, exceptions, instances, postgresql, systemd
from pglift.fixtures.types import CertFactory
from pglift.models import interface, system
from pglift.settings import PostgreSQLVersion, Settings
from pglift.systemd import service_manager
from pglift.testutil import model_copy_validate
from pglift.types import Status

from . import (
    AuthType,
    async_connect,
    check_connect,
    execute,
    passfile_entries,
    running_instance,
)
from .conftest import InstanceFactory

pytestmark = pytest.mark.anyio


async def test_postgresql_directories(pg_instance: system.PostgreSQLInstance) -> None:
    assert pg_instance.datadir.exists()
    assert pg_instance.waldir.exists()
    assert (pg_instance.waldir / "archive_status").is_dir()


async def test_postgresql_config(
    pg_instance: system.PostgreSQLInstance, instance_manifest: interface.Instance
) -> None:
    postgresql_conf = pg_instance.datadir / "postgresql.conf"
    assert postgresql_conf.exists()
    with postgresql_conf.open() as f:
        pgconfig = pgconf.parse(f)
    assert {k for k, v in pgconfig.entries.items() if not v.commented} & set(
        instance_manifest.settings
    )


async def test_psqlrc(
    pg_instance: system.PostgreSQLInstance, pg_version: PostgreSQLVersion
) -> None:
    if pg_version == "16":
        line1 = f"\\set PROMPT1 '[{pg_instance.name} - version {pg_instance.version}] %n@%~%R%x%# '"
    else:
        line1 = f"\\set PROMPT1 '[{pg_instance}] %n@%~%R%x%# '"
    assert pg_instance.psqlrc.read_text().strip().splitlines() == [
        line1,
        "\\set PROMPT2 ' %R%x%# '",
    ]


async def test_systemd(settings: Settings, instance: system.Instance) -> None:
    if settings.service_manager == "systemd":
        assert settings.systemd
        assert await systemd.is_enabled(
            settings.systemd, service_manager.unit("postgresql", instance.qualname)
        )


async def test_pgpass(
    settings: Settings,
    passfile: Path,
    pg_instance: system.PostgreSQLInstance,
    surole_password: str,
    pgbackrest_password: str,
    pgbackrest_available: bool,
) -> None:
    port = pg_instance.port
    backuprole = settings.postgresql.backuprole.name

    assert passfile_entries(passfile) == [f"*:{port}:*:postgres:{surole_password}"]
    if pgbackrest_available:
        assert passfile_entries(passfile, role=backuprole) == [
            f"*:{port}:*:{backuprole}:{pgbackrest_password}"
        ]


async def test_connect(
    settings: Settings,
    instance_manifest: interface.Instance,
    pg_instance: system.PostgreSQLInstance,
    postgresql_auth: AuthType,
    surole_name: str,
) -> None:
    check_connect(
        settings, postgresql_auth, surole_name, instance_manifest, pg_instance
    )


async def test_replrole(pg_instance: system.PostgreSQLInstance) -> None:
    (row,) = execute(
        pg_instance,
        # Simplified version of \du in psql.
        "SELECT rolsuper, rolcanlogin, rolreplication,"
        " ARRAY(SELECT b.rolname"
        "       FROM pg_catalog.pg_auth_members m"
        "       JOIN pg_catalog.pg_roles b ON (m.roleid = b.oid)"
        "       WHERE m.member = r.oid) as memberof"
        " FROM pg_catalog.pg_roles r"
        " WHERE rolname = 'replication'",
    )
    assert row == {
        "rolsuper": False,
        "rolcanlogin": True,
        "rolreplication": True,
        "memberof": ["pg_read_all_stats"],
    }


async def test_hba(
    settings: Settings,
    instance_manifest: interface.Instance,
    pg_instance: system.PostgreSQLInstance,
    postgresql_auth: AuthType,
) -> None:
    hba_path = pg_instance.datadir / "pg_hba.conf"
    hba = hba_path.read_text().splitlines()
    auth_settings = settings.postgresql.auth
    auth_instance = instance_manifest.auth
    assert auth_instance is not None
    if postgresql_auth == "peer":
        regex = re.compile(r"local.*all.*peer")
        assert any(regex.search(item) for item in hba)
    assert (
        f"local   all             all                                     {auth_settings.local}"
        in hba
    )
    assert (
        f"host    all             all             127.0.0.1/32            {auth_instance.host}"
        in hba
    )
    assert (
        f"hostssl all             all             127.0.0.1/32            {auth_settings.hostssl}"
        in hba
    )


async def test_ident(
    pg_instance: system.PostgreSQLInstance, postgresql_auth: AuthType, surole_name: str
) -> None:
    ident_path = pg_instance.datadir / "pg_ident.conf"
    ident = ident_path.read_text().splitlines()
    col_headers = "# MAPNAME       SYSTEM-USERNAME         PG-USERNAME"
    assert col_headers in ident
    if postgresql_auth == "peer":
        regex = re.compile(rf"^test\s+\w+\s+{surole_name}$")
        assert any(regex.search(item) for item in ident)
    else:
        assert ident[-1] == col_headers


async def test_start_stop_restart_running_is_ready_stopped(
    settings: Settings, instance: system.Instance, caplog: pytest.LogCaptureFixture
) -> None:
    pg_instance = instance.postgresql
    assert await postgresql.status(pg_instance) == Status.running
    assert await postgresql.is_ready(pg_instance)
    use_systemd = settings.service_manager == "systemd"
    systemd_settings = settings.systemd
    if use_systemd:
        assert systemd_settings
        assert await systemd.is_active(
            systemd_settings, service_manager.unit("postgresql", pg_instance.qualname)
        )

    await instances.stop(instance)
    try:
        assert await postgresql.status(pg_instance) == Status.not_running
        assert not await postgresql.is_ready(pg_instance)
        if use_systemd:
            assert systemd_settings
            assert not await systemd.is_active(
                systemd_settings,
                service_manager.unit("postgresql", pg_instance.qualname),
            )
        # Stopping a non-running instance is a no-op.
        caplog.clear()
        with caplog.at_level(logging.WARNING, logger="pglift"):
            await instances.stop(instance)
        assert f"instance {instance} is already stopped" in caplog.records[0].message
    finally:
        await instances.start(instance)

    assert await postgresql.is_running(pg_instance)
    assert await postgresql.is_ready(pg_instance)
    if use_systemd:
        assert systemd_settings
        assert await systemd.is_active(
            systemd_settings, service_manager.unit("postgresql", pg_instance.qualname)
        )

    assert await postgresql.status(pg_instance) == Status.running
    assert await postgresql.is_ready(pg_instance)
    if not use_systemd:
        # FIXME: systemctl restart would fail with:
        #   Start request repeated too quickly.
        #   Failed with result 'start-limit-hit'.
        await instances.restart(instance)
        assert await postgresql.is_running(pg_instance)
        assert await postgresql.is_ready(pg_instance)
    await instances.reload(pg_instance)
    assert await postgresql.status(pg_instance) == Status.running
    assert await postgresql.is_ready(pg_instance)

    assert await postgresql.status(pg_instance) == Status.running
    async with instances.stopped(instance):
        assert await postgresql.status(pg_instance) == Status.not_running
        async with instances.stopped(instance):
            assert await postgresql.status(pg_instance) == Status.not_running
            assert not await postgresql.is_ready(pg_instance)
        async with running_instance(instance):
            assert await postgresql.status(pg_instance) == Status.running
            assert await postgresql.is_ready(pg_instance)
            async with running_instance(instance):
                assert await postgresql.status(pg_instance) == Status.running
            async with instances.stopped(instance):
                assert await postgresql.status(pg_instance) == Status.not_running
                assert not await postgresql.is_ready(pg_instance)
            assert await postgresql.status(pg_instance) == Status.running
            assert await postgresql.is_ready(pg_instance)
        assert await postgresql.status(pg_instance) == Status.not_running
    assert await postgresql.status(pg_instance) == Status.running
    assert await postgresql.is_ready(pg_instance)


async def test_apply(
    settings: Settings,
    pg_version: PostgreSQLVersion,
    tmp_path: Path,
    instance_factory: InstanceFactory,
    caplog: pytest.LogCaptureFixture,
    ca_cert: Path,
    cert_factory: CertFactory,
) -> None:
    name = "test_apply"
    i_before = system.PostgreSQLInstance(name, pg_version, settings)
    with pytest.raises(exceptions.InstanceNotFound):
        system.check_instance(i_before)
    hostname = socket.gethostname()
    host = socket.gethostbyname(hostname)
    server_cert = cert_factory(host, common_name=hostname)
    im, i = await instance_factory(
        settings,
        name=name,
        settings={
            "unix_socket_directories": str(tmp_path),
            "ssl": True,
            "ssl_cert_file": str(server_cert.path),
            "ssl_key_file": str(server_cert.private_key),
            "ssl_ca_file": str(ca_cert),
            "log_connections": True,
        },
        auth={"hostssl": "cert"},
        restart_on_changes=False,
        roles=[{"name": "bob", "password": "loooooooooong p3w2d!", "login": True}],
        databases=[
            {"name": "db1", "schemas": [{"name": "sales"}]},
            {
                "name": "db2",
                "owner": "bob",
                "extensions": [{"name": "unaccent", "schema": "public"}],
            },
        ],
        pgbackrest={"stanza": "test_apply_stanza"},
    )
    pg_instance = i.postgresql
    assert pg_instance.port == im.port
    pgconfig = pg_instance.configuration()
    assert pgconfig

    system.check_instance(i_before)

    # Re-applying the same manifest is a no-op.
    result_apply = await instances.apply(settings, im)
    assert result_apply.change_state is None

    # Change the runtime state.
    assert await postgresql.status(pg_instance) == Status.not_running
    im = model_copy_validate(im, {"state": "started"})
    result_apply = await instances.apply(settings, im)
    assert result_apply.change_state == "changed"
    assert await postgresql.status(pg_instance) == Status.running
    async with await async_connect(pg_instance) as conn:
        assert not await instances.pending_restart(conn)

    async with postgresql.running(pg_instance, timeout=5):
        assert await databases.exists(pg_instance, "db1")
        db1 = await databases.get(pg_instance, "db1")
        assert db1.schemas[1].name == "sales"
        assert await databases.exists(pg_instance, "db2")
        db2 = await databases.get(pg_instance, "db2")
        assert db2.extensions[0].name == "unaccent"
        assert db2.owner == "bob"

    # Check SSL client connections
    client_cert = cert_factory("127.0.0.1", common_name="bob")
    connargs = {
        "hostaddr": "127.0.0.1",
        "port": pg_instance.port,
        "user": "bob",
        "password": "!!! invalid but unused !!!",
        "dbname": "db2",
        "sslmode": "require",
        "sslrootcert": str(ca_cert),
        "application_name": "pglift-tests-ssl",
    }
    with pytest.raises(
        psycopg.OperationalError, match="connection requires a valid client certificate"
    ):
        psycopg.connect(**connargs)  # type: ignore[arg-type]

    connargs |= {
        "sslmode": "verify-ca",
        "sslcert": str(client_cert.path),
        "sslkey": str(client_cert.private_key),
    }

    expected = [
        "connection authorized: user=bob database=db2 application_name=pglift-tests-ssl SSL enabled",
    ]
    if pg_version >= "14":
        expected.insert(0, 'connection authenticated: identity="CN=bob,OU=Testing cert')
    with psycopg.connect(**connargs) as conn:  # type: ignore[arg-type]
        cur = conn.execute("SHOW ssl")
        assert cur.fetchone() == ("on",)
        logs = []
        try:
            for line in postgresql.logs(pg_instance, timeout=0):
                logs.append(line.rstrip())
        except TimeoutError:
            pass
        for line in logs:
            if expected[0] in line:
                del expected[0]
                if not expected:
                    break
        if expected:
            pytest.fail(f"expected log line(s) {expected} not found in {logs}")

    # Change PostgreSQL settings.
    newconfig = dict(im.settings)
    newconfig["listen_addresses"] = "*"  # requires restart
    newconfig["autovacuum"] = False  # requires reload
    im = model_copy_validate(im, {"settings": newconfig})
    with caplog.at_level(logging.DEBUG, logger="pgflit"):
        result_apply = await instances.apply(settings, im)
        assert result_apply.change_state == "changed"
    assert (
        f"instance {i} needs restart due to parameter changes: listen_addresses"
        in caplog.messages
    )
    assert await postgresql.status(pg_instance) == Status.running
    async with await async_connect(pg_instance) as conn:
        assert await instances.pending_restart(conn)

    # Change runtime state again.
    im = model_copy_validate(im, {"state": "stopped"})
    result_apply = await instances.apply(settings, im)
    assert result_apply.change_state == "changed"
    assert await postgresql.status(pg_instance) == Status.not_running

    # Delete.
    im = model_copy_validate(im, {"state": "absent"})
    assert (await instances.apply(settings, im)).change_state == "dropped"
    with pytest.raises(exceptions.InstanceNotFound):
        system.check_instance(pg_instance)
    with pytest.raises(exceptions.InstanceNotFound):
        system.check_instance(i_before)


async def test_get(
    settings: Settings,
    instance: system.Instance,
    pg_instance: system.PostgreSQLInstance,
    pgbackrest_available: bool,
    powa_available: bool,
) -> None:
    im = await instances.get(instance)
    assert im is not None
    assert im.name == "test"
    config = dict(im.settings)
    assert im.port == pg_instance.port
    assert im.data_directory == pg_instance.datadir  # type: ignore[attr-defined]
    assert im.wal_directory == pg_instance.waldir  # type: ignore[attr-defined]
    # Pop host-dependent values.
    del config["effective_cache_size"]
    del config["shared_buffers"]
    spl = "passwordcheck"
    if powa_available:
        spl += ", pg_qualstats, pg_stat_statements, pg_stat_kcache"
    socket_directory = str(settings.postgresql.socket_directory).format(
        instance=instance
    )
    expected_config = {
        "cluster_name": "test",
        "lc_messages": "C",
        "lc_monetary": "C",
        "lc_numeric": "C",
        "lc_time": "C",
        "log_destination": "stderr",
        "log_directory": str(settings.postgresql.logpath),
        "log_filename": f"{instance.qualname}-%Y-%m-%d_%H%M%S.log",
        "logging_collector": True,
        "shared_preload_libraries": spl,
        "unix_socket_directories": socket_directory,
    }
    if pgbackrest_available:
        del config["archive_command"]
        expected_config["archive_mode"] = True
        expected_config["wal_level"] = "replica"
    assert config == expected_config
    assert im.data_checksums is False
    assert im.state == "started"
    assert not im.pending_restart


@pytest.mark.usefixtures("instance")
async def test_get_from_name_version(
    pg_version: PostgreSQLVersion, settings: Settings
) -> None:
    im = await instances.get(("test", pg_version), settings=settings)
    assert im is not None
    assert im.state == "started"


async def test_ls(settings: Settings, pg_instance: system.PostgreSQLInstance) -> None:
    not_instance_dir = Path(
        str(settings.postgresql.datadir).format(version="12", name="notAnInstanceDir")
    )
    not_instance_dir.mkdir(parents=True)
    try:
        ilist = [i async for i in instances.ls(settings)]

        for i in ilist:
            assert i.status == Status.running.name
            # this also ensure instance name is not notAnInstanceDir
            assert i.name == "test"

        for i in ilist:
            if (i.version, i.name) == (pg_instance.version, pg_instance.name):
                break
        else:
            pytest.fail(f"Instance {pg_instance.version}/{pg_instance.name} not found")

        iv = await instances.ls(settings, version=pg_instance.version).__anext__()
        assert iv == i
    finally:
        not_instance_dir.rmdir()


async def test_server_settings(pg_instance: system.PostgreSQLInstance) -> None:
    async with await async_connect(pg_instance) as conn:
        pgsettings = await instances.settings(conn)
    port = next(p for p in pgsettings if p.name == "port")
    assert port.setting == str(pg_instance.port)
    assert not port.pending_restart
    assert port.context == "postmaster"


async def test_logs(pg_instance: system.PostgreSQLInstance) -> None:
    try:
        for line in postgresql.logs(pg_instance, timeout=0):
            if "database system is ready to accept connections" in line:
                break
        else:
            pytest.fail("expected log line not found")
    except TimeoutError:
        pass


async def test_get_locale(pg_instance: system.PostgreSQLInstance) -> None:
    assert await postgresql.is_running(pg_instance)
    async with await async_connect(pg_instance) as conn:
        assert await instances.get_locale(conn) == "C"


async def test_data_checksums(
    settings: Settings,
    instance_factory: InstanceFactory,
    caplog: pytest.LogCaptureFixture,
) -> None:
    manifest, instance = await instance_factory(settings, "datachecksums")
    pg_instance = instance.postgresql

    async with postgresql.running(pg_instance, timeout=5):
        assert execute(pg_instance, "SHOW data_checksums") == [
            {"data_checksums": "off"}
        ]

    # explicitly enabled
    manifest = model_copy_validate(manifest, {"data_checksums": True})
    with caplog.at_level(logging.INFO, logger="pglift.instances"):
        result_apply = await instances.apply(settings, manifest)
        assert result_apply.change_state == "changed"
    async with postgresql.running(pg_instance, timeout=5):
        assert execute(pg_instance, "SHOW data_checksums") == [{"data_checksums": "on"}]
    assert "enabling data checksums" in caplog.messages
    caplog.clear()

    assert (await instances._get(instance, Status.not_running)).data_checksums

    # not explicitly disabled so still enabled
    result_apply = await instances.apply(
        settings, model_copy_validate(manifest, {"data_checksums": None})
    )
    assert result_apply.change_state is None
    async with postgresql.running(pg_instance, timeout=5):
        assert execute(pg_instance, "SHOW data_checksums") == [{"data_checksums": "on"}]

    # explicitly disabled
    with caplog.at_level(logging.INFO, logger="pglift.instances"):
        result_apply = await instances.apply(
            settings, model_copy_validate(manifest, {"data_checksums": False})
        )
        assert result_apply.change_state == "changed"
    async with postgresql.running(pg_instance, timeout=5):
        assert execute(pg_instance, "SHOW data_checksums") == [
            {"data_checksums": "off"}
        ]
    assert "disabling data checksums" in caplog.messages
    caplog.clear()
    assert (await instances._get(instance, Status.not_running)).data_checksums is False

    # re-enabled with instance running
    async with postgresql.running(pg_instance, timeout=5):
        with pytest.raises(
            exceptions.InstanceStateError,
            match="cannot alter data_checksums on a running instance",
        ):
            await instances.apply(
                settings, model_copy_validate(manifest, {"data_checksums": True})
            )
    assert (await instances._get(instance, Status.not_running)).data_checksums is False


async def test_is_in_recovery(pg_instance: system.PostgreSQLInstance) -> None:
    async with await async_connect(pg_instance) as conn:
        assert not await instances.is_in_recovery(conn)


async def test_wait_recovery_finished(pg_instance: system.PostgreSQLInstance) -> None:
    async with await async_connect(pg_instance) as conn:
        await instances.wait_recovery_finished(conn, timeout=0)

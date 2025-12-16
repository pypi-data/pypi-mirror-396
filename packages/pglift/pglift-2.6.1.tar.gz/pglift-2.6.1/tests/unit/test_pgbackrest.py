# SPDX-FileCopyrightText: 2021 Dalibo
#
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

import configparser
import io
import logging
from collections.abc import AsyncIterator, Awaitable, Callable
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import AsyncMock, patch

import pytest
from pgtoolkit.conf import Configuration, parse

from pglift import exceptions, systemd, ui
from pglift.models import Instance, PostgreSQLInstance, interface
from pglift.pgbackrest import (
    base,
    repo_host_ssh,
    repo_host_tls,
    repo_path,
    site_configure_check,
    site_configure_install,
    site_configure_uninstall,
)
from pglift.pgbackrest.models import Service
from pglift.pgbackrest.models import interface as i
from pglift.settings import PostgreSQLVersion, Settings, _pgbackrest
from pglift.system.command import CommandType
from pglift.systemd import tmpfilesd
from pglift.testutil import model_copy_validate


@pytest.fixture
def pgbackrest_settings(settings: Settings) -> _pgbackrest.Settings:
    assert settings.pgbackrest is not None
    return settings.pgbackrest


@pytest.fixture
async def pgbackrest_site_configure(
    settings: Settings, pgbackrest_settings: _pgbackrest.Settings
) -> AsyncIterator[None]:
    assert not any(site_configure_check(settings, False))
    await site_configure_install(settings)
    assert all(site_configure_check(settings, True))
    assert pgbackrest_settings.logpath.exists()
    assert pgbackrest_settings.spoolpath.exists()
    yield
    await site_configure_uninstall(settings)
    assert not pgbackrest_settings.logpath.exists()
    assert not pgbackrest_settings.lockpath.exists()


@pytest.mark.usefixtures("pgbackrest_site_configure")
@pytest.mark.anyio
async def test_site_configure_base() -> None:
    # Assertions in pgbackrest_site_configure fixture already.
    pass


@pytest.mark.usefixtures("pgbackrest_site_configure")
@pytest.mark.anyio
async def test_site_configure_repo_path(
    settings: Settings, pgbackrest_settings: _pgbackrest.Settings
) -> None:
    assert isinstance(pgbackrest_settings.repository, _pgbackrest.PathRepository)
    pgbackrest_conf = pgbackrest_settings.configpath / "pgbackrest.conf"

    assert list(repo_path.site_configure_list(settings)) == [
        pgbackrest_settings.configpath / "conf.d",
        pgbackrest_conf,
        pgbackrest_settings.repository.path,
    ]

    assert not any(repo_path.site_configure_check(settings, False))
    await repo_path.site_configure_install(settings)
    assert all(repo_path.site_configure_check(settings, True))
    assert pgbackrest_conf.exists()
    config = pgbackrest_conf.read_text().splitlines()
    assert f"repo1-path = {pgbackrest_settings.repository.path}" in config
    assert "repo1-retention-full = 2" in config
    assert pgbackrest_settings.repository.path.exists()

    include_dir = pgbackrest_settings.configpath / "conf.d"
    assert include_dir.exists()
    leftover = include_dir / "x.conf"
    leftover.touch()
    await repo_path.site_configure_uninstall(settings)
    assert leftover.exists() and include_dir.exists()
    assert pgbackrest_settings.configpath.exists()

    leftover.unlink()

    await repo_path.site_configure_uninstall(settings)
    assert not include_dir.exists()
    assert pgbackrest_settings.repository.path.exists()
    assert not (pgbackrest_settings.configpath / "pgbackrest.conf").exists()

    class YesUI(ui.UserInterface):
        def confirm(self, message: str, default: bool) -> bool:  # noqa: ARG002
            return True

    token = ui.set(YesUI())
    try:
        await repo_path.site_configure_uninstall(settings)
    finally:
        ui.reset(token)
    assert not pgbackrest_settings.repository.path.exists()


def test_setup_stanza(
    tmp_path: Path, pgbackrest_settings: _pgbackrest.Settings
) -> None:
    stanza_path1 = tmp_path / "1.conf"
    datadir1 = tmp_path / "pgdata1"
    service1 = Service(stanza="unittests", datadir=datadir1, path=stanza_path1)
    conf = Configuration()
    with pytest.raises(exceptions.SystemError, match="Missing base config file"):
        base.setup_stanza(service1, pgbackrest_settings, conf, {}, True, "backup")

    pgbackrest_settings.logpath.mkdir(parents=True)
    logfile = pgbackrest_settings.logpath / "unittests-123.log"
    logfile.touch()

    baseconfig = base.base_configpath(pgbackrest_settings)
    baseconfig.parent.mkdir(parents=True)
    baseconfig.touch()
    base.setup_stanza(service1, pgbackrest_settings, conf, {}, True, "backup")

    datadir2 = tmp_path / "pgdata2"
    service2 = Service(stanza="unittests", datadir=datadir2, path=stanza_path1, index=2)
    base.setup_stanza(
        service2,
        pgbackrest_settings,
        parse(io.StringIO("port=5433\nunix_socket_directories=/tmp\n")),
        {},
        True,
        "backuper",
    )
    assert stanza_path1.read_text().rstrip() == (
        "[unittests]\n"
        f"pg1-path = {datadir1}\n"
        "pg1-port = 5432\n"
        "pg1-user = backup\n"
        f"pg2-path = {datadir2}\n"
        "pg2-port = 5433\n"
        "pg2-user = backuper\n"
        "pg2-socket-path = /tmp"
    )

    stanza_path3 = tmp_path / "3.conf"
    datadir3 = tmp_path / "pgdata3"
    service3 = Service(stanza="unittests2", datadir=datadir3, path=stanza_path3)
    base.setup_stanza(service3, pgbackrest_settings, conf, {}, True, "bckp")
    assert stanza_path3.exists()

    base.revert_setup_stanza(service1, pgbackrest_settings)
    assert stanza_path1.exists()
    assert stanza_path3.exists()
    assert str(datadir1) not in stanza_path1.read_text()
    assert logfile.exists()
    base.revert_setup_stanza(service2, pgbackrest_settings)
    assert not stanza_path1.exists()
    assert not logfile.exists()
    assert stanza_path3.exists()
    base.revert_setup_stanza(service3, pgbackrest_settings)
    assert not stanza_path3.exists()


def test_make_cmd(
    settings: Settings,
    pgbackrest_settings: _pgbackrest.Settings,
    pgbackrest_execpath: Path,
) -> None:
    assert base.make_cmd("42-test", pgbackrest_settings, "stanza-upgrade") == [
        str(pgbackrest_execpath),
        f"--config-path={settings.prefix}/etc/pgbackrest",
        "--log-level-stderr=info",
        "--stanza=42-test",
        "stanza-upgrade",
    ]


@pytest.mark.anyio
async def test_backup_info(
    settings: Settings,
    pgbackrest_settings: _pgbackrest.Settings,
    pgbackrest_execpath: Path,
    tmp_path: Path,
) -> None:
    with patch("pglift.system.cmd.run", autospec=True) as run:
        run.return_value.stdout = "[]"
        assert (
            await base.backup_info(
                Service(
                    stanza="testback",
                    datadir=tmp_path / "pgdata",
                    path=tmp_path / "mystanza.conf",
                ),
                pgbackrest_settings,
                backup_set="foo",
            )
        ) == {}
    run.assert_awaited_once_with(
        [
            str(pgbackrest_execpath),
            f"--config-path={settings.prefix}/etc/pgbackrest",
            "--log-level-stderr=info",
            "--stanza=testback",
            "--set=foo",
            "--output=json",
            "info",
        ],
        check=True,
    )


def test_backup_command(
    instance: Instance,
    settings: Settings,
    pgbackrest_settings: _pgbackrest.Settings,
    pgbackrest_execpath: Path,
) -> None:
    svc = instance.service(Service)
    assert repo_path.backup_command(
        svc, pgbackrest_settings, type="full", backup_standby=True
    ) == [
        str(pgbackrest_execpath),
        f"--config-path={settings.prefix}/etc/pgbackrest",
        "--log-level-stderr=info",
        "--stanza=test-stanza",
        "--type=full",
        "--start-fast",
        "--backup-standby",
        "backup",
    ]


def test_restore_command(
    instance: Instance,
    settings: Settings,
    pgbackrest_settings: _pgbackrest.Settings,
    pgbackrest_execpath: Path,
) -> None:
    svc = instance.service(Service)
    with pytest.raises(exceptions.UnsupportedError):
        base.restore_command(
            svc, pgbackrest_settings, date=datetime.now(), backup_set="sunset"
        )

    assert base.restore_command(svc, pgbackrest_settings) == [
        str(pgbackrest_execpath),
        f"--config-path={settings.prefix}/etc/pgbackrest",
        "--log-level-stderr=info",
        "--stanza=test-stanza",
        "--delta",
        "--link-all",
        "restore",
    ]

    assert base.restore_command(
        svc,
        pgbackrest_settings,
        date=datetime(2003, 1, 1).replace(tzinfo=timezone.utc),
    ) == [
        str(pgbackrest_execpath),
        f"--config-path={settings.prefix}/etc/pgbackrest",
        "--log-level-stderr=info",
        "--stanza=test-stanza",
        "--delta",
        "--link-all",
        "--target-action=promote",
        "--type=time",
        "--target=2003-01-01 00:00:00.000000+0000",
        "restore",
    ]

    assert base.restore_command(
        svc,
        pgbackrest_settings,
        backup_set="x",
    ) == [
        str(pgbackrest_execpath),
        f"--config-path={settings.prefix}/etc/pgbackrest",
        "--log-level-stderr=info",
        "--stanza=test-stanza",
        "--delta",
        "--link-all",
        "--target-action=promote",
        "--type=immediate",
        "--set=x",
        "restore",
    ]


@pytest.mark.anyio
@pytest.mark.parametrize(
    ("op", "fn"), (["start", base.start], ["stop", base.stop]), ids=["start", "stop"]
)
async def test_commands(
    pgbackrest_execpath: Path,
    pgbackrest_settings: _pgbackrest.Settings,
    op: str,
    fn: Callable[..., Awaitable[None]],
) -> None:
    cmd = AsyncMock(CommandType)
    await fn("my", pgbackrest_settings, cmd=cmd)
    ((args, kwargs),) = cmd.run.await_args_list
    assert args == (
        [
            str(pgbackrest_execpath),
            f"--config-path={pgbackrest_settings.configpath}",
            "--log-level-stderr=info",
            "--stanza=my",
            op,
        ],
    ) and kwargs == {"check": True}


@pytest.mark.anyio
async def test_standby_restore(
    pgbackrest_settings: _pgbackrest.Settings, standby_instance: Instance
) -> None:
    with pytest.raises(
        exceptions.InstanceReadOnlyError,
        match=f"^{standby_instance.postgresql.version}/standby is a read-only standby",
    ):
        await base.restore(standby_instance, pgbackrest_settings)


def test_stanza_pgpaths(tmp_path: Path) -> None:
    p = tmp_path / "st.conf"
    p.write_text("\n".join(["[s]", "pg1-path = a", "pg3-path = b"]))
    assert list(base.stanza_pgpaths(p, "s")) == [(1, Path("a")), (3, Path("b"))]


@pytest.mark.usefixtures("instance")
def test_get_service(
    pg_version: PostgreSQLVersion,
    settings: Settings,
    pg_instance: PostgreSQLInstance,
    instance_manifest: interface.Instance,
    pgbackrest_settings: _pgbackrest.Settings,
) -> None:
    manifest = instance_manifest.service(i.Service)
    # Plain system_lookup().
    s = base.get_service(pg_instance, manifest, pgbackrest_settings, None)

    # Upgrade.
    upgrade_s = base.get_service(
        pg_instance,
        manifest,
        pgbackrest_settings,
        interface.PostgreSQLInstanceRef(
            name=pg_instance.name,
            version=pg_instance.version,
            port=pg_instance.port,
            datadir=pg_instance.datadir,
        ),
    )
    assert upgrade_s == s

    # Creation/update, with stanza from manifest mismatching.
    m = model_copy_validate(manifest, manifest.model_dump() | {"stanza": "svc"})
    with pytest.raises(
        exceptions.InstanceStateError,
        match=f"instance {pg_instance} is already bound to pgbackrest stanza 'test-stanza'",
    ):
        base.get_service(pg_instance, m, pgbackrest_settings, None)

    # Creation, same stanza, index is guessed (next one).
    instance2 = PostgreSQLInstance("samestanza", pg_version, settings)
    m = model_copy_validate(manifest, manifest.model_dump() | {"stanza": s.stanza})
    assert base.get_service(instance2, m, pgbackrest_settings, None) == Service(
        stanza=s.stanza, path=s.path, datadir=instance2.datadir, index=2
    )

    # Another instance, index retrieved from already available configuration.
    with s.path.open("a") as f:
        f.write(f"\npg6-path = {instance2.datadir}\n")
    assert base.get_service(instance2, m, pgbackrest_settings, None) == Service(
        stanza=s.stanza, path=s.path, datadir=instance2.datadir, index=6
    )

    # Creation.
    s.path.unlink()
    m = model_copy_validate(manifest, manifest.model_dump() | {"stanza": "sv"})
    assert base.get_service(pg_instance, m, pgbackrest_settings, None).stanza == "sv"


def test_env_for(
    instance: Instance,
    settings: Settings,
    pgbackrest_settings: _pgbackrest.Settings,
) -> None:
    service = instance.service(Service)
    assert base.env_for(service, pgbackrest_settings) == {
        "PGBACKREST_CONFIG_PATH": f"{settings.prefix}/etc/pgbackrest",
        "PGBACKREST_STANZA": "test-stanza",
    }


def test_system_lookup(
    pgbackrest_settings: _pgbackrest.Settings, instance: Instance
) -> None:
    pg_instance = instance.postgresql
    stanza_config = (
        base.config_directory(pgbackrest_settings) / f"{instance.name}-stanza.conf"
    )

    stanza_config.write_text("\nempty\n")
    with pytest.raises(configparser.MissingSectionHeaderError):
        base.system_lookup(pg_instance.datadir, pgbackrest_settings)

    stanza_config.write_text("\n[asection]\n")
    assert base.system_lookup(pg_instance.datadir, pgbackrest_settings) is None

    other_config = stanza_config.parent / "aaa.conf"
    other_config.write_text(f"[mystanza]\npg42-path = {pg_instance.datadir}\n")
    s = base.system_lookup(pg_instance.datadir, pgbackrest_settings)
    assert s is not None and s.path == other_config and s.index == 42
    other_config.unlink()

    stanza_config.write_text(f"[mystanza]\npg1-path = {pg_instance.datadir}\n")
    s = base.system_lookup(pg_instance.datadir, pgbackrest_settings)
    assert s is not None and s.stanza == "mystanza" and s.index == 1


def test_system_lookup_not_found(
    caplog: pytest.LogCaptureFixture,
    tmp_path: Path,
    pgbackrest_settings: _pgbackrest.Settings,
) -> None:
    with caplog.at_level(logging.DEBUG):
        s = base.system_lookup(tmp_path, pgbackrest_settings)
    assert s is None
    confdir = base.config_directory(pgbackrest_settings)
    assert caplog.messages == [
        f"no pgBackRest configuration file matching PGDATA={tmp_path} found in {confdir}"
    ]


def test_repo_host_tls_base_config(tmp_path: Path, pgbackrest_execpath: Path) -> None:
    ca_file = tmp_path / "ca.crt"
    ca_file.touch()
    crt = tmp_path / "pgbackrest.crt"
    crt.touch()
    key = tmp_path / "pgbackrest.key"
    key.touch(mode=0o600)
    settings = _pgbackrest.Settings.model_validate(
        {
            "execpath": str(pgbackrest_execpath),
            "repository": {
                "mode": "host-tls",
                "host": "backup-srv",
                "host_port": 8433,
                "host_config": "/conf/pgbackrest.conf",
                "cn": "pghost",
                "certificate": {"ca_cert": ca_file, "cert": crt, "key": key},
            },
        }
    )
    cp = repo_host_tls.base_config(settings)
    s = io.StringIO()
    cp.write(s)
    assert s.getvalue().strip().splitlines() == [
        "[global]",
        "lock-path = pgbackrest/lock",
        "log-path = pgbackrest",
        "spool-path = pgbackrest/spool",
        "repo1-host-type = tls",
        "repo1-host = backup-srv",
        "repo1-host-port = 8433",
        "repo1-host-config = /conf/pgbackrest.conf",
        f"repo1-host-ca-file = {ca_file}",
        f"repo1-host-cert-file = {crt}",
        f"repo1-host-key-file = {key}",
    ]
    cp = repo_host_tls.server_config_from_template(settings)
    s = io.StringIO()
    cp.write(s)
    assert s.getvalue().strip().splitlines() == [
        "[global]",
        "lock-path = pgbackrest/lock",
        "log-path = pgbackrest",
        "tls-server-address = *",
        "tls-server-auth = pghost=*",
        f"tls-server-ca-file = {ca_file}",
        f"tls-server-cert-file = {crt}",
        f"tls-server-key-file = {key}",
        "tls-server-port = 8432",
    ]


def test_repo_host_tls_systemd_units() -> None:
    assert repo_host_tls.systemd_units() == ["pglift-pgbackrest.service"]


def test_repo_host_tls_systemd_unit_templates(
    settings: Settings,
    pgbackrest_settings: _pgbackrest.Settings,
    pgbackrest_execpath: Path,
) -> None:
    ((name, content),) = list(repo_host_tls.systemd_unit_templates(settings=settings))
    assert name == "pglift-pgbackrest.service"
    lines = content.splitlines()
    configpath = repo_host_tls.server_configpath(pgbackrest_settings)
    assert f"ExecStart={pgbackrest_execpath} server --config={configpath}" in lines
    assert f'Environment="PGPASSFILE={settings.postgresql.auth.passfile}"' in lines


def test_install_systemd_tmpfiles_template(
    settings: Settings, tlshostrepo_settings: _pgbackrest.Settings
) -> None:
    assert settings.pgbackrest
    repo = tlshostrepo_settings.model_dump()
    repo["repository"]["pid_file"] = settings.run_prefix / "fake_pgbackrest/pgb.pid"
    s = model_copy_validate(settings, {"pgbackrest": repo})
    ((name, managed_dir),) = list(repo_host_tls.systemd_tmpfilesd_managed_dir(s))
    assert name == "pgbackrest"
    assert managed_dir == s.run_prefix / "fake_pgbackrest"
    content = systemd.template("pglift-tmpfiles.d.conf").format(path=managed_dir)
    assert content == f"d   {s.run_prefix}/fake_pgbackrest  0750    -   -   -\n"


def test_manage_systemd_tmpfiles_conf(
    settings: Settings, tlshostrepo_settings: _pgbackrest.Settings
) -> None:
    assert settings.systemd
    pgbackrest_conf = settings.systemd.tmpfilesd_conf_path / "pglift-pgbackrest.conf"
    repo = tlshostrepo_settings.model_dump()
    repo["repository"]["pid_file"] = settings.run_prefix / "fake_pgbackrest" / "pgb.pid"
    s = model_copy_validate(settings, {"pgbackrest": repo})
    assert pgbackrest_conf in list(tmpfilesd.site_configure_list(s))
    repo["repository"]["pid_file"] = Path("/fake_pgbackrest/pgb.pid")
    s = model_copy_validate(settings, {"pgbackrest": repo})
    assert pgbackrest_conf not in list(tmpfilesd.site_configure_list(s))


@pytest.fixture
def tlshostrepo_settings(
    pgbackrest_settings: _pgbackrest.Settings, tmp_path: Path
) -> _pgbackrest.Settings:
    ca_cert = tmp_path / "ca.crt"
    ca_cert.touch()
    cert = tmp_path / "cert.crt"
    cert.touch()
    key = tmp_path / "key.crt"
    key.touch()
    return model_copy_validate(
        pgbackrest_settings,
        {
            "repository": _pgbackrest.TLSHostRepository(
                mode="host-tls",
                host="test.srv",
                host_port=9090,
                cn="test",
                certificate=_pgbackrest.PgBackRestServerCert(
                    ca_cert=ca_cert, key=key, cert=cert
                ),
            ),
        },
    )


def test_repo_host_tls_server(tlshostrepo_settings: _pgbackrest.Settings) -> None:
    srv = repo_host_tls.Server(tlshostrepo_settings)
    configpath = repo_host_tls.server_configpath(tlshostrepo_settings)
    configpath.parent.mkdir(parents=True, exist_ok=True)
    configpath.touch()
    logfile = srv.logfile()
    assert logfile is None

    configpath.write_text("\n".join(["[global]", "log-path = /var/log/pgbackrest-srv"]))
    cp = repo_host_tls.server_config(tlshostrepo_settings)
    assert cp.get("global", "log-path") == "/var/log/pgbackrest-srv"

    logfile = srv.logfile()
    assert (
        logfile is not None and str(logfile) == "/var/log/pgbackrest-srv/all-server.log"
    )


def test_repo_host_ssh_base_config(tmp_path: Path, pgbackrest_execpath: Path) -> None:
    ca_file = tmp_path / "ca.crt"
    ca_file.touch()
    crt = tmp_path / "pgbackrest.crt"
    crt.touch()
    key = tmp_path / "pgbackrest.key"
    key.touch(mode=0o600)
    settings = _pgbackrest.Settings.model_validate(
        {
            "execpath": str(pgbackrest_execpath),
            "repository": {
                "mode": "host-ssh",
                "host": "backup-srv",
                "host_port": 2222,
                "host_config": "/conf/pgbackrest.conf",
            },
        }
    )
    cp = repo_host_ssh.base_config(settings)
    s = io.StringIO()
    cp.write(s)
    assert s.getvalue().strip().splitlines() == [
        "[global]",
        "lock-path = pgbackrest/lock",
        "log-path = pgbackrest",
        "spool-path = pgbackrest/spool",
        "repo1-host-type = ssh",
        "repo1-host = backup-srv",
        "repo1-host-port = 2222",
        "repo1-host-config = /conf/pgbackrest.conf",
    ]

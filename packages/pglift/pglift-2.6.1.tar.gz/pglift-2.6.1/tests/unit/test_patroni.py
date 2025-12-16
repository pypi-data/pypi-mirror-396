# SPDX-FileCopyrightText: 2021 Dalibo
#
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

import difflib
import io
import json
import logging
import socket
from collections.abc import Iterator
from dataclasses import dataclass
from pathlib import Path
from typing import IO, Any
from unittest.mock import AsyncMock, patch

import pgtoolkit.conf as pgconf
import pydantic
import pytest
import yaml
from pgtoolkit.hba import parse as parse_hba
from pluggy import PluginManager

from pglift import (
    exceptions,
    h,
    hba,
    hooks,
    instances,
    manager,
    postgresql,
    systemd,
    types,
)
from pglift import patroni as patroni_mod
from pglift.models import interface, system
from pglift.patroni import (
    dcs,
    impl,
    instance_env,
    models,
    systemd_tmpfilesd_managed_dir,
    systemd_unit_templates,
    systemd_units,
)
from pglift.patroni.models import Patroni, build
from pglift.patroni.models import interface as i
from pglift.postgresql.models import Initdb
from pglift.settings import PostgreSQLVersion, Settings, _patroni
from pglift.systemd import tmpfilesd
from pglift.testutil import model_copy_validate


@pytest.fixture
def patroni_settings(settings: Settings) -> _patroni.Settings:
    assert settings.patroni
    return settings.patroni


@pytest.fixture(autouse=True)
def _tmp_path_in_yaml(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> Iterator[None]:
    """Monkeypatch yaml module used to load/dump Patroni configuration file in
    "build" module to avoid tmp paths to be inserted.
    """

    @dataclass
    class Yaml:
        prefix: Path

        def safe_load(self, fobj: IO[str]) -> Any:
            f = io.StringIO(fobj.read().replace("$PREFIX", str(self.prefix)))
            return yaml.safe_load(f)

        def dump(self, data: Any, **kwargs: Any) -> str:
            return yaml.dump(data, **kwargs).replace(str(self.prefix), "$PREFIX")  # type: ignore[no-any-return]

    monkeypatch.setattr(build, "yaml", Yaml(tmp_path))
    yield


@pytest.fixture(
    params=[
        "14",
        "17",  # custom postgresql.conf template
    ]
)
def pg_version(request: pytest.FixtureRequest) -> PostgreSQLVersion:
    return request.param  # type: ignore[no-any-return]


@pytest.fixture
def instance_manifest(
    composite_instance_model: type[interface.Instance],
    pg_version: PostgreSQLVersion,
    tmp_path: Path,
) -> interface.Instance:
    certdir = tmp_path / "certs"
    certdir.mkdir()
    repl_cert = certdir / "repl.pem"
    repl_cert.touch()
    repl_key = certdir / "repl.key"
    repl_key.touch()
    return composite_instance_model.model_validate(
        {
            "name": "test",
            "version": pg_version,
            "data_checksums": True,
            "settings": {
                "shared_buffers": "257MB",
                "effective_cache_size": "4 GB",
                "unix_socket_directories": "/tmp/tests",
                "log_connections": "on",
                "log_directory": "/tmp/log",
                "log_filename": "patgres-%Y-%m-%d.log",
                "log_disconnections": "false",
                "log_checkpoints": True,
                "log_min_duration_statement": "3s",
                "shared_preload_libraries": "passwordcheck",
            },
            "surole_password": None,
            "replrole_password": "rrr",
            "patroni": {
                "cluster": "whatever",
                "postgresql": {
                    "connect_host": "pghost.test",
                    "replication": {
                        "ssl": {
                            "cert": repl_cert,
                            "key": repl_key,
                            "password": "repsslpwd",
                        }
                    },
                },
            },
            "pgbackrest": {"stanza": "test-stanza"},
        }
    )


@pytest.fixture
def instance(
    pg_version: PostgreSQLVersion,
    expected_dir: Path,
    patroni_settings: _patroni.Settings,
    instance: system.Instance,
) -> system.Instance:
    patroni_config = impl._configpath(instance.qualname, patroni_settings)
    patroni_config.parent.mkdir(parents=True, exist_ok=True)
    patroni_config.write_text((expected_dir / f"patroni-{pg_version}.yaml").read_text())
    if pg_version == "14":
        with (instance.postgresql.datadir / "patroni.dynamic.json").open("w") as f:
            json.dump({"test": True}, f)
    build.pgpass(instance.qualname, patroni_settings.postgresql).write_text("# test\n")
    patroni = models.patroni(instance.qualname, patroni_settings)
    assert patroni is not None
    svc = models.service(instance.qualname, patroni, patroni_settings)
    instance.services.append(svc)
    return instance


@pytest.fixture
def mock_api_request() -> Iterator[AsyncMock]:
    with patch("pglift.patroni.impl.api_request", autospec=True) as p:
        yield p


def test_servicemanifest_defaults() -> None:
    s = i.Service(cluster="cluster", node=None, restapi=None)
    assert s.node == socket.getfqdn()
    assert set(s.restapi.model_dump()) == {
        "authentication",
        "connect_address",
        "listen",
    }


def test_available(settings: Settings) -> None:
    assert impl.available(settings)


def test_systemd_units() -> None:
    assert systemd_units() == ["pglift-patroni@.service"]


def test_systemd_unit_templates(
    settings: Settings, patroni_execpaths: tuple[Path, Path]
) -> None:
    patroni_execpath = patroni_execpaths[0]
    ((name, content),) = list(systemd_unit_templates(settings=settings))
    assert name == "pglift-patroni@.service"
    assert (
        f"ExecStart={patroni_execpath} {settings.prefix}/etc/patroni/%i.yaml" in content
    )


def test_install_systemd_tmpfiles_template(settings: Settings) -> None:
    ((name, managed_dir),) = list(systemd_tmpfilesd_managed_dir(settings))
    assert name == "patroni"
    assert managed_dir == settings.run_prefix / "patroni"
    content = systemd.template("pglift-tmpfiles.d.conf").format(path=managed_dir)
    assert content == f"d   {settings.run_prefix}/patroni  0750    -   -   -\n"


def test_manage_systemd_tmpfiles_conf(settings: Settings) -> None:
    assert settings.patroni
    assert settings.systemd
    patroni_conf = settings.systemd.tmpfilesd_conf_path / "pglift-patroni.conf"
    patroni_s = settings.patroni.model_dump()
    patroni_s["pid_file"] = settings.run_prefix / "{name}" / "patroni" / "pid_file"
    s = model_copy_validate(settings, {"patroni": patroni_s})
    assert patroni_conf in list(tmpfilesd.site_configure_list(s))
    patroni_s["pid_file"] = "/{name}/patroni/pid_file"
    s = model_copy_validate(settings, {"patroni": patroni_s})
    assert patroni_conf not in list(tmpfilesd.site_configure_list(s))


def test_patroni_incompatible_with_standby(
    composite_instance_model: type[interface.Instance],
) -> None:
    with pytest.raises(
        pydantic.ValidationError,
        match="'patroni' and 'standby' fields are mutually exclusive",
    ):
        composite_instance_model.model_validate(
            {
                "name": "invalid",
                "standby": {"primary_conninfo": "port=5444"},
                "patroni": {"cluster": "tests"},
            }
        )


def test_patroni_extra_allow() -> None:
    p = Patroni.model_validate(
        {
            "scope": "foo",
            "name": "bar",
            "log": {"file_num": 5},
            "postgresql": {
                "connect_address": "db.host:4378",
                "listen": "122.78.9.6:5433",
                "parameters": {"log_connections": True},
                "pg_hba": [],
                "callbacks": {"on_reload": "/my/scripts/reload.sh"},
            },
            "restapi": {
                "connect_address": "api.server:8088",
                "listen": "122.76.9.1:8808",
                "http_extra_headers": {"X-Frame-Options": "SAMEORIGIN"},
            },
            "tags": {"nosync": True},
        }
    ).model_dump()
    assert p == {
        "scope": "foo",
        "name": "bar",
        "log": {"dir": None, "file_num": 5},
        "restapi": {
            "authentication": None,
            "connect_address": "api.server:8088",
            "listen": "122.76.9.1:8808",
            "cafile": None,
            "certfile": None,
            "keyfile": None,
            "verify_client": None,
            "http_extra_headers": {"X-Frame-Options": "SAMEORIGIN"},
        },
        "postgresql": {
            "basebackup": None,
            "connect_address": "db.host:4378",
            "create_replica_methods": None,
            "listen": "122.78.9.6:5433",
            "parameters": {"log_connections": True},
            "pg_hba": [],
            "pgpass": None,
            "callbacks": {"on_reload": "/my/scripts/reload.sh"},
        },
        "tags": {"nosync": True},
    }


def test_servicemanifest_extra_forbid() -> None:
    with pytest.raises(pydantic.ValidationError) as excinfo:
        i.Service.model_validate(
            {
                "cluster": "foo",
                "node": "bar",
                "postgresql": {
                    "connect_host": "db.host:4378",
                    "listen": "122.78.9.6:5433",
                    "parameters": {"log_connections": True},
                },
                "restapi": {
                    "connect_address": "api.server:8088",
                    "listen": "122.76.9.1:8808",
                    "http_extra_headers": {"X-Frame-Options": "SAMEORIGIN"},
                },
                "tags": {"nosync": True},
            }
        )
    assert [{"loc": e["loc"], "msg": e["msg"]} for e in excinfo.value.errors()] == [
        {
            "loc": ("restapi", "http_extra_headers"),
            "msg": "Extra inputs are not permitted",
        },
        {
            "loc": ("postgresql", "listen"),
            "msg": "Extra inputs are not permitted",
        },
        {
            "loc": ("postgresql", "parameters"),
            "msg": "Extra inputs are not permitted",
        },
        {
            "loc": ("tags",),
            "msg": "Extra inputs are not permitted",
        },
    ]


def test_servicemanifest_standalone_convert(
    instance_manifest: interface.Instance,
) -> None:
    """Fields in Service class are read-only for "update" operation involving
    an "instance" in context, i.e. the "standalone convert" case.
    """
    # Instance in context already has 'patroni' set up; cannot change its
    # "cluster" field.
    obj = instance_manifest.service(i.Service).model_dump()
    with (
        pytest.raises(pydantic.ValidationError) as excinfo,
        types.validation_context(operation="update", instance=instance_manifest),
    ):
        i.Service.model_validate(
            obj | {"cluster": "somethingelse"},
        )
    assert [{"loc": e["loc"], "msg": e["msg"]} for e in excinfo.value.errors()] == [
        {"loc": ("cluster",), "msg": "Value error, field is read-only"}
    ]

    # Not changing the "cluster" field is okay.
    with types.validation_context(operation="update", instance=instance_manifest):
        svc = i.Service.model_validate(
            obj | {"cluster": "whatever"},
        )
    assert svc.cluster == "whatever"

    # If Instance in context has no 'patroni' service set up (it's a
    # standalone being converted as a Patroni member), the field can be set.
    m = model_copy_validate(instance_manifest, {"patroni": None})
    with types.validation_context(operation="update", instance=m):
        svc = i.Service.model_validate(
            obj | {"cluster": "newvalue"},
        )
    assert svc.cluster == "newvalue"


@pytest.fixture
def patroni(
    tmp_path: Path,
    settings: Settings,
    patroni_settings: _patroni.Settings,
    pg_instance: system.PostgreSQLInstance,
    instance_manifest: interface.Instance,
) -> Patroni:
    m = model_copy_validate(
        instance_manifest,
        {
            "data_checksums": True,
            "surole_password": None,
            "replrole_password": "rrr",
        },
    )
    configuration = postgresql.configuration(instance_manifest, settings)
    ssl_path = tmp_path / "ssl"
    ssl_path.mkdir()
    cacert = ssl_path / "cacert.pem"
    cacert.touch()
    cert = ssl_path / "host.pem"
    cert.touch()
    key = ssl_path / "host.key"
    key.touch()

    postgresql_svc = m.service(i.Service).postgresql
    assert postgresql_svc is not None and postgresql_svc.connect_host
    parameters = build.parameters_managed(configuration, {})
    postgresql_model = build.postgresql(
        pg_instance, m, configuration, postgresql_svc, parameters
    )
    log = (
        build.Log(
            dir=tmp_path / "log" / "patroni",
            format="%(levelname)-8s: %(message)s",
        )
        if pg_instance.version == "17"
        else None
    )
    p = Patroni(
        scope="test-scope",
        name="pg1",
        log=log,
        bootstrap=build.bootstrap(
            patroni_settings,
            postgresql.initdb_options(instance_manifest, settings.postgresql),
        ),
        etcd3=(
            patroni_settings.etcd.model_dump(exclude={"version"})
            | {
                "protocol": "https",
                "cacert": "/path/to/cacert.pem",
                "cert": "/path/to/host.pem",
                "key": "/path/to/host.key",
                "username": "etcduser",
                "password": "etcdP4zw0rd",
            }
        ),
        postgresql=postgresql_model,
        watchdog={
            "mode": "required",
            "device": "/dev/watchdog",
            "safety_margin": 5,
        },
        restapi={
            "connect_address": "localhost:8080",
            "cafile": cacert,
            "certfile": cert,
            "keyfile": key,
            "verify_client": "optional",
            "authentication": {
                "username": "patroniuser",
                "password": "P4zw0rd",
            },
        },
        ctl={
            "certfile": "/path/to/host.pem",
            "keyfile": "/path/to/host.key",
        },
    )
    return p


@pytest.mark.anyio
async def test_patroni_str(patroni: Patroni) -> None:
    assert str(patroni) == "Patroni node 'pg1' (scope='test-scope')"


@pytest.fixture
async def svc(patroni: Patroni, patroni_settings: _patroni.Settings) -> models.Service:
    return models.service("test", patroni, patroni_settings)


@pytest.mark.anyio
async def test_service_cluster(svc: models.Service) -> None:
    assert svc.cluster == "test-scope"


@pytest.mark.anyio
async def test_service_node(svc: models.Service) -> None:
    assert svc.node == "pg1"


@pytest.mark.anyio
async def test_service_logfile(svc: models.Service) -> None:
    logfile = svc.logfile()
    assert logfile is not None and logfile.name == "patroni.log"


@pytest.mark.anyio
async def test_yaml(
    pg_version: PostgreSQLVersion,
    patroni: Patroni,
    expected_dir: Path,
    write_changes: bool,
) -> None:
    doc = patroni.yaml()
    fpath = expected_dir / f"patroni-{pg_version}.yaml"
    if write_changes:
        fpath.write_text(doc)

    expected = fpath.read_text()
    assert doc == expected


@pytest.mark.anyio
async def test_validate_config(
    patroni: Patroni,
    patroni_settings: _patroni.Settings,
    caplog: pytest.LogCaptureFixture,
) -> None:
    excepted_msg = "invalid Patroni configuration: test test test"
    with caplog.at_level(logging.WARNING):
        patroni_settings_copy = model_copy_validate(
            patroni_settings, {"enforce_config_validation": False}
        )
        impl.validate_config(patroni.yaml(), patroni_settings_copy)
    (msg,) = caplog.messages
    assert msg.strip() == excepted_msg
    with pytest.raises(exceptions.ConfigurationError, match=excepted_msg):
        impl.validate_config(patroni.yaml(), patroni_settings)


@pytest.mark.anyio
async def test_maybe_backup_config(
    instance: system.Instance,
    patroni_settings: _patroni.Settings,
    caplog: pytest.LogCaptureFixture,
) -> None:
    svc = instance.service(models.Service)
    members = [
        i.ClusterMember(host="h", name=svc.node, port=8097, role="leader", state="s")
    ]
    with (
        patch.object(
            impl, "check_api_status", return_value=True, autospec=True
        ) as check_api_status,
        patch.object(
            impl, "cluster_members", return_value=members, autospec=True
        ) as cluster_members,
        caplog.at_level("WARNING", logger="pglift.patroni"),
    ):
        # test with only one node, and fake API "up&running"
        await impl.maybe_backup_config(svc)
        cluster_members.assert_awaited_once_with(svc.patroni)
        check_api_status.assert_awaited_once_with(svc.patroni)
        assert caplog.messages[0].startswith(
            f"{svc.node!r} appears to be the last member of cluster {svc.cluster!r}, saving Patroni configuration file"
        )

        # test with two node and API "up&running"
        members.append(
            i.ClusterMember(
                host="b", name="node1987", port=1987, role="leader", state="s"
            )
        )
        caplog.clear()
        cluster_members.return_value = members
        await impl.maybe_backup_config(svc)
        assert not caplog.messages  # no backup, no message

        # test with only one node, and fake API "down"
        caplog.clear()
        check_api_status.reset_mock()
        check_api_status.return_value = False
        await impl.maybe_backup_config(svc)
        check_api_status.assert_awaited_once_with(svc.patroni)
        assert caplog.messages[0].startswith("saving Patroni configuration file")

    prefix = f"{svc.cluster}-{svc.node}"
    backuppath = next(patroni_settings.configpath.parent.glob(f"{prefix}*.yaml"))
    backupconfig = yaml.safe_load(backuppath.read_text())
    assert backupconfig["etcd3"] == {
        "cacert": "/path/to/cacert.pem",
        "cert": "/path/to/host.pem",
        "hosts": ["etcd1:123", "etcd2:456"],
        "key": "/path/to/host.key",
        "protocol": "https",
        "username": "etcduser",
        "password": "etcdP4zw0rd",
    }
    assert backupconfig["restapi"] == {
        "connect_address": "localhost:8080",
        "cafile": "$PREFIX/ssl/cacert.pem",
        "certfile": "$PREFIX/ssl/host.pem",
        "keyfile": "$PREFIX/ssl/host.key",
        "listen": "localhost:8080",
        "verify_client": "optional",
        "authentication": {"password": "P4zw0rd", "username": "patroniuser"},
    }
    assert backupconfig["ctl"] == {
        "certfile": "/path/to/host.pem",
        "keyfile": "/path/to/host.key",
    }
    pgpass = next(patroni_settings.configpath.parent.glob(f"{prefix}*.pgpass"))
    assert pgpass.read_text() == "# test\n"


@pytest.mark.usefixtures("instance")
def test_postgresql_service_name(
    pm: PluginManager, pg_instance: system.PostgreSQLInstance
) -> None:
    assert hooks(pm, h.postgresql_service_name, instance=pg_instance) == [
        "patroni",
        "postgresql",
    ]


@pytest.mark.usefixtures("instance")
@pytest.mark.anyio
async def test_postgresql_editable_conf(
    pg_version: PostgreSQLVersion, pg_instance: system.PostgreSQLInstance
) -> None:
    with manager.configuration.use(patroni_mod):
        editable_conf = await instances.postgresql_editable_conf(pg_instance)
    assert [c.strip() for c in editable_conf.lines] == [
        "archive_command = 'pgbackrest --config-path=/cfg/pgbackrest --stanza=test-stanza --pg1-path=/pg/data archive-push %p'",
        "archive_mode = on",
        "effective_cache_size = '4 GB'",
        "lc_messages = 'C'",
        "lc_monetary = 'C'",
        "lc_numeric = 'C'",
        "lc_time = 'C'",
        "log_checkpoints = on",
        "log_connections = on",
        "log_destination = 'syslog'",
        "log_directory = '/tmp/log'",
        "log_disconnections = off",
        "log_filename = 'patgres-%Y-%m-%d.log'",
        "log_min_duration_statement = '3s'",
        "logging_collector = on",
        "shared_buffers = '257MB'",
        "shared_preload_libraries = 'passwordcheck, pg_qualstats, pg_stat_statements, pg_stat_kcache'",
        f"syslog_ident = 'postgresql-{pg_version}-test'",
        "unix_socket_directories = '/tmp/tests'",
        "wal_level = 'replica'",
    ]


@pytest.fixture
def api_not_called() -> Iterator[None]:
    side_effect = AssertionError("unexpectedly called")
    with (
        patch("pglift.patroni.impl.check_api_status", side_effect=side_effect),
        patch("pglift.patroni.impl.reload", side_effect=side_effect),
    ):
        yield


@pytest.fixture
def mock_check_api_status() -> Iterator[AsyncMock]:
    with patch("pglift.patroni.impl.check_api_status", autospec=True) as p:
        yield p


@pytest.fixture
def mock_reload() -> Iterator[AsyncMock]:
    with patch("pglift.patroni.impl.reload", autospec=True) as p:
        yield p


@pytest.mark.usefixtures("instance", "api_not_called")
@pytest.mark.anyio
async def test_configure_postgresql_creating(
    settings: Settings,
    instance_manifest: interface.Instance,
    pg_instance: system.PostgreSQLInstance,
) -> None:
    """When 'creating', the hook returns no changes."""
    m = instance_manifest.model_copy(update={"creating": True})
    pgconfig = postgresql.configuration(instance_manifest, settings)
    changes = await patroni_mod.configure_postgresql(pgconfig, pg_instance, m)
    assert not changes


@pytest.mark.usefixtures("instance")
@pytest.mark.anyio
async def test_configure_postgresql_postgresql_changes_only(
    settings: Settings,
    instance_manifest: interface.Instance,
    pg_instance: system.PostgreSQLInstance,
    mock_check_api_status: AsyncMock,
    mock_reload: AsyncMock,
) -> None:
    """Only PostgreSQL configuration changes."""
    instance_manifest = instance_manifest.model_copy(
        update={"settings": dict(instance_manifest.settings) | {"work_mem": "8MB"}}
    )
    pgconfig = postgresql.configuration(instance_manifest, settings)
    assert not instance_manifest.creating
    changes = await patroni_mod.configure_postgresql(
        pgconfig, pg_instance, instance_manifest
    )
    assert changes == {"work_mem": (None, "8MB")}
    assert mock_check_api_status.await_args
    (args, kw) = mock_check_api_status.await_args
    assert args
    (p,) = args
    assert p.restapi.connect_address == "localhost:8080"
    assert kw == {"logger": None}
    assert mock_reload.await_args
    (args, kw) = mock_reload.await_args
    assert args and not kw
    (p,) = args
    assert p.restapi.connect_address == "localhost:8080"


@pytest.mark.usefixtures("instance")
@pytest.mark.anyio
async def test_configure_postgresql_patroni_changes(
    settings: Settings,
    instance_manifest: interface.Instance,
    pg_instance: system.PostgreSQLInstance,
    mock_check_api_status: AsyncMock,
    mock_reload: AsyncMock,
) -> None:
    """Changes outside PostgreSQL parameters."""
    svc = instance_manifest.service(i.Service)
    assert svc.postgresql
    instance_manifest = model_copy_validate(
        instance_manifest,
        {
            "patroni": model_copy_validate(
                svc,
                {
                    "postgresql": model_copy_validate(
                        svc.postgresql, {"connect_host": "otherhost"}
                    )
                },
            )
        },
    )
    pgconfig = postgresql.configuration(instance_manifest, settings)
    assert not instance_manifest.creating
    changes = await patroni_mod.configure_postgresql(
        pgconfig, pg_instance, instance_manifest
    )
    assert not changes
    assert mock_check_api_status.await_args
    (args, kw) = mock_check_api_status.await_args
    (p,) = args
    assert p.restapi.connect_address == "localhost:8080"
    assert args
    assert kw == {"logger": None}
    assert mock_reload.await_args
    (args, kw) = mock_reload.await_args
    assert args and not kw
    (p,) = args
    assert p.restapi.connect_address == "localhost:8080"


@pytest.mark.usefixtures("instance")
@pytest.mark.anyio
async def test_configure_postgresql_postgresql_port_change(
    settings: Settings,
    instance_manifest: interface.Instance,
    pg_instance: system.PostgreSQLInstance,
    mock_check_api_status: AsyncMock,
    mock_reload: AsyncMock,
) -> None:
    """PostgreSQL port and configuration changes."""
    old_pgconfig = postgresql.configuration(instance_manifest, settings)
    assert old_pgconfig
    oldport = old_pgconfig.as_dict().get("port", 5432)
    instance_manifest = instance_manifest.model_copy(
        update={
            "port": 5876,
            "settings": dict(instance_manifest.settings)
            | {"effective_cache_size": "1GB"},
        }
    )
    pgconfig = postgresql.configuration(instance_manifest, settings)
    changes = await patroni_mod.configure_postgresql(
        pgconfig, pg_instance, instance_manifest
    )
    assert changes == {"effective_cache_size": ("4 GB", "1GB"), "port": (oldport, 5876)}
    assert mock_check_api_status.await_args
    (args, kw) = mock_check_api_status.await_args
    assert args
    (p,) = args
    assert p.restapi.connect_address == "localhost:8080"
    assert kw == {"logger": None}
    assert mock_reload.await_args
    (args, kw) = mock_reload.await_args
    assert args and not kw
    (p,) = args
    assert p.restapi.connect_address == "localhost:8080"


def test_env(
    settings: Settings, instance: system.Instance, pg_version: PostgreSQLVersion
) -> None:
    assert instance_env(instance) == {
        "PATRONICTL_CONFIG_FILE": f"{settings.prefix}/etc/patroni/{pg_version}-test.yaml",
        "PATRONI_NAME": "pg1",
        "PATRONI_SCOPE": "test-scope",
    }


@pytest.mark.anyio
async def test_check_api_status(patroni: Patroni) -> None:
    assert not await impl.check_api_status(patroni)


@pytest.mark.anyio
async def test_promote_postgresql(instance: system.Instance) -> None:
    with pytest.raises(exceptions.UnsupportedError):
        await patroni_mod.promote_postgresql(instance.postgresql)


def unified_diff(before: str, after: str) -> str:
    return "\n".join(
        [
            line.strip()
            for line in difflib.unified_diff(
                before.splitlines(), after.splitlines(), n=0
            )
        ]
    )


@pytest.mark.usefixtures("instance")
def test_update(
    settings: Settings,
    patroni_settings: _patroni.Settings,
    pg_instance: system.PostgreSQLInstance,
    pg_version: PostgreSQLVersion,
    instance_manifest: interface.Instance,
    tmp_path: Path,
    expected_dir: Path,
    write_changes: bool,
) -> None:
    """Configuration is updated with edits preserved"""

    configpath = impl._configpath(pg_instance.qualname, patroni_settings)
    config = yaml.safe_load(configpath.read_text())

    # Override a managed field already in settings
    config["restapi"]["verify_client"] = "required"
    # Add an unmanaged "extra" field.
    config["restapi"]["http_extra_headers"] = "Custom-Header-Name: Custom Header Value"

    # PostgreSQL settings only defined in actual Patroni configuration file
    # are preserved.
    assert "work_mem" not in config["postgresql"]["parameters"]
    config["postgresql"]["parameters"]["work_mem"] = "16MB"
    config["postgresql"]["pgpass"] = "/home/db/pgpass"
    assert "port" not in config["postgresql"]["parameters"]
    with configpath.open("w") as f:
        yaml.safe_dump(config, f)
    certdir = tmp_path / "certs"
    repl_cert = certdir / "repl_new.pem"
    repl_cert.touch()
    repl_key = certdir / "repl_new.key"
    repl_key.touch()
    m = model_copy_validate(instance_manifest, update={"port": 5467})
    configuration = postgresql.configuration(m, settings)
    qualname = pg_instance.qualname
    actual = Patroni.get(pg_instance.qualname, patroni_settings)
    patroni_settings_copy = model_copy_validate(
        patroni_settings, {"enforce_config_validation": False}
    )
    service_manifest = instance_manifest.service(i.Service)
    assert service_manifest.postgresql
    service = model_copy_validate(
        service_manifest,
        update={
            "postgresql": model_copy_validate(
                service_manifest.postgresql,
                update={
                    "replication": {
                        "ssl": {
                            "cert": repl_cert,
                            "key": repl_key,
                            "password": "repsslpwd",
                        }
                    },
                },
            ),
            "restapi": model_copy_validate(
                service_manifest.restapi,
                update={
                    "connect_address": "localhost:9090",
                    "listen": "localhost:9909",
                    "authentication": {
                        "username": "otheruser",
                        "password": "newP4zw0rd",
                    },
                },
            ),
            "etcd": {
                "username": "otheruser",
                "password": "newP4zw0rd",
            },
        },
    )
    parameters = build.parameters_managed(configuration, actual.postgresql.parameters)
    patroni = impl.update(
        actual, service, patroni_settings_copy, configuration, parameters
    )
    impl.write_config(qualname, patroni, patroni_settings_copy, validate=True)
    before = (expected_dir / f"patroni-{pg_version}.yaml").read_text()
    after = patroni.yaml()
    diff = unified_diff(before, after)
    fpath = expected_dir / f"patroni-{pg_version}-updated.diff"
    if write_changes:
        fpath.write_text(diff)
    expected = fpath.read_text()
    assert diff == expected

    p = patroni.model_dump()
    assert p["restapi"]["verify_client"] == "required"
    assert (
        p["restapi"]["http_extra_headers"] == "Custom-Header-Name: Custom Header Value"
    )
    assert patroni.postgresql.parameters
    assert patroni.postgresql.parameters["work_mem"] == "16MB"
    assert patroni.postgresql.listen == "*:5467"
    config = yaml.safe_load(configpath.read_text())
    assert config["postgresql"]["parameters"]["work_mem"] == "16MB"
    assert config["postgresql"]["pgpass"] == "/home/db/pgpass"
    assert "port" not in config["postgresql"]["parameters"]

    # PostgreSQL settings from instance manifest take precedence over those
    # defined in actual Patroni configuration file.
    configuration["work_mem"] = "42kB"
    actual = patroni
    parameters = build.parameters_managed(configuration, actual.postgresql.parameters)
    patroni = impl.update(
        actual, service, patroni_settings_copy, configuration, parameters
    )
    impl.write_config(qualname, patroni, patroni_settings_copy)
    assert patroni.postgresql.parameters
    assert patroni.postgresql.parameters["work_mem"] == "42kB"
    config = yaml.safe_load(configpath.read_text())
    assert config["postgresql"]["parameters"]["work_mem"] == "42kB"


@pytest.mark.usefixtures("instance")
@pytest.mark.anyio
async def test_upgrade(
    settings: Settings,
    patroni_settings: _patroni.Settings,
    pg_version: PostgreSQLVersion,
    pg_instance: system.PostgreSQLInstance,
    instance_manifest: interface.Instance,
    expected_dir: Path,
    write_changes: bool,
    caplog: pytest.LogCaptureFixture,
) -> None:
    old_pgconfig = postgresql.configuration(instance_manifest, settings)
    iref = interface.PostgreSQLInstanceRef(
        name=instance_manifest.name,
        version=instance_manifest.version,
        port=old_pgconfig.get("port", 5432),
        datadir=pg_instance.datadir,
    )
    m = instance_manifest.model_copy(
        update={
            "name": "upgraded",
            "version": pg_version,
            "port": 5454,
            "upgrading_from": iref,
        }
    )
    pgconfig = postgresql.configuration(m, settings)
    svc = model_copy_validate(
        m.service(i.Service), {"cluster": "test-scope", "node": "pg1"}
    )
    actual = Patroni.get(pg_instance.qualname, patroni_settings)
    object.__setattr__(pg_instance, "name", "upgraded")
    new_pg_instance = system.PostgreSQLInstance(
        name="upgraded", version=pg_version, settings=settings
    )
    new_pg_instance.datadir.mkdir(parents=True)
    caplog.clear()
    with caplog.at_level(logging.DEBUG, logger="pglift.patroni"):
        parameters = build.parameters_managed(pgconfig, actual.postgresql.parameters)
        patroni = impl.upgrade(
            new_pg_instance,
            m,
            actual,
            svc.postgresql,
            patroni_settings,
            pgconfig,
            parameters,
        )
        impl.write_config(new_pg_instance.qualname, patroni, patroni_settings)
        before = (expected_dir / f"patroni-{pg_version}.yaml").read_text()
        after = patroni.yaml()
        diff = unified_diff(before, after)
        fpath = expected_dir / f"patroni-{pg_version}-upgraded.diff"
        if write_changes:
            fpath.write_text(diff)
        expected = fpath.read_text()
        assert diff == expected
        assert patroni.postgresql.pgpass and patroni.postgresql.pgpass.exists()
    expected_messages = ["upgrading Patroni service"]
    if pg_version == "17":
        assert actual.log and actual.log.dir
        assert patroni.log and patroni.log.dir
        expected_messages.append(f"creating {patroni.log.dir} directory")
    expected_messages.append(
        f"copying {actual.postgresql.pgpass} to {patroni.postgresql.pgpass}",
    )
    if pg_version == "14":
        expected_messages.append(
            f"copying {pg_instance.datadir / 'patroni.dynamic.json'} to {new_pg_instance.datadir / 'patroni.dynamic.json'}"
        )
    assert caplog.messages == expected_messages


@pytest.mark.anyio
@pytest.mark.usefixtures("instance")
async def test_hba_editable(
    pg_instance: system.PostgreSQLInstance, patroni_settings: _patroni.Settings
) -> None:
    c = impl._configpath(pg_instance.qualname, patroni_settings)
    line = "host    all             all             samehost                trust"
    conf = yaml.safe_load(c.read_text())
    assert line not in conf["postgresql"]["pg_hba"]
    with manager.instance.use(patroni_mod), manager.hba.use(patroni_mod):
        await hba.add(
            pg_instance,
            interface.HbaRecord.model_validate(
                {"connection": {"address": "samehost"}, "method": "trust"}
            ),
        )
    conf = yaml.safe_load(c.read_text())
    assert line in conf["postgresql"]["pg_hba"]
    with manager.instance.use(patroni_mod), manager.hba.use(patroni_mod):
        await hba.remove(
            pg_instance,
            interface.HbaRecord.model_validate(
                {"connection": {"address": "samehost"}, "method": "trust"}
            ),
        )
    conf = yaml.safe_load(c.read_text())
    assert line not in conf["postgresql"]["pg_hba"]


def test_postgresql_managed(caplog: pytest.LogCaptureFixture, tmp_path: Path) -> None:
    f = tmp_path / "cert"
    f.touch()
    conf = pgconf.parse_string(
        "\n".join(
            [
                "port=5678",
                "work_mem=5MB",
                "listen_addresses=123.45.67.89",
                "bgwriter_delay=150ms",
                "max_wal_senders=10",
            ]
        )
    )
    caplog.set_level("WARNING", logger="pglift.patroni")
    parameters = build.parameters_managed(
        conf, {"max_connections": 123, "work_mem": "4MB"}
    )
    assert build.postgresql_managed(
        conf,
        i.PostgreSQL(
            connect_host="pgserver.local",
            replication=i.ClientAuth(ssl=i.ClientSSLOptions(cert=f, key=f)),
            rewind=i.ClientAuth(ssl=i.ClientSSLOptions(cert=f, key=f)),
        ),
        parameters,
    ) == {
        "connect_address": "pgserver.local:5678",
        "listen": "123.45.67.89:5678",
        "parameters": {
            "max_connections": 123,
            "work_mem": "5MB",
            "bgwriter_delay": "150 ms",
            "max_wal_senders": 10,
        },
        "authentication": {
            "replication": {"sslcert": tmp_path / "cert", "sslkey": tmp_path / "cert"},
            "rewind": {"sslcert": tmp_path / "cert", "sslkey": tmp_path / "cert"},
        },
    }
    assert caplog.messages == [
        "the following PostgreSQL parameter(s) cannot be changed for a Patroni-managed instance: max_connections"
    ]


def test_boostrap_managed() -> None:
    assert build.bootstrap_managed(
        Initdb(username="akh", waldir=Path("/tmp"), data_checksums=True),
    ) == {
        "initdb": [
            {"locale": "C"},
            {"encoding": "UTF8"},
            {"waldir": Path("/tmp")},
            "data-checksums",
        ]
    }


def test_boostrap(patroni_settings: _patroni.Settings) -> None:
    # only using it with initdb (same result as bootstrap_managed)
    initdb = Initdb(username="akh", waldir=Path("/tmp"), data_checksums=True)
    base_r: dict[str, Any] = {
        "initdb": [
            {"locale": "C"},
            {"encoding": "UTF8"},
            {"waldir": Path("/tmp")},
            "data-checksums",
        ]
    }
    assert build.bootstrap(patroni_settings, initdb) == base_r

    # trying with hba
    hba = ["host    pglifrepl93     db2             ::1/128                 md5"]
    base_r.update({"dcs": {"postgresql": {"pg_hba": hba}}})
    assert build.bootstrap(patroni_settings, initdb, hba=hba) == base_r

    # then with hba, pg_ident and PG parameters
    # An empty pg_ident should not add a configuration, which is the same
    # behavior as in local mode.
    assert build.bootstrap(patroni_settings, initdb, hba=hba, pg_ident=[]) == base_r
    ident = ["backupmap       postgres               backup"]
    params = {"max_connections": 100}
    base_r.update(
        {
            "dcs": {
                "postgresql": {"pg_hba": hba, "pg_ident": ident, "parameters": params}
            }
        }
    )
    assert (
        build.bootstrap(
            patroni_settings, initdb, hba=hba, pg_ident=ident, parameters=params
        )
        == base_r
    )

    # only with pg_ident
    base_r["dcs"]["postgresql"].pop("pg_hba")
    base_r["dcs"]["postgresql"].pop("parameters")
    assert build.bootstrap(patroni_settings, initdb, pg_ident=ident) == base_r

    # only with PG parameters
    base_r.update({"dcs": {"postgresql": {"parameters": params}}})
    assert build.bootstrap(patroni_settings, initdb, parameters=params) == base_r


def test_setup_template_config(
    instance_manifest: interface.Instance,
    patroni_settings: _patroni.Settings,
    pg_instance: system.PostgreSQLInstance,
    settings: Settings,
) -> None:
    t_conf: dict[str, Any] = {
        "bootstrap": {
            "dcs": {"loop_wait": 666},
        },
        "restapi": {
            "authentication": {"username": "bill", "password": "l0v3Op3nSource"}
        },
    }
    svc = model_copy_validate(
        instance_manifest.service(i.Service), {"cluster": "test-scope", "node": "pg1"}
    )
    configuration = postgresql.configuration(instance_manifest, settings)
    p = impl.setup(
        pg_instance,
        instance_manifest,
        svc,
        patroni_settings,
        configuration,
        _template=yaml.dump(t_conf),
    )
    j_p = p.model_dump(mode="json")
    assert (
        j_p["bootstrap"]["dcs"]["loop_wait"] == t_conf["bootstrap"]["dcs"]["loop_wait"]
    )
    assert p.name == "pg1"
    assert p.scope == "test-scope"

    # do some check for authentication
    assert (auth := p.restapi.authentication)
    d_auth = t_conf["restapi"]["authentication"]
    assert auth.username == d_auth["username"]
    assert auth.password.get_secret_value() == d_auth["password"]

    with pytest.raises(
        expected_exception=exceptions.SettingsError, match="invalid patroni.yaml"
    ):
        p = impl.setup(
            pg_instance,
            instance_manifest,
            svc,
            patroni_settings,
            configuration,
            _template="in va lid ?",
        )


@pytest.mark.anyio
async def test_get_and_alter_pg_hba(
    patroni_settings: _patroni.Settings, instance: system.Instance
) -> None:
    """Test altering pg_hba for a PostgreSQL instance managed by Patroni."""
    pg_instance = instance.postgresql
    res = await hba.get(pg_instance, hba_manager=patroni_mod)
    assert [str(r) for r in res] == [
        "local   all             postgres                                peer",
        "local   all             all                                     peer",
        "host    all             all             127.0.0.1/32            password",
        "host    all             all             ::1/128                 password",
    ]

    h = [
        "# a comment",
        "host    pglifrepl13     all             ::1/128                 md5",
    ]
    c = impl._configpath(pg_instance.qualname, patroni_settings)
    config = yaml.safe_load(c.read_text())
    config["postgresql"]["pg_hba"] = h
    c.write_text(yaml.dump(config))
    patroni_config = Patroni.get(pg_instance.qualname, patroni_settings)
    assert patroni_config.postgresql.pg_hba == h
    res = await hba.get(pg_instance, hba_manager=patroni_mod)
    assert [str(r) for r in res] == [h[1]]

    h = [
        "# a new comment",
        "host    pglifrepl93     db2             ::1/128                 md5",
    ]
    actual = Patroni.get(pg_instance.qualname, patroni_settings)
    impl.update_hba(actual, pg_instance.qualname, patroni_settings, hba=h)
    assert yaml.safe_load(c.read_text())["postgresql"]["pg_hba"] == h
    updated = Patroni.get(pg_instance.qualname, patroni_settings)
    assert updated.postgresql.pg_hba == h
    res = await hba.get(pg_instance, hba_manager=patroni_mod)
    assert [str(r) for r in res] == [h[1]]


@pytest.mark.anyio
async def test_local_vs_dynamic_mode(
    instance_manifest: interface.Instance,
    mock_api_request: AsyncMock,
    pg_instance: system.PostgreSQLInstance,
    pg_version: PostgreSQLVersion,
    settings: Settings,
) -> None:
    configuration = postgresql.configuration(instance_manifest, settings)
    svc = model_copy_validate(
        instance_manifest.service(i.Service), {"cluster": "test-scope", "node": "pg1"}
    )

    # let's start with "local" configuration
    # HBA entries are written in the Patroni configuration file, under the
    # postgresql section
    assert settings.patroni
    assert settings.patroni.configuration_mode.auth == "local"
    assert settings.patroni.configuration_mode.parameters == "local"
    patroni = impl.setup(
        pg_instance, instance_manifest, svc, settings.patroni, configuration
    )
    impl.write_config(pg_instance.qualname, patroni, settings.patroni)
    conf_f = impl._configpath(pg_instance.qualname, settings.patroni)
    conf = yaml.safe_load(conf_f.read_text())
    assert "postgresql" not in conf["bootstrap"]["dcs"]
    assert "pg_hba" in conf["postgresql"]
    assert "parameters" in conf["postgresql"]
    # pg_ident is only empty if the pg_ident.conf template is available, which
    # is only the case for one version of PostgreSQL in our tests.
    if postgresql.pg_ident(instance_manifest, settings):
        assert "pg_ident" in conf["postgresql"]
    with manager.hba.use(patroni_mod), manager.instance.use(patroni_mod):
        await hba.save(pg_instance, hba=parse_hba([]))
    mock_api_request.assert_not_called()

    # test with dynamic HBA configuration
    patroni_s = settings.patroni.model_dump()
    patroni_s["configuration_mode"] = {"auth": "dynamic", "parameters": "dynamic"}
    s = model_copy_validate(settings, {"patroni": patroni_s})
    instance = system.PostgreSQLInstance(name="p2", version=pg_version, settings=s)
    assert s.patroni
    # configuring instance with auth managed dynamically (DCS mode) should only
    # write  HBA records in the bootstrap.dcs section
    patroni = impl.setup(instance, instance_manifest, svc, s.patroni, configuration)
    impl.write_config(instance.qualname, patroni, s.patroni)
    conf_f = impl._configpath(instance.qualname, s.patroni)
    conf = yaml.safe_load(conf_f.read_text())
    assert "pg_hba" in conf["bootstrap"]["dcs"]["postgresql"]
    assert "pg_hba" not in conf["postgresql"]
    assert "parameters" in conf["bootstrap"]["dcs"]["postgresql"]
    assert "parameters" not in conf["postgresql"]
    if postgresql.pg_ident(instance_manifest, s):
        assert "pg_ident" in conf["bootstrap"]["dcs"]["postgresql"]
        assert "pg_ident" not in conf["postgresql"]

    # test to update HBA
    h = ["host    pglifrepl93     db2             ::1/128                 md5"]
    with (
        manager.instance.use(patroni_mod),
        manager.hba.use(dcs),
        patch("pglift.patroni.dcs.configure_pg_hba", autospec=True) as configure_pg_hba,
        patch("pglift.patroni.dcs.pg_hba_config", autospec=True) as pg_hba_config,
    ):
        await hba.save(instance, hba=parse_hba(h))
    pg_hba_config.assert_called_once_with(instance)
    configure_pg_hba.assert_called_once_with(instance, hba=h)

# SPDX-FileCopyrightText: 2021 Dalibo
#
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

import asyncio
import logging
import re
import sys
from pathlib import Path
from typing import Any
from unittest.mock import AsyncMock, patch

import pytest
from pgtoolkit.conf import parse as parse_pgconf
from pluggy import PluginManager

from pglift import exceptions, h, hooks, postgresql, systemd
from pglift.models import interface, system
from pglift.postgresql import (
    auth_options,
    bindir,
    ctl,
    initdb_options,
    pg_hba,
    pg_ident,
    pq,
    site_configure_check,
    site_configure_install,
    site_configure_list,
    site_configure_uninstall,
    systemd_tmpfilesd_managed_dir,
    systemd_unit_templates,
    systemd_units,
)
from pglift.settings import PostgreSQLVersion, Settings, _postgresql
from pglift.system.command import CommandType
from pglift.systemd import tmpfilesd
from pglift.testutil import model_copy_validate
from pglift.types import Status


def test_bindir(pg_instance: system.PostgreSQLInstance, settings: Settings) -> None:
    assert bindir(pg_instance) == settings.postgresql.versions[-1].bindir


@pytest.mark.anyio
async def test_site_configure(settings: Settings) -> None:
    assert list(site_configure_list(settings)) == [settings.postgresql.logpath]
    assert settings.postgresql.logpath is not None
    assert not any(site_configure_check(settings, False))
    assert not settings.postgresql.logpath.exists()
    await site_configure_install(settings)
    assert all(site_configure_check(settings, True))
    assert settings.postgresql.logpath.exists()
    await site_configure_uninstall(settings)
    assert not settings.postgresql.logpath.exists()


@pytest.mark.anyio
async def test_init_postgresql_dirty(
    pg_version: PostgreSQLVersion, settings: Settings
) -> None:
    manifest = interface.Instance(name="dirty", version=pg_version)
    i = system.PostgreSQLInstance("dirty", pg_version, settings)
    i.datadir.mkdir(parents=True)
    (i.datadir / "dirty").touch()
    calls = []
    with pytest.raises(exceptions.CommandError):
        with pytest.MonkeyPatch.context() as mp:
            mp.setattr("pglift.systemd.enable", lambda *a: calls.append(a))
            await postgresql.init_postgresql(manifest, i)
    assert not i.waldir.exists()
    if settings.service_manager == "systemd":
        assert not calls


@pytest.mark.parametrize("data_checksums", [True, False])
@pytest.mark.anyio
async def test_init_postgresql_force_data_checksums(
    settings: Settings, pg_version: PostgreSQLVersion, data_checksums: bool
) -> None:
    assert settings.postgresql.initdb.data_checksums is None
    manifest = interface.Instance(
        name="checksums", version=pg_version, data_checksums=data_checksums
    )
    initdb_opts = initdb_options(manifest, settings.postgresql)
    assert bool(initdb_opts.data_checksums) == data_checksums
    instance = system.PostgreSQLInstance(manifest.name, manifest.version, settings)

    async def fake_init(*a: Any, **kw: Any) -> None:
        instance.datadir.mkdir(parents=True)
        (instance.datadir / "postgresql.conf").touch()

    with patch(
        "pgtoolkit.ctl.AsyncPGCtl.init", side_effect=fake_init, autospec=True
    ) as init:
        await postgresql.init_postgresql(manifest, instance)
    expected: dict[str, Any] = {
        "waldir": str(instance.waldir),
        "username": "postgres",
        "encoding": "UTF8",
        "auth_local": "peer",
        "auth_host": "password",
        "locale": "C",
    }
    if data_checksums:
        expected["data_checksums"] = True
    pgctl = await ctl.pg_ctl(bindir(instance))
    init.assert_awaited_once_with(pgctl, instance.datadir, **expected)


def test_postgresql_service_name(
    pm: PluginManager, pg_instance: system.PostgreSQLInstance
) -> None:
    assert hooks(pm, h.postgresql_service_name, instance=pg_instance) == [
        None,
        "postgresql",
    ]


@pytest.mark.anyio
async def test_postgresql_editable_conf(
    settings: Settings, pg_instance: system.PostgreSQLInstance
) -> None:
    assert [
        c.strip()
        for c in (await postgresql.postgresql_editable_conf(pg_instance)).lines
    ] == [
        "port = 999",
        "unix_socket_directories = /socks, /shoes",
        "# backslash_quote = 'safe_encoding'",
    ]


def test_initdb_options(
    settings: Settings,
    instance_manifest: interface.Instance,
    pg_instance: system.PostgreSQLInstance,
) -> None:
    postgresql_settings = settings.postgresql
    expected = postgresql_settings.initdb.model_dump(exclude_none=True) | {
        "username": "postgres",
        "waldir": pg_instance.waldir,
    }
    assert (
        initdb_options(instance_manifest, postgresql_settings).model_dump(
            exclude_none=True
        )
        == expected
    )
    assert initdb_options(
        instance_manifest.model_copy(update={"locale": "X", "data_checksums": True}),
        postgresql_settings,
    ).model_dump(exclude_none=True) == expected | {
        "locale": "X",
        "data_checksums": True,
    }
    assert initdb_options(
        instance_manifest.model_copy(update={"data_checksums": None}),
        postgresql_settings.model_copy(
            update={
                "initdb": postgresql_settings.initdb.model_copy(
                    update={"data_checksums": True}
                )
            }
        ),
    ).model_dump(exclude_none=True) == expected | {"data_checksums": True}


def test_auth_options(
    settings: Settings, instance_manifest: interface.Instance
) -> None:
    assert auth_options(
        instance_manifest.auth, settings.postgresql.auth
    ) == interface.Auth(local="peer", host="password", hostssl="trust")


def test_pg_hba(
    settings: Settings,
    instance_manifest: interface.Instance,
    expected_dir: Path,
    write_changes: bool,
) -> None:
    actual = pg_hba(instance_manifest, settings)
    fpath = expected_dir / "pg_hba.conf"
    if write_changes:
        fpath.write_text(actual)
    expected = fpath.read_text()
    assert actual == expected


def test_instance_pg_ident(
    settings: Settings,
    instance_manifest: interface.Instance,
    expected_dir: Path,
    write_changes: bool,
) -> None:
    actual = pg_ident(instance_manifest, settings)
    fpath = expected_dir / "pg_ident.conf"
    if write_changes:
        fpath.write_text(actual)
    expected = fpath.read_text()
    assert actual == expected


@pytest.mark.usefixtures("nohook")
def test_configuration_base_postgresql_conf(settings: Settings) -> None:
    m = interface.Instance(name="foo", version="16")
    configuration = postgresql.configuration(m, settings)
    config = configuration.as_dict()
    # Remove system-dependant values
    del config["shared_buffers"]
    del config["effective_cache_size"]
    assert config == {
        "cluster_name": "foo",
        "unix_socket_directories": str(settings.run_prefix / "postgresql"),
        "log_directory": str(settings.postgresql.logpath),
        "log_filename": "16-foo-%Y-%m-%d_%H%M%S.log",
        "log_destination": "stderr",
        "logging_collector": True,
        "lc_messages": "C",
        "lc_monetary": "C",
        "lc_numeric": "C",
        "lc_time": "C",
    }


@pytest.mark.usefixtures("nohook")
def test_configuration_custom_postgresql_conf(
    pg_version: PostgreSQLVersion, settings: Settings
) -> None:
    m = interface.Instance(name="foo", version=pg_version)
    configuration = postgresql.configuration(m, settings)
    assert configuration.as_dict() == {
        "cluster_name": "foo",
        "port": 5555,
        "unix_socket_directories": str(settings.run_prefix / "postgresql"),
        "logging_collector": True,
        "lc_messages": "C",
        "lc_monetary": "C",
        "lc_numeric": "C",
        "lc_time": "C",
    }


@pytest.mark.usefixtures("nohook")
def test_configuration_precedence(
    pg_version: PostgreSQLVersion, settings: Settings
) -> None:
    """Settings defined in manifest take precedence over postgresql.conf site template."""
    template = "\n".join(
        [
            "bonjour = 'hello, {name}'",
            "max_connections = 101",
            "port=9876",
            "unix_socket_directories = /tmp, /var/run/postgresql",
        ]
    )

    m = interface.Instance(
        name="foo", version=pg_version, settings={"max_connections": 100, "ssl": True}
    )
    configuration = postgresql.configuration(m, settings, _template=template)
    assert configuration.as_dict() == {
        "bonjour": "hello, foo",
        "lc_messages": "C",
        "lc_monetary": "C",
        "lc_numeric": "C",
        "lc_time": "C",
        "max_connections": 100,
        "port": 9876,
        "ssl": True,
        "unix_socket_directories": "/tmp, /var/run/postgresql",
    }

    m = model_copy_validate(m, {"port": 1234})
    configuration = postgresql.configuration(m, settings, _template=template)
    assert configuration.as_dict() == {
        "bonjour": "hello, foo",
        "lc_messages": "C",
        "lc_monetary": "C",
        "lc_numeric": "C",
        "lc_time": "C",
        "max_connections": 100,
        "port": 1234,
        "ssl": True,
        "unix_socket_directories": "/tmp, /var/run/postgresql",
    }

    # When setting a port with the default value, it must take precedence over
    # the template.
    m = model_copy_validate(m, {"port": 5432, "settings": {"work_mem": "100MB"}})
    configuration = postgresql.configuration(m, settings, _template=template)
    assert configuration.as_dict() == {
        "bonjour": "hello, foo",
        "lc_messages": "C",
        "lc_monetary": "C",
        "lc_numeric": "C",
        "lc_time": "C",
        "max_connections": 101,
        "work_mem": "100MB",
        "port": 5432,
        "unix_socket_directories": "/tmp, /var/run/postgresql",
    }


def test_configuration_shared_preload_libraries(
    pg_version: PostgreSQLVersion,
    settings: Settings,
    composite_instance_model: type[interface.Instance],
) -> None:
    template = "shared_preload_libraries = 'auto_explain'"
    manifest = composite_instance_model.model_validate(
        {"name": "spl", "version": pg_version, "pgbackrest": {"stanza": "spl"}}
    )
    configuration = postgresql.configuration(manifest, settings, _template=template)
    assert (
        configuration.as_dict()["shared_preload_libraries"]
        == "auto_explain, pg_qualstats, pg_stat_statements, pg_stat_kcache"
    )

    manifest = composite_instance_model.model_validate(
        {
            "name": "spl",
            "version": pg_version,
            "port": 5444,
            "settings": {"shared_preload_libraries": 42},
            "pgbackrest": {"stanza": "spl"},
        }
    )
    with pytest.raises(
        exceptions.InstanceStateError,
        match="expecting a string value for 'shared_preload_libraries' setting: 42",
    ):
        postgresql.configuration(manifest, settings)


def test_configuration_include(
    settings: Settings, instance_manifest: interface.Instance, tmp_path: Path
) -> None:
    included = tmp_path / "incl.conf"
    included.write_text("foo = bar\n")
    template = "shared_preload_libraries = 'auto_explain'"
    template = "\n".join(["foo = baz", "work_mem = 123MB", f"include = {included}"])
    configuration = postgresql.configuration(
        instance_manifest, settings, _template=template
    )
    assert configuration.as_dict()["foo"] == "bar"


def test_configuration_include_notfound(
    settings: Settings, instance_manifest: interface.Instance
) -> None:
    template = "include = xyz\n"
    with pytest.raises(
        exceptions.SettingsError,
        match="invalid postgresql.conf template: cannot process include",
    ):
        postgresql.configuration(instance_manifest, settings, _template=template)


@pytest.mark.usefixtures("nohook")
@pytest.mark.anyio
async def test_configure_configure_postgresql(
    settings: Settings,
    pg_instance: system.PostgreSQLInstance,
    instance_manifest: interface.Instance,
) -> None:
    configdir = pg_instance.datadir
    postgresql_conf = configdir / "postgresql.conf"
    with postgresql_conf.open("w") as f:
        f.write("bonjour_name = 'overridden'\n")

    changes = await postgresql.configure(
        pg_instance,
        model_copy_validate(
            instance_manifest,
            {
                "settings": dict(
                    instance_manifest.settings,
                    max_connections=100,
                    shared_buffers="10 %",
                    effective_cache_size="5MB",
                ),
                "port": 5433,
            },
        ),
    )
    old_shared_buffers, new_shared_buffers = changes.pop("shared_buffers")
    assert old_shared_buffers is None
    assert new_shared_buffers is not None and new_shared_buffers != "10 %"
    assert changes == {
        "bonjour_name": ("overridden", None),
        "cluster_name": (None, "test"),
        "effective_cache_size": (None, "5MB"),
        "lc_messages": (None, "C"),
        "lc_monetary": (None, "C"),
        "lc_numeric": (None, "C"),
        "lc_time": (None, "C"),
        "logging_collector": (None, True),
        "max_connections": (None, 100),
        "port": (None, 5433),
        "shared_preload_libraries": (None, "passwordcheck"),
        "unix_socket_directories": (
            None,
            str(settings.postgresql.socket_directory),
        ),
    }

    postgresql_conf = configdir / "postgresql.conf"
    content = postgresql_conf.read_text()
    lines = content.splitlines()
    assert "port = 5433" in lines
    assert "cluster_name = 'test'" in lines
    assert re.search(r"shared_buffers = '\d+ [kMGT]?B'", content)
    assert "effective_cache_size" in content
    assert f"unix_socket_directories = '{settings.prefix}/run/postgresql'" in content

    with postgresql_conf.open() as f:
        config = parse_pgconf(f)
    assert config.port == 5433
    assert config.entries["bonjour_name"].commented
    assert config.cluster_name == "test"

    changes = await postgresql.configure(
        pg_instance,
        model_copy_validate(
            instance_manifest,
            {
                "settings": dict(
                    instance_manifest.settings,
                    listen_address="*",
                    log_directory="pglogs",
                ),
                "port": 5432,
            },
        ),
    )
    old_effective_cache_size, new_effective_cache_size = changes.pop(
        "effective_cache_size"
    )
    assert old_effective_cache_size == "5MB"
    assert new_effective_cache_size != old_effective_cache_size
    old_shared_buffers1, new_shared_buffers1 = changes.pop("shared_buffers")
    assert old_shared_buffers1 == new_shared_buffers
    assert new_shared_buffers1 != old_shared_buffers1
    assert changes == {
        "listen_address": (None, "*"),
        "max_connections": (100, None),
        "port": (5433, 5432),
        "log_directory": (None, "pglogs"),
    }

    # Port no longer set.
    changes = await postgresql.configure(
        pg_instance,
        model_copy_validate(
            instance_manifest,
            {
                "settings": dict(
                    instance_manifest.settings,
                    listen_address="*",
                    log_directory="pglogs",
                ),
            },
        ),
    )
    assert changes == {"port": (5432, 5555)}
    with postgresql_conf.open() as f:
        config = parse_pgconf(f)
    assert config["port"] == 5555

    # Same configuration, no change.
    mtime_before = postgresql_conf.stat().st_mtime
    changes = await postgresql.configure(
        pg_instance,
        model_copy_validate(
            instance_manifest,
            {
                "settings": dict(
                    instance_manifest.settings,
                    listen_address="*",
                    log_directory="pglogs",
                ),
            },
        ),
    )
    assert changes == {}
    mtime_after = postgresql_conf.stat().st_mtime
    assert mtime_before == mtime_after


@pytest.mark.anyio
async def test_configure_configure_include(
    pg_instance: system.PostgreSQLInstance,
    instance_manifest: interface.Instance,
    tmp_path: Path,
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Reconfigure PostgreSQL with a postgresql.conf having an 'include' directive."""
    # Start from a configured instance, so as to limit changes after.
    await postgresql.configure(pg_instance, instance_manifest)

    included = tmp_path / "included.conf"
    included.write_text("foo = bar\nbonjour = on\n")
    configdir = pg_instance.datadir
    postgresql_conf = configdir / "postgresql.conf"
    with postgresql_conf.open("a") as f:
        f.write(
            "\n".join(
                [
                    "",
                    "bonjour_name = 'test'",
                    f"include = {included}",
                    "",
                ]
            )
        )

    caplog.clear()
    with caplog.at_level(logging.WARNING, "pglift.postgresql"):
        changes = await postgresql.configure(
            pg_instance,
            model_copy_validate(
                instance_manifest,
                {
                    "settings": dict(instance_manifest.settings)
                    | {"bonjour": False, "bonjour_name": "test"},
                },
            ),
        )
    (msg, *others) = caplog.messages
    assert not others
    assert msg.startswith(f"entry 'bonjour' not directly found in {postgresql_conf}")
    assert changes == {
        "bonjour": (True, False),
        "cluster_name": (None, "test"),
        "foo": ("bar", None),
    }
    lines = postgresql_conf.read_text().splitlines()
    assert "bonjour = off" in lines
    assert "bonjour_name = 'test'" in lines
    assert not any("bar" in line for line in lines)


def test_configure_auth(
    instance_manifest: interface.Instance, pg_instance: system.PostgreSQLInstance
) -> None:
    hba = pg_instance.datadir / "pg_hba.conf"
    ident = pg_instance.datadir / "pg_ident.conf"
    orig_hba = hba.read_text()
    orig_ident = ident.read_text()
    postgresql.configure_auth(pg_instance, instance_manifest)
    hba_after = hba.read_text()
    assert hba_after != orig_hba
    assert "# pg_hba.conf" in hba_after
    ident_after = ident.read_text()
    assert ident_after != orig_ident
    assert "# pg_ident.conf" in ident_after


@pytest.mark.anyio
async def test_is_ready(pg_instance: system.PostgreSQLInstance) -> None:
    assert not await ctl.is_ready(pg_instance)


@pytest.fixture
def broken_instance(
    pg_version: PostgreSQLVersion, settings: Settings
) -> system.PostgreSQLInstance:
    """A PostgreSQLInstance with non-existing data and WAL directories."""
    i = system.PostgreSQLInstance(name="broken", version=pg_version, settings=settings)
    assert not i.datadir.exists() and not i.waldir.exists()
    return i


@pytest.mark.anyio
async def test_status(pg_instance: system.PostgreSQLInstance) -> None:
    assert await postgresql.status(pg_instance) == Status.not_running


@pytest.mark.anyio
async def test_status_notfound(broken_instance: system.PostgreSQLInstance) -> None:
    with pytest.raises(
        exceptions.InstanceNotFound, match=r"'pg_ctl status' exited with code 4"
    ):
        await postgresql.status(broken_instance)


@pytest.mark.anyio
async def test_is_running(pg_instance: system.PostgreSQLInstance) -> None:
    assert await postgresql.is_running(pg_instance) is False


@pytest.mark.anyio
async def test_is_running_notfound(broken_instance: system.PostgreSQLInstance) -> None:
    assert await postgresql.is_running(broken_instance) is False


@pytest.mark.anyio
async def test_check_status(pg_instance: system.PostgreSQLInstance) -> None:
    with pytest.raises(exceptions.InstanceStateError, match="instance is not_running"):
        await postgresql.check_status(pg_instance, Status.running)
    await postgresql.check_status(pg_instance, Status.not_running)


@pytest.mark.anyio
async def test_start_foreground(pg_instance: system.PostgreSQLInstance) -> None:
    with patch("os.execv", autospec=True) as execv:
        await postgresql.start_postgresql(pg_instance, foreground=True, wait=False)
    postgres = bindir(pg_instance) / "postgres"
    execv.assert_called_once_with(
        str(postgres), f"{postgres} -D {pg_instance.datadir}".split()
    )


@pytest.mark.anyio
async def test_rewind(pg_instance: system.PostgreSQLInstance) -> None:
    source = postgresql.RewindSource(
        conninfo="host=pgsrv.example.com user=rewd port=5555", password="abcd"
    )
    cmd = AsyncMock(CommandType)
    await postgresql.rewind(pg_instance, source, extra_opts=["--progress"], cmd=cmd)
    ((args, kwargs),) = cmd.run.await_args_list
    assert args == (
        [
            f"{bindir(pg_instance) / 'pg_rewind'}",
            "-D",
            f"{pg_instance.datadir}",
            "--source-server",
            "host=pgsrv.example.com port=5555 user=rewd",
            "--write-recovery-conf",
            "--progress",
        ],
    )
    assert kwargs["check"] is True
    assert kwargs["env"]["PGPASSWORD"] == "abcd"


def test_pq_environ(settings: Settings, pg_instance: system.PostgreSQLInstance) -> None:
    postgres_settings = settings.postgresql
    assert pq.environ(pg_instance, postgres_settings.surole.name, base={}) == {
        "PGPASSFILE": str(postgres_settings.auth.passfile)
    }
    assert pq.environ(
        pg_instance,
        postgres_settings.surole.name,
        base={"PGPASSFILE": "/var/lib/pgsql/pgpass"},
    ) == {"PGPASSFILE": "/var/lib/pgsql/pgpass"}


def test_pq_environ_password_command(
    settings: Settings,
    bindir_template: str,
    pg_version: PostgreSQLVersion,
    tmp_path: Path,
) -> None:
    s = settings.model_copy(
        update={
            "postgresql": _postgresql.Settings.model_validate(
                {
                    "bindir": bindir_template,
                    "surole": {"name": "bob"},
                    "auth": {
                        "password_command": [
                            sys.executable,
                            "-c",
                            "import sys; print(f'{{sys.argv[1]}}-secret')",
                            "{instance}",
                            "--blah",
                        ],
                        "passfile": str(tmp_path / "pgpass"),
                    },
                }
            )
        }
    )
    instance = system.PostgreSQLInstance("xyz", pg_version, settings=s)
    assert pq.environ(instance, "bob", base={}) == {
        "PGPASSFILE": str(tmp_path / "pgpass"),
        "PGPASSWORD": f"{pg_version}/xyz-secret",
    }


@pytest.mark.parametrize(
    "connargs, expected",
    [
        (
            {"user": "bob"},
            "dbname=mydb sslmode=off user=bob port=999 host=/socks passfile={passfile}",
        ),
        (
            {"user": "alice", "password": "s3kret"},
            "dbname=mydb sslmode=off user=alice password=s3kret port=999 host=/socks passfile={passfile}",
        ),
    ],
)
def test_pq_dsn(
    settings: Settings,
    pg_instance: system.PostgreSQLInstance,
    connargs: dict[str, str],
    expected: str,
) -> None:
    passfile = settings.postgresql.auth.passfile
    conninfo = pq.dsn(pg_instance, dbname="mydb", sslmode="off", **connargs)
    assert conninfo == expected.format(passfile=passfile)


def test_pq_dsn_badarg(pg_instance: system.PostgreSQLInstance) -> None:
    with pytest.raises(TypeError, match="unexpected 'port' argument"):
        pq.dsn(pg_instance, port=123)


def test_systemd_units() -> None:
    assert systemd_units() == ["pglift-postgresql@.service"]


def test_install_systemd_unit_template(
    monkeypatch: pytest.MonkeyPatch, settings: Settings
) -> None:
    monkeypatch.setenv("PGLIFT_DEBUG", "no")
    ((name, content),) = list(systemd_unit_templates(settings))

    assert name == "pglift-postgresql@.service"
    lines = content.splitlines()
    for line in lines:
        if line.startswith("ExecStart"):
            execstart = line.split("=", 1)[-1]
            assert execstart == f"{sys.executable} -m pglift_cli postgres %i"
            break
    else:
        raise AssertionError("ExecStart line not found")
    assert 'Environment="PGLIFT_DEBUG=no"' in lines


def test_install_systemd_tmpfiles_template(settings: Settings) -> None:
    ((name, managed_dir),) = list(systemd_tmpfilesd_managed_dir(settings))
    assert name == "postgresql"
    assert managed_dir == settings.run_prefix / "postgresql"
    content = systemd.template("pglift-tmpfiles.d.conf").format(path=managed_dir)
    assert content == f"d   {settings.run_prefix}/postgresql  0750    -   -   -\n"


def test_manage_systemd_tmpfiles_conf(settings: Settings) -> None:
    assert settings.systemd
    postgresql_conf = settings.systemd.tmpfilesd_conf_path / "pglift-postgresql.conf"
    postgresql_s = settings.postgresql.model_dump()
    postgresql_s["socket_directory"] = settings.run_prefix / "postgresql"
    s = model_copy_validate(settings, {"postgresql": postgresql_s})
    assert postgresql_conf in list(tmpfilesd.site_configure_list(s))
    postgresql_s["socket_directory"] = "/postgresql/"
    s = model_copy_validate(settings, {"postgresql": postgresql_s})
    assert postgresql_conf not in list(tmpfilesd.site_configure_list(s))


def test_logs(
    pg_instance: system.PostgreSQLInstance,
    tmp_path: Path,
    caplog: pytest.LogCaptureFixture,
) -> None:
    with pytest.raises(
        exceptions.FileNotFoundError,
        match=r"file 'current_logfiles' for instance \d{2}/test not found",
    ):
        next(ctl.logs(pg_instance))

    current_logfiles = pg_instance.datadir / "current_logfiles"
    current_logfiles.write_text("csvlog log/postgresql.csv\n")
    with pytest.raises(ValueError, match="no record matching 'stderr'"):
        next(ctl.logs(pg_instance, timeout=0.1))

    with (pg_instance.datadir / "postgresql.conf").open("a") as f:
        f.write("\nlog_destination = syslog, stderr, csvlog, jsonlog\n")

    stderr_logpath = tmp_path / "postgresql-1.log"
    current_logfiles.write_text(
        f"stderr {stderr_logpath}\n"
        f"csvlog {tmp_path / 'postgresql-1.csv'}\n"
        f"jsonlog {tmp_path / 'postgresql-1.json'}\n"
    )
    with pytest.raises(exceptions.SystemError, match="failed to read"):
        next(ctl.logs(pg_instance, timeout=0.1))

    logger = ctl.logs(pg_instance, timeout=0.1)
    stderr_logpath.write_text("line1\nline2\n")
    caplog.clear()
    with caplog.at_level(logging.INFO, logger="pglift.postgresql.ctl"):
        assert [next(logger) for _ in range(2)] == ["line1\n", "line2\n"]
    assert caplog.messages == [
        f"reading logs of instance {pg_instance} from {stderr_logpath}"
    ]

    with pytest.raises(TimeoutError):
        next(logger)

    logger = ctl.logs(pg_instance)
    assert [next(logger) for _ in range(2)] == ["line1\n", "line2\n"]

    stderr_logpath = tmp_path / "postgresql-2.log"
    current_logfiles.write_text(f"stderr {stderr_logpath}\n")
    stderr_logpath.write_text("line3\nline4\n")

    caplog.clear()
    with caplog.at_level(logging.INFO, logger="pglift.postgresql.ctl"):
        assert [next(logger) for _ in range(2)] == ["line3\n", "line4\n"]
    assert caplog.messages == [
        f"reading logs of instance {pg_instance} from {stderr_logpath}"
    ]


@pytest.mark.anyio
async def test_log(
    pg_instance: system.PostgreSQLInstance,
    tmp_path: Path,
    caplog: pytest.LogCaptureFixture,
) -> None:
    current_logfiles = pg_instance.datadir / "current_logfiles"
    with (pg_instance.datadir / "postgresql.conf").open("a") as f:
        f.write("\nlog_destination = stderr\n")
    stderr_logpath = tmp_path / "pgsql.log"
    current_logfiles.write_text(f"stderr {stderr_logpath}\n")
    stderr_logpath.write_text("msg 0\n")
    postgres = bindir(pg_instance) / "postgres"
    with caplog.at_level(logging.DEBUG, logger="pglift.postgresql.ctl"):
        async with ctl.log(pg_instance):
            await asyncio.sleep(0.1)
            with stderr_logpath.open("a") as f:
                f.write("msg 1\n")
                f.write("msg 2\n")
                f.flush()
                await asyncio.sleep(0.1)
                assert caplog.messages == [
                    f"{postgres}: msg 1",
                    f"{postgres}: msg 2",
                ]
                f.write("msg 3\n")
                caplog.clear()
            await asyncio.sleep(0.1)
            assert caplog.messages == [f"{postgres}: msg 3"]

    current_logfiles.unlink()
    caplog.clear()
    with caplog.at_level(logging.DEBUG, logger="pglift.postgresql.ctl"):
        async with ctl.log(pg_instance):
            with stderr_logpath.open("a") as f:
                f.write("msg 4\n")
    assert not caplog.messages


@pytest.mark.anyio
async def test_replication_lag(pg_instance: system.PostgreSQLInstance) -> None:
    with pytest.raises(TypeError, match="not a standby"):
        await postgresql.replication_lag(pg_instance)

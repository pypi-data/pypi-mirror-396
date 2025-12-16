# SPDX-FileCopyrightText: 2021 Dalibo
#
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

import logging
from collections.abc import Iterator
from pathlib import Path
from unittest.mock import AsyncMock, patch

import attrs
import pytest

from pglift import exceptions, instances, manager, postgresql, ui
from pglift.models import Instance, PGSetting, PostgreSQLInstance
from pglift.settings import PostgreSQLVersion, Settings
from pglift.types import ConfigChanges


def test_postgresql_service_names(pg_instance: PostgreSQLInstance) -> None:
    assert list(instances.postgresql_service_names(pg_instance)) == ["postgresql"]


def test_system_list_no_instance(settings: Settings) -> None:
    assert list(instances.system_list(settings)) == []


def test_system_list(
    settings: Settings, pg_version: PostgreSQLVersion, instance: Instance
) -> None:
    assert list(map(str, instances.system_list(settings))) == [
        f"{pg_version}/{instance.name}"
    ]


def test_system_list_custom_datadir(tmp_path: Path, settings: Settings) -> None:
    # {name} before {version} in datadir path
    datadir = tmp_path / "{name}" / "post" / "gres" / "{version}" / "data"
    object.__setattr__(settings.postgresql, "datadir", datadir)

    i1 = Path(str(datadir).format(name="foo", version="17"))
    i1.mkdir(parents=True)
    (i1 / "PG_VERSION").write_text("17\n")
    (i1 / "postgresql.conf").touch()
    i2 = Path(str(datadir).format(name="bar", version="14"))
    i2.mkdir(parents=True)
    (i2 / "PG_VERSION").write_text("14\n")
    (i2 / "postgresql.conf").touch()
    assert list(map(str, instances.system_list(settings))) == ["14/bar", "17/foo"]

    # {version} before {name} in datadir path
    datadir = tmp_path / "{version}" / "post" / "gres" / "{name}" / "data"
    object.__setattr__(settings.postgresql, "datadir", datadir)

    i3 = Path(str(datadir).format(name="dude", version="17"))
    i3.mkdir(parents=True)
    (i3 / "PG_VERSION").write_text("17\n")
    (i3 / "postgresql.conf").touch()
    assert list(map(str, instances.system_list(settings))) == ["17/dude"]

    # Datadir with parts not exactly matching formatted values
    datadir = tmp_path / "version_{version}" / "name_{name}" / "data"
    object.__setattr__(settings.postgresql, "datadir", datadir)

    i4 = Path(str(datadir).format(name="baz", version="14"))
    i4.mkdir(parents=True)
    (i4 / "PG_VERSION").write_text("14\n")
    (i4 / "postgresql.conf").touch()
    assert list(map(str, instances.system_list(settings))) == ["14/baz"]

    # Datadir with {name} and {version} in the same path part
    datadir = tmp_path / "{version}-{name}" / "data"
    object.__setattr__(settings.postgresql, "datadir", datadir)

    i5 = Path(str(datadir).format(name="qux", version="17"))
    i5.mkdir(parents=True)
    (i5 / "PG_VERSION").write_text("17\n")
    (i5 / "postgresql.conf").touch()
    assert list(map(str, instances.system_list(settings))) == ["17/qux"]


def test_system_lookup_version_no_version_in_datadir_template(tmp_path: Path) -> None:
    datadir_template = tmp_path / "pgsql" / "{name}" / "data"
    assert list(instances.system_version_lookup(None, datadir_template)) == []
    names = ["foo", "bar"]
    for name in names:
        Path(str(datadir_template).format(name=name)).mkdir(parents=True)
    assert set(instances.system_version_lookup(None, datadir_template)) == set(names)


@pytest.fixture
def no_confirm_ui() -> Iterator[list[tuple[str, bool]]]:
    args = []

    class NoUI(ui.UserInterface):
        def confirm(self, message: str, default: bool) -> bool:
            args.append((message, default))
            return False

    token = ui.set(NoUI())
    yield args
    ui.reset(token)


@pytest.mark.anyio
async def test_drop(instance: Instance, no_confirm_ui: list[tuple[str, bool]]) -> None:
    with pytest.raises(exceptions.Cancelled):
        await instances.drop(instance)
    assert no_confirm_ui == [
        (f"Confirm complete deletion of instance {instance}?", True)
    ]


def test_env_for(
    settings: Settings, instance: Instance, pg_instance: PostgreSQLInstance
) -> None:
    expected_env = {
        "PGDATA": str(pg_instance.datadir),
        "PGHOST": "/socks",
        "PGPASSFILE": str(settings.postgresql.auth.passfile),
        "PGPORT": "999",
        "PGUSER": "postgres",
        "PSQLRC": f"{pg_instance.datadir}/.psqlrc",
        "PSQL_HISTORY": f"{pg_instance.datadir}/.psql_history",
        "PGBACKREST_CONFIG_PATH": f"{settings.prefix}/etc/pgbackrest",
        "PGBACKREST_STANZA": "test-stanza",
    }
    assert instances.env_for(instance) == expected_env


def test_exec(
    settings: Settings, instance: Instance, pg_instance: PostgreSQLInstance
) -> None:
    with (
        patch("os.execve", autospec=True) as patched,
        patch.dict("os.environ", {"PGUSER": "me", "PGPASSWORD": "qwerty"}, clear=True),
    ):
        instances.exec(instance, command=("psql", "--user", "test", "--dbname", "test"))
    expected_env = {
        "PGDATA": str(pg_instance.datadir),
        "PGPASSFILE": str(settings.postgresql.auth.passfile),
        "PGPORT": "999",
        "PGUSER": "me",
        "PGHOST": "/socks",
        "PGPASSWORD": "qwerty",
        "PSQLRC": str(pg_instance.psqlrc),
        "PSQL_HISTORY": str(pg_instance.psql_history),
        "PGBACKREST_CONFIG_PATH": f"{settings.prefix}/etc/pgbackrest",
        "PGBACKREST_STANZA": "test-stanza",
    }

    bindir = postgresql.bindir(pg_instance)
    cmd = [
        f"{bindir}/psql",
        "--user",
        "test",
        "--dbname",
        "test",
    ]
    patched.assert_called_once_with(f"{bindir}/psql", cmd, expected_env)

    with patch("os.execve", autospec=True) as patched:
        instances.exec(instance, command=("true",))
    assert patched.called

    with (
        patch("os.execve", autospec=True) as patched,
        pytest.raises(exceptions.FileNotFoundError, match="nosuchprogram"),
    ):
        instances.exec(instance, command=("nosuchprogram",))
    assert not patched.called


def test_env(
    settings: Settings, instance: Instance, pg_instance: PostgreSQLInstance
) -> None:
    bindir = postgresql.bindir(pg_instance)
    with patch.dict("os.environ", {"PATH": "/pg10/bin"}):
        expected_env = [
            f"export PATH={bindir}:/pg10/bin",
            f"export PGBACKREST_CONFIG_PATH={settings.prefix}/etc/pgbackrest",
            "export PGBACKREST_STANZA=test-stanza",
            f"export PGDATA={pg_instance.datadir}",
            "export PGHOST=/socks",
            f"export PGPASSFILE={settings.postgresql.auth.passfile}",
            "export PGPORT=999",
            "export PGUSER=postgres",
            f"export PSQLRC={pg_instance.psqlrc}",
            f"export PSQL_HISTORY={pg_instance.psql_history}",
        ]
        assert instances.env(instance) == "\n".join(expected_env)


def test_exists(settings: Settings, pg_instance: PostgreSQLInstance) -> None:
    assert instances.exists(pg_instance.name, pg_instance.version, settings)
    assert not instances.exists("doesnotexists", pg_instance.version, settings)


@pytest.mark.anyio
async def test_upgrade_forbid_same_instance(instance: Instance) -> None:
    pg_instance = instance.postgresql
    with pytest.raises(
        exceptions.InvalidVersion,
        match=f"Could not upgrade {pg_instance.version}/test using same name and same version",
    ):
        await instances.upgrade(instance, version=pg_instance.version)


@pytest.mark.anyio
async def test_upgrade_target_instance_exists(
    instance: Instance, pg_instance: PostgreSQLInstance
) -> None:
    orig_instance = attrs.evolve(
        instance, postgresql=attrs.evolve(pg_instance, name="old")
    )
    with pytest.raises(exceptions.InstanceAlreadyExists):
        await instances.upgrade(
            orig_instance, version=pg_instance.version, name=pg_instance.name
        )


@pytest.mark.anyio
async def test_invalid_downgrade_instance(
    instance: Instance, pg_instance: PostgreSQLInstance
) -> None:
    orig_instance = attrs.evolve(
        instance, postgresql=attrs.evolve(pg_instance, name="old", version="17")
    )
    with pytest.raises(
        exceptions.InvalidVersion, match="Could not upgrade 17/old from 17 to 14"
    ):
        await instances.upgrade(orig_instance, version="14", name="new")


@pytest.mark.anyio
async def test_upgrade_confirm(
    instance: Instance,
    pg_version: PostgreSQLVersion,
    no_confirm_ui: list[tuple[str, bool]],
) -> None:
    with pytest.raises(exceptions.Cancelled):
        await instances.upgrade(instance, name="new", version=pg_version)
    assert no_confirm_ui == [
        (f"Confirm upgrade of instance {instance} to version {pg_version}?", True)
    ]


@pytest.mark.anyio
async def test_standby_upgrade(
    standby_instance: Instance, pg_version: PostgreSQLVersion
) -> None:
    with pytest.raises(
        exceptions.InstanceReadOnlyError,
        match=f"^{pg_version}/standby is a read-only standby instance$",
    ):
        await instances.upgrade(standby_instance)


@pytest.mark.anyio
async def test_non_standby_promote(
    instance: Instance, pg_version: PostgreSQLVersion
) -> None:
    with (
        manager.instance.use(postgresql),
        manager.hba.use(postgresql),
        pytest.raises(
            exceptions.InstanceStateError,
            match=f"^{pg_version}/test is not a standby$",
        ),
    ):
        await instances.promote(instance)


@pytest.mark.anyio
async def test_check_pending_actions(
    pg_instance: PostgreSQLInstance,
    caplog: pytest.LogCaptureFixture,
    no_confirm_ui: list[tuple[str, bool]],
) -> None:
    _settings = [
        PGSetting(
            name="needs_restart",
            context="postmaster",
            setting="somevalue",
            pending_restart=False,
        ),
        PGSetting(
            name="needs_reload",
            context="sighup",
            setting="somevalue",
            pending_restart=False,
        ),
    ]
    changes: ConfigChanges = {
        "needs_restart": ("before", "after"),
        "needs_reload": ("before", "after"),
    }

    restart_on_changes = True
    with (
        patch.object(postgresql, "is_running", return_value=True, autospec=True),
        patch("pglift.system.db.connect", autospec=True) as db_connect,
        patch.object(
            instances, "settings", return_value=_settings, autospec=True
        ) as settings,
        patch.object(instances, "reload", new_callable=AsyncMock) as reload,
        caplog.at_level(logging.INFO),
    ):
        await instances.check_pending_actions(pg_instance, changes, restart_on_changes)
    db_connect.assert_called_once_with(pg_instance)
    assert no_confirm_ui == [
        ("PostgreSQL needs to be restarted; restart now?", restart_on_changes)
    ]
    settings.assert_awaited_once()
    assert (
        f"instance {pg_instance} needs restart due to parameter changes: needs_restart"
        in caplog.messages
    )
    assert (
        f"instance {pg_instance} needs reload due to parameter changes: needs_reload"
        in caplog.messages
    )
    reload.assert_awaited_once_with(pg_instance)


@pytest.mark.parametrize(
    ["changes", "requires_confirm", "db_connect_called", "settings_awaited"],
    [
        # Change port only, but keep the default value
        ({"port": (None, 5432)}, False, True, True),
        ({"port": (5432, None)}, False, True, True),
        # Change port from None to default + other parameter
        (
            {
                "needs_restart": ("before", "after"),
                "port": (None, 5432),
            },
            True,
            True,
            True,
        ),
        # Change port
        ({"port": (None, 5433)}, True, False, False),
        ({"port": (5433, None)}, True, False, False),
        ({"port": (5433, 5432)}, True, False, False),
        # Change port + other parameter
        (
            {
                "needs_restart": ("before", "after"),
                "port": (None, 5433),
            },
            True,
            False,
            False,
        ),
    ],
)
@pytest.mark.anyio
async def test_check_pending_actions_port_change(
    pg_instance: PostgreSQLInstance,
    caplog: pytest.LogCaptureFixture,
    no_confirm_ui: list[tuple[str, bool]],
    changes: ConfigChanges,
    requires_confirm: bool,
    db_connect_called: bool,
    settings_awaited: bool,
) -> None:
    _settings = [
        PGSetting(
            name="needs_restart",
            context="postmaster",
            setting="somevalue",
            pending_restart=False,
        ),
    ]
    restart_on_changes = True
    with (
        patch.object(postgresql, "is_running", return_value=True, autospec=True),
        patch("pglift.system.db.connect", autospec=True) as db_connect,
        patch.object(
            instances, "settings", return_value=_settings, autospec=True
        ) as settings,
        caplog.at_level(logging.INFO),
    ):
        await instances.check_pending_actions(pg_instance, changes, restart_on_changes)
    if requires_confirm:
        assert no_confirm_ui == [
            ("PostgreSQL needs to be restarted; restart now?", restart_on_changes)
        ]
    else:
        assert no_confirm_ui == []
    if db_connect_called:
        db_connect.assert_called_once_with(pg_instance)
    if settings_awaited:
        settings.assert_awaited_once()

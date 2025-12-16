# SPDX-FileCopyrightText: 2021 Dalibo
#
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

import datetime
from pathlib import Path

import pytest
from psycopg.conninfo import conninfo_to_dict

from pglift import exceptions
from pglift.models import Instance, PostgreSQLInstance, system
from pglift.settings import PostgreSQLVersion, Settings


def test_instance_str(pg_version: PostgreSQLVersion, instance: Instance) -> None:
    assert str(instance) == f"{pg_version}/test"


def test_postgresqlinstance_qualname(
    pg_version: PostgreSQLVersion, pg_instance: PostgreSQLInstance
) -> None:
    assert pg_instance.qualname == f"{pg_version}-test"


def test_instance_name(instance: Instance) -> None:
    assert instance.name == "test"


def test_instance_qualname(pg_version: PostgreSQLVersion, instance: Instance) -> None:
    assert instance.qualname == f"{pg_version}-test"


@pytest.mark.parametrize(
    ["attrname", "expected_suffix"],
    [
        ("datadir", "srv/pgsql/{version}/test/data"),
        ("waldir", "srv/pgsql/{version}/test/wal"),
    ],
)
def test_postgresqlinstance_paths(
    pg_version: PostgreSQLVersion,
    pg_instance: PostgreSQLInstance,
    attrname: str,
    expected_suffix: str,
) -> None:
    path = getattr(pg_instance, attrname)
    assert path.match(expected_suffix.format(version=pg_version))


@pytest.mark.parametrize("dirtype", ["datadir", "waldir"])
def test_postgresqlinstance_creating_already_exists(
    pg_version: PostgreSQLVersion, settings: Settings, dirtype: str
) -> None:
    """PostgreSQLInstance.creating() raises InstanceAlreadyExists if datadir/waldir exist."""
    setting_dir, kind = {
        "datadir": (settings.postgresql.datadir, "DATA"),
        "waldir": (settings.postgresql.waldir, "WAL"),
    }[dirtype]
    name = "testing"
    dirpath = (
        Path(str(setting_dir).format(name=name, version=pg_version)) / "fake-lost+found"
    )
    dirpath.mkdir(parents=True)
    cm = PostgreSQLInstance.creating(name, pg_version, settings)
    with pytest.raises(
        exceptions.InstanceAlreadyExists,
        match=f"{kind} directory for instance {pg_version}/testing already exists",
    ):
        cm.__enter__()


def test_postgresqlinstance_invalid_version(settings: Settings) -> None:
    with pytest.raises(
        ValueError,
        match="version 13 not amongst 'postgresql.versions' setting: 14, 17",
    ):
        system.PostgreSQLInstance("versioned_instance", "13", settings)


def test_postgresqlinstance_system_lookup(
    settings: Settings, pg_instance: PostgreSQLInstance
) -> None:
    i = system.PostgreSQLInstance.system_lookup(
        pg_instance.name, pg_instance.version, settings
    )
    assert i == pg_instance


def test_instance_validate(pg_instance: PostgreSQLInstance) -> None:
    class Service:
        pass

    with pytest.raises(
        ValueError, match="values for 'services' field must be of distinct types"
    ):
        system.Instance(postgresql=pg_instance, services=[Service(), Service()])

    class Service2:
        pass

    i = system.Instance(postgresql=pg_instance, services=[Service(), Service2()])
    assert i.services


def test_instance_system_lookup(
    settings: Settings, instance: Instance, pg_instance: PostgreSQLInstance
) -> None:
    i = system.Instance.from_postgresql(pg_instance)
    assert i == instance

    i = system.Instance.system_lookup(pg_instance.name, pg_instance.version, settings)
    assert i == instance


def test_instance_system_lookup_misconfigured(
    settings: Settings, pg_version: PostgreSQLVersion, pg_instance: PostgreSQLInstance
) -> None:
    (pg_instance.datadir / "postgresql.conf").unlink()
    with pytest.raises(exceptions.InstanceNotFound, match=str(pg_instance)):
        system.Instance.system_lookup(pg_instance.name, pg_version, settings)


def test_check_instance(pg_version: PostgreSQLVersion, settings: Settings) -> None:
    instance = system.PostgreSQLInstance(
        name="exists", version=pg_version, settings=settings
    )
    with pytest.raises(exceptions.InstanceNotFound, match="data directory"):
        system.check_instance(instance)
    instance.datadir.mkdir(parents=True)
    with pytest.raises(exceptions.InstanceNotFound, match="PG_VERSION"):
        system.check_instance(instance)
    (instance.datadir / "PG_VERSION").write_text("42\n")
    with pytest.raises(
        exceptions.InvalidVersion, match=rf"version mismatch \(42 != {pg_version}\)"
    ):
        system.check_instance(instance)
    (instance.datadir / "PG_VERSION").write_text(pg_version)
    with pytest.raises(
        exceptions.InstanceNotFound,
        match=r"configuration file not found: .+ No such file or directory: '.+/postgresql.conf'",
    ):
        system.check_instance(instance)
    (instance.datadir / "postgresql.conf").touch()
    system.check_instance(instance)


def test_postgresqlinstance_port(pg_instance: PostgreSQLInstance) -> None:
    assert pg_instance.port == 999


def test_postgresqlinstance_socket_directory(pg_instance: PostgreSQLInstance) -> None:
    assert pg_instance.socket_directory == "/socks"

    (pg_instance.datadir / "postgresql.conf").write_text(
        "unix_socket_directories = '@a , b '\n"
    )
    assert pg_instance.socket_directory == "b"

    (pg_instance.datadir / "postgresql.conf").write_text("pif = paf\n")
    assert pg_instance.socket_directory is None


def test_postgresqlinstance_configuration(pg_instance: PostgreSQLInstance) -> None:
    assert pg_instance.configuration().as_dict() == {
        "port": 999,
        "unix_socket_directories": "/socks, /shoes",
    }


def test_postgresqlinstance_standby_for(
    pg_instance: PostgreSQLInstance, standby_pg_instance: PostgreSQLInstance
) -> None:
    assert not pg_instance.standby
    assert standby_pg_instance.standby
    assert conninfo_to_dict(standby_pg_instance.standby.primary_conninfo) == {
        "host": "/tmp",
        "port": "4242",
        "user": "pg",
    }
    assert standby_pg_instance.standby.user == "pg"
    assert standby_pg_instance.standby.slot == "aslot"


def test_databasedump_from_path() -> None:
    path = Path("/tmp/xyz.dump")
    assert system.DatabaseDump.from_path(path) is None
    path = Path("/tmp/mydb_2024-05-15T09:01:39.764144+00:00.sql")
    date = datetime.datetime(
        2024, 5, 15, 9, 1, 39, 764144, tzinfo=datetime.timezone.utc
    )
    assert system.DatabaseDump.from_path(path) == system.DatabaseDump(
        id="mydb_84b03a475e",
        dbname="mydb",
        date=date,
        path=path,
    )


def test_databasedump_build() -> None:
    date = datetime.datetime(2023, 3, 14, 0, 0, 0, tzinfo=datetime.timezone.utc)
    dump = system.DatabaseDump.build("postgres", date, Path("x"))
    assert "postgres_" in dump.id
    assert dump.dbname == "postgres"
    assert dump.date.isoformat() == "2023-03-14T00:00:00+00:00"
    assert dump.path == Path("x")

    dump = system.DatabaseDump.build("postgres", date, Path("y"))
    assert "postgres_" in dump.id
    assert dump.dbname == "postgres"
    assert dump.date.isoformat() == "2023-03-14T00:00:00+00:00"

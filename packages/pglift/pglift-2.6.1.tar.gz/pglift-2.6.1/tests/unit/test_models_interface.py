# SPDX-FileCopyrightText: 2021 Dalibo
#
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

import socket
from pathlib import Path
from typing import Any

import psycopg.conninfo
import pydantic
import pytest

from pglift import plugin_manager, types
from pglift.models import Instance, interface
from pglift.pgbackrest import base as pgbackrest_base
from pglift.prometheus.models import interface as prometheus_models
from pglift.settings import PostgreSQLVersion, Settings
from pglift.testutil import model_copy_validate


def test_instance_name() -> None:
    interface.Instance(name="without_dash", version="17")
    with pytest.raises(pydantic.ValidationError, match="should match pattern"):
        interface.Instance(name="with-dash", version="17")
    with pytest.raises(pydantic.ValidationError, match="should match pattern"):
        interface.Instance(name="with/slash", version="17")


def test_composite_instance_model(
    composite_instance_model: type[interface.Instance],
) -> None:
    assert not composite_instance_model.model_fields["pgbackrest"].is_required()
    assert not composite_instance_model.model_fields["patroni"].is_required()


def test_instance_version(settings: Settings, pg_version: PostgreSQLVersion) -> None:
    with types.validation_context(operation="create", settings=settings):
        i = interface.Instance.model_validate({"name": "foo"})
    assert i.version == pg_version
    i = interface.Instance.model_validate({"name": "foo", "version": "15"})
    assert i.version == "15"


def test_instance_settings_port(settings: Settings) -> None:
    with types.validation_context(operation="create", settings=settings):
        with pytest.raises(
            pydantic.ValidationError, match="'port' entry is disallowed"
        ):
            interface.Instance.model_validate(
                {"name": "foo", "settings": {"port": 1212}}
            )


@pytest.mark.parametrize(
    "pg_version, port",
    [
        ("17", 5555),  # custom postgresql.conf template
        ("14", 5432),
    ],
    ids=["site template", "default port"],
)
def test_instance_port_unset_available(
    settings: Settings, pg_version: str, port: int
) -> None:
    with types.validation_context(operation="create", settings=settings):
        with socket.socket() as s:
            try:
                s.bind(("", port))
            except OSError as e:
                pytest.skip(f"cannot use {port=}: {e}")
            s.listen()
            with pytest.raises(
                pydantic.ValidationError, match=f"port {port} already in use"
            ):
                interface.Instance.model_validate(
                    {"name": "foo", "version": pg_version}
                )

        interface.Instance.model_validate({"name": "foo", "version": pg_version})


def test_instance_no_password_required(settings: Settings) -> None:
    assert settings.postgresql.auth.local == "peer"
    with types.validation_context(operation="create", settings=settings):
        i = interface.Instance.model_validate({"name": "foo"})
        assert i.surole_password is None


@pytest.fixture
def postgresql_ref(tmp_path: Path) -> interface.PostgreSQLInstanceRef:
    return interface.PostgreSQLInstanceRef.model_validate(
        {
            "name": "original",
            "version": "16",
            "port": 123,
            "datadir": tmp_path,
        }
    )


def test_instance_password_required(
    settings: Settings, postgresql_ref: interface.PostgreSQLInstanceRef
) -> None:
    settings = model_copy_validate(
        settings,
        update={
            "postgresql": settings.postgresql.model_dump()
            | {"auth": {"local": "scram-sha-256"}}
        },
    )
    assert settings.postgresql.auth.local == "scram-sha-256"

    with types.validation_context(operation="create", settings=settings):
        i = interface.Instance.model_validate(
            {"name": "foo", "surole_password": "qwerty", "replrole_password": "poiuy"}
        )
        assert i.surole_password is not None

    expected_errors = {
        "surole_password": "Value error, a value is required per local authentication method 'scram-sha-256'",
    }
    with types.validation_context(operation="create", settings=settings):
        with pytest.raises(pydantic.ValidationError) as cm:
            interface.Instance.model_validate({"name": "foo"})
    assert {e["loc"][0]: e["msg"] for e in cm.value.errors()} == expected_errors

    # No validation when upgrading.
    with types.validation_context(operation="create", settings=settings):
        interface.Instance.model_validate(
            {"name": "upgrading", "upgrading_from": postgresql_ref}
        )

    with types.validation_context(operation="update", settings=settings):
        i = interface.Instance.model_validate({"name": "foo"})
        assert i.surole_password is None


def test_instance_creating_upgrading_from(
    pg_version: str, postgresql_ref: interface.PostgreSQLInstanceRef
) -> None:
    i = interface.Instance.model_validate(
        {"name": "up", "version": pg_version, "upgrading_from": postgresql_ref}
    )
    assert i.creating


def test_replication_slots_not_with_standby(pg_version: str) -> None:
    with pytest.raises(
        pydantic.ValidationError,
        match="replication slots cannot be set on a standby instance",
    ):
        interface.Instance.model_validate(
            {
                "name": "bad",
                "version": pg_version,
                "standby": {"primary_conninfo": "host=srv port=123"},
                "replication_slots": ["aslot"],
            }
        )


def test_replication_slots_with_promoted_standby(pg_version: str) -> None:
    i = interface.Instance.model_validate(
        {
            "name": "promoted",
            "version": pg_version,
            "standby": {"primary_conninfo": "host=srv port=123", "status": "promoted"},
            "replication_slots": ["aslot"],
        }
    )
    assert i.model_dump(include={"name", "standby", "replication_slots"}) == {
        "name": "promoted",
        "standby": {
            "primary_conninfo": "host=srv port=123",
            "slot": None,
            "replication_lag": None,
            "wal_sender_state": None,
            "wal_replay_pause_state": "not paused",
        },
        "replication_slots": [{"name": "aslot"}],
    }


def test_replication_slots_with_primary(pg_version: str) -> None:
    i = interface.Instance.model_validate(
        {
            "name": "primary",
            "version": pg_version,
            "replication_slots": ["aslot"],
        }
    )
    assert i.model_dump(include={"name", "standby", "replication_slots"}) == {
        "name": "primary",
        "standby": None,
        "replication_slots": [{"name": "aslot"}],
    }


def test_instance_composite_service(settings: Settings, pg_version: str) -> None:
    pm = plugin_manager(settings)
    Instance = interface.Instance.composite(pm)
    with pytest.raises(
        ValueError,
        match=r"validation error for Instance\nprometheus\n  Input should be a valid dictionary",
    ):
        m = Instance.model_validate(
            {
                "name": "test",
                "version": pg_version,
                "prometheus": None,
                "pgbackrest": {"stanza": "mystanza"},
            }
        )

    m = Instance.model_validate(
        {
            "name": "test",
            "version": pg_version,
            "prometheus": {"port": 123},
            "pgbackrest": {"stanza": "mystanza"},
        }
    )
    s = m.service(prometheus_models.Service)
    assert s.port == 123

    class MyService(types.Service, service_name="notfound"):
        pass

    with pytest.raises(ValueError, match="notfound"):
        m.service(MyService)


def test_role_state() -> None:
    assert interface.Role(name="exist").state == "present"
    assert interface.Role(name="notexist", state="absent").state == "absent"
    assert interface.RoleDropped(name="dropped").state == "absent"
    with pytest.raises(pydantic.ValidationError, match=r"Input should be 'absent'"):
        interface.RoleDropped(name="p", state="present")


def test_database_clone() -> None:
    with pytest.raises(pydantic.ValidationError, match="Input should be a valid URL"):
        interface.Database.model_validate(
            {"name": "cloned_db", "clone": {"dsn": "blob"}}
        )

    expected = {
        "dbname": "base",
        "host": "server",
        "password": "pwd",
        "user": "dba",
    }
    db = interface.Database.model_validate(
        {"name": "cloned_db", "clone": {"dsn": "postgres://dba:pwd@server/base"}}
    )
    assert db.clone is not None
    assert psycopg.conninfo.conninfo_to_dict(str(db.clone.dsn)) == expected


def test_database_schemas_owner() -> None:
    db = interface.Database.model_validate(
        {
            "name": "db",
            "owner": "dba",
            "schemas": ["foo", {"name": "bar", "owner": "postgres"}],
        }
    )
    assert db.model_dump()["schemas"] == [
        {"name": "foo", "owner": "dba"},
        {"name": "bar", "owner": "postgres"},
    ]


def test_connectionstring() -> None:
    assert (
        interface.ConnectionString(conninfo="host=x dbname=y").conninfo
        == "dbname=y host=x"
    )

    with pytest.raises(
        pydantic.ValidationError, match="forbidden connection option 'password'"
    ):
        interface.ConnectionString(conninfo="host=x password=s")


@pytest.mark.parametrize(
    "value, expected",
    [
        ("host=x password=y", {"conninfo": "host=x", "password": "y"}),
        ("host=y", {"conninfo": "host=y", "password": None}),
    ],
)
def test_connectionstring_parse(value: str, expected: dict[str, Any]) -> None:
    parsed = interface.ConnectionString.parse(value)
    assert {
        "conninfo": parsed.conninfo,
        "password": parsed.password.get_secret_value() if parsed.password else None,
    } == expected


@pytest.mark.parametrize(
    "conninfo, password, full_conninfo",
    [
        ("host=x", "secret", "host=x password=secret"),
        ("host=y", None, "host=y"),
    ],
)
def test_connectionstring_full_conninfo(
    conninfo: str, password: str | None, full_conninfo: str
) -> None:
    assert (
        interface.ConnectionString(conninfo=conninfo, password=password).full_conninfo
        == full_conninfo
    )


def test_privileges_sorted() -> None:
    p = interface.Privilege(  # type: ignore[call-arg]
        database="postgres",
        schema="main",
        object_type="table",
        object_name="foo",
        role="postgres",
        privileges=["select", "delete", "update"],
        column_privileges={"postgres": ["update", "delete", "reference"]},
    )
    assert p.model_dump(by_alias=True) == {
        "column_privileges": {"postgres": ["delete", "reference", "update"]},
        "database": "postgres",
        "object_name": "foo",
        "object_type": "table",
        "privileges": ["delete", "select", "update"],
        "role": "postgres",
        "schema": "main",
    }


def test_pgbackrest_service_validator(
    settings: Settings, pg_version: str, instance: Instance
) -> None:
    pm = plugin_manager(settings)
    Instance = interface.Instance.composite(pm)

    # No stanza configured yet, doesn't raise a validation error
    with types.validation_context(operation="create", settings=settings):
        Instance.model_validate(
            {
                "name": "test",
                "version": pg_version,
                "pgbackrest": {"stanza": "mystanza"},
            }
        )

    # Stanza already bound to an other instance, raises a validation error
    assert settings.pgbackrest is not None
    stanza_config = (
        pgbackrest_base.config_directory(settings.pgbackrest)
        / f"{instance.name}-stanza.conf"
    )
    stanza_config.touch()
    stanza_config.write_text("[mystanza]\npg1-path = /some/path/to/datadir\n")

    with (
        types.validation_context(operation="create", settings=settings),
        pytest.raises(
            pydantic.ValidationError, match="already bound to another instance"
        ),
    ):
        Instance.model_validate(
            {
                "name": "test",
                "version": pg_version,
                "pgbackrest": {"stanza": "mystanza"},
            }
        )

    # Stanza already bound to the same instance (ie. same datadir used for pgN-path)
    # Doesn't raise a validation error
    datadir = str(settings.postgresql.datadir).format(version=pg_version, name="test")
    stanza_config.write_text(f"[otherstanza]\npg1-path = {datadir}\n")
    with types.validation_context(operation="create", settings=settings):
        Instance.model_validate(
            {
                "name": "test",
                "version": pg_version,
                "pgbackrest": {"stanza": "otherstanza"},
            }
        )

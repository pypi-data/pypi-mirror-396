# SPDX-FileCopyrightText: 2025 Dalibo
#
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

from typing import Any, TypeVar

import pydantic

from pglift.models import system
from pglift.pgbackrest.models import system as pgbackrest_models
from pglift.prometheus import impl as prometheus_mod
from pglift.prometheus.models import system as prometheus_models
from pglift.settings import PostgreSQLVersion, Settings
from pglift.temboard import impl as temboard_mod
from pglift.temboard.models import system as temboard_models

M = TypeVar("M", bound=pydantic.BaseModel)


def model_copy_validate(model: M, update: dict[str, Any]) -> M:
    """Like BaseModel.copy(), but with validation (and default value setting)."""
    return model.__class__.model_validate(
        dict(model.model_dump(by_alias=True), **update)
    )


def pg_instance(
    name: str, version: PostgreSQLVersion, postgresql_conf: str, settings: Settings
) -> system.PostgreSQLInstance:
    pginstance = system.PostgreSQLInstance(
        name=name, version=version, settings=settings
    )
    assert not pginstance.datadir.exists()
    pginstance.datadir.mkdir(parents=True)
    (pginstance.datadir / "PG_VERSION").write_text(pginstance.version)
    (pginstance.datadir / "postgresql.conf").write_text(postgresql_conf)
    (pginstance.datadir / "pg_hba.conf").write_text(
        "# pg_hba.conf\n"
        "# TYPE  DATABASE        USER            ADDRESS                 METHOD\n"
        "local all postgres peer\n"
    )
    (pginstance.datadir / "pg_ident.conf").write_text(
        "# pg_ident.conf\n# MAPNAME  SYSTEM-USERNAME  PG-USERNAME\nmymap test dba\n"
    )
    system.check_instance(pginstance)
    return pginstance


def instance(
    settings: Settings, pginstance: system.PostgreSQLInstance
) -> system.Instance:
    name, version = pginstance.name, pginstance.version

    # Services are looked-up in reverse order of plugin registration.
    services: list[Any] = []

    assert settings.temboard is not None
    temboard_port = 2345
    temboard = temboard_models.Service(
        name=f"{version}-{name}",
        settings=settings.temboard,
        port=temboard_port,
        password=pydantic.SecretStr("dorade"),
    )
    services.append(temboard)

    assert settings.prometheus is not None
    prometheus_port = 9817
    prometheus = prometheus_models.Service(
        name=f"{version}-{name}",
        settings=settings.prometheus,
        port=prometheus_port,
        password=pydantic.SecretStr("truite"),
    )
    services.append(prometheus)

    assert settings.pgbackrest is not None
    pgbackrest = pgbackrest_models.Service(
        stanza=f"{name}-stanza",
        path=settings.pgbackrest.configpath / "conf.d" / f"{name}-stanza.conf",
        datadir=pginstance.datadir,
    )
    services.append(pgbackrest)

    prometheus_config = prometheus_mod._configpath(
        pginstance.qualname, settings.prometheus
    )
    assert not prometheus_config.exists()
    prometheus_config.parent.mkdir(parents=True, exist_ok=True)
    prometheus_config.write_text(
        f"DATA_SOURCE_NAME=dbname=postgres port={pginstance.port} host={settings.postgresql.socket_directory} user=monitoring sslmode=disable password=truite\n"
        f"POSTGRES_EXPORTER_OPTS='--log.level=info --web.listen-address :{prometheus.port}'"
    )

    temboard_config = temboard_mod._configpath(pginstance.qualname, settings.temboard)
    assert not temboard_config.exists()
    temboard_config.parent.mkdir(parents=True, exist_ok=True)
    temboard_config.write_text(
        "\n".join(
            [
                "[temboard]",
                f"port = {temboard.port}",
                "ui_url = https://0.0.0.0:8888",
                "[postgresql]",
                f"port = {pginstance.port}",
                f"host = {settings.postgresql.socket_directory}",
                "user = temboardagent",
                "password = dorade",
            ]
        )
    )

    stanza_config = pgbackrest.path
    assert not stanza_config.exists()
    stanza_config.parent.mkdir(parents=True, exist_ok=True)
    stanza_config.write_text(
        "\n".join(
            [
                f"[{pgbackrest.stanza}]",
                f"pg1-path = {pginstance.datadir}",
                f"pg1-port = {pginstance.port}",
                "pg1-user = backup",
            ]
        )
    )

    assert settings.logrotate
    settings.logrotate.configdir.mkdir(parents=True, exist_ok=True)
    assert settings.rsyslog
    settings.rsyslog.configdir.mkdir(parents=True, exist_ok=True)

    return system.Instance(postgresql=pginstance, services=services)

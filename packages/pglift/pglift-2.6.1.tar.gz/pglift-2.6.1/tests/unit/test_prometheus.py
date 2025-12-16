# SPDX-FileCopyrightText: 2021 Dalibo
#
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

from pathlib import Path

import pydantic
import pytest

from pglift import exceptions
from pglift.models import Instance
from pglift.prometheus import impl as prometheus
from pglift.prometheus import systemd_unit_templates, systemd_units
from pglift.prometheus.models import Service
from pglift.prometheus.models.interface import PostgresExporter
from pglift.settings import Settings, _prometheus


@pytest.fixture
def prometheus_settings(settings: Settings) -> _prometheus.Settings:
    assert settings.prometheus is not None
    return settings.prometheus


def test_systemd_units() -> None:
    assert systemd_units() == ["pglift-postgres_exporter@.service"]


def test_install_systemd_unit_template(
    settings: Settings, prometheus_execpath: Path | None
) -> None:
    assert prometheus_execpath
    ((name, content),) = list(systemd_unit_templates(settings=settings))
    assert name == "pglift-postgres_exporter@.service"
    lines = content.splitlines()
    assert (
        f"EnvironmentFile=-{settings.prefix}/etc/prometheus/postgres_exporter-%i.conf"
        in lines
    )
    assert f"ExecStart={prometheus_execpath} $POSTGRES_EXPORTER_OPTS" in lines


@pytest.mark.parametrize(
    "opts, listen_address",
    [
        ("--log.level=info --web.listen-address=:123 --log.format json", ":123"),
        ("--web.listen-address srv.net:8989 --log.format json", "srv.net:8989"),
        ("----log.format json", None),
    ],
)
def test_listen_address_rgx(opts: str, listen_address: str | None) -> None:
    m = prometheus.listen_address_rgx.search(opts)
    if listen_address is None:
        assert m is None
    else:
        assert m and m.group(1) == listen_address


@pytest.mark.parametrize(
    "content, args",
    [
        (
            "\n".join(
                [
                    "DATA_SOURCE_NAME=postgresql://prometheus@:5432/postgres",
                    "POSTGRES_EXPORTER_OPTS='--log.level=info --web.listen-address :9187'",
                ]
            ),
            [
                "--log.level=info",
                "--web.listen-address",
                ":9187",
            ],
        ),
        (
            "\n".join(
                [
                    "DATA_SOURCE_NAME=postgresql://prometheus@:5432/postgres",
                    "POSTGRES_EXPORTER_OPTS=--log.level=warning --log.format json",
                    "PG_EXPORTER_WEB_LISTEN_ADDRESS=:9187",
                ]
            ),
            [
                "--log.level=warning",
                "--log.format",
                "json",
                "--web.listen-address",
                ":9187",
            ],
        ),
    ],
)
def test__args(tmp_path: Path, content: str, args: list[str]) -> None:
    execpath = tmp_path / "pge"
    configpath = tmp_path / "p.conf"
    configpath.write_text(content)
    config = prometheus._config(configpath)
    assert prometheus._args(execpath, config) == [str(execpath)] + args


def test__args_duplicate_listen(tmp_path: Path) -> None:
    execpath = tmp_path / "pge"
    configpath = tmp_path / "p.conf"
    configpath.write_text(
        "\n".join(
            [
                "PG_EXPORTER_WEB_LISTEN_ADDRESS=:9187",
                'POSTGRES_EXPORTER_OPTS="--log.level=info --web.listen-address :9899 --log.level json"',
            ]
        )
    )
    config = prometheus._config(configpath)
    with pytest.raises(exceptions.ConfigurationError, match="defined both in"):
        prometheus._args(execpath, config)


def test__args_malformatter_opts(tmp_path: Path) -> None:
    execpath = tmp_path / "pge"
    configpath = tmp_path / "p.conf"
    configpath.write_text(
        "\n".join(
            [
                "DATA_SOURCE_NAME=postgresql://prometheus@:5432/postgres?host=%2Frun%2Fuser%2F1000%2Fpglift%2Fpostgresql&sslmode=disable",
                "PG_EXPORTER_WEB_LISTEN_ADDRESS=:9187",
                "POSTGRES_EXPORTER_OPTS='--log.level=info x \"a'",
            ]
        )
    )
    config = prometheus._config(configpath)
    with pytest.raises(
        exceptions.ConfigurationError,
        match="malformatted POSTGRES_EXPORTER_OPTS parameter: '--log.level=info x \"a'",
    ):
        prometheus._args(execpath, config)


def test_service(instance: Instance) -> None:
    s = instance.service(Service)
    assert s is not None
    assert s.name == instance.qualname
    assert s.port == 9817
    assert s.logfile() is None  # type: ignore[func-returns-value]


def test_port(prometheus_settings: _prometheus.Settings, instance: Instance) -> None:
    configpath = prometheus._configpath(instance.qualname, prometheus_settings)
    config = prometheus._config(configpath)
    port = prometheus.port(config)
    assert port == 9817

    configpath.write_text("\nempty\n# comment\n")
    config = prometheus._config(configpath)
    with pytest.raises(LookupError, match="listen-address not found"):
        prometheus.port(config)

    configpath.write_text("\nPG_EXPORTER_WEB_LISTEN_ADDRESS=42\n")
    config = prometheus._config(configpath)
    with pytest.raises(
        LookupError, match="malformatted PG_EXPORTER_WEB_LISTEN_ADDRESS parameter"
    ):
        prometheus.port(config)

    configpath.write_text(
        "# postgres_exporter config\nPG_EXPORTER_WEB_LISTEN_ADDRESS=monitor.example.com:9816\n"
    )
    config = prometheus._config(configpath)
    assert prometheus.port(config) == 9816

    configpath.write_text(
        "\nPOSTGRES_EXPORTER_OPTS=--web.listen-address=monitor.example.com:9816\n"
    )
    config = prometheus._config(configpath)
    assert prometheus.port(config) == 9816

    configpath.write_text("\nPOSTGRES_EXPORTER_OPTS=--log.format=json\n")
    config = prometheus._config(configpath)
    with pytest.raises(LookupError, match="listen-address not found"):
        prometheus.port(config)


def test_password(
    prometheus_settings: _prometheus.Settings, instance: Instance
) -> None:
    configpath = prometheus._configpath(instance.qualname, prometheus_settings)
    config = prometheus._config(configpath)
    password = prometheus.password(config)
    assert password and password.get_secret_value() == "truite"

    configpath = Path(
        str(prometheus_settings.configpath).format(name=instance.qualname)
    )
    configpath.write_text("\nempty\n")
    config = prometheus._config(configpath)
    with pytest.raises(LookupError, match="DATA_SOURCE_NAME not found"):
        prometheus.password(config)

    configpath.write_text("\nDATA_SOURCE_NAME=foo=bar\n")
    config = prometheus._config(configpath)
    with pytest.raises(LookupError, match="malformatted DATA_SOURCE_NAME"):
        prometheus.password(config)


def test_exists(prometheus_settings: _prometheus.Settings, instance: Instance) -> None:
    assert prometheus.exists(instance.qualname, prometheus_settings)


def test_postgresexporter_name() -> None:
    PostgresExporter(name="without-slash", dsn="", port=12)
    with pytest.raises(pydantic.ValidationError, match="should match pattern"):
        PostgresExporter(name="with/slash", dsn="", port=12)


def test_postgresexporter_dsn() -> None:
    m = PostgresExporter(name="12-x", dsn="dbname=postgres", port=9876)
    assert m.dsn == "dbname=postgres"
    with pytest.raises(pydantic.ValidationError):
        PostgresExporter(name="test", dsn="x=y", port=9876)


@pytest.mark.anyio
async def test_apply(
    settings: Settings, instance: Instance, prometheus_settings: _prometheus.Settings
) -> None:
    m = PostgresExporter(name=instance.qualname, dsn="", port=123)
    with pytest.raises(exceptions.InstanceStateError, match="exists locally"):
        await prometheus.apply(m, settings, prometheus_settings)

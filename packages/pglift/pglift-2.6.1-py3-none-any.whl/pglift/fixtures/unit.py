# SPDX-FileCopyrightText: 2025 Dalibo
#
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

from collections.abc import Iterator
from pathlib import Path
from unittest.mock import patch

import pytest

from .. import testutil
from ..models.system import Instance, PostgreSQLInstance
from ..settings import PostgreSQLVersion, Settings, _systemd


@pytest.fixture
def config_dir(tmp_path_factory: pytest.TempPathFactory) -> Path:
    """An empty PGLIFT_CONFIG_DIR, to prevent usage of user's site configuration."""
    return tmp_path_factory.mktemp("pglift-config-dir")


@pytest.fixture(autouse=True)
def _pglift_env(config_dir: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Setup pglift environment (e.g. PGLIFT_CONFIG_DIR) for tests."""
    monkeypatch.setenv("PGLIFT_CONFIG_DIR", str(config_dir))


@pytest.fixture
def pg_version() -> PostgreSQLVersion:
    return "17"


@pytest.fixture
def bin_path(tmp_path: Path) -> Path:
    p = tmp_path / "bin"
    p.mkdir()
    return p


@pytest.fixture
def pgbackrest_execpath(bin_path: Path) -> Path:
    execpath = bin_path / "pgbackrest"
    execpath.touch(0o700)
    execpath.write_text("#!/bin/sh\nexit 1\n")
    return execpath


@pytest.fixture
def prometheus_execpath(bin_path: Path) -> Path:
    execpath = bin_path / "postgres_exporter"
    execpath.touch(0o700)
    execpath.write_text("#!/bin/sh\nexit 1\n")
    return execpath


@pytest.fixture
def temboard_execpath(bin_path: Path) -> Path:
    execpath = bin_path / "temboard-agent"
    execpath.touch(0o700)
    execpath.write_text("#!/bin/sh\nexit 1\n")
    return execpath


@pytest.fixture
def patroni_execpaths(bin_path: Path) -> tuple[Path, Path]:
    execpath = bin_path / "patroni"
    execpath.touch(0o700)
    execpath.write_text(
        "\n".join(
            [
                "#!/bin/sh",
                'if [ "$1" = "--validate-config" ]',
                "then",
                "  echo 'test test test'",
                "fi",
                "exit 1",
            ]
        )
    )
    ctlpath = bin_path / "patronictl"
    ctlpath.touch(0o700)
    ctlpath.write_text("#!/bin/sh\nexit 1\n")
    return execpath, ctlpath


@pytest.fixture
def systemctl(tmp_path: Path) -> Iterator[str]:
    p = str(tmp_path / "systemctl")
    with patch("pglift.settings._systemd.Settings.systemctl", create=True, new=p):
        yield p


@pytest.fixture
def systemd_tmpfiles(tmp_path: Path) -> Iterator[str]:
    # create a file to make field / settings validation works (e.g. on system
    # without systemd).
    p = str(tmp_path / "systemd-tmpfiles")
    with patch(
        "pglift.settings._systemd.Settings.systemd_tmpfiles", create=True, new=p
    ):
        yield p


@pytest.fixture
def systemd_settings(
    tmp_path: Path,
    systemctl: str,  # noqa: ARG001
    systemd_tmpfiles: str,  # noqa: ARG001
) -> _systemd.Settings:
    return _systemd.Settings.model_validate({"unit_path": str(tmp_path / "systemd")})


@pytest.fixture
def postgresql_bindir(tmp_path: Path) -> Iterator[str]:
    bindir = str(tmp_path / "postgresql" / "{version}" / "bin")
    with patch(
        "pglift.settings._postgresql._postgresql_bindir", return_value=bindir
    ) as p:
        yield bindir
    assert p.called


@pytest.fixture
def settings(
    tmp_path: Path,
    postgresql_bindir: str,
    patroni_execpaths: tuple[Path, Path],
    pgbackrest_execpath: Path,
    prometheus_execpath: Path,
    temboard_execpath: Path,
    systemd_settings: _systemd.Settings,
) -> Settings:
    passfile = tmp_path / "pgass"
    passfile.touch()
    signing_key = tmp_path / "signing-public.pem"
    signing_key.touch()
    ssl_cert_file = tmp_path / "temboard-agent.pem"
    ssl_cert_file.touch()
    ssl_key_file = tmp_path / "temboard-agent.key"
    ssl_key_file.touch()
    ssl_ca_cert_file = tmp_path / "mycacert.pem"
    ssl_ca_cert_file.touch()

    def pg_bindir(path: Path, version: int) -> Path:
        """Make a bindir with minimal versions of pg_* executables.

        - pg_ctl should work for --version and status
        - pg_checksums returns 0, as it's invoked upon instances._get()
        - psql exists, but always fails
        - pg_isready returns 1
        """
        path.mkdir(parents=True)
        pg_ctl = path / "pg_ctl"
        pg_ctl.touch(mode=0o700)
        pg_ctl.write_text(
            "\n".join(
                [
                    "#!/bin/sh",
                    "case $1 in",
                    "  --version)",
                    f"     echo 'pg_ctl (PostgreSQL) {version}.1'",
                    "     exit 0",
                    "     ;;",
                    "  status)",
                    '     test -d "$3" || exit 4',  # data directory not found
                    "     exit 3",  # not running
                    "     ;;",
                    "  *)",
                    '     echo "unexpected invocation pg_ctl $1" >&2',
                    "     exit 1",
                    "     ;;",
                    "esac",
                ]
            )
        )

        pg_checksums = path / "pg_checksums"
        pg_checksums.touch(mode=0o700)
        pg_checksums.write_text("#!/bin/sh\nexit 0")

        pg_controldata = path / "pg_controldata"
        pg_controldata.touch(mode=0o700)
        pg_controldata.write_text(
            "\n".join(
                [
                    "#!/bin/sh",
                    'echo "Data page checksum version:           1"',
                    "exit 0",
                ]
            )
        )

        psql = path / "psql"
        psql.touch(mode=0o700)
        psql.write_text(
            "\n".join(
                ["#!/bin/sh", 'echo "unexpected psql $* invocation" >&2', "exit 1"]
            )
        )

        pg_isready = path / "pg_isready"
        pg_isready.touch(mode=0o700)
        pg_isready.write_text("#!/bin/sh\nexit 1")

        return path

    pg14_bindir = pg_bindir(tmp_path / "pgsql-14" / "bin", 14)
    pg_bindir(Path(postgresql_bindir.format(version=17)), 17)
    patroni_restapi_certfile = tmp_path / "patroni-restapi.pem"
    patroni_restapi_certfile.touch()
    crldir = tmp_path / "crls"
    crldir.mkdir()
    obj = {
        "prefix": str(tmp_path),
        "run_prefix": str(tmp_path / "run"),
        "postgresql": {
            "auth": {
                "local": "peer",
                "host": "password",
                "passfile": str(passfile),
            },
            "default_version": "17",
            "versions": [
                {"version": "14", "bindir": str(pg14_bindir)},
            ],
            "replrole": "replication",
        },
        "systemd": systemd_settings,
        "service_manager": None,
        "scheduler": None,
        "tmpfiles_manager": None,
        "patroni": {
            "execpath": patroni_execpaths[0],
            "ctlpath": patroni_execpaths[1],
            "etcd": {
                "hosts": ["etcd1:123", "etcd2:456"],
            },
            "postgresql": {
                "connection": {
                    "ssl": {
                        "mode": "verify-ca",
                        "crldir": crldir,
                    },
                },
                "use_pg_rewind": True,
            },
            "restapi": {
                "certfile": patroni_restapi_certfile,
                "verify_client": "optional",
            },
        },
        "pgbackrest": {
            "execpath": pgbackrest_execpath,
            "repository": {"mode": "path", "path": tmp_path / "backups"},
        },
        "prometheus": {"execpath": prometheus_execpath},
        "logrotate": {},
        "rsyslog": {},
        "temboard": {
            "execpath": temboard_execpath,
            "ui_url": "https://0.0.0.0:8888",
            "signing_key": str(signing_key),
            "certificate": {
                "ca_cert": str(ssl_ca_cert_file),
                "cert": str(ssl_cert_file),
                "key": str(ssl_key_file),
            },
        },
        "powa": {},
    }
    settings = Settings.model_validate(obj)
    assert settings.postgresql.bindir == postgresql_bindir
    assert {v.version for v in settings.postgresql.versions} == {"14", "17"}
    return settings


@pytest.fixture
def postgresql_conf() -> str:
    return "\n".join(
        [
            "port = 999",
            "unix_socket_directories = /socks, /shoes",
            "# backslash_quote = 'safe_encoding'",
        ]
    )


@pytest.fixture
def pg_instance(
    pg_version: PostgreSQLVersion, postgresql_conf: str, settings: Settings
) -> PostgreSQLInstance:
    return testutil.pg_instance("test", pg_version, postgresql_conf, settings)


@pytest.fixture
def instance(settings: Settings, pg_instance: PostgreSQLInstance) -> Instance:
    return testutil.instance(settings, pg_instance)


@pytest.fixture
def instance2(
    pg_version: PostgreSQLVersion, postgresql_conf: str, settings: Settings
) -> Instance:
    pg_instance = testutil.pg_instance("test2", pg_version, postgresql_conf, settings)
    return testutil.instance(settings, pg_instance)

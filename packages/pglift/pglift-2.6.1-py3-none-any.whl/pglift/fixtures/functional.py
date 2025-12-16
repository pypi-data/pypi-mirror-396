# SPDX-FileCopyrightText: 2025 Dalibo
#
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

import itertools
import shutil
import tempfile
from pathlib import Path

import pytest
from anyio.pytest_plugin import FreePortFactory
from trustme import CA

from .etcd import Etcd
from .types import CertFactory, Certificate


def pytest_addoption(parser: pytest.Parser) -> None:
    parser.addoption(
        "--no-plugins",
        action="store_true",
        default=False,
        help="Run tests without any pglift plugin loaded.",
    )


@pytest.fixture(scope="session")
def no_plugins(request: pytest.FixtureRequest) -> bool:
    value = request.config.option.no_plugins
    assert isinstance(value, bool)
    return value


@pytest.fixture(scope="session")
def pgbackrest_execpath(no_plugins: bool) -> Path | None:
    if no_plugins:
        return None
    if (path := shutil.which("pgbackrest")) is not None:
        return Path(path)
    return None


@pytest.fixture(scope="session")
def pgbackrest_available(pgbackrest_execpath: Path | None) -> bool:
    return pgbackrest_execpath is not None


@pytest.fixture(scope="session")
def pg_back_execpath(no_plugins: bool) -> Path | None:
    if no_plugins:
        return None
    if (path := shutil.which("pg_back")) is not None:
        return Path(path)
    return None


@pytest.fixture(scope="session")
def prometheus_execpath(no_plugins: bool) -> Path | None:
    if no_plugins:
        return None
    for name in ("prometheus-postgres-exporter", "postgres_exporter"):
        path = shutil.which(name)
        if path is not None:
            return Path(path)
    return None


@pytest.fixture(scope="session")
def temboard_execpath(no_plugins: bool) -> Path | None:
    if no_plugins:
        return None
    path = shutil.which("temboard-agent")
    if path is not None:
        return Path(path)
    return None


@pytest.fixture(scope="session")
def patroni_execpaths(no_plugins: bool) -> tuple[Path, Path] | None:
    if no_plugins:
        return None
    patroni, patronictl = shutil.which("patroni"), shutil.which("patronictl")
    if patroni is not None and patronictl is not None:
        return Path(patroni), Path(patronictl)
    return None


@pytest.fixture(scope="package")
def etcd_host(
    tmp_path_factory: pytest.TempPathFactory,
    free_tcp_port_factory: FreePortFactory,
    ca: CA,
) -> Etcd | None:
    if (p := shutil.which("etcd")) is None:
        return None
    execdir = Path(p).parent
    if not (execdir / "etcdctl").exists():
        pytest.skip("etcdctl executable not found")
    return Etcd(
        execdir=execdir,
        name="pglift-tests",
        basedir=tmp_path_factory.mktemp("etcd"),
        client_port=free_tcp_port_factory(),
        peer_port=free_tcp_port_factory(),
        ca=ca,
    )


@pytest.fixture(scope="package")
def ca() -> CA:
    return CA(organization_name="dalibo", organization_unit_name="pglift")


@pytest.fixture(scope="package")
def _ssldir(tmp_path_factory: pytest.TempPathFactory) -> Path:
    return tmp_path_factory.mktemp("ssl")


@pytest.fixture(scope="package")
def ca_cert(_ssldir: Path, ca: CA) -> Path:
    p = _ssldir / "root.crt"
    ca.cert_pem.write_to_path(p)
    return p


@pytest.fixture(scope="package")
def ca_private_key(_ssldir: Path, ca: CA) -> Path:
    p = _ssldir / "root.key"
    p.touch(mode=0o600)
    ca.private_key_pem.write_to_path(p)
    return p


@pytest.fixture(scope="package")
def cert_factory(ca: CA, _ssldir: Path) -> CertFactory:
    itertools.count()

    def factory(*identities: str, common_name: str | None = None) -> Certificate:
        cert = ca.issue_cert(*identities, common_name=common_name)
        with tempfile.NamedTemporaryFile(
            dir=_ssldir, delete=False, suffix=".pem"
        ) as certfile:
            certfile.write(cert.cert_chain_pems[0].bytes())
        with tempfile.NamedTemporaryFile(
            dir=_ssldir, delete=False, suffix=".pem"
        ) as keyfile:
            keyfile.write(cert.private_key_pem.bytes())
        return Certificate(path=Path(certfile.name), private_key=Path(keyfile.name))

    return factory

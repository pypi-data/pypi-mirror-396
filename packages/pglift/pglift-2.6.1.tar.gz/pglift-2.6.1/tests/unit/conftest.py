# SPDX-FileCopyrightText: 2025 Dalibo
#
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

from collections.abc import Iterator
from pathlib import Path

import pydantic
import pytest

from pglift import plugin_manager, testutil
from pglift.models import interface
from pglift.models.system import Instance, PostgreSQLInstance
from pglift.pm import PluginManager
from pglift.settings import PostgreSQLVersion, Settings, _postgresql
from pglift.system.imfs import InMemoryFS

pytest_plugins = [
    "pglift.fixtures",
    "pglift.fixtures.unit",
]


def pytest_addoption(parser: pytest.Parser) -> None:
    parser.addoption(
        "--write-changes",
        action="store_true",
        default=False,
        help="Write-back changes to test data.",
    )


@pytest.fixture(scope="package")
def anyio_backend() -> str:
    return "asyncio"


@pytest.fixture
def write_changes(request: pytest.FixtureRequest) -> bool:
    value = request.config.option.write_changes
    assert isinstance(value, bool)
    return value


@pytest.fixture
def datadir() -> Path:
    """Path to directory containing test data files."""
    return Path(__file__).parent / "data"


@pytest.fixture
def config_dir(datadir: Path) -> Path:
    """A test-local PGLIFT_CONFIG_DIR."""
    return datadir / "config"


@pytest.fixture
def expected_dir(datadir: Path) -> Path:
    """Path to directory containing "expected" test data files."""
    return datadir / "expected"


@pytest.fixture
def pm(settings: Settings) -> PluginManager:
    return plugin_manager(settings)


@pytest.fixture
def nohook(pm: PluginManager) -> Iterator[None]:
    unregistered = pm.unregister_all()
    yield
    for plugin in unregistered:
        pm.register(plugin)


@pytest.fixture
def composite_instance_model(pm: PluginManager) -> type[interface.Instance]:
    return interface.Instance.composite(pm)


@pytest.fixture
def composite_role_model(pm: PluginManager) -> type[interface.Role]:
    return interface.Role.composite(pm)


@pytest.fixture
def instance_manifest(
    composite_instance_model: type[interface.Instance], pg_version: PostgreSQLVersion
) -> interface.Instance:
    return composite_instance_model(
        name="test",
        version=pg_version,
        surole_password=pydantic.SecretStr("p0st.g're$"),
        replrole_password=pydantic.SecretStr("repl1&c"),
        settings={"shared_preload_libraries": "passwordcheck"},
        pgbackrest={"stanza": "test-stanza"},
    )


@pytest.fixture
def standby_pg_instance(
    pg_version: PostgreSQLVersion, postgresql_conf: str, settings: Settings
) -> PostgreSQLInstance:
    pg_instance = testutil.pg_instance("standby", pg_version, postgresql_conf, settings)
    (pg_instance.datadir / "standby.signal").write_text("")
    (pg_instance.datadir / "postgresql.auto.conf").write_text(
        "\n".join(
            [
                "primary_conninfo = 'host=/tmp port=4242 user=pg'",
                "primary_slot_name = aslot",
            ]
        )
    )
    assert pg_instance.standby is not None
    return pg_instance


@pytest.fixture
def standby_instance(
    settings: Settings, standby_pg_instance: PostgreSQLInstance
) -> Instance:
    return testutil.instance(settings, standby_pg_instance)


@pytest.fixture
def bindir_template(tmp_path: Path) -> str:
    bindir = tmp_path / "17" / "bin"
    bindir.mkdir(parents=True)
    (bindir / "pg_ctl").touch(mode=0o755)
    return str(tmp_path / "{version}" / "bin")


@pytest.fixture
def postgresql_settings(bindir_template: str) -> _postgresql.Settings:
    return _postgresql.Settings(bindir=bindir_template)


@pytest.fixture
def memfs() -> Iterator[InMemoryFS]:
    value = InMemoryFS()
    yield value
    value.backend.store.clear()
    value.backend.pseudo_dirs.clear()

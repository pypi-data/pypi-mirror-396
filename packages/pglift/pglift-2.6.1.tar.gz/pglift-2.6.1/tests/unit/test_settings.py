# SPDX-FileCopyrightText: 2021 Dalibo
#
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

import json
from collections.abc import Mapping
from pathlib import Path
from typing import Annotated, Any
from unittest.mock import patch

import pytest
from pydantic import BaseModel, ValidationError
from pydantic_settings import BaseSettings

from pglift import exceptions
from pglift.settings import (
    Settings,
    SiteSettings,
    _patroni,
    _pgbackrest,
    _postgresql,
    _systemd,
    base,
)


class SubSubSub(BaseModel):
    cfg: Annotated[Path, base.ConfigPath] = Path("settings.json")


class SubSub(BaseModel):
    data: Annotated[Path, base.DataPath] = Path("things")
    config: SubSubSub = SubSubSub()


class Sub(BaseModel):
    sub: SubSub
    pid: Annotated[Path, base.RunPath] = Path("pid")


class S(BaseSettings):
    sub: Sub


def test_prefix_values() -> None:
    bases = {"prefix": Path("/opt"), "run_prefix": Path("/tmp")}
    values = base.prefix_values(S(sub=Sub(sub=SubSub())), bases)
    assert S.model_validate(values).model_dump() == {
        "sub": {
            "pid": Path("/tmp/pid"),
            "sub": {
                "config": {
                    "cfg": Path("/opt/etc/settings.json"),
                },
                "data": Path("/opt/srv/things"),
            },
        },
    }


def test_settings_sources(monkeypatch: pytest.MonkeyPatch) -> None:
    """Settings only uses "init" source, no env vars, in contrast with
    SiteSettings.
    """
    monkeypatch.setenv("pglift_prefix", "/srv/pglift")
    s = Settings()
    ss = SiteSettings()
    assert ss.prefix == Path("/srv/pglift")
    assert s.prefix != ss.prefix


def test_yaml_settings(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    bindir = tmp_path / "pgbin"
    bindir.mkdir()
    configdir = tmp_path / "pglift"
    configdir.mkdir()
    settings_fpath = configdir / "settings.yaml"
    settings_fpath.write_text(
        "\n".join(
            [
                "prefix: /tmp",
                "postgresql:",
                "  versions:",
                "    - version: '15'",
                f"      bindir: {bindir}",
            ]
        )
    )
    monkeypatch.setattr(SiteSettings, "yaml_file", settings_fpath)
    s = SiteSettings()
    assert str(s.prefix) == "/tmp"
    settings_fpath.write_text("hello")
    with pytest.raises(exceptions.SettingsError, match="invalid site settings"):
        SiteSettings()


def test_validation_dependencies() -> None:
    with pytest.raises(ValidationError) as cm:
        Settings.model_validate(
            {
                "postgresql": {
                    "auth": {"host": "peer"},
                    "backuprole": {"name": "backup"},
                }
            }
        )
    assert cm.value.errors(include_url=False, include_context=False) == [
        {
            "input": "peer",
            "loc": ("postgresql", "auth", "host"),
            "msg": (
                "Input should be 'trust', 'reject', 'md5', 'password', "
                "'scram-sha-256', 'gss', 'sspi', 'ident', 'pam', 'ldap' or 'radius'"
            ),
            "type": "literal_error",
        },
        {
            "input": {"name": "backup"},
            "loc": ("postgresql", "backuprole"),
            "msg": "Value error, cannot validate 'backuprole': missing or invalid 'auth' field",
            "type": "value_error",
        },
        {
            "input": None,
            "loc": ("patroni",),
            "msg": "Value error, cannot validate 'patroni': missing or invalid 'postgresql' field",
            "type": "value_error",
        },
    ]


def test_postgresqlsettings_bindir(tmp_path: Path) -> None:
    bindir = tmp_path / "bin"
    bindir.mkdir()
    with pytest.raises(
        ValidationError, match="missing '{version}' template placeholder"
    ):
        _postgresql.Settings.model_validate(
            {"bindir": "xxx", "versions": [{"version": "16", "bindir": str(bindir)}]}
        )


def test_postgresqlsettings_versions(tmp_path: Path) -> None:
    with patch(
        "pglift.settings._postgresql._postgresql_bindir", return_value=None
    ) as p:
        with pytest.warns(
            RuntimeWarning, match="cannot guess 'postgresql.versions' setting"
        ):
            _postgresql.Settings.model_validate({"versions": [], "bindir": None})
        p.assert_called_once_with()
    with pytest.raises(ValidationError, match="no value could be inferred"):
        _postgresql.Settings.model_validate(
            {"versions": [], "bindir": str(tmp_path / "{version}" / "bin")}
        )
    bindir = str(tmp_path / "{version}" / "bin")
    bindir_15 = tmp_path / "15" / "bin"
    bindir_15.mkdir(parents=True)
    (bindir_15 / "pg_ctl").touch(mode=0o755)
    s = _postgresql.Settings.model_validate({"versions": [], "bindir": bindir})
    assert [v.model_dump() for v in s.versions] == [
        {"bindir": bindir_15, "version": "15"}
    ]


def test_postgresqlsettings_default_version(tmp_path: Path) -> None:
    with pytest.raises(
        ValidationError, match="value must be amongst available 'versions': 13"
    ):
        _postgresql.Settings.model_validate(
            {
                "versions": [{"version": "13", "bindir": str(tmp_path)}],
                "default_version": "14",
                "bindir": "foo",
            }
        )


def test_role_pgpass(bindir_template: str) -> None:
    base = {"bindir": bindir_template}
    with pytest.raises(
        ValidationError, match="cannot set 'pgpass' without 'auth.passfile'"
    ):
        _postgresql.Settings.model_validate(
            {"auth": {"passfile": None}, "surole": {"pgpass": True}} | base
        )
    assert not _postgresql.Settings.model_validate(
        {"auth": {"passfile": None}} | base
    ).surole.pgpass


@pytest.mark.parametrize(
    ["prefix", "expected"],
    [
        ("/srv/pg/{name}", False),
        ("/srv/pg/{name}-{version}", True),
    ],
)
def test_postgresqlsettings_data_paths_versioned(
    bindir_template: str, prefix: str, expected: bool
) -> None:
    base = {"bindir": bindir_template}
    s = _postgresql.Settings.model_validate(
        {"datadir": prefix + "/data", "waldir": prefix + "/wals"} | base
    )
    assert s.data_paths_versioned() is expected


def test_settings(tmp_path: Path, bindir_template: str) -> None:
    s = Settings.model_validate(
        {"prefix": "/", "postgresql": {"bindir": bindir_template}}
    )
    assert hasattr(s, "postgresql")
    assert hasattr(s.postgresql, "datadir")
    assert s.postgresql.datadir == Path("/srv/pgsql/{version}/{name}/data")

    datadir = tmp_path / "{version}" / "{name}"
    s = Settings.model_validate(
        {
            "prefix": "/prefix",
            "run_prefix": "/runprefix",
            "postgresql": {"bindir": bindir_template, "datadir": str(datadir)},
        }
    )
    assert s.postgresql.datadir == datadir


def test_settings_nested_prefix(
    tmp_path: Path, pgbackrest_execpath: Path, bindir_template: str
) -> None:
    f = tmp_path / "f"
    f.touch()
    s = Settings.model_validate(
        {
            "run_prefix": "/test",
            "postgresql": {"bindir": bindir_template},
            "pgbackrest": {
                "execpath": str(pgbackrest_execpath),
                "repository": {
                    "mode": "host-tls",
                    "host": "repo",
                    "cn": "test",
                    "certificate": {"ca_cert": f, "cert": f, "key": f},
                    "pid_file": "backrest.pid",
                },
            },
        }
    )
    assert (
        str(s.model_dump()["pgbackrest"]["repository"]["pid_file"])
        == "/test/backrest.pid"
    )


def test_validate_not_templated_path(bindir_template: str) -> None:
    obj = {
        "postgresql": {
            "logpath": "/var/log/pgsql/{name}/{version}",
            "bindir": bindir_template,
        }
    }
    with pytest.raises(ValidationError, match="logpath accepts no template variable"):
        Settings.model_validate(obj)


def test_settings_validate_prefix(postgresql_settings: _postgresql.Settings) -> None:
    with pytest.raises(ValueError, match="expecting an absolute path"):
        Settings(prefix="x", postgresql=postgresql_settings)


def test_settings_validate_service_manager_scheduler(
    postgresql_settings: _postgresql.Settings,
) -> None:
    with pytest.raises(
        ValueError, match="cannot use systemd, if 'systemd' is not enabled globally"
    ):
        _ = Settings(
            service_manager="systemd", postgresql=postgresql_settings
        ).service_manager


def test_postgresql_versions(tmp_path: Path) -> None:
    base_bindir = tmp_path / "postgresql"
    base_bindir.mkdir()
    for v in range(14, 17):
        (base_bindir / str(v) / "bin").mkdir(parents=True)
        (base_bindir / str(v) / "bin" / "pg_ctl").touch(mode=0o755)
    other_bindir = tmp_path / "pgsql-14" / "bin"
    other_bindir.mkdir(parents=True)
    (other_bindir / "pg_ctl").touch(mode=0o755)
    # we also test directory without pg_ctl
    (base_bindir / "17" / "bin").mkdir(parents=True)
    config: dict[str, Any] = {
        "postgresql": {
            "bindir": str(base_bindir / "{version}" / "bin"),
            "versions": [
                {
                    "version": "14",
                    "bindir": str(other_bindir),
                },
            ],
        },
    }

    def set_envvar(mp: pytest.MonkeyPatch, settings: dict[str, Any]) -> None:
        for k, v in settings.items():
            mp.setenv(
                f"PGLIFT_{k}",
                json.dumps(v) if isinstance(v, Mapping | list | type(None)) else str(v),
            )

    with pytest.MonkeyPatch.context() as mp:
        set_envvar(mp, config)
        s = SiteSettings()
    pgversions = s.postgresql.versions
    assert {v.version for v in pgversions} == {"14", "15", "16"}
    assert next(v.bindir for v in pgversions if v.version == "14") == other_bindir
    assert (
        next(v.bindir for v in pgversions if v.version == "15")
        == base_bindir / "15" / "bin"
    )

    config["postgresql"]["default_version"] = "7"
    with pytest.MonkeyPatch.context() as mp:
        set_envvar(mp, config)
        with pytest.raises(
            ValidationError,
            match="Input should be '17', '16', '15', '14' or '13'",
        ):
            SiteSettings()

    config["postgresql"]["default_version"] = "14"
    with pytest.MonkeyPatch.context() as mp:
        set_envvar(mp, config)
        s = SiteSettings()
    assert s.postgresql.default_version == "14"

    config["postgresql"]["default_version"] = "7"
    with pytest.MonkeyPatch.context() as mp:
        set_envvar(mp, config)
        with pytest.raises(
            ValidationError,
            match="Input should be '17', '16', '15', '14' or '13'",
        ):
            SiteSettings()

    config["postgresql"]["default_version"] = "14"
    with pytest.MonkeyPatch.context() as mp:
        set_envvar(mp, config)
        s = SiteSettings()
    assert s.postgresql.default_version == "14"


def test_postgresql_dump_commands(bindir_template: str) -> None:
    with pytest.raises(ValidationError) as excinfo:
        _postgresql.Settings.model_validate(
            {
                "bindir": bindir_template,
                "dump_commands": [
                    ["{bindir}/pg_dump", "--debug"],
                    ["/no/such/file", "{conninfo}"],
                ],
            }
        )
    assert [
        {k: v for k, v in err.items() if k in ("loc", "msg")}
        for err in excinfo.value.errors()
    ] == [
        {
            "loc": ("dump_commands",),
            "msg": "Value error, program '/no/such/file' from command #2 does not exist",
        }
    ]


def test_systemd_systemctl() -> None:
    with patch("shutil.which", return_value=None, autospec=True) as which:
        with pytest.raises(ValidationError, match="systemctl command not found"):
            _systemd.Settings()
    which.assert_called_once_with("systemctl")


@pytest.mark.usefixtures("systemctl", "systemd_tmpfiles")
def test_systemd_sudo_user() -> None:
    with pytest.raises(ValidationError, match="cannot be used with 'user' mode"):
        _systemd.Settings(user=True, sudo=True)


def test_systemd_disabled(postgresql_settings: _postgresql.Settings) -> None:
    with pytest.raises(ValidationError, match="cannot use systemd"):
        Settings(scheduler="systemd", postgresql=postgresql_settings)
    with pytest.raises(ValidationError, match="cannot use systemd"):
        Settings(service_manager="systemd", postgresql=postgresql_settings)


@pytest.mark.usefixtures("systemctl", "systemd_tmpfiles")
def test_systemd_service_manager_scheduler_tmpfiles(
    postgresql_settings: _postgresql.Settings,
) -> None:
    assert (
        Settings(systemd={}, postgresql=postgresql_settings).service_manager
        == "systemd"
    )
    assert (
        Settings(
            systemd={}, service_manager="systemd", postgresql=postgresql_settings
        ).service_manager
        == "systemd"
    )
    assert (
        Settings(
            systemd={}, service_manager=None, postgresql=postgresql_settings
        ).service_manager
        is None
    )
    assert (
        Settings(
            systemd={}, tmpfiles_manager="systemd", postgresql=postgresql_settings
        ).tmpfiles_manager
        == "systemd"
    )


def test_pgbackrest_repository(tmp_path: Path, pgbackrest_execpath: Path) -> None:
    f = tmp_path / "f"
    f.touch()
    s = _pgbackrest.Settings.model_validate(
        {
            "execpath": str(pgbackrest_execpath),
            "repository": {
                "mode": "host-tls",
                "host": "repo",
                "cn": "test",
                "certificate": {"ca_cert": f, "cert": f, "key": f},
            },
        }
    )
    assert isinstance(s.repository, _pgbackrest.HostRepository)

    s = _pgbackrest.Settings.model_validate(
        {
            "execpath": str(pgbackrest_execpath),
            "repository": {"mode": "path", "path": str(tmp_path)},
        }
    )
    assert isinstance(s.repository, _pgbackrest.PathRepository)

    with pytest.raises(ValidationError, match="repository.path.foo"):
        _pgbackrest.Settings.model_validate(
            {
                "execpath": str(pgbackrest_execpath),
                "repository": {"mode": "path", "path": str(tmp_path), "foo": 1},
            }
        )
    with pytest.raises(ValidationError, match="repository.host-tls.foo"):
        _pgbackrest.Settings.model_validate(
            {
                "execpath": str(pgbackrest_execpath),
                "repository": {
                    "mode": "host-tls",
                    "host": "repo",
                    "cn": "test",
                    "certificate": {"ca_cert": f, "cert": f, "key": f},
                    "foo": "bar",
                },
            }
        )


def test_patroni_requires_replrole(bindir_template: str) -> None:
    with pytest.raises(
        ValidationError,
        match="'postgresql.replrole' must be provided to use 'patroni'",
    ):
        Settings.model_validate(
            {
                "postgresql": {
                    "bindir": bindir_template,
                },
                "patroni": {},
            }
        )


def test_patroni_etcd_cert_and_protocol(tmp_path: Path) -> None:
    cacert = tmp_path / "ca.pem"
    cacert.touch()
    with pytest.raises(ValidationError, match="'https' protocol is required"):
        _patroni.Etcd(cacert=cacert)
    _patroni.Etcd(cacert=cacert, protocol="https")
    _patroni.Etcd(protocol="https")


def test_patroni_restapi_verify_client(tmp_path: Path) -> None:
    with pytest.raises(ValidationError, match="requires 'certfile' to enable TLS"):
        _patroni.RESTAPI(verify_client="required")

    certfile = tmp_path / "cert.pem"
    certfile.touch()
    _patroni.RESTAPI(certfile=certfile, verify_client="required")


def test_patroni_restapi_verify_client_ctl(tmp_path: Path) -> None:
    certfile = tmp_path / "cert.pem"
    certfile.touch()
    cert = tmp_path / "host.pem"
    cert.touch()
    key = tmp_path / "host.key"
    key.touch()
    with pytest.raises(
        ValidationError,
        match="'ctl' must be provided",
    ):
        _patroni.Settings.model_validate(
            {
                "restapi": {
                    "certfile": certfile,
                    "verify_client": "required",
                },
            }
        )

    _patroni.Settings.model_validate(
        {
            "restapi": {
                "certfile": certfile,
                "verify_client": "required",
            },
            "ctl": {
                "certfile": cert,
                "keyfile": key,
            },
        }
    )


@pytest.mark.usefixtures("systemctl", "systemd_tmpfiles")
def test_none_environment_var() -> None:
    s = SiteSettings()
    assert s.scheduler is None
    with pytest.MonkeyPatch.context() as mp:
        mp.setenv("pglift_systemd", "{}")
        s = SiteSettings()
        assert s.scheduler == "systemd"
        assert s.service_manager == "systemd"
        mp.setenv("pglift_scheduler", "N0n3")
        with pytest.raises(
            ValidationError, match="1 validation error for SiteSettings\nscheduler"
        ):
            s = SiteSettings()
        mp.setenv("pglift_scheduler", "null")
        s = SiteSettings()
        assert s.scheduler is None


def test_env_nested_delimiter() -> None:
    s = SiteSettings()
    assert s.postgresql.auth.local == "trust"
    with pytest.MonkeyPatch.context() as mp:
        mp.setenv("pglift_postgresql__auth__local", "md5")
        s = SiteSettings()
        assert s.postgresql.auth.local == "md5"

# SPDX-FileCopyrightText: 2021 Dalibo
#
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

from pathlib import Path
from unittest import mock

import pytest

from pglift import systemd
from pglift.settings import Settings, _postgresql, _systemd, default_sysuser
from pglift.systemd import service_manager
from pglift.types import CompletedProcess


@pytest.mark.usefixtures("systemctl", "systemd_tmpfiles")
def test_executeas(postgresql_settings: _postgresql.Settings) -> None:
    s = Settings.model_validate(
        {"systemd": {"user": True}, "postgresql": postgresql_settings.model_dump()}
    )
    assert systemd.executeas(s) == ""

    s = Settings.model_validate(
        {
            "systemd": {"user": False},
            "sysuser": ["postgres", "pgsql"],
            "postgresql": postgresql_settings,
        }
    )
    assert systemd.executeas(s) == "User=postgres\nGroup=pgsql"


def test_systemctl_cmd(systemctl: str, systemd_tmpfiles: str) -> None:
    settings = _systemd.Settings()
    assert systemd.systemctl_cmd(settings, "status", "-n", "2", unit="foo.service") == [
        systemctl,
        "--user",
        "-n",
        "2",
        "status",
        "foo.service",
    ]

    settings = _systemd.Settings(user=False)
    assert systemd.systemctl_cmd(settings, "daemon-reload", unit=None) == [
        systemctl,
        "--system",
        "daemon-reload",
    ]

    settings = _systemd.Settings(user=False, sudo=True)
    assert systemd.systemctl_cmd(settings, "start", unit="foo.service") == [
        "sudo",
        systemctl,
        "--system",
        "start",
        "foo.service",
    ]


@pytest.mark.usefixtures("systemctl", "systemd_tmpfiles")
def test_systemctl_env(caplog: pytest.LogCaptureFixture) -> None:
    settings = _systemd.Settings(user=False)
    assert systemd.systemctl_env(settings) == {}
    settings = _systemd.Settings(user=True)
    systemd.systemctl_env.cache_clear()
    with (
        mock.patch.dict("os.environ", {}, clear=True),
        mock.patch(
            "subprocess.run",
            autospec=True,
            side_effect=[
                CompletedProcess(
                    [],
                    0,
                    "/run/user/test\nno\n",
                    "",
                ),
                CompletedProcess(
                    [],
                    0,
                    "SOMEVAR=value\nDBUS_SESSION_BUS_ADDRESS=unix:path=/run/user/test/bus\n",
                    "",
                ),
            ],
        ) as suprocess_run,
    ):
        assert systemd.systemctl_env(settings) == {
            "DBUS_SESSION_BUS_ADDRESS": "unix:path=/run/user/test/bus",
            "XDG_RUNTIME_DIR": "/run/user/test",
        }

    username, _ = default_sysuser()
    assert suprocess_run.mock_calls == [
        mock.call(
            [
                "loginctl",
                "show-user",
                username,
                "--value",
                "--property",
                "RuntimePath",
                "--property",
                "Linger",
            ],
            check=True,
            capture_output=True,
            text=True,
        ),
        mock.call(
            ["systemctl", "--user", "show-environment"],
            env={"XDG_RUNTIME_DIR": "/run/user/test"},
            check=True,
            capture_output=True,
            text=True,
        ),
    ]
    assert [r.message for r in caplog.records] == [
        f"systemd lingering for user {username} is not enabled, "
        "pglift services won't start automatically at boot"
    ]


@pytest.mark.usefixtures("systemctl", "systemd_tmpfiles")
def test_install_uninstall(tmp_path: Path) -> None:
    settings = _systemd.Settings(unit_path=tmp_path)
    assert systemd.install("foo", "ahah", settings)
    unit_path = tmp_path / "foo"
    mtime = unit_path.stat().st_mtime
    assert unit_path.read_text() == "ahah"
    assert systemd.installed("foo", settings)
    assert not systemd.install("foo", "ahah", settings)
    assert unit_path.stat().st_mtime == mtime
    assert not systemd.install("foo", "ahahah", settings)
    assert systemd.installed("foo", settings)
    assert systemd.uninstall("foo", settings)
    assert not unit_path.exists()
    assert not systemd.uninstall("foo", settings)  # no-op


def test_service_manager_site_configure_list(settings: Settings) -> None:
    assert settings.systemd is not None
    base = settings.systemd.unit_path
    assert list(service_manager.site_configure_list(settings)) == [
        base / f"pglift-{name}@.service"
        for name in ["temboard_agent", "postgres_exporter", "patroni", "postgresql"]
    ]

# SPDX-FileCopyrightText: 2021 Dalibo
#
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

import logging
from pathlib import Path
from unittest.mock import patch

import pytest

from pglift import exceptions, util


def test_environ(config_dir: Path) -> None:
    base = {"PGLIFT_CONFIG_DIR": str(config_dir)}
    assert util.environ() == base
    with pytest.MonkeyPatch.context() as mp:
        mp.setenv("PGLIFT_XYZ", "abc")
        assert util.environ() == base | {"PGLIFT_XYZ": "abc"}


def test_xdg_config_home(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("pglift.util.Path.home", lambda: Path("/ho/me"))
    assert util.xdg_config_home() == Path("/ho/me/.config")


def test_xdg_data_home(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("XDG_DATA_HOME", "/x/y")
    assert util.xdg_data_home() == Path("/x/y")
    monkeypatch.delenv("XDG_DATA_HOME", raising=False)
    monkeypatch.setattr("pglift.util.Path.home", lambda: Path("/ho/me"))
    assert util.xdg_data_home() == Path("/ho/me/.local/share")


def test_xdg_config(tmp_path: Path) -> None:
    configdir = tmp_path / "pglift"
    configdir.mkdir()
    configfile = configdir / "x"
    configfile.touch()
    with pytest.MonkeyPatch.context() as mp:
        mp.setenv("XDG_CONFIG_HOME", str(tmp_path))
        assert util.xdg_config("x") is not None
    assert util.xdg_config("x") is None


def test_custom_dir(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("PGLIFT_CONFIG_DIR")
    assert util.custom_dir() is None

    monkeypatch.setenv("PGLIFT_CONFIG_DIR", "/not/existing/path")
    with pytest.raises(exceptions.FileNotFoundError, match="does not exist"):
        util.custom_dir()

    monkeypatch.setenv("PGLIFT_CONFIG_DIR", str(tmp_path))
    assert util.custom_dir() == tmp_path


def test_site_config(caplog: pytest.LogCaptureFixture, tmp_path: Path) -> None:
    f = tmp_path / "c" / "d" / "f.conf"
    f.parent.mkdir(parents=True)
    f.write_text("something\n")
    alt_conf = tmp_path / "alt" / "pglift" / "c" / "d" / "other.conf"
    alt_conf.parent.mkdir(parents=True)
    alt_conf.touch()

    with pytest.MonkeyPatch.context() as mp:
        mp.setenv("PGLIFT_CONFIG_DIR", str(tmp_path))
        with caplog.at_level(logging.DEBUG, logger="pglift.util"):
            assert util.site_config(("c",), "d", "f.conf") is not None
        assert caplog.messages == [
            f"using 'c/d/f.conf' configuration file from site (source: PGLIFT_CONFIG_DIR={tmp_path})"
        ]

        # verify whether /etc/pglift is used or ignored based on the
        # presence of PGLIFT_CONFIG_DIR
        with patch("pglift.util.etc", return_value=tmp_path / "alt") as p_etc:
            assert util.site_config(("c",), "d", "other.conf") is None
            p_etc.assert_not_called()
            assert util.site_config(("c",), "d", "f.conf") == f
            mp.delenv("PGLIFT_CONFIG_DIR")
            assert util.site_config(("c",), "d", "other.conf") == alt_conf
            p_etc.assert_called_once()

        # verify whether XDG_CONFIG_HOME is used or ignored based on the
        # presence of PGLIFT_CONFIG_DIR
        mp.setenv("XDG_CONFIG_HOME", str(tmp_path / "alt"))
        assert util.site_config(("c",), "d", "other.conf") == alt_conf
        mp.setenv("PGLIFT_CONFIG_DIR", str(tmp_path))
        assert util.site_config(("c",), "d", "other.conf") is None


def test_read_site_config(
    caplog: pytest.LogCaptureFixture, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    f = tmp_path / "c" / "d" / "f.conf"
    f.parent.mkdir(parents=True)
    f.write_text("something\n")
    monkeypatch.setenv("PGLIFT_CONFIG_DIR", str(tmp_path))
    with caplog.at_level(logging.DEBUG, logger="pglift.util"):
        assert util.read_site_config(("c",), "d", "f.conf") == "something\n"
    assert caplog.messages == [
        f"using 'c/d/f.conf' configuration file from site (source: PGLIFT_CONFIG_DIR={tmp_path})"
    ]

    caplog.clear()

    with caplog.at_level(logging.DEBUG, logger="pglift.util"):
        content = util.read_site_config(("postgresql",), "pg_hba.conf")
        assert content is not None
        assert "local   all" in content
    assert caplog.messages == [
        "using 'postgresql/pg_hba.conf' configuration file from distribution"
    ]


def test_read_dist_config(caplog: pytest.LogCaptureFixture) -> None:
    with caplog.at_level(logging.DEBUG, "pglift.util"):
        content = util.read_dist_config("postgresql", "pg_hba.conf")
    assert caplog.messages == [
        "using 'postgresql/pg_hba.conf' configuration file from distribution"
    ]
    assert content is not None
    assert "local   all" in content


@pytest.fixture
def meminfo(tmp_path: Path) -> Path:
    fpath = tmp_path / "meminfo"
    fpath.write_text(
        "\n".join(
            [
                "MemTotal:        6022056 kB",
                "MemFree:         3226640 kB",
                "MemAvailable:    4235060 kB",
                "Buffers:          206512 kB",
            ]
        )
    )
    return fpath


def test_total_memory(meminfo: Path) -> None:
    assert util.total_memory(meminfo) == 6166585344.0


def test_total_memory_error(tmp_path: Path) -> None:
    meminfo = tmp_path / "meminfo"
    meminfo.touch()
    with pytest.raises(Exception, match="could not retrieve memory information from"):
        util.total_memory(meminfo)


def test_check_or_create_directory(
    tmp_path: Path, caplog: pytest.LogCaptureFixture
) -> None:
    d = tmp_path / "f"
    d.touch()
    with pytest.raises(
        exceptions.SystemError,
        match=f"{d} exists but is not a directory",
    ):
        util.check_or_create_directory(d, "notadir")

    d = tmp_path / "x"
    d.mkdir(mode=0o500)
    with pytest.raises(
        exceptions.SystemError,
        match=f"w_nok directory {d} exists but is not writable",
    ):
        util.check_or_create_directory(d, "w_nok")

    d = tmp_path / "z"
    with caplog.at_level(logging.INFO, logger="pglift.util"):
        util.check_or_create_directory(d, "ok")
    assert f"creating ok directory: {d}" in caplog.messages


def test_rmdir(tmp_path: Path, caplog: pytest.LogCaptureFixture) -> None:
    d = tmp_path / "x"
    subd = d / "y"
    subd.mkdir(parents=True)

    with caplog.at_level(logging.WARNING):
        assert not util.rmdir(d)
    assert "Directory not empty" in caplog.messages[0]
    assert d.exists()

    caplog.clear()

    with caplog.at_level(logging.WARNING):
        assert util.rmdir(subd)
        assert util.rmdir(d)
    assert not caplog.messages
    assert not d.exists()


def test_rmtree(tmp_path: Path, caplog: pytest.LogCaptureFixture) -> None:
    d1 = tmp_path / "d1"
    d1.mkdir()
    d2 = tmp_path / "d2"
    d2.symlink_to(d1, target_is_directory=True)
    with caplog.at_level(logging.WARNING):
        util.rmtree(d2)
    msg, *others = caplog.messages
    assert msg.startswith(f"failed to delete {d2} during tree deletion of {d2}: ")
    assert not others

    caplog.clear()

    with caplog.at_level(logging.WARNING):
        util.rmtree(d1)
    assert not caplog.messages


def test_empty_dir(tmp_path: Path) -> None:
    empty_d = tmp_path / "empty"
    empty_d.mkdir()
    assert util.is_empty_dir(empty_d)
    assert not util.is_empty_dir(tmp_path)
    no_empty = tmp_path / "no_empty"
    no_empty.mkdir()
    (no_empty / "zelda").symlink_to(tmp_path)
    assert not util.is_empty_dir(no_empty)

# SPDX-FileCopyrightText: 2021 Dalibo
#
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

from pathlib import Path

import pgtoolkit.conf as pgconf
import pytest

from pglift import conf
from pglift.system.fs import AbstractFS


def test_read(memfs: AbstractFS[Path]) -> None:
    datadir = Path("/data/pgsql")
    memfs.mkdir(datadir, parents=True)
    postgresql_conf = datadir / "postgresql.conf"
    memfs.write_text(postgresql_conf, "\n".join(["bonjour = hello", "port=1234"]))
    memfs.write_text(
        datadir / "postgresql.auto.conf", "primary_conn_info = host=primary\n"
    )
    config = conf.read(datadir, fs=memfs)
    assert config.bonjour == "hello"
    assert config.port == 1234
    assert config.primary_conn_info == "host=primary"

    config = conf.read(datadir, managed_only=True, fs=memfs)
    assert config.bonjour == "hello"
    assert config.port == 1234
    assert "primary_conn_info" not in config

    memfs.unlink(postgresql_conf)
    with pytest.raises(FileNotFoundError, match=str(postgresql_conf)):
        conf.read(datadir, True, fs=memfs)


def test_update(datadir: Path, expected_dir: Path, write_changes: bool) -> None:
    with (datadir / "postgresql.conf.sample").open() as f:
        cfg = pgconf.parse(f)
    conf.update(
        cfg,
        max_connections=10,  # changed
        bonjour=True,  # uncommented
        log_destination="stderr",  # added
    )
    fpath = expected_dir / "postgresql.conf"
    if write_changes:
        cfg.save(fpath)
    expected = fpath.read_text().splitlines(keepends=True)
    assert cfg.lines == expected


def test_merge(datadir: Path, expected_dir: Path, write_changes: bool) -> None:
    with (datadir / "postgresql.conf.sample").open() as f:
        cfg = pgconf.parse(f)
    conf.merge(
        cfg,
        max_connections=10,  # changed
        bonjour=True,  # uncommented
        log_destination="stderr",  # added
    )
    fpath = expected_dir / "postgresql.merged.conf"
    if write_changes:
        cfg.save(fpath)
    expected = fpath.read_text().splitlines(keepends=True)
    assert cfg.lines == expected


def test_changes() -> None:
    assert conf.changes(
        {"unchanged": "x", "changed": 5432, "removed": "rmme"},
        {"unchanged": "x", "changed": 5433, "added": "x,y,z"},
    ) == {
        "changed": (5432, 5433),
        "removed": ("rmme", None),
        "added": (None, "x,y,z"),
    }

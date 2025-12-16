# SPDX-FileCopyrightText: 2024 Dalibo
#
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

import os
from pathlib import Path

import pytest

from pglift.system import fs


def test_localfs(tmp_path: Path) -> None:
    lfs = fs.LocalFS()
    f = tmp_path / "f"

    lfs.write_text(f, "f")
    assert f.read_text() == "f"

    assert lfs.exists(f)

    assert lfs.is_file(f) and not lfs.is_dir(f)
    assert lfs.is_dir(tmp_path) and not lfs.is_file(tmp_path)

    assert lfs.read_text(f) == "f"

    with lfs.open(f, mode="w") as fobj:
        assert fobj.write("f+") == 2
    assert f.read_text() == "f+"
    with lfs.open(f) as fobj:
        assert fobj.read() == "f+"

    with lfs.open(f, "rb") as bfobj:
        assert bfobj.read(1) == b"f"

    lfs.unlink(f)
    assert not f.exists()

    lfs.unlink(f, missing_ok=True)
    with pytest.raises(FileNotFoundError):
        lfs.unlink(f)

    c = tmp_path / "c"
    c.write_text("original")
    t = tmp_path / "t"
    assert not t.exists()
    lfs.copy(c, t)
    assert t.exists() and t.read_text() == "original"
    assert c.exists()

    d = tmp_path / "x"
    lfs.mkdir(d)
    assert d.is_dir()
    lfs.rmdir(d)
    assert not d.exists()

    f = tmp_path / "af"
    umask = os.umask(0o002)
    try:
        lfs.touch(f)
    finally:
        os.umask(umask)
    assert f.exists()

    assert [m.name for m in lfs.glob(tmp_path, "*f")] == ["af"]

    assert f.stat().st_mode == 0o100664
    lfs.chmod(f, 0o600)
    assert f.stat().st_mode == 0o100600

    assert sorted([x.name for x in lfs.iterdir(tmp_path)]) == ["af", "c", "t"]

    lfs.rmtree(tmp_path)
    assert not tmp_path.exists()

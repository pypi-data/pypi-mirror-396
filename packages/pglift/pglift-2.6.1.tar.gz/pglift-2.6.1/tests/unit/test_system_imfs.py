# SPDX-FileCopyrightText: 2024 Dalibo
#
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

from pathlib import Path

import pytest
from fsspec.implementations.memory import MemoryFileSystem

from pglift.system.imfs import InMemoryFS, RoFS


@pytest.fixture
def f() -> Path:
    return Path("f")


@pytest.fixture
def d() -> Path:
    return Path("/d")


@pytest.fixture
def memfs(f: Path, d: Path) -> InMemoryFS:
    backend = MemoryFileSystem()
    # Clear global states.
    backend.store.clear()
    backend.pseudo_dirs.clear()
    backend.touch(f)
    backend.makedirs(d, exist_ok=True)  # XXX
    return InMemoryFS(backend=backend)


@pytest.fixture
def rofs(memfs: InMemoryFS) -> RoFS:
    return RoFS(in_mem=memfs)


def test_rofs_exists_memory(rofs: RoFS, f: Path, d: Path) -> None:
    assert rofs.exists(f)
    assert rofs.exists(d)
    assert not rofs.exists(d / "g")

    u = Path("u")
    rofs.deleted.add(u)
    assert not rofs.exists(u)


def test_rofs_exists_realfs(tmp_path: Path) -> None:
    rofs = RoFS()
    f = tmp_path / "f"
    f.write_text("f")
    assert rofs.exists(f)
    g = tmp_path / "d" / "f"
    assert not rofs.exists(g)
    g.parent.mkdir()
    g.write_text("g")
    assert rofs.exists(g)


def test_rofs_is_file_memory(rofs: RoFS, f: Path, d: Path) -> None:
    assert rofs.is_file(f)
    assert not rofs.is_file(d)

    u = Path("u")
    rofs.deleted.add(u)
    assert not rofs.is_file(u)


def test_rofs_is_file_realfs(tmp_path: Path) -> None:
    f = tmp_path / "f"
    f.write_text("f")
    rofs = RoFS()
    assert rofs.is_file(f)
    g = tmp_path / "d" / "f"
    assert not rofs.is_file(g)
    g.parent.mkdir()
    g.write_text("g")
    assert rofs.is_file(g)


def test_rofs_is_dir_memory(rofs: RoFS, f: Path, d: Path) -> None:
    assert rofs.is_dir(d)
    assert not rofs.is_dir(f)


def test_rofs_is_dir_realfs(tmp_path: Path) -> None:
    rofs = RoFS()
    f = tmp_path / "f"
    f.touch()
    assert rofs.is_dir(tmp_path)
    assert not rofs.is_dir(f)

    u = Path("u")
    rofs.deleted.add(u)
    assert not rofs.is_dir(u)


def test_rofs_open_memory(memfs: InMemoryFS, rofs: RoFS, f: Path, d: Path) -> None:
    with rofs.open(f) as fobj:
        content = fobj.read()
    assert content == ""

    u = d / "u"
    with rofs.open(u, mode="w") as fobj:
        assert fobj.write("u") == 1
    assert memfs.read_text(u) == "u"


def test_rofs_open_realfs(tmp_path: Path) -> None:
    f = tmp_path / "f"
    f.write_text("f")
    rofs = RoFS()
    with rofs.open(f) as fobj:
        assert fobj.read() == "f"

    with pytest.raises(FileNotFoundError):
        rofs.open(tmp_path / "nf").__enter__()

    u = tmp_path / "u"
    with rofs.open(u, mode="w") as fobj:
        assert fobj.write("u") == 1
    assert rofs.in_mem.read_text(u) == "u"
    assert not u.exists()

    d = tmp_path / "d"
    rofs.deleted.add(d)
    with pytest.raises(FileNotFoundError, match=f"{d} got deleted"):
        rofs.open(d).__enter__()


def test_rofs_read_text(tmp_path: Path) -> None:
    f = tmp_path / "f"
    f.write_text("f")

    rofs = RoFS()

    # First read from real fs
    assert rofs.read_text(f) == "f"

    assert not rofs.in_mem.exists(f)

    rofs.deleted.add(f)
    with pytest.raises(FileNotFoundError, match=f"{f} got deleted"):
        rofs.read_text(f)

    g = Path("g")
    rofs.in_mem.write_text(g, "g")
    # Direct read from in-memory fs.
    assert rofs.read_text(g) == "g"


def test_rofs_write_text(tmp_path: Path) -> None:
    rofs = RoFS()

    in_mem = tmp_path / "in-mem"
    assert rofs.write_text(in_mem, "m") == 1
    assert not in_mem.exists()
    assert rofs.in_mem.read_text(in_mem) == "m"

    assert rofs.read_text(in_mem) == "m"

    with pytest.raises(FileNotFoundError):
        rofs.write_text(tmp_path / "otherdir" / "f", "x")


def test_rofs_iterdir_inmemory(memfs: InMemoryFS, rofs: RoFS, d: Path) -> None:
    assert memfs.is_dir(d)
    assert list(memfs.iterdir(d)) == []
    assert list(rofs.iterdir(d)) == []
    u = d / "u"
    memfs.touch(u)
    assert list(rofs.iterdir(d)) == [u]
    rofs.deleted.add(u)
    assert list(rofs.iterdir(d)) == []
    rofs.deleted.add(d)
    with pytest.raises(FileNotFoundError):
        next(rofs.iterdir(d))


def test_rofs_iterdir_realfs(tmp_path: Path) -> None:
    f = tmp_path / "f"
    f.touch()
    d = tmp_path / "d"
    d.mkdir()
    rofs = RoFS()
    assert set(rofs.iterdir(tmp_path)) == {f, d}


def test_rofs_glob_memory(memfs: InMemoryFS, rofs: RoFS, d: Path) -> None:
    xy = d / "x.y"
    z = d / "z.y"
    assert list(rofs.glob(d, "*.y")) == []
    memfs.touch(xy)
    rofs.deleted.add(z)
    assert list(rofs.glob(d, "*.y")) == [xy]


def test_rofs_glob_realfs(tmp_path: Path) -> None:
    xy = tmp_path / "x.y"
    z = tmp_path / "z.y"
    rofs = RoFS(deleted={z})
    assert list(rofs.glob(tmp_path, "*.y")) == []
    xy.touch()
    assert list(rofs.glob(tmp_path, "*.y")) == [xy]


def test_rofs_touch(memfs: InMemoryFS, rofs: RoFS, f: Path, d: Path) -> None:
    with pytest.raises(FileExistsError):
        rofs.touch(f, exist_ok=False)
    rofs.touch(f)
    n = d / "n"
    rofs.touch(n)
    assert memfs.exists(n)


def test_rofs_mkdir(memfs: InMemoryFS, rofs: RoFS, d: Path) -> None:
    with pytest.raises(FileExistsError):
        rofs.mkdir(d)
    rofs.mkdir(d, exist_ok=True)
    n = Path("/x/y")
    rofs.mkdir(n, parents=True)


def test_rofs_copy(
    memfs: InMemoryFS, rofs: RoFS, f: Path, d: Path, tmp_path: Path
) -> None:
    g = d / "g"
    rofs.copy(f, g)
    rofs.deleted.add(f)
    with pytest.raises(FileNotFoundError):
        rofs.copy(f, Path("u"))
    x = tmp_path / "l"
    x.write_text("x")
    rofs.copy(x, f)
    assert memfs.read_text(f) == "x"
    assert f not in rofs.deleted
    with pytest.raises(FileNotFoundError):
        rofs.copy(tmp_path / "y", f)


def test_rofs_unlink_missing_ok(rofs: RoFS, tmp_path: Path) -> None:
    g = Path("g")
    with pytest.raises(FileNotFoundError):
        rofs.unlink(g)
    rofs.unlink(g, missing_ok=True)

    dlt = Path("/d/lt")
    rofs.deleted.add(dlt)
    with pytest.raises(FileNotFoundError):
        rofs.unlink(dlt)
    rofs.unlink(dlt, missing_ok=True)

    nf = tmp_path / "fn"
    with pytest.raises(FileNotFoundError):
        rofs.unlink(nf)
    rofs.unlink(nf, missing_ok=True)


def test_rofs_unlink_memory(f: Path, memfs: InMemoryFS, rofs: RoFS) -> None:
    assert memfs.exists(f) and rofs.exists(f)
    rofs.unlink(f)
    assert not memfs.exists(f) and not rofs.exists(f)
    assert f in rofs.deleted

    with pytest.raises(FileNotFoundError):
        rofs.unlink(f)
    rofs.unlink(f, missing_ok=True)


def test_rofs_unlink_realfs(memfs: InMemoryFS, rofs: RoFS, tmp_path: Path) -> None:
    x = tmp_path / "x"
    x.touch()
    rofs.unlink(x)
    assert x in rofs.deleted
    assert x.exists()
    assert not rofs.exists(x)


def test_rofs_modify_then_unlink_memory(
    memfs: InMemoryFS, rofs: RoFS, tmp_path: Path
) -> None:
    x = tmp_path / "x"
    x.touch()
    with rofs.open(x, mode="w") as fobj:
        fobj.write("u")
    assert memfs.exists(x)
    rofs.unlink(x)
    assert not rofs.exists(x)


def test_rofs_rmdir(
    memfs: InMemoryFS, rofs: RoFS, d: Path, f: Path, tmp_path: Path
) -> None:
    with pytest.raises(NotADirectoryError):
        rofs.rmdir(f)
    rofs.rmdir(d)
    assert d in rofs.deleted
    with pytest.raises(FileNotFoundError):
        rofs.rmdir(d)
    rofs.rmdir(tmp_path)
    assert tmp_path in rofs.deleted
    assert tmp_path.exists()


def test_rofs_chmod(rofs: RoFS, f: Path, tmp_path: Path) -> None:
    """chmod() is a no-op if path exists."""
    assert rofs.exists(f)
    rofs.chmod(f, 0o766)

    rf = tmp_path / "x"
    rf.touch(mode=0o644)
    mode = rf.stat().st_mode
    rofs.chmod(rf, 0o777)
    assert rf.stat().st_mode == mode

    rofs.deleted.add(f)
    with pytest.raises(FileNotFoundError):
        rofs.chmod(f, 0o766)

    with pytest.raises(FileNotFoundError):
        rofs.chmod(tmp_path / "nf", mode=0o600)


def test_rofs_rmtree(memfs: InMemoryFS, rofs: RoFS, d: Path, tmp_path: Path) -> None:
    memfs.mkdir(d / "sd")
    memfs.touch(d / "sf")
    rofs.rmtree(d)
    assert not memfs.exists(d)

    with pytest.raises(FileNotFoundError):
        rofs.rmtree(d)

    f = tmp_path / "f"
    f.touch()

    rofs.rmtree(tmp_path)
    assert f.exists()
    assert tmp_path in rofs.deleted
    assert tmp_path.exists()

    with pytest.raises(FileNotFoundError):
        rofs.rmtree(tmp_path / "d")

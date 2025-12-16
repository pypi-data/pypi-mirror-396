# SPDX-FileCopyrightText: 2025 Dalibo
#
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

from pathlib import Path, PurePath
from typing import Any, Literal

import pytest

from pglift import diff
from pglift._compat import assert_type
from pglift.models import interface
from pglift.system import fs


def test_types() -> None:
    adiffer = diff.Differ("ansible")
    assert_type(adiffer, diff.Differ[Literal["ansible"]])
    assert_type(next(adiffer.dump(), None), dict[str, str] | None)

    udiffer = diff.Differ("unified")
    assert_type(udiffer, diff.Differ[Literal["unified"]])
    assert_type(next(udiffer.dump(), None), str | None)


@pytest.mark.parametrize(
    "differ, expected",
    [
        (
            diff.Differ("ansible"),
            [
                {
                    "before_header": "a",
                    "after_header": "a changed",
                    "before": "a",
                    "after": "A",
                },
                {
                    "before_header": "/dev/null",
                    "after_header": "b created",
                    "after": "b",
                },
                {
                    "before_header": "c",
                    "after_header": "/dev/null deleted",
                    "before": "c",
                },
            ],
        ),
        (
            diff.Differ("unified"),
            [
                "--- a\n+++ a\n@@ -1 +1 @@\n-a\n+A",
                "--- /dev/null\n+++ b\n@@ -0,0 +1 @@\n+b",
                "--- c\n+++ /dev/null\n@@ -1 +0,0 @@\n-c",
            ],
        ),
    ],
)
def test_differ_dump(differ: diff.Differ[Any], expected: Any) -> None:
    differ.record(
        before=(PurePath("a"), None, "a"), after=(PurePath("a"), "changed", "A")
    )
    differ.record(before=(None, None, None), after=(PurePath("b"), "created", "b"))
    differ.record(before=(PurePath("c"), None, "c"), after=(None, "deleted", None))
    assert list(differ.dump()) == expected


def test_diff_context() -> None:
    with diff.enabled(None):
        assert diff.DIFFER.get() is None
    with diff.enabled("unified"):
        assert (differ := diff.DIFFER.get()) is not None and differ.format == "unified"


def test_diff_context_records(tmp_path: Path) -> None:
    localfs = fs.LocalFS()
    apath = tmp_path / "a"
    bpath = tmp_path / "b"
    bpath.write_text("b")
    cpath = tmp_path / "c"
    dpath = tmp_path / "d"
    c_path = tmp_path / "c'"
    xpath = tmp_path / "x"
    xpath.write_text("x")
    dirpath = tmp_path / "dir" / "dir"
    dirpath.mkdir(parents=True)
    (dirpath / "f").write_text("f")
    (dirpath / "otherdir").mkdir()
    parentdir = dirpath.parent
    assert diff.DIFFER.get() is None
    with diff.enabled("unified"):
        differ = diff.DIFFER.get()
        assert differ is not None and differ.format == "unified"
        with localfs.open(apath, "w") as f:
            f.write("a")
        localfs.write_text(bpath, "B")
        localfs.touch(cpath)
        localfs.write_text(cpath, "c")
        localfs.mkdir(dpath)
        localfs.copy(cpath, c_path)
        localfs.unlink(xpath)
        localfs.chmod(bpath, 0o600)
        localfs.rmtree(dirpath)
        localfs.rmdir(parentdir)
    localfs.write_text(tmp_path / "not-recorded", "'cause outside context!")
    assert differ.records == [
        ((None, None, None), (apath, "created", "a")),
        ((bpath, None, "b"), (bpath, None, "B")),
        ((None, None, None), (cpath, "new file (mode: 438)", None)),
        ((cpath, None, ""), (cpath, None, "c")),
        ((None, None, None), (dpath, "new directory", None)),
        ((None, None, None), (c_path, f"copied from {cpath}", "c")),
        ((xpath, "deleted", "x"), (None, None, None)),
        ((bpath, None, None), (bpath, "mode -> 384", None)),
        ((dirpath, "directory tree deleted", None), (None, None, None)),
        ((parentdir, "directory deleted", None), (None, None, None)),
    ]


def test_diff_result() -> None:
    r = interface.ApplyResult()
    assert r.diff is None
    with diff.enabled("ansible"):
        assert (differ := diff.DIFFER.get()) is not None
        differ.record((PurePath("x"), None, "x"), (PurePath("x"), "changed", "y"))
        r = interface.ApplyResult()
    assert r.diff is not None and r.diff == [
        {
            "before_header": "x",
            "before": "x",
            "after_header": "x changed",
            "after": "y",
        }
    ]

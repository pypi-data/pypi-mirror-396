# SPDX-FileCopyrightText: 2025 Dalibo
#
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

import difflib
import os
from collections.abc import Iterator
from contextlib import contextmanager
from contextvars import ContextVar
from dataclasses import dataclass, field
from pathlib import PurePath
from typing import Any, Generic, Literal, TypeAlias, TypeVar, overload

from ._compat import assert_never

State: TypeAlias = tuple[PurePath | None, str | None, str | None]

EMPTY_STATE: State = (None, None, None)

Format: TypeAlias = Literal["unified", "ansible"]
_F = TypeVar("_F", bound=Format)


@dataclass(frozen=True)
class Differ(Generic[_F]):
    format: _F
    records: list[tuple[State, State]] = field(default_factory=list)

    def record(self, before: State, after: State) -> None:
        self.records.append((before, after))

    @overload
    def dump(self: Differ[Literal["ansible"]]) -> Iterator[dict[str, str]]: ...

    @overload
    def dump(self: Differ[Literal["unified"]]) -> Iterator[str]: ...

    def dump(self: Differ[Any]) -> Iterator[dict[str, str]] | Iterator[str]:
        for (before_path, before_detail, before_content), (
            after_path,
            after_detail,
            after_content,
        ) in self.records:
            fromfile = str(before_path or os.devnull)
            tofile = str(after_path or os.devnull)
            if self.format == "ansible":
                yield (
                    {
                        "before_header": (
                            fromfile
                            + (f" {before_detail}" if before_detail is not None else "")
                        ),
                        "after_header": (
                            tofile
                            + (f" {after_detail}" if after_detail is not None else "")
                        ),
                    }
                    | ({"before": before_content} if before_content is not None else {})
                    | ({"after": after_content} if after_content is not None else {})
                )
            elif self.format == "unified":
                if udiff := "\n".join(
                    difflib.unified_diff(
                        before_content.splitlines()
                        if before_content is not None
                        else (),
                        after_content.splitlines() if after_content is not None else (),
                        fromfile=fromfile,
                        tofile=tofile,
                        lineterm="",
                    )
                ):
                    yield udiff
            else:  # pragma: nocover
                assert_never(self.format)


DIFFER = ContextVar[Differ[Any] | None]("Differ", default=None)


@contextmanager
def enabled(format: Format | None) -> Iterator[None]:
    """Enable diff recording using specified format, if format is not None."""
    if format is None:
        yield
        return
    token = DIFFER.set(Differ(format))
    try:
        yield
    finally:
        DIFFER.reset(token)


def get() -> list[Any] | None:
    """Return recorded diffs or None if no differ is enabled."""
    if differ := DIFFER.get():
        return list(differ.dump())
    return None

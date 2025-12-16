# SPDX-FileCopyrightText: 2024 Dalibo
#
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

import abc
import shutil
from collections.abc import Iterator
from contextlib import contextmanager, nullcontext
from contextvars import ContextVar
from pathlib import Path, PurePath
from typing import (
    IO,
    Annotated,
    Any,
    Generic,
    Literal,
    TypeAlias,
    TypeVar,
    overload,
)

from .. import diff
from ..deps import Dependency

P = TypeVar("P", Path, PurePath)


class AbstractFS(abc.ABC, Generic[P]):
    """Abstract interface to a filesystem, mostly following pathlib.Path API."""

    @abc.abstractmethod
    def exists(self, path: P) -> bool: ...

    @abc.abstractmethod
    def is_file(self, path: P) -> bool: ...

    @abc.abstractmethod
    def is_dir(self, path: P) -> bool: ...

    @overload
    @contextmanager
    def open(self, path: P, mode: Literal["rb", "wb"]) -> Iterator[IO[bytes]]: ...

    @overload
    @contextmanager
    def open(self, path: P, mode: Literal["r", "w"] = ...) -> Iterator[IO[str]]: ...

    @contextmanager
    def open(
        self, path: P, mode: Literal["r", "w", "rb", "wb"] = "r"
    ) -> Iterator[IO[bytes]] | Iterator[IO[str]]:
        with (
            self._record_file(path) if mode[0] == "w" else nullcontext(),
            self._open(path, mode=mode) as f,
        ):
            yield f

    @overload
    @contextmanager
    def _open(self, path: P, mode: Literal["rb", "wb"]) -> Iterator[IO[bytes]]: ...

    @overload
    @contextmanager
    def _open(self, path: P, mode: Literal["r", "w"] = ...) -> Iterator[IO[str]]: ...

    @abc.abstractmethod
    @contextmanager
    def _open(
        self, path: P, mode: Literal["r", "w", "rb", "wb"] = "r"
    ) -> Iterator[IO[bytes]] | Iterator[IO[str]]: ...

    @abc.abstractmethod
    def read_text(self, path: P) -> str: ...

    def write_text(self, path: P, text: str) -> int:
        with self._record_file(path, newcontent=text):
            return self._write_text(path, text)

    @abc.abstractmethod
    def _write_text(self, path: P, text: str) -> int: ...

    @abc.abstractmethod
    def iterdir(self, path: P) -> Iterator[P]: ...

    @abc.abstractmethod
    def glob(self, path: P, pattern: str) -> Iterator[Path]: ...

    def touch(self, path: P, mode: int = 0o666, exist_ok: bool = True) -> None:
        if differ := diff.DIFFER.get():
            differ.record(diff.EMPTY_STATE, (path, f"new file (mode: {mode})", None))
        self._touch(path, mode=mode, exist_ok=exist_ok)

    @abc.abstractmethod
    def _touch(self, path: P, mode: int = 0o666, exist_ok: bool = True) -> None: ...

    def mkdir(
        self,
        path: P,
        mode: int = 0o777,
        parents: bool = False,
        exist_ok: bool = False,
    ) -> None:
        if differ := diff.DIFFER.get():
            differ.record(diff.EMPTY_STATE, (path, "new directory", None))
        return self._mkdir(path, mode=mode, parents=parents, exist_ok=exist_ok)

    @abc.abstractmethod
    def _mkdir(
        self,
        path: P,
        mode: int = 0o777,
        parents: bool = False,
        exist_ok: bool = False,
    ) -> None: ...

    def copy(self, path: P, target: P) -> None:
        if differ := diff.DIFFER.get():
            differ.record(
                diff.EMPTY_STATE, (target, f"copied from {path}", self.read_text(path))
            )
        self._copy(path, target)

    @abc.abstractmethod
    def _copy(self, path: P, target: P) -> None: ...

    def unlink(self, path: P, missing_ok: bool = False) -> None:
        if differ := diff.DIFFER.get():
            try:
                content = self.read_text(path)
            except FileNotFoundError:
                if not missing_ok:
                    raise
            else:
                differ.record((path, "deleted", content), diff.EMPTY_STATE)
        self._unlink(path, missing_ok=missing_ok)

    @abc.abstractmethod
    def _unlink(self, path: P, missing_ok: bool = False) -> None: ...

    def rmdir(self, path: P) -> None:
        if differ := diff.DIFFER.get():
            differ.record((path, "directory deleted", None), diff.EMPTY_STATE)
        self._rmdir(path)

    @abc.abstractmethod
    def _rmdir(self, path: P) -> None: ...

    def chmod(self, path: P, mode: int) -> None:
        if differ := diff.DIFFER.get():
            differ.record((path, None, None), (path, f"mode -> {mode}", None))
        self._chmod(path, mode)

    @abc.abstractmethod
    def _chmod(self, path: P, mode: int) -> None: ...

    def rmtree(self, path: Path, **kwargs: Any) -> None:
        if differ := diff.DIFFER.get():
            differ.record((path, "directory tree deleted", None), diff.EMPTY_STATE)
        self._rmtree(path, **kwargs)

    @abc.abstractmethod
    def _rmtree(self, path: Path, **kwargs: Any) -> None: ...

    @contextmanager
    def _record_file(self, path: P, newcontent: str | None = None) -> Iterator[None]:
        """Context manager recording changes to 'path' during a write operation."""
        if not (differ := diff.DIFFER.get()):
            yield None
            return

        detail = None
        try:
            content = self.read_text(path)
        except FileNotFoundError:
            content = None
            fromfile = None
            detail = "created"
        else:
            fromfile = path

        try:
            yield None
        finally:
            if newcontent is None:
                newcontent = self.read_text(path)
            differ.record((fromfile, None, content), (path, detail, newcontent))


class LocalFS(AbstractFS[Path]):
    """Interface to the local filesystem."""

    def exists(self, path: Path) -> bool:
        return path.exists()

    def is_file(self, path: Path) -> bool:
        return path.is_file()

    def is_dir(self, path: Path) -> bool:
        return path.is_dir()

    @overload
    @contextmanager
    def _open(self, path: Path, mode: Literal["rb", "wb"]) -> Iterator[IO[bytes]]: ...

    @overload
    @contextmanager
    def _open(self, path: Path, mode: Literal["r", "w"] = ...) -> Iterator[IO[str]]: ...

    @contextmanager
    def _open(
        self, path: Path, mode: Literal["r", "w", "rb", "wb"] = "r"
    ) -> Iterator[IO[bytes]] | Iterator[IO[str]]:
        with path.open(mode) as f:
            yield f

    def read_text(self, path: Path) -> str:
        return path.read_text()

    def _write_text(self, path: Path, text: str) -> int:
        return path.write_text(text)

    def iterdir(self, path: Path) -> Iterator[Path]:
        return path.iterdir()

    def glob(self, path: Path, pattern: str) -> Iterator[Path]:
        return path.glob(pattern)

    def _touch(self, path: Path, mode: int = 0o666, exist_ok: bool = True) -> None:
        path.touch(mode, exist_ok)

    def _mkdir(
        self,
        path: Path,
        mode: int = 0o777,
        parents: bool = False,
        exist_ok: bool = False,
    ) -> None:
        path.mkdir(mode, parents, exist_ok)

    def _copy(self, path: Path, target: Path) -> None:
        # src.copy(dst) from Python 3.14
        shutil.copy(path, target)

    def _unlink(self, path: Path, missing_ok: bool = False) -> None:
        path.unlink(missing_ok)

    def _rmdir(self, path: Path) -> None:
        path.rmdir()

    def _chmod(self, path: Path, mode: int) -> None:
        path.chmod(mode)

    def _rmtree(self, path: Path, **kwargs: Any) -> None:
        shutil.rmtree(path, **kwargs)


LOCAL_FS = LocalFS()

FSType: TypeAlias = AbstractFS[PurePath] | AbstractFS[Path]
VAR = ContextVar[FSType]("FileSystem", default=LOCAL_FS)

FileSystem = Annotated[FSType, Dependency(VAR)]


get = VAR.get
set = VAR.set
reset = VAR.reset

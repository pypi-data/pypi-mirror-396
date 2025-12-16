# SPDX-FileCopyrightText: 2025 Dalibo
#
# SPDX-License-Identifier: GPL-3.0-or-later

"""In-memory filesystem."""

from __future__ import annotations

import itertools
from collections.abc import Iterator
from contextlib import contextmanager
from dataclasses import dataclass, field
from pathlib import Path, PurePath
from typing import IO, Any, Literal, overload

from fsspec.implementations.memory import MemoryFileSystem

from .fs import AbstractFS


@dataclass(frozen=True)
class InMemoryFS(AbstractFS[Path]):
    """In-memory filesystem, using fsspec's MemoryFileSystem as a backend."""

    backend: MemoryFileSystem = field(default_factory=MemoryFileSystem)

    def exists(self, path: Path) -> bool:
        return self.backend.exists(path)  # type: ignore[no-any-return]

    def is_file(self, path: Path) -> bool:
        return self.backend.isfile(path)  # type: ignore[no-any-return]

    def is_dir(self, path: Path) -> bool:
        return self.backend.isdir(path)  # type: ignore[no-any-return]

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
        with self.backend.open(path, mode) as f:
            yield f

    def read_text(self, path: Path) -> str:
        return self.backend.read_text(path)  # type: ignore[no-any-return]

    def _write_text(self, path: Path, text: str) -> int:
        return self.backend.write_text(path, text)  # type: ignore[no-any-return]

    def iterdir(self, path: Path) -> Iterator[Path]:
        for info in self.backend.ls(path):
            yield Path(info["name"])

    def glob(self, path: Path, pattern: str) -> Iterator[Path]:
        for f in self.backend.glob(str(path / pattern)):
            yield Path(f)

    def _touch(
        self,
        path: Path,
        mode: int = 0o666,  # noqa: ARG002
        exist_ok: bool = True,
    ) -> None:
        if not exist_ok and self.backend.exists(path):
            raise FileExistsError(f"{path} already exist")
        self.backend.touch(path)

    def _mkdir(
        self,
        path: Path,
        mode: int = 0o777,  # noqa: ARG002
        parents: bool = False,
        exist_ok: bool = False,
    ) -> None:
        try:
            self.backend.mkdir(path, create_parents=parents)
        except FileExistsError:
            if not exist_ok:
                raise

    def _copy(self, path: Path, target: Path) -> None:
        self.backend.copy(str(path), str(target))

    def _unlink(self, path: Path, missing_ok: bool = False) -> None:
        try:
            self.backend.rm_file(path)
        except FileNotFoundError:
            if not missing_ok:
                raise

    def _rmdir(self, path: Path) -> None:
        self.backend.rmdir(path)

    def _chmod(
        self,
        path: Path,
        mode: int,  # noqa: ARG002
    ) -> None:
        if not self.backend.exists(path):
            raise FileNotFoundError(path)

    def _rmtree(self, path: Path, **kwargs: Any) -> None:
        self.backend.rm(str(path), recursive=True)


@dataclass(frozen=True)
class RoFS(AbstractFS[Path]):
    """A file system that reads from real fs, but writes in-memory.

    When deleting a node, its path is added to 'deleted' set in order to keep
    track of the deletion in-memory (otherwise the real file-system will be
    queried again upon next read of a deleted file).
    """

    in_mem: InMemoryFS = field(default_factory=InMemoryFS)
    deleted: set[PurePath] = field(default_factory=set)

    def exists(self, path: Path) -> bool:
        return path not in self.deleted and (self.in_mem.exists(path) or path.exists())

    def is_file(self, path: Path) -> bool:
        if path in self.deleted:
            return False
        if self.in_mem.exists(path):
            return self.in_mem.is_file(path)
        return path.is_file()

    def is_dir(self, path: Path) -> bool:
        if path in self.deleted:
            return False
        if self.in_mem.exists(path):
            return self.in_mem.is_dir(path)
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
        if mode[0] == "w":
            # In 'w' mode, we always use in-memory filesystem; if opening fails
            # (raising FileNotFoundError), this usually means that parent
            # directory does not exists.
            with self.in_mem._open(path, mode) as f:
                yield f
            self.deleted.discard(path)
            return

        if path in self.deleted:
            raise FileNotFoundError(f"{path} got deleted")

        # In 'r' mode, we first read from in-memory filesystem, then fall back
        # to local filesystem.
        try:
            with self.in_mem._open(path, mode) as f:
                yield f
        except FileNotFoundError:
            with path.open(mode) as f:
                yield f

    def read_text(self, path: Path) -> str:
        if path in self.deleted:
            raise FileNotFoundError(f"{path} got deleted")
        try:
            return self.in_mem.read_text(path)
        except FileNotFoundError:
            return path.read_text()

    def _write_text(self, path: Path, text: str) -> int:
        parent = path.parent
        if not self.in_mem.is_dir(parent) and not parent.is_dir():
            raise FileNotFoundError(f"{parent} directory not found")
        n = self.in_mem._write_text(path, text)
        self.deleted.discard(path)
        return n

    def iterdir(self, path: Path) -> Iterator[Path]:
        if path in self.deleted:
            raise FileNotFoundError(f"{path} got deleted")
        if self.in_mem.exists(path):
            for p in self.in_mem.iterdir(path):
                if p not in self.deleted:
                    yield p
        else:
            yield from path.iterdir()

    def glob(self, path: Path, pattern: str) -> Iterator[Path]:
        for f in itertools.chain(self.in_mem.glob(path, pattern), path.glob(pattern)):
            if f not in self.deleted:
                yield Path(f)

    def _touch(
        self,
        path: Path,
        mode: int = 0o666,
        exist_ok: bool = True,
    ) -> None:
        self.in_mem._touch(path, mode=mode, exist_ok=exist_ok)
        self.deleted.discard(path)

    def _mkdir(
        self,
        path: Path,
        mode: int = 0o777,
        parents: bool = False,
        exist_ok: bool = False,
    ) -> None:
        self.in_mem._mkdir(path, mode=mode, parents=parents, exist_ok=exist_ok)
        self.deleted.discard(path)

    def _copy(self, path: Path, target: Path) -> None:
        if path in self.deleted:
            raise FileNotFoundError(f"{path} got deleted")
        if self.in_mem.exists(path):
            self.in_mem._copy(path, target)
            self.deleted.discard(target)
        elif path.exists():
            self.in_mem.backend.put_file(path, target)
            self.deleted.discard(target)
        else:
            raise FileNotFoundError(f"{path} not found on local filesystem")

    def _unlink(self, path: Path, missing_ok: bool = False) -> None:
        if path in self.deleted:
            if not missing_ok:
                raise FileNotFoundError(path)
            return
        try:
            self.in_mem._unlink(path)
        except FileNotFoundError:
            if not missing_ok and not path.exists():
                raise
        self.deleted.add(path)

    def _rmdir(self, path: Path) -> None:
        if path.is_dir():
            self.deleted.add(path)
            return
        if path in self.deleted:
            raise FileNotFoundError(path)
        if not self.in_mem.is_dir(path):
            raise NotADirectoryError(path)
        self.in_mem._rmdir(path)
        self.deleted.add(path)

    def _chmod(self, path: Path, mode: int) -> None:
        if path in self.deleted:
            raise FileNotFoundError(path)
        try:
            self.in_mem._chmod(path, mode)
        except FileNotFoundError:
            if not path.exists():
                raise

    def _rmtree(self, path: Path, **kwargs: Any) -> None:
        if path in self.deleted:
            raise FileNotFoundError(path)
        try:
            self.in_mem._rmtree(path)
        except FileNotFoundError:
            if not path.exists():
                raise
        self.deleted.add(path)

# SPDX-FileCopyrightText: 2021 Dalibo
#
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

import functools
import logging
import os
from collections.abc import Callable
from pathlib import Path, PurePath
from types import TracebackType
from typing import Any, ParamSpec, TypeVar

import humanize

from . import __name__ as pkgname
from . import deps, exceptions
from ._compat import read_resource
from .system import FileSystem

logger = logging.getLogger(__name__)


def get_logger(name: str) -> logging.Logger:
    """Return a logger for 'name' with only two levels of nesting.

    >>> get_logger("foo.bar.baz")
    <Logger foo.bar (WARNING)>
    >>> get_logger("top")
    <Logger top (WARNING)>
    """
    return logging.getLogger(".".join(name.split(".", 2)[:2]))


P = ParamSpec("P")
R = TypeVar("R")


def cache(fn: Callable[P, R], /) -> Callable[P, R]:
    if "PYTEST_VERSION" in os.environ:
        return fn
    return functools.cache(fn)  # type: ignore[return-value]


def joinpath(base: str | PurePath, *args: str) -> Path:
    """Shorthand for Path.joinpath().

    >>> p = joinpath("a", "b", "c")
    >>> p.as_posix()
    'a/b/c'
    """
    return Path(base).joinpath(*args)


def environ() -> dict[str, str]:
    """Return the pglift-specific environment mapping."""
    prefix = pkgname.upper()
    return {k: v for k, v in os.environ.items() if k.startswith(f"{prefix}_")}


def template(bases: str | tuple[tuple[str, ...] | str, ...], *args: str) -> str:
    r"""Return the content of a configuration file template, either found in
    site configuration or in distribution data.

    :param bases: The base component(s) of the path where the template file
        will be looked for; may be a single string or a tuple of string-tuples
        describing alternative "bases" to look into.
    :param args: Final path components of the template file to look for.

    :return: The content of found template file.

    Examples:

    Look for 'postgresql/pg_hba.conf' in site configuration and then
    distribution data::

        >>> print(template("postgresql", "pg_hba.conf"))
        local   all             {surole}                                {auth.local}
        local   all             all                                     {auth.local}
        host    all             all             127.0.0.1/32            {auth.host}
        host    all             all             ::1/128                 {auth.host}
        <BLANKLINE>

    Look for 'postgresql.conf' template first in 'postgresql/16' directory in
    site configuration and fall back to 'postgresql/postgresql.conf' in
    distribution data::

        >>> print(template((("postgresql", "16"), "postgresql"), "postgresql.conf"))
        cluster_name = {name}
        shared_buffers = 25%
        effective_cache_size = 66%
        unix_socket_directories = {settings.socket_directory}
        log_directory = {settings.logpath}
        log_filename = '{version}-{name}-%Y-%m-%d_%H%M%S.log'
        log_destination = 'stderr'
        logging_collector = on
        <BLANKLINE>
    """
    file_content = read_site_config(bases, *args)
    assert file_content is not None
    return file_content


def etc() -> Path:
    return Path("/etc")


def xdg_config_home() -> Path:
    return Path(os.environ.get("XDG_CONFIG_HOME", Path.home() / ".config"))


def xdg_data_home() -> Path:
    return Path(os.environ.get("XDG_DATA_HOME", Path.home() / ".local" / "share"))


@deps.use
def xdg_runtime_dir(uid: int, *, fs: FileSystem = deps.Auto) -> Path:
    runtime_dir = Path(os.environ.get("XDG_RUNTIME_DIR", f"/run/user/{uid}"))
    if fs.exists(runtime_dir):
        return runtime_dir
    raise exceptions.FileNotFoundError(f"{runtime_dir} does not exist")


def etc_config(*parts: str) -> tuple[Path, str] | None:
    """Return content of a configuration file in /etc."""
    base = etc() / pkgname
    return fs_config(base, *parts)


def xdg_config(*parts: str) -> tuple[Path, str] | None:
    """Return content of a configuration file in $XDG_CONFIG_HOME."""
    base = xdg_config_home() / pkgname
    return fs_config(base, *parts)


@deps.use
def fs_config(
    base: Path, *parts: str, fs: FileSystem = deps.Auto
) -> tuple[Path, str] | None:
    config = joinpath(base, *parts)
    if fs.exists(config):
        return config, str(base)
    return None


@deps.use
def custom_dir(fs: FileSystem = deps.Auto) -> Path | None:
    """Return the custom configuration path from PGLIFT_CONFIG_DIR environment
    variable. Return None if the variable is unset.

    :raise ~exceptions.FileNotFoundError: if custom configuration directory is missing.
    """
    if (env_var := os.environ.get("PGLIFT_CONFIG_DIR", None)) is None:
        return None
    c_dir = Path(env_var)
    if fs.exists(c_dir):
        return c_dir
    raise exceptions.FileNotFoundError(
        f"{env_var} (set via PGLIFT_CONFIG_DIR) does not exist"
    )


def site_config(
    bases: str | tuple[tuple[str, ...] | str, ...], *args: str
) -> Path | None:
    """Lookup for a configuration file path in custom, user or site
    configuration.
    """
    _custom_dir = custom_dir()
    if isinstance(bases, str):
        bases = (bases,)
    for bs in bases:
        if isinstance(bs, str):
            bs = (bs,)
        if _custom_dir is not None:
            result = fs_config(_custom_dir, *bs, *args)
        else:
            for hdlr in (xdg_config, etc_config):
                if result := hdlr(*bs, *args):
                    break
        if result is not None:
            config, source = result
            logger.debug(
                "using '%s' configuration file from site (source: %s)",
                joinpath(*bs, *args),
                source if _custom_dir is None else f"PGLIFT_CONFIG_DIR={source}",
            )
            return config
    return None


def read_dist_config(*parts: str) -> str | None:
    """Return content of a configuration file in distribution resources."""
    subpkgs, resource_name = parts[:-1], parts[-1]
    pkg = ".".join([pkgname] + list(subpkgs))
    logger.debug(
        "using '%s' configuration file from distribution",
        joinpath(*subpkgs).joinpath(resource_name),
    )
    return read_resource(pkg, resource_name)


@deps.use
def read_site_config(
    bases: str | tuple[tuple[str, ...] | str, ...],
    *args: str,
    fs: FileSystem = deps.Auto,
) -> str | None:
    """Return content of a configuration file looked-up in custom, user or
    site location, and fall back to distribution if not found.
    """
    if config := site_config(bases, *args):
        return fs.read_text(config)
    if isinstance(bases, tuple):
        base = bases[-1]
        assert isinstance(base, str), f"expecting a string as last item of {bases}"
    else:
        base = bases
    return read_dist_config(base, *args)


def with_header(content: str, header: str) -> str:
    """Possibly insert `header` on top of `content`.

    >>> print(with_header("blah", "% head"))
    % head
    blah
    >>> with_header("content", "")
    'content'
    """
    if header:
        content = "\n".join([header, content])
    return content


def parse_filesize(value: str) -> float:
    """Parse a file size string as float, in bytes unit.

    >>> parse_filesize("6022056 kB")
    6166585344.0
    >>> parse_filesize("0")
    Traceback (most recent call last):
        ...
    ValueError: malformatted file size '0'
    >>> parse_filesize("5 km")
    Traceback (most recent call last):
        ...
    ValueError: invalid unit 'km'
    >>> parse_filesize("5 yb")
    Traceback (most recent call last):
        ...
    ValueError: invalid unit 'yb'
    """
    units = ["B", "K", "M", "G", "T"]
    try:
        val, unit = value.split(None, 1)
        mult, b = list(unit)
    except ValueError as e:
        raise ValueError(f"malformatted file size {value!r}") from e
    if b.lower() != "b":
        raise ValueError(f"invalid unit {unit!r}")
    try:
        scale = units.index(mult.upper())
    except ValueError as e:
        raise ValueError(f"invalid unit {unit!r}") from e
    return (1024**scale) * float(val)  # type: ignore[no-any-return]


@deps.use
def total_memory(
    path: Path = Path("/proc/meminfo"), *, fs: FileSystem = deps.Auto
) -> float:
    """Read 'MemTotal' field from /proc/meminfo.

    :raise ~exceptions.SystemError: if reading the value failed.
    """
    with fs.open(path) as meminfo:
        for line in meminfo:
            if not line.startswith("MemTotal:"):
                continue
            return parse_filesize(line.split(":", 1)[-1].strip())
        else:
            raise exceptions.SystemError(
                f"could not retrieve memory information from {path}"
            )


def percent_memory(value: str, total: float) -> str:
    """Convert 'value' from a percentage of total memory into a memory setting
    or return (as is if not a percentage value).

    >>> percent_memory(" 1GB", 1)
    '1GB'
    >>> percent_memory("25%", 4e9)
    '1 GB'
    >>> percent_memory("xyz%", 3e9)
    Traceback (most recent call last):
      ...
    ValueError: invalid percent value 'xyz'
    """
    value = value.strip()
    if value.endswith("%"):
        value = value[:-1].strip()
        try:
            percent_value = float(value) / 100
        except ValueError as e:
            raise ValueError(f"invalid percent value {value!r}") from e
        value = humanize.naturalsize(total * percent_value, format="%d")
    return value


@deps.use
def check_or_create_directory(
    path: Path, purpose: str, *, fs: FileSystem = deps.Auto, **kwargs: Any
) -> None:
    """Ensure that 'path' directory is writable, or create it."""
    if fs.exists(path):
        if not fs.is_dir(path):
            raise exceptions.SystemError(f"{path} exists but is not a directory")
        if not os.access(path, os.W_OK):
            raise exceptions.SystemError(
                f"{purpose} directory {path} exists but is not writable"
            )
    else:
        logger.info("creating %s directory: %s", purpose, path)
        fs.mkdir(path, parents=True, exist_ok=True, **kwargs)


@deps.use
def rmdir(path: Path, *, fs: FileSystem = deps.Auto) -> bool:
    """Try to remove 'path' directory, log a warning in case of failure,
    return True upon success.
    """
    try:
        fs.rmdir(path)
        return True
    except OSError as e:
        logger.warning("failed to remove directory %s: %s", path, e)
        return False


@deps.use
def rmtree(
    path: Path, ignore_errors: bool = False, *, fs: FileSystem = deps.Auto
) -> None:
    def log(
        _func: Any,
        thispath: Any,
        exc_info: tuple[type[BaseException], BaseException, TracebackType],
    ) -> None:
        logger.warning(
            "failed to delete %s during tree deletion of %s: %s",
            thispath,
            path,
            exc_info[1],
        )

    fs.rmtree(path, ignore_errors=ignore_errors, onerror=log)


@deps.use
def is_empty_dir(path: Path, *, fs: FileSystem = deps.Auto) -> bool:
    """Check that a directory is empty or not."""
    return next(fs.iterdir(path), None) is None


KeyType = TypeVar("KeyType")


def deep_update(
    mapping: dict[KeyType, Any], *updating_mappings: dict[KeyType, Any]
) -> dict[KeyType, Any]:
    """
    Recursively update a mapping with one or more update dicts.

    This mimics `pydantic.v1.utils.deep_update`.

    >>> ori = {"a": {"x": 1}}
    >>> patch = {"a": {"y": 2}}
    >>> deep_update(ori, patch)
    {'a': {'x': 1, 'y': 2}}
    >>> ori
    {'a': {'x': 1}}
    >>> patch
    {'a': {'y': 2}}

    >>> ori = {"a": {"x": {"m": 1, "o": 2}}}
    >>> patch = {"a": {"y": 2, "x": {"m": 4}}}
    >>> deep_update(ori, patch)
    {'a': {'x': {'m': 4, 'o': 2}, 'y': 2}}
    >>> ori
    {'a': {'x': {'m': 1, 'o': 2}}}
    >>> patch
    {'a': {'y': 2, 'x': {'m': 4}}}
    """
    updated_mapping = mapping.copy()
    for updating_mapping in updating_mappings:
        for k, v in updating_mapping.items():
            if (
                k in updated_mapping
                and isinstance(updated_mapping[k], dict)
                and isinstance(v, dict)
            ):
                updated_mapping[k] = deep_update(updated_mapping[k], v)
            else:
                updated_mapping[k] = v
    return updated_mapping


def lenient_issubclass(
    cls: Any, class_or_tuple: type[Any] | tuple[type[Any], ...]
) -> bool:
    """
    Safe version of issubclass that returns False instead of raising TypeError
    when `cls` is not a class.

    This mimics `pydantic.v1.utils.lenient_issubclass`.

    >>> lenient_issubclass(int, object)
    True
    >>> lenient_issubclass(123, object)
    False
    >>> lenient_issubclass("str", str)
    False
    >>> lenient_issubclass(str, (int, float))
    False
    """
    try:
        return issubclass(cls, class_or_tuple)
    except TypeError:
        return False

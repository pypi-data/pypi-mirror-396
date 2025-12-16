# SPDX-FileCopyrightText: 2021 Dalibo
#
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

from functools import partial
from pathlib import Path
from typing import Any

import pgtoolkit.conf as pgconf

from . import deps, exceptions, util
from .settings import _postgresql
from .system import FileSystem
from .types import ConfigChanges


def make(**confitems: pgconf.Value | None) -> pgconf.Configuration:
    """Return a :class:`pgtoolkit.conf.Configuration` filled with given items."""
    conf = pgconf.Configuration()
    for key, value in confitems.items():
        if value is not None:
            conf[key] = value
    return conf


@deps.use
def read(
    configdir: Path, managed_only: bool = False, *, fs: FileSystem = deps.Auto
) -> pgconf.Configuration:
    """Return parsed PostgreSQL configuration for given `configdir`.

    If ``managed_only`` is ``True``, only the managed configuration is
    returned excluding 'postgresql.auto.conf' or 'recovery.conf', otherwise
    the fully parsed configuration is returned.

    :raises ~exceptions.FileNotFoundError: if expected configuration file is missing.
    """
    postgresql_conf = configdir / "postgresql.conf"
    try:
        with fs.open(postgresql_conf) as f:
            config = pgconf.parse(f)
    except FileNotFoundError as e:
        raise exceptions.FileNotFoundError(
            f"PostgreSQL configuration file not found: {e}"
        ) from e

    if managed_only:
        return config

    for extra_conf in ("postgresql.auto.conf", "recovery.conf"):
        try:
            with fs.open(configdir / extra_conf) as f:
                config += pgconf.parse(f)
        except FileNotFoundError:
            pass
    return config


@deps.use
def save(
    configdir: Path, conf: pgconf.Configuration, *, fs: FileSystem = deps.Auto
) -> None:
    with fs.open(configdir / "postgresql.conf", "w") as f:
        conf.save(f)


def update(base: pgconf.Configuration, **values: pgconf.Value) -> None:
    """Update 'base' configuration so that it contains new values.

    Entries absent from 'values' but present in 'base' are commented out.
    """
    with base.edit() as entries:
        for key, value in list(entries.items()):
            if value.commented:
                continue
            try:
                new = values.pop(key)
            except KeyError:
                entries[key].commented = True
            else:
                entries[key].value = new
                entries[key].commented = False
        for key, val in values.items():
            try:
                entries[key].value = val
                entries[key].commented = False
            except KeyError:
                entries.add(key, val)


def merge(base: pgconf.Configuration, **values: pgconf.Value) -> None:
    """Merge new values into 'base' configuration.

    Only entries from 'values' are updated in 'base'. Entries not in values
    will be left untouched, as opposed to with update where they are
    commented out.
    """
    with base.edit() as entries:
        for key, val in values.items():
            try:
                entries[key].value = val
                entries[key].commented = False
            except KeyError:
                entries.add(key, val)


def changes(before: dict[str, Any], after: dict[str, Any]) -> ConfigChanges:
    """Return changes between two PostgreSQL configuration."""
    changes = {}
    for k in set(before) | set(after):
        pv = before.get(k)
        nv = after.get(k)
        if nv != pv:
            changes[k] = (pv, nv)
    return changes


def merge_lists(first: str, second: str) -> str:
    """Concatenate two coma separated lists eliminating duplicates.

    >>> old = ""
    >>> new = "foo"
    >>> merge_lists(old, new)
    'foo'

    >>> old = "foo, bar, dude"
    >>> new = "bar, truite"
    >>> merge_lists(old, new)
    'foo, bar, dude, truite'
    """
    first_list = [s.strip() for s in first.split(",") if s.strip()]
    second_list = [s.strip() for s in second.split(",") if s.strip()]
    return ", ".join(first_list + [s for s in second_list if s not in first_list])


def format_values(
    confitems: dict[str, Any],
    name: str,
    version: str,
    settings: _postgresql.Settings,
    memtotal: float = util.total_memory(),
) -> None:
    """Replace placeholders in 'confitems' values by formatted values.

    >>> settings = _postgresql.Settings()
    >>> confitems = {
    ...     "shared_buffers": "12%",
    ...     "name": "{version}+{name}",
    ...     "enc": "{settings.initdb.locale}",
    ... }
    >>> format_values(confitems, "foo", "12", settings, memtotal=123456)
    >>> confitems
    {'shared_buffers': '14 kB', 'name': '12+foo', 'enc': 'C'}
    """
    for k in ("shared_buffers", "effective_cache_size"):
        try:
            v = confitems[k]
        except KeyError:
            continue
        if v is None:
            continue
        try:
            confitems[k] = util.percent_memory(v, memtotal)
        except ValueError:
            pass
    for k, v in confitems.items():
        if isinstance(v, str):
            confitems[k] = v.format(name=name, version=version, settings=settings)


def get_str(config: pgconf.Configuration, key: str, default: str | None = None) -> str:
    r"""Get a string value from a Configuration.

    >>> config = pgconf.parse(["port=5555\n", "work_mem=10MB\n"])
    >>> get_str(config, "work_mem")
    '10MB'
    >>> get_str(config, "foo", "xyz")
    'xyz'
    >>> get_str(config, "bar")
    Traceback (most recent call last):
      ...
    KeyError: 'bar'
    >>> get_str(config, "port")
    Traceback (most recent call last):
      ...
    ValueError: unexpected int type for 'port' option
    """
    try:
        value = config[key]
    except KeyError:
        if default is None:
            raise
        return default
    if not isinstance(value, str):
        raise ValueError(f"unexpected {type(value).__name__} type for {key!r} option")
    return value


def get_int(config: pgconf.Configuration, key: str, default: int | None = None) -> int:
    r"""Get an integer value from a Configuration.

    >>> config = pgconf.parse(["port=5555\n", "work_mem=10MB\n"])
    >>> get_int(config, "port")
    5555
    >>> get_int(config, "foo", 0)
    0
    >>> get_int(config, "bar")
    Traceback (most recent call last):
      ...
    KeyError: 'bar'
    >>> get_int(config, "work_mem")
    Traceback (most recent call last):
        ...
    ValueError: invalid literal for int() with base 10: '10MB'

    >>> get_port(config)
    5555
    """
    try:
        value = config[key]
    except KeyError:
        if default is None:
            raise
        return default
    return int(value)  # type: ignore[arg-type]


get_port = partial(get_int, key="port", default=5432)

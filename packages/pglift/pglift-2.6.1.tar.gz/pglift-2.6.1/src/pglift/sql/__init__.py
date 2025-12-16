# SPDX-FileCopyrightText: 2021 Dalibo
#
# SPDX-License-Identifier: GPL-3.0-or-later
#
"""SQL query functions based on queries.sql file."""

import re
from collections.abc import Iterator

from psycopg.sql import SQL as SQL
from psycopg.sql import Composable as Composable
from psycopg.sql import Composed as Composed
from psycopg.sql import Identifier as Identifier
from psycopg.sql import Literal as Literal

from .._compat import read_resource
from . import __name__ as pkgname


def query(name: str, **kwargs: Composable) -> Composed:
    q = _query(name)
    return SQL(q).format(**kwargs)


def queries(name: str, **kwargs: Composable) -> Iterator[Composed]:
    q = _query(name)
    for line in q.split(";"):
        yield SQL(line.strip()).format(**kwargs)


def _query(name: str) -> str:
    for qname, qstr in _queries_by_name():
        if qname == name:
            return qstr
    raise ValueError(name)


def _queries_by_name() -> Iterator[tuple[str, str]]:
    content = read_resource(pkgname, "queries.sql")
    assert content is not None
    for block in re.split("-- name:", content):
        if not (block := block.strip()):
            continue
        qname, query = block.split("\n", 1)
        yield qname.strip(), query.strip()

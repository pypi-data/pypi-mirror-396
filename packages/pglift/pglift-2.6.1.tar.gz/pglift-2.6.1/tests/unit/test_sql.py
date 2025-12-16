# SPDX-FileCopyrightText: 2021 Dalibo
#
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import patch

from pglift import sql


def test__queries_by_name(expected_dir: Path, write_changes: bool) -> None:
    actual = dict(sql._queries_by_name())
    fpath = expected_dir / "queries.json"
    if write_changes:
        fpath.write_text(json.dumps(actual, indent=2, sort_keys=True) + "\n")
    expected = json.loads(fpath.read_text())
    assert actual == expected


def test_query() -> None:
    query = sql.query(
        "role_alter",
        username=sql.Identifier("bob"),
        options=sql.Literal("PASSWORD 'ha'"),
    )
    assert list(query) == [
        sql.SQL("ALTER ROLE "),
        sql.Identifier("bob"),
        sql.SQL(" "),
        sql.Literal("PASSWORD 'ha'"),
        sql.SQL(";"),
    ]


def test_queries() -> None:
    with patch(
        "pglift.sql._queries_by_name",
        return_value=[
            ("foo", "select 123"),
            ("bar", "select {x}; select {y}; select {z}"),
        ],
    ) as queries_by_name:
        queries = list(
            sql.queries(
                "bar",
                x=sql.Identifier("x"),
                y=sql.Identifier("y"),
                z=sql.Identifier("z"),
            )
        )
        queries_by_name.assert_called_once_with()
        assert queries == [
            sql.Composed([sql.SQL("select "), sql.Identifier("x")]),
            sql.Composed([sql.SQL("select "), sql.Identifier("y")]),
            sql.Composed([sql.SQL("select "), sql.Identifier("z")]),
        ]

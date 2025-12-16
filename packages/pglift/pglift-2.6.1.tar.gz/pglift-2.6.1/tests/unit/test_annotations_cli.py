# SPDX-FileCopyrightText: 2024 Dalibo
#
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

import pytest

from pglift.annotations import cli


@pytest.mark.parametrize(
    "opt, argname, expected",
    [
        (cli.ListOption(), "foo", ("add_foo", "remove_foo")),
        (
            cli.ListOption(names={"add": "--foo", "remove": "--no-foo"}),
            "whatever",
            ("foo", "no_foo"),
        ),
    ],
)
def test_listoption_argnames(
    opt: cli.ListOption, argname: str, expected: tuple[str, str]
) -> None:
    assert opt.argnames(argname) == expected


@pytest.mark.parametrize(
    "opt, optname, expected",
    [
        (cli.ListOption(name="foo"), None, ("--add-foo", "--remove-foo")),
        (
            cli.ListOption(names={"add": "--foo", "remove": "--no-foo"}),
            None,
            ("--foo", "--no-foo"),
        ),
        (cli.ListOption(), "foo", ("--add-foo", "--remove-foo")),
    ],
)
def test_listoption_optnames(
    opt: cli.ListOption, optname: str | None, expected: tuple[str, str]
) -> None:
    assert opt.optnames(optname) == expected


@pytest.mark.parametrize(
    "opt, optdesc, expected",
    [
        (cli.ListOption(), "my desc", ("my desc", "my desc")),
        (
            cli.ListOption(descriptions={"add": "add", "remove": "rm"}),
            None,
            ("add", "rm"),
        ),
    ],
)
def test_listoption_optdescs(
    opt: cli.ListOption, optdesc: str | None, expected: tuple[str, str]
) -> None:
    assert opt.optdescs(optdesc) == expected

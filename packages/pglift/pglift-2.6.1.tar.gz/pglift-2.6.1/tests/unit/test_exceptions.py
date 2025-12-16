# SPDX-FileCopyrightText: 2021 Dalibo
#
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

from pathlib import Path

from pglift import exceptions


def test_error() -> None:
    err = exceptions.Error("oups")
    assert str(err) == "oups"


def test_notfound() -> None:
    err = exceptions.InstanceNotFound("12/main")
    assert str(err) == "instance '12/main' not found"


def test_configurationerror() -> None:
    err = exceptions.ConfigurationError(Path("/etc/tool.conf"), "missing 'foo' option")
    assert str(err) == "missing 'foo' option (path: /etc/tool.conf)"

# SPDX-FileCopyrightText: 2021 Dalibo
#
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

import re

import pglift


def test_execpath() -> None:
    assert re.match(r".*python\S* -m pglift_cli$", pglift.execpath)

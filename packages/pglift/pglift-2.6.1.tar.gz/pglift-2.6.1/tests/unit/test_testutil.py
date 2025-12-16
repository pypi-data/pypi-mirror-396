# SPDX-FileCopyrightText: 2024 Dalibo
#
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

import pydantic

from pglift.testutil import model_copy_validate


def test_model_copy_validate() -> None:
    class S(pydantic.BaseModel):
        f: str
        g: str = pydantic.Field(default="unset", exclude=True)

    s = S(f="f", g="g")
    assert model_copy_validate(s, {"g": "G"}).g == "G"

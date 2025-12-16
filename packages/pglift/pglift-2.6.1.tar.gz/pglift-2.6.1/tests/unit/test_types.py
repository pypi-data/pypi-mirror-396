# SPDX-FileCopyrightText: 2021 Dalibo
#
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

import typing
from dataclasses import dataclass

import pydantic
import pytest

from pglift import types
from pglift.types import Address, field_annotation


@dataclass(frozen=True)
class MyAnnotation:
    x: str


class M(pydantic.BaseModel):
    x: int
    y: typing.Annotated[str, MyAnnotation("a"), ("a", "b")]


def test_field_annotation() -> None:
    assert field_annotation(M.model_fields["x"], MyAnnotation) is None
    assert field_annotation(M.model_fields["y"], dict) is None
    assert field_annotation(M.model_fields["y"], MyAnnotation) == MyAnnotation("a")
    assert field_annotation(M.model_fields["y"], tuple) == ("a", "b")


def test_address() -> None:
    class Cfg(pydantic.BaseModel):
        addr: Address

    cfg = Cfg(addr="server:123")
    assert cfg.addr == "server:123"
    assert types.address_host(cfg.addr) == "server"
    assert types.address_port(cfg.addr) == 123

    a = Address("server:123")
    assert types.address_host(a) == "server"
    assert types.address_port(a) == 123

    # no validation
    assert str(Address("server")) == "server"

    with pytest.raises(pydantic.ValidationError, match="String should match pattern"):
        Cfg(addr="server")
    with pytest.raises(pydantic.ValidationError, match="String should match pattern"):
        Cfg(addr="server:ab")

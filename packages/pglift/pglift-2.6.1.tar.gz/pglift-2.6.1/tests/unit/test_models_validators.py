# SPDX-FileCopyrightText: 2021 Dalibo
#
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

import socket
from typing import Annotated, Any
from unittest.mock import create_autospec

import port_for
import pydantic
import pytest

from pglift import types
from pglift.models.types import Port
from pglift.models.validators import check_port_available


def test_check_port_available() -> None:
    p = port_for.select_random()
    info = create_autospec(pydantic.ValidationInfo)
    info.context = {"operation": "create"}
    assert check_port_available(p, info) == p
    with socket.socket() as s:
        s.bind(("", p))
        s.listen()
        with pytest.raises(ValueError, match=f"port {p} already in use"):
            check_port_available(p, info)
        info.context = {"operation": "update"}
        assert check_port_available(p, info) == p


p1 = port_for.select_random()
p2 = port_for.select_random()


def short_str(value: str) -> str:
    if len(value) > 2:
        raise AssertionError(f"string is too long: {value}")
    return value


class S(types.BaseModel):
    name: Annotated[str, pydantic.AfterValidator(short_str)] = "ab"
    s_port: Annotated[Port, pydantic.Field(validate_default=True)] = p2


class M(types.BaseModel):
    m_port: Annotated[Port, pydantic.Field(validate_default=True)] = p1
    s: Annotated[S, pydantic.Field(default_factory=dict, validate_default=True)]


@pytest.mark.parametrize(
    "obj, is_valid, expected_errors",
    [
        (
            {"m_port": p1, "s": {"s_port": p2}},
            True,
            [
                {
                    "input": p1,
                    "loc": ("m_port",),
                    "msg": f"Value error, port {p1} already in use",
                    "type": "value_error",
                },
                {
                    "input": p2,
                    "loc": ("s", "s_port"),
                    "msg": f"Value error, port {p2} already in use",
                    "type": "value_error",
                },
            ],
        ),
        (
            {"s": {"name": "xyz"}},
            False,
            [
                {
                    "input": p1,
                    "loc": ("m_port",),
                    "msg": f"Value error, port {p1} already in use",
                    "type": "value_error",
                },
                {
                    "input": "xyz",
                    "loc": ("s", "name"),
                    "msg": "Assertion failed, string is too long: xyz",
                    "type": "assertion_error",
                },
                {
                    "type": "value_error",
                    "loc": ("s", "s_port"),
                    "msg": f"Value error, port {p2} already in use",
                    "input": p2,
                },
            ],
        ),
        (
            {},
            True,
            [
                {
                    "type": "value_error",
                    "loc": ("m_port",),
                    "msg": f"Value error, port {p1} already in use",
                    "input": p1,
                },
                {
                    "type": "value_error",
                    "loc": ("s", "s_port"),
                    "msg": f"Value error, port {p2} already in use",
                    "input": p2,
                },
            ],
        ),
    ],
    ids=["specified values", "default ports", "default values"],
)
def test_port_validator(
    obj: Any, is_valid: bool, expected_errors: list[dict[str, Any]]
) -> None:
    if is_valid:
        with types.validation_context(operation="create"):
            m = M.model_validate(obj)
        assert m.model_dump() == {
            "m_port": p1,
            "s": {"name": "ab", "s_port": p2},
        }

    def filter_error(d: Any) -> Any:
        del d["ctx"]
        del d["url"]
        return d

    with socket.socket() as s1, socket.socket() as s2:
        s1.bind(("", p1))
        s1.listen()
        s2.bind(("", p2))
        s2.listen()
        with types.validation_context(operation="create"):
            with pytest.raises(pydantic.ValidationError) as cm:
                M.model_validate(obj)
        errors = cm.value.errors()
        assert [filter_error(e) for e in errors] == expected_errors

        if is_valid:
            with types.validation_context(operation="update"):
                m = M.model_validate(obj)
            assert m.model_dump() == {"m_port": p1, "s": {"name": "ab", "s_port": p2}}

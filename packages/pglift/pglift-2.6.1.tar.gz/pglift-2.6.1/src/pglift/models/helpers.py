# SPDX-FileCopyrightText: 2021 Dalibo
#
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

import typing
from collections.abc import Mapping
from datetime import datetime
from types import NoneType, UnionType
from typing import Any, Union

import pydantic
import pydantic_core

from .._compat import assert_never
from ..annotations import ansible
from ..types import field_annotation
from ..util import lenient_issubclass
from .types import Port

ModelType = type[pydantic.BaseModel]


def is_optional(t: Any) -> bool:
    """Return True if the field info is an optional type.

    >>> is_optional(typing.Optional[str])
    True
    >>> is_optional(dict[str, int])
    False
    """
    if (origin := typing.get_origin(t)) is typing.Optional:
        return True
    if origin in (Union, UnionType):
        args = typing.get_args(t)
        return len(args) == 2 and NoneType in args
    return False


def optional_type(t: Any) -> type:
    """Return the inner type of field, if an Optional.

    >>> optional_type(typing.Optional[str])
    <class 'str'>
    >>> optional_type(dict[str, int])
    Traceback (most recent call last):
        ...
    ValueError: dict[str, int] is not an optional
    """
    if not is_optional(t):
        raise ValueError(f"{t} is not an optional")
    for a in typing.get_args(t):
        if a is not NoneType:
            return a  # type: ignore[no-any-return]
    assert_never(a)


PYDANTIC2ANSIBLE: Mapping[type[Any] | str, ansible.ArgSpec] = {
    bool: {"type": "bool"},
    float: {"type": "float"},
    Port: {"type": "int"},
    int: {"type": "int"},
    str: {"type": "str"},
    pydantic.PostgresDsn: {"type": "str"},
    pydantic.SecretStr: {"type": "str", "no_log": True},
    datetime: {"type": "str"},
}


def argspec_from_model(model_type: ModelType) -> dict[str, ansible.ArgSpec]:
    """Return the Ansible module argument spec object corresponding to a
    pydantic model class.
    """
    spec = {}

    def description_list(value: str) -> list[str]:
        return list(filter(None, (s.strip() for s in value.rstrip(".").split(". "))))

    for fname, field in model_type.model_fields.items():
        if field_annotation(field, ansible.Hidden):
            continue

        ftype = field.annotation
        assert ftype is not None
        assert not isinstance(ftype, typing.ForwardRef), (
            f"field {fname!r} of {model_type} is a ForwardRef"
        )
        if is_optional(ftype):
            ftype = optional_type(ftype)

        origin_type = typing.get_origin(ftype)
        if origin_type is typing.Annotated:
            ftype = typing.get_args(ftype)[0]
            assert ftype is not None
        is_model = lenient_issubclass(origin_type or ftype, pydantic.BaseModel)
        is_list = lenient_issubclass(origin_type or ftype, list)
        is_dict = lenient_issubclass(origin_type or ftype, Mapping)

        if spec_config := field_annotation(field, ansible.Spec):
            arg_spec = spec_config.spec
        else:
            arg_spec = ansible.ArgSpec()
            try:
                arg_spec.update(PYDANTIC2ANSIBLE[ftype])
            except KeyError:
                if is_model:
                    arg_spec = {
                        "type": "dict",
                        "options": argspec_from_model(ftype),
                        "description": description_list(field.description or fname),
                    }
                elif origin_type is typing.Literal:  # const or enum
                    if choices_config := field_annotation(field, ansible.Choices):
                        arg_spec["choices"] = choices_config.choices
                    else:
                        arg_spec["choices"] = list(typing.get_args(ftype))
                elif is_list:
                    arg_spec["type"] = "list"
                    (sub_type,) = typing.get_args(ftype)
                    if typing.get_origin(sub_type) is typing.Annotated:
                        sub_type = typing.get_args(sub_type)[0]
                        assert sub_type is not None
                    if lenient_issubclass(sub_type, pydantic.BaseModel):
                        arg_spec["elements"] = "dict"
                        arg_spec["options"] = argspec_from_model(sub_type)
                    else:
                        arg_spec["elements"] = sub_type.__name__
                elif is_dict:
                    arg_spec["type"] = "dict"

        if field.is_required():
            arg_spec.setdefault("required", True)

        if field.default not in (None, pydantic_core.PydanticUndefined):
            default = field.get_default(call_default_factory=True)
            if is_model and isinstance(default, pydantic.BaseModel):
                default = default.model_dump(by_alias=True)
            arg_spec.setdefault("default", default)

        if field.description:
            arg_spec.setdefault("description", description_list(field.description))
        spec[field.alias or fname] = arg_spec

    return spec

# SPDX-FileCopyrightText: 2024 Dalibo
#
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

from typing import Any, TypedDict

import attrs


@attrs.define(frozen=True)
class Hidden:
    """Mark the field as hidden."""


HIDDEN = Hidden()


class ArgSpec(TypedDict, total=False):
    required: bool
    type: str
    default: Any
    choices: list[str]
    description: list[str]
    no_log: bool
    elements: str
    options: dict[str, Any]


@attrs.define(frozen=True)
class Spec:
    """Completely configure the field with given 'spec'."""

    spec: ArgSpec


@attrs.define(frozen=True)
class Choices:
    """Restrict field values to specified choices."""

    choices: list[str]

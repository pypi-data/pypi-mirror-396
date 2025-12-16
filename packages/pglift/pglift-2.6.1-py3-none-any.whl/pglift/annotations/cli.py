# SPDX-FileCopyrightText: 2024 Dalibo
#
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

from typing import TypedDict

import attrs


@attrs.define(frozen=True)
class Hidden:
    """Mark the field as hidden."""


HIDDEN = Hidden()


@attrs.define(frozen=True, kw_only=True)
class Parameter:
    """Base class for CLI annotations (positional arguments and options).

    This class is used to filter CLI annotations from Annotated arguments;
    actual CLI annotations should be defined using more specific classes.
    """

    name: str | None = None


@attrs.define(frozen=True, kw_only=True)
class Choices(Parameter):
    """Choices parameter (may be an argument or an option)."""

    choices: list[str]


@attrs.define(frozen=True, kw_only=True)
class Argument(Parameter):
    """Positional parameter, usually non-optional."""

    metavar: str | None = None


class Option(Argument):
    """Option-like parameter, optional in general, but may be attached to a
    required field intentionally for UX purpose.
    """


class AddRemove(TypedDict):
    add: str
    remove: str


@attrs.define(frozen=True, kw_only=True)
class ListOption(Option):
    item_key: str = "name"
    names: AddRemove | None = None
    descriptions: AddRemove | None = None

    def argnames(self, name: str, /) -> tuple[str, str]:
        def asargname(optname: str) -> str:
            return optname.removeprefix("--").replace("-", "_")

        if self.names:
            return asargname(self.names["add"]), asargname(self.names["remove"])
        return f"add_{name}", f"remove_{name}"

    def optnames(self, name: str | None = None, /) -> tuple[str, str]:
        if self.names:
            return self.names["add"], self.names["remove"]
        if self.name:
            name = self.name
        elif not name:
            raise TypeError("a default name is required")
        name = name.replace("_", "-")
        return f"--add-{name}", f"--remove-{name}"

    def optdescs(self, description: str | None = None) -> tuple[str | None, str | None]:
        if self.descriptions:
            return self.descriptions["add"], self.descriptions["remove"]
        return description, description

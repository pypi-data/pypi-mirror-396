# SPDX-FileCopyrightText: 2023 Dalibo
#
# SPDX-License-Identifier: GPL-3.0-or-later
from __future__ import annotations

from typing import Protocol


class UserInterface(Protocol):
    def confirm(self, message: str, /, *, default: bool) -> bool:
        """Possible ask for confirmation of an action before running.

        Interactive implementations should prompt for confirmation with
        'message' and use the 'default' value as default. Non-interactive
        implementations (this one), will always return the 'default' value.
        """
        ...

    def prompt(self, message: str, /, *, hide_input: bool = False) -> str | None:
        """Possible ask for user input.

        Interactive implementation should prompt for input with 'message' and
        return a string value. Non-Interactive implementations (this one), will
        always return None.
        """
        ...

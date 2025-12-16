# SPDX-FileCopyrightText: 2021 Dalibo
#
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

import importlib.resources
import sys
from datetime import datetime

if sys.version_info[:2] >= (3, 11):
    from typing import Self, assert_never, assert_type

    def read_resource(pkgname: str, name: str) -> str | None:
        resource = importlib.resources.files(pkgname).joinpath(name)
        if resource.is_file():
            return resource.read_text()
        return None

    datetime_fromisoformat = datetime.fromisoformat

else:
    from backports._datetime_fromisoformat import datetime_fromisoformat
    from typing_extensions import Self, assert_never, assert_type

    def read_resource(pkgname: str, name: str) -> str | None:
        if importlib.resources.is_resource(pkgname, name):
            return importlib.resources.read_text(pkgname, name)
        return None


__all__ = [
    "Self",
    "assert_never",
    "assert_type",
    "datetime_fromisoformat",
    "read_resource",
]

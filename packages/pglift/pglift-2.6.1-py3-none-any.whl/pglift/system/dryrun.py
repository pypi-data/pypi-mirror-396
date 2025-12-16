# SPDX-FileCopyrightText: 2021 Dalibo
#
# SPDX-License-Identifier: GPL-3.0-or-later

from collections.abc import Iterator
from contextlib import contextmanager
from contextvars import ContextVar

VAR = ContextVar("DryRun", default=False)

enabled = VAR.get


@contextmanager
def configure(enable: bool, /) -> Iterator[None]:
    token = VAR.set(enable)
    try:
        yield
    finally:
        VAR.reset(token)

# SPDX-FileCopyrightText: 2024 Dalibo
#
# SPDX-License-Identifier: GPL-3.0-or-later

"""Operational interface to the underlying the system."""

from collections.abc import Iterator
from contextlib import contextmanager

from . import command, dryrun, fs, imfs
from .command import Command as Command
from .fs import FileSystem as FileSystem


@contextmanager
def configure(*, dry_run: bool) -> Iterator[None]:
    with dryrun.configure(dry_run):
        if not dry_run:
            yield
            return
        fs_token = fs.set(imfs.RoFS())
        cmd_token = command.set(command.NoOpCommand())
        try:
            yield
        finally:
            fs.reset(fs_token)
            command.reset(cmd_token)

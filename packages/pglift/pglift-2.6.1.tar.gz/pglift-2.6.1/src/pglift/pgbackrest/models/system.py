# SPDX-FileCopyrightText: 2021 Dalibo
#
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

from pathlib import Path, PurePath

from attrs import frozen


@frozen(kw_only=True)
class Service:
    """A pgbackrest service bound to a PostgreSQL instance."""

    stanza: str
    """Name of the stanza"""

    path: Path
    """Path to configuration file for this stanza"""

    datadir: PurePath
    """Path to PostgreSQL data directory of the instance bound to this service."""

    index: int = 1
    """index of pg-path option in the stanza"""

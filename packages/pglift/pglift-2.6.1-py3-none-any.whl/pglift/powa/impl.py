# SPDX-FileCopyrightText: 2021 Dalibo
#
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

from ..settings import Settings, _powa

POWA_EXTENSIONS = [
    "btree_gist",
    "pg_qualstats",
    "pg_stat_statements",
    "pg_stat_kcache",
    "powa",
]

# Libraries to load in shared_preload_libraries and to install.
# Order is important here, for example `pg_stat_statements` needs to be loaded
# before `pg_stat_kcache` in shared_preload_libraries
POWA_LIBRARIES = ["pg_qualstats", "pg_stat_statements", "pg_stat_kcache"]


def available(settings: Settings) -> _powa.Settings | None:
    return settings.powa

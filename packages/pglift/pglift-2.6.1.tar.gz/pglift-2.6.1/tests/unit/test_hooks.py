# SPDX-FileCopyrightText: 2024 Dalibo
#
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

from pglift import h, hooks
from pglift.models import interface
from pglift.settings import Settings


def test_rolename(settings: Settings) -> None:
    assert hooks(settings, h.rolename, settings=settings) == [
        "temboardagent",
        "powa",
        "backup",
    ]


def test_role(settings: Settings, instance_manifest: interface.Instance) -> None:
    roles = [
        m.model_dump(exclude_unset=True, exclude_defaults=True)
        for m in hooks(settings, h.role, settings=settings, manifest=instance_manifest)
        if m is not None
    ]
    assert roles == [
        {
            "name": "temboardagent",
            "login": True,
            "superuser": True,
        },
        {
            "name": "powa",
            "login": True,
            "superuser": True,
        },
        {
            "name": "prometheus",
            "login": True,
            "memberships": [
                {
                    "role": "pg_monitor",
                },
            ],
        },
        {
            "name": "backup",
            "login": True,
            "pgpass": False,
            "superuser": True,
        },
    ]


def test_database(settings: Settings, instance_manifest: interface.Instance) -> None:
    databases = [
        m.model_dump(exclude_unset=True, exclude_defaults=True)
        for m in hooks(
            settings, h.database, settings=settings, manifest=instance_manifest
        )
    ]
    assert databases == [
        {
            "name": "powa",
            "extensions": [
                {"name": "btree_gist"},
                {"name": "pg_qualstats"},
                {"name": "pg_stat_statements"},
                {"name": "pg_stat_kcache"},
                {"name": "powa"},
            ],
        }
    ]

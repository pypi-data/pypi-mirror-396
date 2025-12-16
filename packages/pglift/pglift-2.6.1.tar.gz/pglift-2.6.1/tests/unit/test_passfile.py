# SPDX-FileCopyrightText: 2021 Dalibo
#
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

from pathlib import Path

import pytest
from pydantic import SecretStr

from pglift import passfile as passfile_mod
from pglift.models import PostgreSQLInstance, interface
from pglift.settings import Settings


class Role(interface.Role):
    def __init__(
        self, name: str, password: str | None = None, pgpass: bool = False
    ) -> None:
        super().__init__(
            name=name,
            password=SecretStr(password) if password is not None else None,
            pgpass=pgpass,
        )


@pytest.fixture
def passfile(settings: Settings) -> Path:
    fpath = settings.postgresql.auth.passfile
    assert fpath is not None
    fpath.write_text("*:999:*:edgar:fbi\n")
    return fpath


@pytest.mark.parametrize(
    "role, changed, pgpass",
    [
        (Role("alice"), False, "*:999:*:edgar:fbi\n"),
        (Role("bob", "secret"), False, "*:999:*:edgar:fbi\n"),
        (Role("charles", pgpass=True), False, "*:999:*:edgar:fbi\n"),
        (Role("danny", "sss", True), True, "*:999:*:danny:sss\n*:999:*:edgar:fbi\n"),
        (Role("edgar", "cia", True), True, "*:999:*:edgar:cia\n"),
        (Role("edgar", None, False), True, None),
    ],
)
@pytest.mark.anyio
async def test_role_change(
    pg_instance: PostgreSQLInstance,
    passfile: Path,
    role: Role,
    changed: bool,
    pgpass: str | None,
) -> None:
    assert (await passfile_mod.role_change(instance=pg_instance, role=role))[
        0
    ] == changed
    if pgpass is not None:
        assert passfile.read_text() == pgpass
    else:
        # Do not leave an empty file.
        assert not passfile.exists()


@pytest.mark.anyio
async def test_role_inspect(pg_instance: PostgreSQLInstance) -> None:
    fpath = pg_instance._settings.postgresql.auth.passfile
    assert fpath is not None
    fpath.write_text("*:999:*:edgar:fbi\n")
    assert await passfile_mod.role_inspect(pg_instance, "edgar") == {"pgpass": True}
    assert await passfile_mod.role_inspect(pg_instance, "alice") == {"pgpass": False}

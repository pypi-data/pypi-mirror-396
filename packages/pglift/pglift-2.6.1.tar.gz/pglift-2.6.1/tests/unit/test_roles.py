# SPDX-FileCopyrightText: 2021 Dalibo
#
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

import pytest

from pglift import exceptions, hba, manager, postgresql, roles
from pglift.models import PostgreSQLInstance
from pglift.models.interface import HbaRecordForRole, Role
from pglift.settings import PostgreSQLVersion


@pytest.mark.anyio
async def test_standby_role_drop(
    pg_version: PostgreSQLVersion, standby_pg_instance: PostgreSQLInstance
) -> None:
    role = Role(name="alice")
    with pytest.raises(
        exceptions.InstanceReadOnlyError,
        match=f"^{pg_version}/standby is a read-only standby instance$",
    ):
        await roles.drop(standby_pg_instance, role)


@pytest.mark.anyio
async def test_records(pg_instance: PostgreSQLInstance) -> None:
    hba_r = [
        "host	db	machin	127.0.0.1/32	md5",
        "host	machin_db	machin	127.0.0.1/32	md5",
        "host	db	bidule	127.0.0.1/32	md5",
    ]
    (pg_instance.datadir / "pg_hba.conf").write_text("\n".join(hba_r))
    with manager.hba.use(postgresql):
        assert [record async for record in hba.records(pg_instance, "machin")] == [
            HbaRecordForRole(
                connection=HbaRecordForRole.HostConnectionInfo(
                    type="host", address="127.0.0.1/32", netmask=None
                ),
                database="db",
                method="md5",
                state="present",
            ),
            HbaRecordForRole(
                connection=HbaRecordForRole.HostConnectionInfo(
                    type="host", address="127.0.0.1/32", netmask=None
                ),
                database="machin_db",
                method="md5",
                state="present",
            ),
        ]

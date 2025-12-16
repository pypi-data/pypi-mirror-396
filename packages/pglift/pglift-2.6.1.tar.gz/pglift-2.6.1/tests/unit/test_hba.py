# SPDX-FileCopyrightText: 2025 Dalibo
#
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

from unittest.mock import AsyncMock, patch

import pytest
from pgtoolkit.hba import HBA, HBARecord
from pgtoolkit.hba import parse as parse_hba

from pglift import hba, manager, postgresql
from pglift.models import system
from pglift.settings import Settings


@pytest.mark.anyio
async def test_save_hba(
    settings: Settings, pg_instance: system.PostgreSQLInstance
) -> None:
    # testing if postgresql is reloaded on HBA changes (only for running instance)
    with (
        patch.object(postgresql, "is_running", return_value=True, autospec=True),
        patch.object(
            postgresql, "reload_postgresql", new_callable=AsyncMock
        ) as reload_postgresql,
        manager.instance.use(postgresql),
        manager.hba.use(postgresql),
    ):
        # try without changing the HBA
        cur_hba = await hba.get(pg_instance)
        await hba.save(pg_instance, cur_hba, reload_on_change=True)
        reload_postgresql.assert_not_awaited()
        # then update the HBA and make sure postgresql is reloaded
        hba_r = HBARecord(conntype="local", user="bla", database="much", method="md5")
        assert hba_r not in parse_hba(pg_instance.datadir / "pg_hba.conf")
        new_hba = HBA([hba_r])
        await hba.save(pg_instance, new_hba, reload_on_change=True)
        reload_postgresql.assert_awaited_once()
        assert hba_r in parse_hba(pg_instance.datadir / "pg_hba.conf")

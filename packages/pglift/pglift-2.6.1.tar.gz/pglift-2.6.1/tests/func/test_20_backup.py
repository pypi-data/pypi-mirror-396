# SPDX-FileCopyrightText: 2021 Dalibo
#
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

import pytest

from pglift import instances, systemd
from pglift.models import system
from pglift.settings import _systemd
from pglift.systemd import scheduler


@pytest.mark.usefixtures("require_systemd_scheduler", "require_pgbackrest_localrepo")
@pytest.mark.anyio
async def test_systemd_backup_job(
    systemd_settings: _systemd.Settings, instance: system.Instance
) -> None:
    unit = scheduler.unit("backup", instance.qualname)
    assert await systemd.is_enabled(systemd_settings, unit)
    assert await systemd.is_active(systemd_settings, unit)
    async with instances.stopped(instance):
        assert not await systemd.is_active(systemd_settings, unit)
    assert await systemd.is_active(systemd_settings, unit)

# SPDX-FileCopyrightText: 2021 Dalibo
#
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

import pytest

from pglift import logrotate
from pglift.settings import Settings


@pytest.mark.anyio
async def test_site_configure(settings: Settings) -> None:
    logrotate_settings = settings.logrotate
    assert logrotate_settings is not None
    config = logrotate_settings.configdir / "logrotate.conf"
    assert list(logrotate.site_configure_list(settings)) == [config]

    assert not logrotate_settings.configdir.exists()
    assert not any(logrotate.site_configure_check(settings, False))
    await logrotate.site_configure_install(settings)
    assert all(logrotate.site_configure_check(settings, True))
    assert logrotate_settings.configdir.exists()
    assert config.exists()
    assert settings.pgbackrest is not None
    assert settings.patroni is not None
    assert config.read_text() == "\n".join(
        [
            f"{settings.patroni.logpath}/*/patroni.log {{",
            "  weekly",
            "  rotate 10",
            "  copytruncate",
            "  delaycompress",
            "  compress",
            "  notifempty",
            "  missingok",
            "}",
            "",
            f"{settings.pgbackrest.logpath}/*.log {{",
            "  weekly",
            "  rotate 10",
            "  copytruncate",
            "  delaycompress",
            "  compress",
            "  notifempty",
            "  missingok",
            "}",
            "",
            f"{settings.postgresql.logpath}/*.log {{",
            "  weekly",
            "  rotate 10",
            "  copytruncate",
            "  delaycompress",
            "  compress",
            "  notifempty",
            "  missingok",
            "}",
            "",
        ]
    )
    await logrotate.site_configure_uninstall(settings)
    assert not logrotate_settings.configdir.exists()

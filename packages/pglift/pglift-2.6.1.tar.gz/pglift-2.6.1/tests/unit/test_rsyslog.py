# SPDX-FileCopyrightText: 2021 Dalibo
#
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

import pytest

from pglift import rsyslog
from pglift.models import interface
from pglift.settings import PostgreSQLVersion, Settings


@pytest.mark.anyio
async def test_site_configure(settings: Settings) -> None:
    rsyslog_settings = settings.rsyslog
    assert rsyslog_settings is not None
    rsyslog_config_file = rsyslog_settings.configdir / "rsyslog.conf"

    assert list(rsyslog.site_configure_list(settings)) == [rsyslog_config_file]

    assert not rsyslog_config_file.exists()

    assert not any(rsyslog.site_configure_check(settings, False))

    await rsyslog.site_configure_install(settings)
    assert rsyslog_settings.configdir.exists()
    assert rsyslog_config_file.exists()
    assert all(rsyslog.site_configure_check(settings, True))

    username, group = settings.sysuser
    assert rsyslog_config_file.read_text().strip() == "\n".join(
        [
            "$umask 0027",
            "$FileCreateMode 0640",
            f"$FileOwner {username}",
            f"$FileGroup {group}",
            f'template (name="pglift_postgresql_template" type="string" string="{settings.postgresql.logpath}/%PROGRAMNAME%.log")',
            'if (re_match($programname, "postgresql-.*")) then -?pglift_postgresql_template',
            "&stop",
        ]
    )

    await rsyslog.site_configure_uninstall(settings=settings)
    assert not rsyslog_config_file.exists()


def test_instance_settings(pg_version: PostgreSQLVersion) -> None:
    m = interface.PostgreSQLInstance(name="test", version=pg_version)
    (_, config) = rsyslog.instance_settings(m)
    assert config.as_dict() == {
        "log_destination": "syslog",
        "syslog_ident": f"postgresql-{pg_version}-test",
    }

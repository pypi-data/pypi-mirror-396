# SPDX-FileCopyrightText: 2021 Dalibo
#
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

import sys

import pytest

from pglift.backup import systemd_unit_templates, systemd_units
from pglift.settings import Settings


def test_systemd_units() -> None:
    assert systemd_units() == ["pglift-backup@.service", "pglift-backup@.timer"]


def test_systemd_unit_templates(settings: Settings) -> None:
    with pytest.MonkeyPatch.context() as mp:
        mp.setenv("PGLIFT_DEBUG", "no")
        ((service_name, service_content), (timer_name, timer_content)) = list(
            systemd_unit_templates(settings)
        )
    assert service_name == "pglift-backup@.service"
    service_lines = service_content.splitlines()
    for line in service_lines:
        if line.startswith("ExecStart"):
            execstart = line.split("=", 1)[-1]
            assert execstart == f"{sys.executable} -m pglift_cli instance backup %I"
            break
    else:
        raise AssertionError("ExecStart line not found")
    assert 'Environment="PGLIFT_DEBUG=no"' in service_lines
    assert timer_name == "pglift-backup@.timer"
    timer_lines = timer_content.splitlines()
    assert "OnCalendar=daily" in timer_lines

# SPDX-FileCopyrightText: 2025 Dalibo
#
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

import logging
from collections.abc import Iterator
from unittest.mock import patch

import pytest


@pytest.fixture(scope="session", autouse=True)
def _log_level() -> None:
    """Set the level of pglift logger to DEBUG."""
    logging.getLogger("pglift").setLevel(logging.DEBUG)


@pytest.fixture(autouse=True, scope="package")
def _site_settings_no_yaml_file() -> Iterator[None]:
    """Prevent usage of user's site settings.yaml when using SiteSettings."""
    with patch("pglift.settings.SiteSettings.yaml_file", new=None):
        yield

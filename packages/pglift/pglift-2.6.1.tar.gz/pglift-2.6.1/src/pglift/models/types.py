# SPDX-FileCopyrightText: 2024 Dalibo
#
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

from typing import Annotated

from pydantic import AfterValidator

from .validators import check_port_available

Port = Annotated[int, AfterValidator(check_port_available)]

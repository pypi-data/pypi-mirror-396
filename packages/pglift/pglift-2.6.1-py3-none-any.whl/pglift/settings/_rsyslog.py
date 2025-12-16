# SPDX-FileCopyrightText: 2021 Dalibo
#
# SPDX-License-Identifier: GPL-3.0-or-later

from pathlib import Path
from typing import Annotated

from pydantic import Field

from .base import BaseModel, ConfigPath


class Settings(BaseModel):
    """Settings for rsyslog."""

    configdir: Annotated[
        Path, ConfigPath, Field(description="rsyslog config directory")
    ] = Path("rsyslog")

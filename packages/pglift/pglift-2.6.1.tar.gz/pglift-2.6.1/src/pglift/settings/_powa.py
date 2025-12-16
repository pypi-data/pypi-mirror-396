# SPDX-FileCopyrightText: 2021 Dalibo
#
# SPDX-License-Identifier: GPL-3.0-or-later
from typing import Annotated

from pydantic import Field

from .base import BaseModel


class Settings(BaseModel):
    """Settings for PoWA."""

    dbname: Annotated[str, Field(description="Name of the PoWA database")] = "powa"
    role: Annotated[str, Field(description="Instance role used for PoWA.")] = "powa"

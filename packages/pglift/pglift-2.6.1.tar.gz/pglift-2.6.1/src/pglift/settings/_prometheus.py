# SPDX-FileCopyrightText: 2021 Dalibo
#
# SPDX-License-Identifier: GPL-3.0-or-later

from pathlib import Path
from typing import Annotated

from pydantic import AfterValidator, Field, FilePath

from .base import BaseModel, ConfigPath, RunPath, TemplatedPath


class Settings(BaseModel):
    """Settings for Prometheus postgres_exporter"""

    execpath: Annotated[
        FilePath, Field(description="Path to the postgres_exporter executable.")
    ]

    role: Annotated[
        str,
        Field(
            description="Name of the PostgreSQL role for Prometheus postgres_exporter."
        ),
    ] = "prometheus"

    configpath: Annotated[
        Path,
        AfterValidator(TemplatedPath({"name"})),
        ConfigPath,
        Field(description="Path to the config file.", validate_default=True),
    ] = Path("prometheus/postgres_exporter-{name}.conf")

    pid_file: Annotated[
        Path,
        AfterValidator(TemplatedPath({"name"})),
        RunPath,
        Field(
            description="Path to which postgres_exporter process PID will be written.",
            validate_default=True,
        ),
    ] = Path("prometheus/{name}.pid")

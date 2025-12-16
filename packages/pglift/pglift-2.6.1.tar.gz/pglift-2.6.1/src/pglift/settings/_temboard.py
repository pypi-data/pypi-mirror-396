# SPDX-FileCopyrightText: 2021 Dalibo
#
# SPDX-License-Identifier: GPL-3.0-or-later

from pathlib import Path
from typing import Annotated, Literal

from pydantic import AfterValidator, AnyHttpUrl, Field, FilePath

from .base import (
    BaseModel,
    ConfigPath,
    DataPath,
    LogPath,
    RunPath,
    ServerCert,
    TemplatedPath,
    not_templated,
)

Plugin = Literal[
    "activity",
    "administration",
    "dashboard",
    "maintenance",
    "monitoring",
    "pgconf",
    "statements",
]


class Settings(BaseModel):
    """Settings for temBoard agent"""

    ui_url: Annotated[AnyHttpUrl, Field(description="URL of the temBoard UI.")]

    signing_key: Annotated[
        FilePath, Field(description="Path to the public key for UI connection.")
    ]

    certificate: Annotated[
        ServerCert,
        Field(description="TLS certificate files for the temboard-agent HTTP server."),
    ]

    execpath: Annotated[
        FilePath, Field(description="Path to the temboard-agent executable.")
    ] = Path("/usr/bin/temboard-agent")

    role: Annotated[
        str, Field(description="Name of the PostgreSQL role for temBoard agent.")
    ] = "temboardagent"

    configpath: Annotated[
        Path,
        AfterValidator(TemplatedPath({"name"})),
        ConfigPath,
        Field(description="Path to the config file.", validate_default=True),
    ] = Path("temboard-agent/temboard-agent-{name}.conf")

    pid_file: Annotated[
        Path,
        AfterValidator(TemplatedPath({"name"})),
        RunPath,
        Field(
            description="Path to which temboard-agent process PID will be written.",
            validate_default=True,
        ),
    ] = Path("temboard-agent/temboard-agent-{name}.pid")

    plugins: Annotated[tuple[Plugin, ...], Field(description="Plugins to load.")] = (
        "monitoring",
        "dashboard",
        "activity",
    )

    home: Annotated[
        Path,
        AfterValidator(TemplatedPath({"name"})),
        DataPath,
        Field(
            description="Path to agent home directory containing files used to store temporary data",
            validate_default=True,
        ),
    ] = Path("temboard-agent/{name}")

    logpath: Annotated[
        Path,
        AfterValidator(not_templated),
        LogPath,
        Field(description="Path where log files are stored."),
    ] = Path("temboard")

    logmethod: Annotated[
        Literal["stderr", "syslog", "file"],
        Field(description="Method used to send the logs."),
    ] = "stderr"

    loglevel: Annotated[
        Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        Field(description="Log level."),
    ] = "INFO"

# SPDX-FileCopyrightText: 2021 Dalibo
#
# SPDX-License-Identifier: GPL-3.0-or-later

from pathlib import Path
from typing import Annotated, Literal

from pydantic import AfterValidator, Field, FilePath

from .base import (
    BaseModel,
    ConfigPath,
    DataPath,
    LogPath,
    RunPath,
    ServerCert,
    not_templated,
)


class HostRepository(BaseModel):
    """Remote repository host for pgBackRest."""

    host: Annotated[str, Field(description="Host name of the remote repository.")]
    host_port: Annotated[
        int | None, Field(description="Port to connect to the remote repository.")
    ] = None
    host_config: Annotated[
        Path | None,
        Field(
            description="pgBackRest configuration file path on the remote repository."
        ),
    ] = None


class PgBackRestServerCert(ServerCert):
    """TLS certificate files for the pgBackRest server on site."""

    ca_cert: Annotated[
        FilePath,
        Field(
            description="Certificate Authority certificate to verify client requests."
        ),
    ]


class TLSHostRepository(HostRepository):
    mode: Literal["host-tls"]
    cn: Annotated[
        str, Field(description="Certificate Common Name of the remote repository.")
    ]
    certificate: Annotated[
        PgBackRestServerCert,
        Field(description="TLS certificate files for the pgBackRest server on site."),
    ]
    port: Annotated[int, Field(description="Port for the TLS server on site.")] = 8432
    pid_file: Annotated[
        Path,
        RunPath,
        Field(
            description="Path to which pgbackrest server process PID will be written."
        ),
    ] = Path("pgbackrest.pid")


class SSHHostRepository(HostRepository):
    mode: Literal["host-ssh"]
    host_user: Annotated[
        str | None,
        Field(
            description="Name of the user that will be used for operations on the repository host.",
        ),
    ] = None
    cmd_ssh: Annotated[
        Path | None,
        Field(
            description="SSH client command. Use a specific SSH client command when an alternate is desired or the ssh command is not in $PATH.",
        ),
    ] = None


class Retention(BaseModel):
    """Retention settings."""

    archive: int = 2
    diff: int = 3
    full: int = 2


class PathRepository(BaseModel):
    """Remote repository (path) for pgBackRest."""

    mode: Literal["path"]
    path: Annotated[
        Path,
        AfterValidator(not_templated),
        DataPath,
        Field(
            description="Base directory path where backups and WAL archives are stored."
        ),
    ]
    retention: Annotated[Retention, Field(description="Retention options.")] = (
        Retention()
    )


class Settings(BaseModel):
    """Settings for pgBackRest."""

    execpath: Annotated[
        FilePath, Field(description="Path to the pbBackRest executable.")
    ] = Path("/usr/bin/pgbackrest")

    configpath: Annotated[
        Path,
        AfterValidator(not_templated),
        ConfigPath,
        Field(description="Base path for pgBackRest configuration files."),
    ] = Path("pgbackrest")

    repository: Annotated[
        TLSHostRepository | SSHHostRepository | PathRepository,
        Field(
            description="Repository definition, either as a (local) path-repository or as a host-repository.",
            discriminator="mode",
        ),
    ]

    logpath: Annotated[
        Path,
        AfterValidator(not_templated),
        LogPath,
        Field(description="Path where log files are stored."),
    ] = Path("pgbackrest")

    spoolpath: Annotated[
        Path,
        AfterValidator(not_templated),
        DataPath,
        Field(description="Spool path."),
    ] = Path("pgbackrest/spool")

    lockpath: Annotated[
        Path,
        AfterValidator(not_templated),
        RunPath,
        Field(description="Path where lock files are stored."),
    ] = Path("pgbackrest/lock")

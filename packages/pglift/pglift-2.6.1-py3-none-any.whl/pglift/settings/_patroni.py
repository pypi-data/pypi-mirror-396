# SPDX-FileCopyrightText: 2021 Dalibo
#
# SPDX-License-Identifier: GPL-3.0-or-later
import warnings
from pathlib import Path
from typing import Annotated, Any, Literal

from pydantic import AfterValidator, DirectoryPath, Field, FilePath, ValidationInfo

from .. import types
from .base import BaseModel, ConfigPath, LogPath, RunPath, TemplatedPath, not_templated


def check_cert_and_protocol(
    value: FilePath | None, info: ValidationInfo
) -> FilePath | None:
    """Make sure protocol https is used when setting certificates."""
    if value is not None:
        protocol = types.info_data_get(info, "protocol")
        if protocol == "http":
            raise ValueError("'https' protocol is required")
    return value


def _field_deprecated(value: Any | None, info: ValidationInfo) -> Any | None:
    if value is not None:
        warnings.warn(
            f"{info.field_name!r} setting is deprecated, use Patroni template instead.",
            FutureWarning,
            stacklevel=2,
        )
    return value


class Etcd(BaseModel):
    """Settings for Etcd (for Patroni)."""

    version: Annotated[
        Literal["etcd", "etcd3"],
        Field(description="Version of etcd to use."),
    ] = "etcd3"

    hosts: Annotated[
        tuple[types.Address, ...], Field(description="List of etcd endpoint.")
    ] = (types.local_address(2379),)

    protocol: Annotated[
        Literal["http", "https"],
        Field(description="http or https, if not specified http is used."),
    ] = "http"

    cacert: Annotated[
        FilePath | None,
        Field(description="Certificate authority to validate the server certificate."),
        AfterValidator(check_cert_and_protocol),
    ] = None

    cert: Annotated[
        FilePath | None,
        Field(description="Client certificate for authentication."),
        AfterValidator(check_cert_and_protocol),
    ] = None

    key: Annotated[
        FilePath | None,
        Field(description="Private key corresponding to the client certificate."),
    ] = None


# Custom validator is required because FilePath can't be used with special
# character devices. FilePath relies on Path.is_file() which returns False
# for non regular files.
def check_path_exists(value: Path) -> Path:
    if value and not value.exists():
        raise ValueError(f"path {value} does not exists")
    return value


class WatchDog(BaseModel):
    """Settings for watchdog (for Patroni)."""

    mode: Annotated[
        Literal["off", "automatic", "required"], Field(description="watchdog mode.")
    ] = "off"

    device: Annotated[
        Path | None,
        Field(description="Path to watchdog."),
        AfterValidator(check_path_exists),
    ] = None

    safety_margin: Annotated[
        int | None,
        Field(
            description="Number of seconds of safety margin between watchdog triggering and leader key expiration."
        ),
    ] = None


def check_verify_client_and_certfile(
    value: Any | None, info: ValidationInfo
) -> Any | None:
    """Make sure that certfile is set when verify_client is."""
    if value is not None and info.data.get("certfile") is None:
        raise ValueError("requires 'certfile' to enable TLS")
    return value


class RESTAPI(BaseModel):
    """Settings for Patroni's REST API."""

    cafile: Annotated[
        FilePath | None,
        Field(
            description="Certificate authority (or bundle) to verify client certificates."
        ),
    ] = None

    certfile: Annotated[
        FilePath | None,
        Field(description="PEM-encoded server certificate to enable HTTPS."),
    ] = None

    keyfile: Annotated[
        FilePath | None,
        Field(
            description="PEM-encoded private key corresponding to the server certificate."
        ),
    ] = None

    verify_client: Annotated[
        Literal["optional", "required"] | None,
        Field(description="Whether to check client certificates."),
        AfterValidator(check_verify_client_and_certfile),
    ] = None


class CTL(BaseModel):
    """Settings for Patroni's CTL."""

    certfile: Annotated[FilePath, Field(description="PEM-encoded client certificate.")]

    keyfile: Annotated[
        FilePath,
        Field(
            description="PEM-encoded private key corresponding to the client certificate."
        ),
    ]


class ServerSSLOptions(BaseModel):
    """Settings for server certificate verification."""

    mode: Annotated[
        Literal["disable", "allow", "prefer", "require", "verify-ca", "verify-full"]
        | None,
        Field(description="Verification mode."),
    ] = None
    crl: Annotated[
        FilePath | None, Field(description="Certificate Revocation List (CRL).")
    ] = None
    crldir: Annotated[
        DirectoryPath | None, Field(description="Directory with CRL files.")
    ] = None
    rootcert: Annotated[FilePath | None, Field(description="Root certificate(s).")] = (
        None
    )


class ConnectionOptions(BaseModel):
    ssl: Annotated[
        ServerSSLOptions | None,
        Field(
            description="Settings for server certificate verification when connecting to remote PostgreSQL instances."
        ),
    ] = None


class PostgreSQL(BaseModel):
    connection: Annotated[
        ConnectionOptions | None,
        Field(
            description="Client (libpq) connection options.",
        ),
    ] = None
    passfile: Annotated[
        Path,
        AfterValidator(TemplatedPath({"name"})),
        ConfigPath,
        Field(description="Path to .pgpass password file managed by Patroni."),
    ] = Path("patroni/{name}.pgpass")
    use_pg_rewind: Annotated[
        bool, Field(description="Whether or not to use pg_rewind.")
    ] = False


def check_restapi_verify_client(value: RESTAPI, info: ValidationInfo) -> RESTAPI:
    """Make sure 'ctl' client certificates are provided when setting
    restapi.verify_client to required.
    """
    if value.verify_client == "required" and info.data.get("ctl") is None:
        raise ValueError(
            f"'ctl' must be provided when '{info.field_name}.verify_client' is set to 'required'"
        )
    return value


ConfigMode = Literal["local", "dynamic"]


class ConfigurationMode(BaseModel):
    auth: Annotated[
        ConfigMode,
        Field(
            description="Configuration mode for the HBA records. 'local' for HBA managed via the patroni configuration file, 'dynamic' to manage them via the DCS."
        ),
    ] = "local"
    parameters: Annotated[
        ConfigMode,
        Field(
            description="Configuration mode for the PostgreSQL parameters. 'local' for parameters managed via the patroni configuration file, 'dynamic' to manage them via the DCS."
        ),
    ] = "local"


class Settings(BaseModel):
    """Settings for Patroni."""

    execpath: Annotated[FilePath, Field(description="Path to patroni executable.")] = (
        Path("/usr/bin/patroni")
    )

    ctlpath: Annotated[
        FilePath, Field(description="Path to patronictl executable.")
    ] = Path("/usr/bin/patronictl")

    configpath: Annotated[
        Path,
        AfterValidator(TemplatedPath({"name"})),
        ConfigPath,
        Field(description="Path to the config file.", validate_default=True),
    ] = Path("patroni/{name}.yaml")

    logpath: Annotated[
        Path,
        AfterValidator(not_templated),
        LogPath,
        Field(
            description="Path where directories are created (based on instance name) to store patroni log files.",
        ),
    ] = Path("patroni")

    pid_file: Annotated[
        Path,
        AfterValidator(TemplatedPath({"name"})),
        RunPath,
        Field(
            description="Path to which Patroni process PID will be written.",
            validate_default=True,
        ),
    ] = Path("patroni/{name}.pid")

    loop_wait: Annotated[
        int | None, Field(deprecated=True), AfterValidator(_field_deprecated)
    ] = None

    etcd: Annotated[Etcd, Field(default_factory=Etcd, description="Etcd settings.")]

    watchdog: Annotated[
        WatchDog | None, Field(deprecated=True), AfterValidator(_field_deprecated)
    ] = None

    ctl: Annotated[CTL | None, Field(description="CTL settings.")] = None

    configuration_mode: Annotated[
        ConfigurationMode,
        Field(
            description="Define how Patroni configuration should be managed ('local' or 'dynamic' mode)."
        ),
    ] = ConfigurationMode()

    postgresql: Annotated[
        PostgreSQL,
        Field(default_factory=PostgreSQL, description="PostgreSQL settings."),
    ]

    restapi: Annotated[
        RESTAPI,
        Field(default_factory=RESTAPI, description="REST API settings."),
        AfterValidator(check_restapi_verify_client),
    ]

    enforce_config_validation: Annotated[
        bool, Field(description="Enforce Patroni settings validation.")
    ] = True

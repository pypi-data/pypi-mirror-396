# SPDX-FileCopyrightText: 2021 Dalibo
#
# SPDX-License-Identifier: GPL-3.0-or-later

from typing import Annotated, Final, Literal

from pydantic import AfterValidator, Field, SecretStr

from ... import types
from ...annotations import cli
from ...models.types import Port
from ...models.validators import check_conninfo

default_port: Final = 9187


def check_password(v: SecretStr | None) -> SecretStr | None:
    """Validate 'password' field.

    >>> Service(password="without_space")  # doctest: +ELLIPSIS
    Service(...)
    >>> Service(password="with space")  # doctest: +ELLIPSIS
    Traceback (most recent call last):
      ...
    pydantic_core._pydantic_core.ValidationError: 1 validation error for Service
    password
      Value error, password must not contain blank spaces [type=value_error, input_value='with space', input_type=str]
        ...
    """
    # Avoid spaces as this will break postgres_exporter configuration.
    # See https://github.com/prometheus-community/postgres_exporter/issues/393
    if v is not None and " " in v.get_secret_value():
        raise ValueError("password must not contain blank spaces")
    return v


class Service(types.Service, service_name="prometheus"):
    port: Annotated[
        Port,
        Field(
            description="TCP port for the web interface and telemetry of Prometheus",
            validate_default=True,
        ),
    ] = default_port
    password: Annotated[
        SecretStr | None,
        Field(
            description="Password of PostgreSQL role for Prometheus postgres_exporter.",
            exclude=True,
        ),
        AfterValidator(check_password),
    ] = None


class PostgresExporter(types.BaseModel):
    """Prometheus postgres_exporter service."""

    name: Annotated[
        str,
        Field(
            description="locally unique identifier of the service",
            pattern=r"^[^/]+$",
        ),
    ]
    dsn: Annotated[
        str,
        Field(description="connection string of target instance"),
        AfterValidator(check_conninfo),
    ]
    password: Annotated[SecretStr | None, Field(description="connection password")] = (
        None
    )
    port: Annotated[
        Port, Field(description="TCP port for the web interface and telemetry")
    ]
    state: Annotated[
        Literal["started", "stopped", "absent"],
        cli.Choices(choices=["started", "stopped"]),
        Field(description="runtime state"),
    ] = "started"

# SPDX-FileCopyrightText: 2021 Dalibo
#
# SPDX-License-Identifier: GPL-3.0-or-later

import socket
from typing import Annotated, Any

from pydantic import (
    BeforeValidator,
    Field,
    FilePath,
    SecretStr,
    ValidationInfo,
    field_validator,
)

from ... import types
from ...annotations import ansible, cli
from ...models.validators import default_if_none
from .common import RESTAPI


class ClusterMember(types.BaseModel, extra="allow", frozen=True):
    """An item of the list of members returned by Patroni API /cluster endpoint."""

    host: str
    name: str
    port: int
    role: str
    state: str


class ClientSSLOptions(types.BaseModel):
    cert: Annotated[FilePath, Field(description="Client certificate.")]
    key: Annotated[FilePath, Field(description="Private key.")]
    password: Annotated[
        SecretStr | None, Field(description="Password for the private key.")
    ] = None


class ClientAuth(types.BaseModel):
    ssl: Annotated[
        ClientSSLOptions | None, Field(description="Client certificate options.")
    ] = None


class PostgreSQL(types.BaseModel):
    connect_host: Annotated[
        str | None,
        Field(
            description="Host or IP address through which PostgreSQL is externally accessible.",
        ),
    ] = None
    replication: Annotated[
        ClientAuth | None,
        Field(
            description="Authentication options for client (libpq) connections to remote PostgreSQL by the replication user.",
        ),
    ] = None
    rewind: Annotated[
        ClientAuth | None,
        Field(
            description="Authentication options for client (libpq) connections to remote PostgreSQL by the rewind user.",
        ),
    ] = None


class Etcd(types.BaseModel):
    username: Annotated[
        str,
        Field(
            description="Username for basic authentication to etcd.",
        ),
    ]
    password: Annotated[
        SecretStr, Field(description="Password for basic authentication to etcd.")
    ]


def _allowed_if_updating_a_standalone(value: Any, info: ValidationInfo) -> Any:
    # XXX or assert info.context?
    if (
        info.context
        and info.context.get("operation") == "update"
        # 'instance' will be None when being dropped or already "absent".
        and (instance := info.context["instance"]) is not None
    ):
        try:
            s = instance.service(Service)
        except ValueError:
            pass
        else:
            assert info.field_name is not None
            if getattr(s, info.field_name) != value:
                raise ValueError("field is read-only")
    return value


class Service(types.Service, service_name="patroni"):
    cluster: Annotated[
        str,
        Field(description="Name (scope) of the Patroni cluster."),
        BeforeValidator(_allowed_if_updating_a_standalone),
    ]

    node: Annotated[
        str,
        Field(
            default_factory=socket.getfqdn,
            description="Name of the node (usually the host name).",
        ),
        BeforeValidator(_allowed_if_updating_a_standalone),
    ]

    restapi: Annotated[
        RESTAPI,
        Field(default_factory=RESTAPI, description="REST API configuration"),
    ]

    postgresql: Annotated[
        PostgreSQL | None,
        Field(
            description="Configuration for PostgreSQL setup and remote connection.",
        ),
    ] = None

    etcd: Annotated[
        Etcd | None,
        Field(
            description="Instance-specific options for etcd DCS backend.",
        ),
    ] = None

    cluster_members: Annotated[
        list[ClusterMember],
        cli.HIDDEN,
        ansible.HIDDEN,
        Field(
            description="Members of the Patroni cluster this instance is member of.",
            json_schema_extra={"readOnly": True},
        ),
    ] = []

    is_paused: Annotated[
        bool | None,
        cli.HIDDEN,
        ansible.HIDDEN,
        Field(description="Whether the Patroni cluster is in pause mode."),
    ] = None

    __validate_none_values_ = field_validator("node", "restapi", mode="before")(
        classmethod(default_if_none)
    )

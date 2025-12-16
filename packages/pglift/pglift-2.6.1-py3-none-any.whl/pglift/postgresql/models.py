# SPDX-FileCopyrightText: 2021 Dalibo
#
# SPDX-License-Identifier: GPL-3.0-or-later

from decimal import Decimal
from functools import partial
from pathlib import Path
from typing import Annotated, Literal

import psycopg.conninfo
from pydantic import AfterValidator, Field, SecretStr

from ..annotations import ansible, cli
from ..models.validators import check_conninfo
from ..settings._postgresql import InitdbSettings
from ..types import BaseModel

WALSenderState = Literal["startup", "catchup", "streaming", "backup", "stopping"]


class Initdb(InitdbSettings):
    username: str
    waldir: Path


# Actually only two values, but when dropping support for PostgreSQL 13, we will
# add 'pause requested', more information about pg_get_wal_replay_pause_state():
# https://www.postgresql.org/docs/current/functions-admin.html#FUNCTIONS-RECOVERY-CONTROL-TABLE
WALReplayPauseState = Literal["paused", "not paused"]


class Standby(BaseModel):
    """Standby information."""

    """Validate 'primary_conninfo' field.

    >>> Standby.model_validate({"primary_conninfo": "host=localhost"})  # doctest: +ELLIPSIS
    Standby(primary_conninfo='host=localhost', password=None, ...)
    >>> Standby.model_validate({"primary_conninfo": "hello"})
    Traceback (most recent call last):
      ...
    pydantic_core._pydantic_core.ValidationError: 1 validation error for Standby
    primary_conninfo
      Value error, missing "=" after "hello" in connection info string
     [type=value_error, input_value='hello', input_type=str]
        ...
    >>> Standby.model_validate({"primary_conninfo": "host=localhost password=xx"})
    Traceback (most recent call last):
      ...
    pydantic_core._pydantic_core.ValidationError: 1 validation error for Standby
    primary_conninfo
      Value error, must not contain a password [type=value_error, input_value='host=localhost password=xx', input_type=str]
        ...
    """

    primary_conninfo: Annotated[
        str,
        cli.Argument(name="for", metavar="DSN"),
        Field(
            description="DSN of primary for streaming replication.",
            json_schema_extra={"readOnly": True},
        ),
        AfterValidator(partial(check_conninfo, exclude=["password"])),
    ]
    password: Annotated[
        SecretStr | None,
        Field(
            description="Password for the replication user.",
            exclude=True,
            json_schema_extra={"readOnly": True},
        ),
    ] = None
    status: Annotated[
        Literal["demoted", "promoted"],
        cli.HIDDEN,
        Field(
            description="Instance standby state.",
            json_schema_extra={"writeOnly": True},
            exclude=True,
        ),
    ] = "demoted"
    slot: Annotated[
        str | None,
        Field(
            description="Replication slot name. Must exist on primary.",
            json_schema_extra={"readOnly": True},
        ),
    ] = None
    replication_lag: Annotated[
        Decimal | None,
        cli.HIDDEN,
        ansible.HIDDEN,
        Field(
            description="Replication lag.",
            json_schema_extra={"readOnly": True},
        ),
    ] = None
    wal_sender_state: Annotated[
        WALSenderState | None,
        cli.HIDDEN,
        ansible.HIDDEN,
        Field(
            description="State of the WAL sender process (on primary) this standby is connected to.",
            json_schema_extra={"readOnly": True},
        ),
    ] = None
    wal_replay_pause_state: Annotated[
        WALReplayPauseState,
        cli.HIDDEN,
        ansible.HIDDEN,
        Field(
            description="Whether the WAL recovery pause is requested.",
            json_schema_extra={"readOnly": True},
        ),
    ] = "not paused"

    @property
    def full_primary_conninfo(self) -> str:
        """Connection string to the primary, including password.

        >>> s = Standby.model_validate(
        ...     {"primary_conninfo": "host=primary port=5444", "password": "qwerty"}
        ... )
        >>> s.full_primary_conninfo
        'host=primary port=5444 password=qwerty'
        """
        kw = {}
        if self.password:
            kw["password"] = self.password.get_secret_value()
        return psycopg.conninfo.make_conninfo(self.primary_conninfo, **kw)


class RewindSource(BaseModel):
    """Configuration for pg_rewind."""

    conninfo: Annotated[
        str,
        cli.Option(name="from", metavar="DSN"),
        Field(
            description="DSN of source server to synchronize from.",
            exclude=True,
            json_schema_extra={"readOnly": True},
        ),
        AfterValidator(partial(check_conninfo, exclude=["password"])),
    ]
    password: Annotated[
        SecretStr | None,
        Field(
            description="Password for the rewind user.",
            exclude=True,
            json_schema_extra={"readOnly": True},
        ),
    ] = None

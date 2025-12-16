# SPDX-FileCopyrightText: 2021 Dalibo
#
# SPDX-License-Identifier: GPL-3.0-or-later

import warnings
from collections.abc import Mapping, MutableMapping
from datetime import datetime
from functools import partial
from pathlib import Path
from typing import Annotated, Any, Literal, TypeVar

import pgtoolkit.conf as pgconf
import psycopg.conninfo
from pydantic import (
    AfterValidator,
    BeforeValidator,
    Field,
    PostgresDsn,
    SecretStr,
    SerializationInfo,
    SerializerFunctionWrapHandler,
    ValidationInfo,
    WrapSerializer,
    model_validator,
)

from .. import conf, postgresql, types
from .. import diff as diffmod
from .. import settings as s
from .._compat import Self, assert_never
from ..annotations import ansible, cli
from ..exceptions import MutuallyExclusiveError
from ..pm import PluginManager
from ..postgresql.models import Standby
from ..settings import PostgreSQLVersion, default_postgresql_version
from ..settings import _postgresql as pgs
from ..types import (
    BaseModel,
    ByteSize,
    CompositeModel,
    Service,
    Status,
)
from .types import Port
from .validators import (
    check_conninfo,
    check_mutually_exclusive_with,
    check_port_available,
)


def as_dict(value: str | dict[str, Any], *, key: str = "name") -> dict[str, Any]:
    """Possibly wrap a str value as a dict with specified 'key'.

    >>> as_dict({"x": 1})
    {'x': 1}
    >>> as_dict("x")
    {'name': 'x'}
    >>> as_dict("x", key="foo")
    {'foo': 'x'}
    """
    if isinstance(value, str):
        return {key: value}
    return value


def serialize(
    value: Any,
    handler: SerializerFunctionWrapHandler,
    info: SerializationInfo,
    *,
    key: str = "name",
) -> Any:
    """Serialize a complex field

    >>> class Foo(BaseModel):
    ...     attr1: str = ""
    >>> class Bar(BaseModel):
    ...     foos: list[
    ...         Annotated[Foo, WrapSerializer(partial(serialize, key="attr1"))]
    ...     ] = []
    >>> bar = Bar(foos=[{"attr1": "blah"}, {"attr1": "truite"}])
    >>> bar.model_dump()
    {'foos': [{'attr1': 'blah'}, {'attr1': 'truite'}]}
    >>> bar.model_dump(context={"pretty": True})
    {'foos': ['blah', 'truite']}
    """
    if info.context and info.context["pretty"]:
        return getattr(value, key)
    return handler(value)


def validate_state_is_absent(value: bool | str, info: ValidationInfo) -> bool | str:
    """Make sure state is absent.

    >>> Role(name="bob", drop_owned=False).state
    'present'
    >>> r = Role(name="bob", drop_owned=True)
    Traceback (most recent call last):
      ...
    pydantic_core._pydantic_core.ValidationError: 1 validation error for Role
    drop_owned
      Value error, drop_owned can not be set if state is not 'absent' [type=value_error, input_value=True, input_type=bool]
        ...

    >>> r = Role(name="bob", reassign_owned="postgres")
    Traceback (most recent call last):
      ...
    pydantic_core._pydantic_core.ValidationError: 1 validation error for Role
    reassign_owned
      Value error, reassign_owned can not be set if state is not 'absent' [type=value_error, input_value='postgres', input_type=str]
        ...

    >>> r = Database(name="db1", force_drop=True)
    Traceback (most recent call last):
      ...
    pydantic_core._pydantic_core.ValidationError: 1 validation error for Database
    force_drop
      Value error, force_drop can not be set if state is not 'absent' [type=value_error, input_value=True, input_type=bool]
        ...
    """
    if value and info.data.get("state") != "absent":
        raise ValueError(f"{info.field_name} can not be set if state is not 'absent'")
    return value


InstanceState = Literal["stopped", "started", "absent", "restarted"]


def state_from_pg_status(status: Status) -> InstanceState:
    """Instance state from PostgreSQL status.

    >>> state_from_pg_status(Status.running)
    'started'
    >>> state_from_pg_status(Status.not_running)
    'stopped'
    """
    if status is Status.running:
        return "started"
    elif status is Status.not_running:
        return "stopped"
    assert_never(status)


PresenceState = Literal["present", "absent"]


class HbaRecordForRole(BaseModel):
    class HostConnectionInfo(BaseModel):
        type: Annotated[
            Literal["host", "hostssl", "hostnossl", "hostgssenc", "hostnogssenc"],
            Field(description="Connection type"),
        ] = "host"

        address: Annotated[
            str,
            Field(
                description="Client machine address(es); can be either a hostname, an IP or an IP address range.",
                json_schema_extra={
                    "readOnly": True,
                    "examples": [
                        "192.168.0.1",
                        "192.168.12.10/32",
                        "2001:db8::1000",
                        "example.com",
                    ],
                },
            ),
            cli.Option(),
        ]

        netmask: Annotated[
            str | None,
            Field(
                description="Client machine netmask.",
                json_schema_extra={
                    "readOnly": True,
                    "examples": ["255.255.255.0"],
                },
            ),
        ] = None

    connection: Annotated[
        HostConnectionInfo | None,
        Field(
            description="Connection information for this HBA record. If unspecified a 'local' record is assumed."
        ),
    ] = None

    database: Annotated[
        str,
        Field(
            description="Database name(s). Multiple database names can be supplied by separating them with commas.",
            json_schema_extra={"readOnly": True},
        ),
    ] = "all"

    method: Annotated[
        str,
        Field(
            description="Authentication method.",
            json_schema_extra={
                "readOnly": True,
                "examples": ["trust", "reject", "peer"],
            },
        ),
        cli.Option(),
    ]

    state: Annotated[
        PresenceState,
        cli.HIDDEN,
        Field(
            description="Whether the entry should be written in or removed from pg_hba.conf.",
            exclude=True,
        ),
    ] = "present"


class HbaRecord(HbaRecordForRole):
    user: Annotated[
        str,
        Field(
            description="User name(s). Multiple user names can be supplied by separating them with commas.",
            json_schema_extra={"readOnly": True},
        ),
    ] = "all"


class RoleProfile(BaseModel):
    """Associate a usage profile to a role in a database for a list of
    database schema.
    """

    kind: Annotated[
        Literal["read-only", "read-write"],
        Field(description="The kind of profile to attach to target role."),
    ]
    database: Annotated[
        str,
        Field(description="The database scoped by this profile."),
        cli.Option(),
    ]
    schemas: Annotated[
        list[str],
        Field(description="List of database schema scoped by this profile."),
        cli.Option(name="schema"),
    ] = ["public"]


class BaseRole(CompositeModel):
    name: Annotated[
        str, Field(description="Role name.", json_schema_extra={"readOnly": True})
    ]
    state: Annotated[
        PresenceState,
        Field(
            description="Whether the role be present or absent.",
            exclude=True,
        ),
    ] = "present"
    password: Annotated[
        SecretStr | None, Field(description="Role password.", exclude=True)
    ] = None
    encrypted_password: Annotated[
        SecretStr | None,
        Field(description="Role password, already encrypted.", exclude=True),
    ] = None

    @classmethod
    def component_models(cls, pm: PluginManager) -> list[types.ComponentModel]:
        return pm.hook.role_model()  # type: ignore[no-any-return]

    @model_validator(mode="after")
    def __validate_passwords_(self) -> Self:
        if self.password is not None and self.encrypted_password is not None:
            raise MutuallyExclusiveError(("password", "encrypted_password"))
        return self


DropOwned = Field(
    description="Drop all PostgreSQL's objects owned by the role being dropped.",
    exclude=True,
)
ReassignOwned = Field(
    description="Reassign all PostgreSQL's objects owned by the role being dropped to the specified role name.",
    min_length=1,
    exclude=True,
)


class RoleDropped(BaseRole):
    """Model for a role that is being dropped."""

    state: Literal["absent"] = "absent"
    password: Literal[None] = None
    encrypted_password: Literal[None] = None
    drop_owned: Annotated[bool, DropOwned] = False
    reassign_owned: Annotated[str | None, ReassignOwned] = None

    @model_validator(mode="after")
    def __validate_drop_reassign_owned_(self) -> Self:
        if self.drop_owned and self.reassign_owned is not None:
            raise MutuallyExclusiveError(("drop_owned", "reassign_owned"))
        return self


def _set_has_password(value: bool, info: ValidationInfo) -> bool:
    """Set 'has_password' field according to 'password'.

    >>> r = Role(name="postgres")
    >>> r.has_password
    False
    >>> r = Role(name="postgres", password="P4zzw0rd")
    >>> r.has_password
    True
    >>> r = Role(name="postgres", has_password=True)
    >>> r.has_password
    True
    """
    return (
        value
        or info.data["password"] is not None
        or info.data["encrypted_password"] is not None
    )


class RoleMembership(BaseModel):
    role: Annotated[
        str, Field(description="Role name.", json_schema_extra={"readOnly": True})
    ]

    state: Annotated[
        PresenceState,
        Field(
            description="Membership state. 'present' for 'granted', 'absent' for 'revoked'.",
            exclude=True,
            json_schema_extra={"examples": ["present"]},
        ),
    ] = "present"


def _validate_role_validity(
    value: datetime | None, info: ValidationInfo
) -> datetime | None:
    """Redefine value of valid_until based on validity.

    >>> Role(name="foo", validity="2025-01-01T00:00")
    Traceback (most recent call last):
        ...
    FutureWarning: 'validity' is deprecated, use valid_until instead
    >>>
    >>> warnings.simplefilter(action="ignore", category=FutureWarning)
    >>> r = Role(name="foo", validity="2025-01-01T00:00")
    >>> r.valid_until
    datetime.datetime(2025, 1, 1, 0, 0)
    >>>
    >>> warnings.simplefilter(action="ignore", category=DeprecationWarning)
    >>> r = Role(name="foo", valid_until="2025-01-01T00:00")
    >>> r.validity
    datetime.datetime(2025, 1, 1, 0, 0)
    """
    if value is not None:
        warnings.warn(
            f"{info.field_name!r} is deprecated, use valid_until instead",
            FutureWarning,
            stacklevel=2,
        )
        info.data["valid_until"] = value
    else:
        value = info.data["valid_until"]
    return value


class _RoleExisting(BaseRole):
    """Base model for a role that exists (or should exist, after creation)."""

    has_password: Annotated[
        bool,
        cli.HIDDEN,
        ansible.HIDDEN,
        Field(
            description="True if the role has a password.",
            validate_default=True,
            json_schema_extra={"readOnly": True},
        ),
        AfterValidator(_set_has_password),
    ] = False
    inherit: Annotated[
        bool,
        Field(
            description="Let the role inherit the privileges of the roles it is a member of.",
        ),
    ] = True
    login: Annotated[bool, Field(description="Allow the role to log in.")] = False
    superuser: Annotated[
        bool, Field(description="Whether the role is a superuser.")
    ] = False
    createdb: Annotated[
        bool, Field(description="Whether role can create new databases.")
    ] = False
    createrole: Annotated[
        bool, Field(description="Whether role can create new roles.")
    ] = False
    replication: Annotated[
        bool, Field(description="Whether the role is a replication role.")
    ] = False
    connection_limit: Annotated[
        int | None,
        Field(description="How many concurrent connections the role can make."),
    ] = None
    valid_until: Annotated[
        datetime | None,
        Field(
            description="Date and time after which the role's password is no longer valid."
        ),
    ] = None
    validity: Annotated[
        datetime | None,
        Field(
            deprecated=True,
            description="DEPRECATED. Use 'valid_until' instead.",
            validate_default=True,
        ),
        AfterValidator(
            partial(
                check_mutually_exclusive_with,
                "valid_until",
                operations={"create", "update"},
            )
        ),
        AfterValidator(_validate_role_validity),
    ] = None
    memberships: Annotated[
        list[
            Annotated[
                RoleMembership,
                BeforeValidator(partial(as_dict, key="role")),
                WrapSerializer(partial(serialize, key="role")),
            ]
        ],
        cli.ListOption(
            name="in_role",
            metavar="role",
            item_key="role",
            names={"add": "--grant", "remove": "--revoke"},
            descriptions={
                "add": "Grant membership of the given role.",
                "remove": "Revoke membership of the given role.",
            },
        ),
        Field(description="Roles which this role should be a member of."),
    ] = []
    hba_records: Annotated[
        list[HbaRecordForRole],
        cli.HIDDEN,
        Field(description="Entries in the pg_hba.conf file for this role."),
    ] = []
    state: Annotated[
        PresenceState,
        cli.HIDDEN,
        Field(
            description="Whether the role be present or absent.",
            exclude=True,
        ),
    ] = "present"


class Role(_RoleExisting, RoleDropped):
    """PostgreSQL role"""

    drop_owned: Annotated[
        bool, DropOwned, cli.HIDDEN, AfterValidator(validate_state_is_absent)
    ] = False
    reassign_owned: Annotated[
        str | None,
        ReassignOwned,
        cli.HIDDEN,
        AfterValidator(validate_state_is_absent),
    ] = None


class Tablespace(BaseModel):
    name: str
    location: str
    size: ByteSize


class DatabaseListItem(BaseModel):
    name: str
    owner: str
    encoding: str
    collation: str
    ctype: str
    acls: list[str]
    size: ByteSize
    description: str | None
    tablespace: Tablespace

    @classmethod
    def build(
        cls,
        *,
        tablespace: str,
        tablespace_location: str,
        tablespace_size: int,
        **kwargs: Any,
    ) -> Self:
        tblspc = Tablespace(
            name=tablespace, location=tablespace_location, size=tablespace_size
        )
        return cls(tablespace=tblspc, **kwargs)


class BaseDatabase(BaseModel):
    name: Annotated[
        str,
        Field(
            description="Database name.",
            json_schema_extra={"readOnly": True, "examples": ["demo"]},
        ),
    ]


ForceDrop = Field(description="Force the drop.", exclude=True)


class DatabaseDropped(BaseDatabase):
    """Model for a database that is being dropped."""

    force_drop: Annotated[bool, ForceDrop, cli.Option(name="force")] = False


class Schema(BaseModel):
    name: Annotated[
        str, Field(description="Schema name.", json_schema_extra={"readOnly": True})
    ]

    state: Annotated[
        PresenceState,
        Field(
            description="Schema state.",
            exclude=True,
            json_schema_extra={"examples": ["present"]},
        ),
    ] = "present"

    owner: Annotated[
        str | None,
        Field(
            description="The role name of the user who will own the schema.",
            json_schema_extra={"examples": ["postgres"]},
        ),
    ] = None


class Extension(BaseModel, frozen=True):
    name: Annotated[
        str, Field(description="Extension name.", json_schema_extra={"readOnly": True})
    ]
    schema_: Annotated[
        str | None,
        Field(
            alias="schema",
            description="Name of the schema in which to install the extension's object.",
        ),
    ] = None
    version: Annotated[
        str | None, Field(description="Version of the extension to install.")
    ] = None

    state: Annotated[
        PresenceState,
        Field(
            description="Extension state.",
            exclude=True,
            json_schema_extra={"examples": ["present"]},
        ),
    ] = "present"


class Publication(BaseModel):
    name: Annotated[
        str,
        Field(
            description="Name of the publication, unique in the database.",
        ),
    ]
    state: Annotated[
        PresenceState,
        Field(
            description="Presence state.",
            exclude=True,
            json_schema_extra={"examples": ["present"]},
        ),
    ] = "present"


class ConnectionString(BaseModel):
    conninfo: Annotated[
        str,
        Field(
            description="The libpq connection string, without password.",
        ),
        AfterValidator(partial(check_conninfo, exclude=["password"])),
    ]
    password: Annotated[
        SecretStr | None,
        Field(
            description="Optional password to inject into the connection string.",
            exclude=True,
            json_schema_extra={"readOnly": True},
        ),
    ] = None

    @classmethod
    def parse(cls, value: str) -> Self:
        conninfo = psycopg.conninfo.conninfo_to_dict(value)
        password = conninfo.pop("password", None)
        return cls(
            conninfo=psycopg.conninfo.make_conninfo("", **conninfo), password=password
        )

    @property
    def full_conninfo(self) -> str:
        """The full connection string, including password field."""
        password = None
        if self.password:
            password = self.password.get_secret_value()
        return psycopg.conninfo.make_conninfo(self.conninfo, password=password)


class Subscription(BaseModel):
    name: Annotated[str, Field(description="Name of the subscription.")]
    connection: Annotated[
        ConnectionString,
        Field(
            description="The libpq connection string defining how to connect to the publisher database.",
            json_schema_extra={"readOnly": True},
        ),
    ]
    publications: Annotated[
        list[str],
        Field(
            description="Publications on the publisher to subscribe to.",
            min_length=1,
        ),
    ]
    enabled: Annotated[
        bool, Field(description="Enable or disable the subscription.")
    ] = True
    state: Annotated[
        PresenceState,
        Field(
            description="Presence state.",
            exclude=True,
            json_schema_extra={"examples": ["present"]},
        ),
    ] = "present"

    @classmethod
    def from_row(cls, **kwargs: Any) -> Self:
        return cls(
            connection=ConnectionString.parse(kwargs.pop("connection")), **kwargs
        )


class CloneOptions(BaseModel):
    dsn: Annotated[
        PostgresDsn,
        cli.Argument(name="from", metavar="conninfo"),
        Field(
            description="Data source name of the database to restore into this one, specified as a libpq connection URI.",
        ),
    ]
    schema_only: Annotated[
        bool,
        Field(
            description="Only restore the schema (data definitions).",
        ),
    ] = False


def check_tablespace(value: str) -> str | None:
    """Make sure tablespace is valid (ie. forbid 'default' or 'DEFAULT')

    >>> Database(name="x", tablespace="xyz")
    Database(name='x', force_drop=False, state='present', owner=None, settings=None, schemas=[], extensions=[], locale=None, publications=[], subscriptions=[], clone=None, tablespace='xyz')
    >>> Database(name="x", tablespace="default")
    Traceback (most recent call last):
      ...
    pydantic_core._pydantic_core.ValidationError: 1 validation error for Database
    tablespace
      Value error, 'default' is not a valid value for 'tablespace'. Don't provide a value if you want the tablespace to be set to DEFAULT. [type=value_error, input_value='default', input_type=str]
        ...
    >>> Database(name="x", tablespace="DEFAULT")
    Traceback (most recent call last):
      ...
    pydantic_core._pydantic_core.ValidationError: 1 validation error for Database
    tablespace
      Value error, 'DEFAULT' is not a valid value for 'tablespace'. Don't provide a value if you want the tablespace to be set to DEFAULT. [type=value_error, input_value='DEFAULT', input_type=str]
        ...
    """
    if value and value.lower() == "default":
        raise ValueError(
            f"{value!r} is not a valid value for 'tablespace'. "
            "Don't provide a value if you want the tablespace to be set to DEFAULT."
        )
    return value


def _set_schemas_owner(v: list[Schema], info: ValidationInfo) -> list[Schema]:
    """Set schemas owner to that of the database, unless explicitly specified."""
    if (owner := info.data.get("owner")) is not None:
        return [
            s.model_copy(update={"owner": owner}) if s.owner is None else s for s in v
        ]
    return v


class Database(DatabaseDropped):
    """PostgreSQL database"""

    state: Annotated[
        PresenceState,
        cli.HIDDEN,
        Field(
            description="Database state.",
            exclude=True,
            json_schema_extra={"examples": ["present"]},
        ),
    ] = "present"
    owner: Annotated[
        str | None,
        Field(
            description="The role name of the user who will own the database.",
            json_schema_extra={"examples": ["postgres"]},
        ),
    ] = None
    settings: Annotated[
        MutableMapping[str, pgconf.Value | None] | None,
        cli.HIDDEN,
        ansible.Spec(spec={"type": "dict", "required": False}),
        Field(
            description=(
                "Session defaults for run-time configuration variables for the database. "
                "Upon update, an empty (dict) value would reset all settings."
            ),
            json_schema_extra={"examples": [{"work_mem": "5MB"}]},
        ),
    ] = None
    schemas: Annotated[
        list[
            Annotated[
                Schema,
                BeforeValidator(as_dict),
                WrapSerializer(serialize),
            ]
        ],
        cli.ListOption(
            name="schema",
            descriptions={
                "add": "Schemas to add to this database.",
                "remove": "Schemas to remove from this database.",
            },
        ),
        Field(
            description="Schemas in this database.",
            json_schema_extra={"examples": [{"name": "sales"}, "accounting"]},
        ),
        AfterValidator(_set_schemas_owner),
    ] = []
    extensions: Annotated[
        list[
            Annotated[
                Extension,
                BeforeValidator(as_dict),
                WrapSerializer(serialize),
            ]
        ],
        cli.ListOption(
            name="extension",
            descriptions={
                "add": "Extensions to add to this database.",
                "remove": "Extensions to remove from this database.",
            },
        ),
        Field(
            description="Extensions in this database.",
            json_schema_extra={
                "examples": [
                    {"name": "unaccent", "schema": "ext", "version": "1.0"},
                    "hstore",
                ]
            },
        ),
    ] = []
    locale: Annotated[
        str | None,
        Field(
            description="Locale for this database. Database will be created from template0 if the locale differs from the one set for template1.",
            json_schema_extra={
                "examples": ["fr_FR.utf8"],
                "readOnly": True,
                "writeOnly": True,
            },
        ),
    ] = None

    publications: Annotated[
        list[Publication],
        cli.HIDDEN,
        Field(
            description="Publications in this database.",
            json_schema_extra={"examples": [{"name": "mypub"}]},
        ),
    ] = []

    subscriptions: Annotated[
        list[Subscription],
        cli.HIDDEN,
        Field(
            description="Subscriptions in this database.",
            json_schema_extra={
                "examples": [
                    {"name": "mysub", "publications": ["mypub"], "enabled": False},
                ]
            },
        ),
    ] = []

    clone: Annotated[
        CloneOptions | None,
        Field(
            description="Options for cloning a database into this one.",
            exclude=True,
            json_schema_extra={
                "readOnly": True,
                "writeOnly": True,
                "examples": [
                    "postgresql://app:password@dbserver:5455/appdb",
                    {
                        "dsn": "postgresql://app:password@dbserver:5455/appdb",
                        "schema_only": True,
                    },
                ],
            },
        ),
    ] = None

    tablespace: Annotated[
        str | None,
        Field(
            description="The name of the tablespace that will be associated with the database.",
        ),
        AfterValidator(check_tablespace),
    ] = None

    force_drop: Annotated[
        bool, ForceDrop, cli.HIDDEN, AfterValidator(validate_state_is_absent)
    ] = False


class ReplicationSlot(BaseModel):
    """Replication slot"""

    name: Annotated[str, Field(description="Name of the replication slot.")]

    state: Annotated[
        PresenceState,
        cli.HIDDEN,
        Field(
            description="Whether the slot should be present or not.",
            exclude=True,
            json_schema_extra={"examples": ["present"]},
        ),
    ] = "present"


def _sort(value: list[str]) -> list[str]:
    value.sort()
    return value


def _sort_values(value: dict[str, list[str]]) -> dict[str, list[str]]:
    for v in value.values():
        v.sort()
    return value


class DefaultPrivilege(BaseModel):
    """Default access privilege"""

    database: str
    schema_: Annotated[str, Field(alias="schema")]
    object_type: str
    role: str
    privileges: Annotated[list[str], AfterValidator(_sort)]


class Privilege(DefaultPrivilege):
    """Access privilege"""

    object_name: str
    column_privileges: Annotated[Mapping[str, list[str]], AfterValidator(_sort_values)]


class Auth(types.BaseModel):
    local: Annotated[
        pgs.AuthLocalMethods | None,
        Field(
            description="Authentication method for local-socket connections",
            json_schema_extra={"readOnly": True},
        ),
    ] = None
    host: Annotated[
        pgs.AuthHostMethods | None,
        Field(
            description="Authentication method for local TCP/IP connections",
            json_schema_extra={"readOnly": True},
        ),
    ] = None
    hostssl: Annotated[
        pgs.AuthHostSSLMethods | None,
        Field(
            description="Authentication method for SSL-encrypted TCP/IP connections",
            json_schema_extra={"readOnly": True},
        ),
    ] = None


class PostgreSQLInstanceRef(BaseModel):
    """The minimal model for an existing PostgreSQL instance."""

    name: Annotated[str, Field(description="Instance name.")]
    version: Annotated[str, Field(description="PostgreSQL version.")]
    port: Annotated[
        int, Field(description="TCP port the PostgreSQL instance is listening to.")
    ]
    datadir: Annotated[Path, Field(description="PostgreSQL data directory.")]

    @property
    def qualname(self) -> str:
        return f"{self.version}-{self.name}"


class InstanceListItem(PostgreSQLInstanceRef):
    status: Annotated[str, Field(description="Runtime status.")]


def _default_version(value: Any, info: ValidationInfo) -> Any:
    if value is None:
        assert info.context, f"cannot validate {info.field_name} without a context"
        settings = info.context["settings"]
        return default_postgresql_version(settings.postgresql)
    return value


def _no_port_in_settings(value: dict[str, Any]) -> dict[str, Any]:
    if "port" in value:
        raise ValueError("'port' entry is disallowed; use the main 'port' field")
    return value


def _port_unset_is_available(value: Port | None, info: ValidationInfo) -> Port | None:
    """Check availability of the 'port' if the field is unset and its value
    would be picked from site template or the default 5432.
    """
    if value is None:
        template = postgresql.template(info.data["version"], "postgresql.conf")
        config = pgconf.parse_string(template)
        check_port_available(conf.get_port(config), info)
    return value


def _password_required_for_local_auth(
    value: SecretStr | None, info: ValidationInfo
) -> SecretStr | None:
    """Validate that 'value' is not None if local auth method requires a
    password.
    """
    if (
        value is None
        and info.context
        and info.context.get("operation") == "create"
        and not info.data.get("upgrading_from")
    ):
        settings = info.context["settings"].postgresql
        auth = postgresql.auth_options(info.data["auth"], settings.auth)
        if auth.local in ("password", "md5", "scram-sha-256"):
            raise ValueError(
                f"a value is required per local authentication method {auth.local!r}"
            )
    return value


class PostgreSQLInstance(BaseModel):
    """A PostgreSQL instance."""

    name: Annotated[
        str,
        Field(
            description="Instance name.",
            json_schema_extra={"readOnly": True},
            pattern=r"^[^/-]+$",
        ),
    ]

    version: Annotated[
        PostgreSQLVersion,
        Field(
            default=None,
            description="PostgreSQL version; if unspecified, determined from site settings or most recent PostgreSQL installation available on site.",
            json_schema_extra={"readOnly": True},
            validate_default=True,
        ),
        BeforeValidator(_default_version),
    ]

    standby: Annotated[
        Standby | None,
        Field(description="Standby information."),
    ] = None

    upgrading_from: Annotated[
        PostgreSQLInstanceRef | None,
        cli.HIDDEN,
        ansible.HIDDEN,
        Field(
            description="Internal field to keep a reference to the instance this manifest will be upgraded from.",
            exclude=True,
        ),
    ] = None

    port: Annotated[
        Port | None,
        AfterValidator(_port_unset_is_available),
        Field(
            description="TCP port the PostgreSQL instance will be listening to.",
            validate_default=True,
        ),
    ] = None

    settings: Annotated[
        MutableMapping[str, Any],
        AfterValidator(_no_port_in_settings),
        cli.HIDDEN,
        Field(
            description=("Settings for the PostgreSQL instance."),
            json_schema_extra={
                "examples": [
                    {
                        "listen_addresses": "*",
                        "shared_buffers": "1GB",
                        "ssl": True,
                        "ssl_key_file": "/etc/certs/db.key",
                        "ssl_cert_file": "/etc/certs/db.key",
                        "shared_preload_libraries": "pg_stat_statements",
                    }
                ]
            },
        ),
    ] = {}

    data_checksums: Annotated[
        bool | None,
        Field(
            description=(
                "Enable or disable data checksums. "
                "If unspecified, fall back to site settings choice."
            ),
        ),
    ] = None

    locale: Annotated[
        str | None,
        Field(
            description="Default locale.",
            json_schema_extra={"readOnly": True},
        ),
    ] = None

    encoding: Annotated[
        str | None,
        Field(
            description="Character encoding of the PostgreSQL instance.",
            json_schema_extra={"readOnly": True},
        ),
    ] = None

    auth: Annotated[
        Auth | None, Field(exclude=True, json_schema_extra={"writeOnly": True})
    ] = None

    surole_password: Annotated[
        SecretStr | None,
        cli.Option(metavar="password"),
        AfterValidator(_password_required_for_local_auth),
        Field(
            description="Super-user role password.",
            exclude=True,
            validate_default=True,
            json_schema_extra={"readOnly": True},
        ),
    ] = None

    replrole_password: Annotated[
        SecretStr | None,
        cli.Option(metavar="password"),
        Field(
            description="Replication role password.",
            exclude=True,
            json_schema_extra={"readOnly": True},
        ),
    ] = None

    pending_restart: Annotated[
        bool,
        cli.HIDDEN,
        ansible.HIDDEN,
        Field(
            description="Whether the instance needs a restart to account for settings changes.",
            json_schema_extra={"readOnly": True},
        ),
    ] = False

    def surole(self, settings: s.Settings) -> Role:
        s = settings.postgresql.surole
        extra = {}
        if settings.postgresql.auth.passfile is not None:
            extra["pgpass"] = s.pgpass
        return Role(name=s.name, password=self.surole_password, **extra)

    def replrole(self, settings: s.Settings) -> Role | None:
        if (name := settings.postgresql.replrole) is None:
            return None
        return Role(
            name=name,
            password=self.replrole_password,
            login=True,
            replication=True,
            memberships=["pg_read_all_stats"],
        )


def _set_creating_when_upgrading_from(value: bool, info: ValidationInfo) -> bool:
    if info.data["upgrading_from"] is not None:
        return True
    return value


def _replication_slots_not_with_demoted_standby(
    value: list[ReplicationSlot], info: ValidationInfo
) -> list[ReplicationSlot]:
    if value:
        try:
            standby = info.data["standby"]
        except KeyError:
            pass
        else:
            if standby is not None:
                assert isinstance(standby, Standby)
                if standby.status == "demoted":
                    raise ValueError(
                        "replication slots cannot be set on a standby instance"
                    )
    return value


class Instance(PostgreSQLInstance, CompositeModel, extra="allow"):
    """A pglift instance, on top of a PostgreSQL instance.

    This combines the definition of a base PostgreSQL instance with extra
    satellite components or cluster objects.

    When unspecified, some fields values are computed from site settings and
    site templates, the combination of which serves as a default "template"
    for the Instance model.
    """

    @classmethod
    def component_models(cls, pm: PluginManager) -> list[types.ComponentModel]:
        return pm.hook.instance_model()  # type: ignore[no-any-return]

    state: Annotated[
        InstanceState,
        cli.Choices(choices=["started", "stopped"]),
        Field(description="Runtime state."),
    ] = "started"

    creating: Annotated[
        bool,
        cli.HIDDEN,
        ansible.HIDDEN,
        AfterValidator(_set_creating_when_upgrading_from),
        Field(
            description="Internal field to indicate that the instance is being created.",
            exclude=True,
            validate_default=True,
        ),
    ] = False

    databases: Annotated[
        list[Database],
        cli.HIDDEN,
        Field(
            description="Databases defined in this instance (non-exhaustive list).",
            exclude=True,
            json_schema_extra={"writeOnly": True},
        ),
    ] = []

    roles: Annotated[
        list[Role],
        cli.HIDDEN,
        Field(
            description="Roles defined in this instance (non-exhaustive list).",
            exclude=True,
            json_schema_extra={"writeOnly": True},
        ),
    ] = []

    replication_slots: Annotated[
        list[
            Annotated[
                ReplicationSlot,
                BeforeValidator(as_dict),
                WrapSerializer(serialize),
            ]
        ],
        cli.ListOption(
            name="slot",
            names={
                "add": "--create-slot",
                "remove": "--drop-slot",
            },
            descriptions={
                "add": "Replication slots to create in this instance.",
                "remove": "Replication slots to drop from this instance",
            },
        ),
        Field(
            description="Replication slots in this instance (non-exhaustive list).",
            json_schema_extra={"examples": [{"name": "myslot"}, "someslot"]},
        ),
        AfterValidator(_replication_slots_not_with_demoted_standby),
    ] = []

    restart_on_changes: Annotated[
        bool,
        cli.HIDDEN,
        Field(
            description="Whether or not to automatically restart the instance to account for settings changes.",
            exclude=True,
            json_schema_extra={"writeOnly": True},
        ),
    ] = False

    @model_validator(mode="before")
    @classmethod
    def __validate_standby_and_patroni_(cls, values: dict[str, Any]) -> dict[str, Any]:
        if values.get("standby") and values.get("patroni"):
            raise ValueError("'patroni' and 'standby' fields are mutually exclusive")
        return values

    _S = TypeVar("_S", bound=Service)

    def service(self, stype: type["_S"]) -> "_S":
        """Return satellite Service attached to this instance.

        :raises ValueError: if not found.
        """
        fname = stype.__service__
        try:
            s = getattr(self, fname)
        except AttributeError as e:
            raise ValueError(fname) from e
        if s is None:
            raise ValueError(fname)
        assert isinstance(s, stype), (
            f"expecting field {fname} to have type {stype} (got {type(s)})"
        )
        return s


class ApplyResult(BaseModel):
    """
    ApplyResult allows to describe the result of a call to apply function
    (Eg: pglift.database.apply) to an object (Eg: database, instance,...).

    The `change_state` attribute of this class can be set to one of to those values:
      - `'created'` if the object has been created,
      - `'changed'` if the object has been changed,
      - `'dropped'` if the object has been dropped,
      - :obj:`None` if nothing happened to the object we manipulate (neither created,
        changed or dropped)
    """

    change_state: Annotated[
        Literal["created", "changed", "dropped"] | None,
        Field(
            description="Define the change applied (created, changed or dropped) to a manipulated object",
        ),
    ] = None  #:

    diff: Any | None = Field(
        default_factory=diffmod.get,
        description="Changes on the filesystem resulting of applied operation. Only set if diff computation was requested.",
    )


class InstanceApplyResult(ApplyResult):
    pending_restart: Annotated[
        bool,
        Field(
            description="Whether the instance needs a restart to account for settings changes.",
        ),
    ] = False


class RoleApplyResult(ApplyResult):
    pending_reload: Annotated[
        bool,
        Field(
            description="Whether the instance needs a reload to account for changes.",
        ),
    ] = False

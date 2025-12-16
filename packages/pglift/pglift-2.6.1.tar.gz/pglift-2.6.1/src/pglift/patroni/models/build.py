# SPDX-FileCopyrightText: 2021 Dalibo
#
# SPDX-License-Identifier: GPL-3.0-or-later

import warnings
from datetime import timedelta
from pathlib import Path, PurePath
from typing import Annotated, Any, Final, Literal, TypedDict

import pgtoolkit.conf as pgconf
import psycopg.conninfo
import pydantic
import yaml
from pydantic import Field, SecretStr

from ... import conf, deps, exceptions, h, hooks, types, util
from ... import postgresql as postgresql_mod
from ..._compat import Self, assert_never
from ...models import PostgreSQLInstance, interface
from ...postgresql.models import Initdb
from ...settings import _patroni
from ...system import FileSystem
from .. import impl
from . import common
from . import interface as i

logger = util.get_logger(__name__)


class BootstrapManaged(TypedDict):
    initdb: list[str | dict[str, str | PurePath]]


def bootstrap_managed(initdb_options: Initdb) -> BootstrapManaged:
    """Return managed settings for Patroni "bootstrap" configuration."""
    initdb: list[str | dict[str, str | PurePath]] = [
        {key: value}
        for key, value in initdb_options.model_dump(
            exclude={"data_checksums", "username"}, exclude_none=True
        ).items()
    ]
    if initdb_options.data_checksums:
        initdb.append("data-checksums")
    return {"initdb": initdb}


def bootstrap(
    settings: _patroni.Settings,
    initdb_options: Initdb,
    hba: list[str] | None = None,
    pg_ident: list[str] | None = None,
    parameters: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Return values for the "bootstrap" section of Patroni configuration."""
    dcs_conf = {}
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", DeprecationWarning)
        if settings.loop_wait is not None:
            dcs_conf = {"dcs": {"loop_wait": settings.loop_wait}}
    if hba is not None or pg_ident or parameters is not None:
        postgresql: dict[str, dict[str, Any]] = {"postgresql": {}}
        if parameters is not None:
            postgresql["postgresql"].update({"parameters": parameters})
        if hba is not None:
            postgresql["postgresql"].update({"pg_hba": hba})
        # ignore pg_ident None value or empty (it's what we do for local auth mode)
        if pg_ident:
            postgresql["postgresql"].update({"pg_ident": pg_ident})
        dcs_conf = util.deep_update(dcs_conf, {"dcs": postgresql})

    return bootstrap_managed(initdb_options) | dcs_conf


def export_model(model: pydantic.BaseModel) -> dict[str, Any]:
    """Export a model as a dict unshadowing secret fields.

    >>> class S(pydantic.BaseModel):
    ...     user: str
    ...     pw: SecretStr | None = None
    >>> export_model(S(user="bob", pw="s3kret"))
    {'user': 'bob', 'pw': 's3kret'}
    """
    return {
        n: v.get_secret_value() if isinstance(v, SecretStr) else v
        for n, v in model
        if v is not None
    }


def libpq_ssl_settings(model: pydantic.BaseModel) -> dict[str, Any]:
    """Return a dict suitable for libpq connection SSL options.

    >>> class S(pydantic.BaseModel):
    ...     cert: str
    ...     password: SecretStr | None = None
    ...     rootcert: str | None

    >>> libpq_ssl_settings(S(cert="a", rootcert=None))
    {'sslcert': 'a'}
    >>> libpq_ssl_settings(S(cert="z", rootcert="y", password="pwd"))
    {'sslcert': 'z', 'sslpassword': 'pwd', 'sslrootcert': 'y'}
    """
    options = {f"ssl{n}": v for n, v in export_model(model).items()}
    # Verify that the result is valid for libpq.
    assert not options or psycopg.conninfo.make_conninfo(**options)
    return options


def pgpass(qualname: str, /, settings: _patroni.PostgreSQL) -> Path:
    return Path(str(settings.passfile).format(name=qualname))


class PostgreSQLAuthentication(TypedDict):
    superuser: dict[str, Any]
    replication: dict[str, Any]
    rewind: dict[str, Any]


def postgresql_authentication(
    postgresql_options: i.PostgreSQL | None,
    connection_settings: _patroni.ConnectionOptions | None,
    *,
    surole: interface.Role,
    replrole: interface.Role,
) -> PostgreSQLAuthentication:
    """Return a dict for 'postgresql.authentication' entry of Patroni
    configuration.

    >>> postgresql_authentication(
    ...     None,
    ...     None,
    ...     surole=interface.Role(name="postgres"),
    ...     replrole=interface.Role(name="replication", password="s3kret"),
    ... )
    {'superuser': {'username': 'postgres'}, 'replication': {'username': 'replication', 'password': 's3kret'}, 'rewind': {'username': 'postgres'}}
    """
    if connection_settings and connection_settings.ssl:
        sslopts = libpq_ssl_settings(connection_settings.ssl)
    else:
        sslopts = {}

    def r(role: interface.Role, opts: i.ClientAuth | None) -> dict[str, str]:
        d = {"username": role.name} | sslopts
        if role.password:
            d["password"] = role.password.get_secret_value()
        if opts and opts.ssl:
            d |= libpq_ssl_settings(opts.ssl)
        return d

    return {
        "superuser": r(surole, None),
        "replication": r(
            replrole,
            postgresql_options.replication if postgresql_options else None,
        ),
        "rewind": r(
            surole,
            postgresql_options.rewind if postgresql_options else None,
        ),
    }


class PostgreSQLManaged(TypedDict, total=False):
    connect_address: types.Address
    listen: types.Address
    parameters: dict[str, Any] | None
    authentication: dict[str, Any]


# https://patroni.readthedocs.io/en/latest/patroni_configuration.html#postgresql-parameters-controlled-by-patroni
postgresql_parameters_controlled_by_patroni: Final = {
    "max_connections": 100,
    "max_locks_per_transaction": 64,
    "max_worker_processes": 8,
    "max_prepared_transactions": 0,
    "wal_level": "replica",
    "track_commit_timestamp": False,
    "max_wal_senders": 10,
    "max_replication_slots": 10,
    "wal_keep_segments": 8,
    "wal_keep_size": "128MB",
    "hot_standby": True,
}
postgresql_parameters_dynamically_controlled_by_patroni: Final = [
    "cluster_name",
    "listen_addresses",
    "port",
]


def postgresql_managed(
    configuration: pgconf.Configuration,
    postgresql_options: i.PostgreSQL | None,
    parameters: dict[str, Any] | None,
) -> PostgreSQLManaged:
    """Return the managed part of 'postgresql' options."""
    port = conf.get_port(configuration)

    listen_addresses = conf.get_str(configuration, "listen_addresses", "*")
    listen = types.make_address(listen_addresses, port)

    authentication = {}
    connect_address = types.local_address(port)
    if postgresql_options is not None:
        if (
            postgresql_options.replication is not None
            and postgresql_options.replication.ssl is not None
        ):
            authentication["replication"] = libpq_ssl_settings(
                postgresql_options.replication.ssl
            )

        if (
            postgresql_options.rewind is not None
            and postgresql_options.rewind.ssl is not None
        ):
            authentication["rewind"] = libpq_ssl_settings(postgresql_options.rewind.ssl)

        if postgresql_options.connect_host is not None:
            connect_address = types.make_address(postgresql_options.connect_host, port)

    managed: PostgreSQLManaged = {
        "connect_address": connect_address,
        "listen": listen,
        "authentication": authentication,
    }
    if parameters is not None:
        managed["parameters"] = parameters
    return managed


def parameters_managed(
    configuration: pgconf.Configuration,
    parameters: dict[str, Any] | None,
    local_mode: bool = True,
) -> dict[str, Any]:
    """Return managed parameters of 'postgresql' options."""

    def s(entry: pgconf.Entry) -> str | bool | int | float:
        # Serialize pgtoolkit entry without quoting; specially needed to
        # timedelta.
        if isinstance(entry.value, timedelta):
            return entry.serialize().strip("'")
        return entry.value

    params = parameters.copy() if parameters is not None else {}
    params |= {
        k: s(e)
        for k, e in sorted(configuration.entries.items())
        if k not in postgresql_parameters_dynamically_controlled_by_patroni
    }

    if local_mode and (
        controlled_by_patroni := [
            name
            for name, value in params.items()
            if (
                postgresql_parameters_controlled_by_patroni.get(name)
                not in (None, value)
            )
        ]
    ):
        logger.warning(
            "the following PostgreSQL parameter(s) cannot be changed for a Patroni-managed instance: %s",
            ", ".join(sorted(controlled_by_patroni)),
        )
    return params


def postgresql_default(
    instance: PostgreSQLInstance,
    manifest: interface.Instance,
    postgresql_options: i.PostgreSQL | None,
) -> dict[str, Any]:
    """Return default values for the "postgresql" section of Patroni
    configuration.
    """
    settings = instance._settings
    patroni_settings = settings.patroni
    assert patroni_settings is not None
    args: dict[str, Any] = {}

    surole = manifest.surole(settings)
    replrole = manifest.replrole(settings)
    assert replrole  # Per settings validation
    args["authentication"] = postgresql_authentication(
        postgresql_options,
        patroni_settings.postgresql.connection,
        surole=surole,
        replrole=replrole,
    )

    args["pgpass"] = pgpass(instance.qualname, patroni_settings.postgresql)

    args["use_unix_socket"] = True
    args["use_unix_socket_repl"] = True
    args["data_dir"] = instance.datadir
    args["bin_dir"] = postgresql_mod.bindir(instance)
    if patroni_settings.configuration_mode.auth == "local":
        args["pg_hba"] = postgresql_mod.pg_hba(manifest, settings).splitlines()
        if lines := postgresql_mod.pg_ident(manifest, settings).splitlines():
            args["pg_ident"] = lines
    args["use_pg_rewind"] = patroni_settings.postgresql.use_pg_rewind

    args["create_replica_methods"] = []
    for method, config in filter(
        None,
        hooks(
            settings,
            h.patroni_create_replica_method,
            manifest=manifest,
            instance=instance,
        ),
    ):
        args["create_replica_methods"].append(method)
        args[method] = config
    args["create_replica_methods"].append("basebackup")
    args["basebackup"] = [{"waldir": instance.waldir}]

    return args


def postgresql_upgrade_from(
    old: "PostgreSQL", instance: PostgreSQLInstance, manifest: interface.Instance
) -> dict[str, Any]:
    settings = instance._settings
    patroni_settings = settings.patroni
    assert patroni_settings is not None
    args: dict[str, Any] = {
        "data_dir": instance.datadir,
        "bin_dir": postgresql_mod.bindir(instance),
        "pgpass": pgpass(instance.qualname, patroni_settings.postgresql),
    }
    if old.create_replica_methods:
        args["create_replica_methods"] = old.create_replica_methods[:]
        for method, config in filter(
            None,
            hooks(
                settings,
                h.patroni_create_replica_method,
                manifest=manifest,
                instance=instance,
            ),
        ):
            if method in args["create_replica_methods"]:
                args[method] = config
        if "basebackup" in old.create_replica_methods and old.basebackup:
            # 'basebackup' parameters may be specified either as a map or a list of
            # elements (see end of https://patroni.readthedocs.io/en/latest/replica_bootstrap.html).
            # We need need to handle both alternatives in case the field has been
            # modified or written outside of our control.
            if isinstance(old.basebackup, dict):
                args["basebackup"] = old.basebackup | {"waldir": instance.waldir}
            elif isinstance(old.basebackup, list):
                args["basebackup"] = [
                    item | {"waldir": instance.waldir}
                    if isinstance(item, dict) and "waldir" in item
                    else item
                    for item in old.basebackup
                ]
            else:
                assert_never()
    return args


def postgresql(
    instance: PostgreSQLInstance,
    manifest: interface.Instance,
    configuration: pgconf.Configuration,
    postgresql_options: i.PostgreSQL | None,
    parameters: dict[str, Any] | None,
) -> dict[str, Any]:
    """Return values for the "postgresql" section of Patroni configuration
    when initially setting up the instance (at creation).
    """
    return util.deep_update(
        postgresql_default(instance, manifest, postgresql_options),
        dict(postgresql_managed(configuration, postgresql_options, parameters)),
    )


def etcd(model: i.Etcd | None, settings: _patroni.Settings) -> dict[str, Any]:
    return settings.etcd.model_dump(
        mode="json", exclude={"version"}, exclude_none=True
    ) | (export_model(model) if model is not None else {})


def restapi(model: common.RESTAPI, settings: _patroni.RESTAPI) -> dict[str, Any]:
    v = settings.model_dump(mode="json", exclude_none=True) | model.model_dump(
        exclude={"authentication"}, exclude_none=True
    )
    if (a := model.authentication) is not None:
        return v | {"authentication": export_model(a)}
    return v


class _BaseModel(types.BaseModel, extra="allow"):
    """A BaseModel with extra inputs allowed.

    >>> types.BaseModel(x=1)
    Traceback (most recent call last):
        ...
    pydantic_core._pydantic_core.ValidationError: 1 validation error for BaseModel
    x
      Extra inputs are not permitted [type=extra_forbidden, input_value=1, input_type=int]
      ...
    >>> _BaseModel(x=1)
    _BaseModel(x=1)
    """


class PostgreSQL(_BaseModel):
    connect_address: types.Address
    listen: types.Address
    parameters: dict[str, Any] | None = None
    pg_hba: list[str] | None = None
    pgpass: Path | None = None
    create_replica_methods: list[str] | None = None
    basebackup: None | dict[str, Any] | list[str | dict[str, Any]] = None


class RESTAPI(common.RESTAPI, _BaseModel):
    cafile: Path | None = None
    certfile: Path | None = None
    keyfile: Path | None = None
    verify_client: Literal["optional", "required"] | None = None


class Log(_BaseModel):
    dir: Path | None = None


class Patroni(_BaseModel):
    """A partial representation of a patroni instance, as defined in a YAML
    configuration.

    Only fields that are handled explicitly on our side are modelled here.
    Other fields are loaded as "extra" (allowed by _BaseModel class).
    """

    scope: str
    name: str
    log: Log | None = None
    restapi: Annotated[RESTAPI, Field(default_factory=RESTAPI)]
    postgresql: PostgreSQL

    def __str__(self) -> str:
        return f"Patroni node {self.name!r} (scope={self.scope!r})"

    @classmethod
    @deps.use
    def get(
        cls,
        qualname: str,
        settings: _patroni.Settings,
        *,
        fs: FileSystem = deps.Auto,
    ) -> Self:
        """Get a Patroni instance from its qualified name, by loading
        respective YAML configuration file.
        """
        fpath = impl._configpath(qualname, settings)
        try:
            with fs.open(fpath) as f:
                data = yaml.safe_load(f)
        except FileNotFoundError as e:
            raise exceptions.FileNotFoundError(
                f"Patroni configuration for {qualname} node not found: {e}"
            ) from e
        return cls.model_validate(data)

    def yaml(self, **kwargs: Any) -> str:
        data = self.model_dump(mode="json", exclude_none=True, **kwargs)
        if (a := self.restapi.authentication) is not None:
            data["restapi"]["authentication"] = export_model(a)
        return yaml.dump(data, sort_keys=True)

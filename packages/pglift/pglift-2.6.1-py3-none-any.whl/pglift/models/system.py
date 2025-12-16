# SPDX-FileCopyrightText: 2021 Dalibo
#
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

import hashlib
from collections.abc import Iterator
from contextlib import contextmanager
from datetime import datetime
from functools import partial
from pathlib import Path, PurePath
from typing import Any, ClassVar, TypeVar

import psycopg.conninfo
import pydantic
from attrs import Attribute, field, frozen
from attrs.validators import instance_of
from pgtoolkit.conf import Configuration

from .. import conf, deps, exceptions, h, hooks
from .._compat import Self, datetime_fromisoformat
from ..settings import (
    PostgreSQLVersion,
    Settings,
    postgresql_datadir,
    postgresql_waldir,
    valid_postgresql_version,
)
from ..system import FileSystem
from ..util import is_empty_dir


@frozen
class Standby:
    primary_conninfo: str
    slot: str | None
    user: str | None
    password: pydantic.SecretStr | None

    @classmethod
    def system_lookup(cls, instance: PostgreSQLInstance) -> Self | None:
        if not _is_standby(instance):
            return None
        config = _postgresql_configuration(instance.datadir)
        try:
            dsn = config["primary_conninfo"]
        except KeyError:
            return None
        if not dsn:
            return None
        assert isinstance(dsn, str), dsn
        primary_conninfo = psycopg.conninfo.conninfo_to_dict(dsn)
        try:
            conn_password = primary_conninfo.pop("password")
        except KeyError:
            password = None
        else:
            assert isinstance(conn_password, str)
            password = pydantic.SecretStr(conn_password)
        slot = config.get("primary_slot_name")
        if slot is not None:
            assert isinstance(slot, str), slot
        user = primary_conninfo.get("user")
        if user is not None:
            assert isinstance(user, str), user
        return cls(
            primary_conninfo=psycopg.conninfo.make_conninfo("", **primary_conninfo),
            slot=slot or None,
            user=user,
            password=password,
        )


@frozen
class PostgreSQLInstance:
    """A bare PostgreSQL instance."""

    name: str
    version: PostgreSQLVersion = field()

    _settings: Settings = field(validator=instance_of(Settings), repr=False)

    datadir: Path = field(init=False, repr=False)
    waldir: Path = field(init=False, repr=False)

    @version.validator
    def _validate_version(
        self, attribute: Attribute[PostgreSQLVersion], value: PostgreSQLVersion
    ) -> None:
        versions = [v.version for v in self._settings.postgresql.versions]
        if self.version not in versions:
            raise ValueError(
                f"{attribute.alias} {value} not amongst 'postgresql.versions' setting: {', '.join(versions)}"
            )

    @datadir.default
    def _datadir_factory(self) -> Path:
        return postgresql_datadir(
            self._settings.postgresql, version=self.version, name=self.name
        )

    @waldir.default
    def _waldir_factory(self) -> Path:
        return postgresql_waldir(
            self._settings.postgresql, version=self.version, name=self.name
        )

    @classmethod
    @contextmanager
    def creating(
        cls, name: str, version: PostgreSQLVersion, settings: Settings
    ) -> Iterator[Self]:
        """Context manager to initialize a PostgreSQLInstance while deferring
        its "checks" at exit thus leaving the opportunity for actual creation
        and configuration tasks to run within the context.
        """
        self = cls(name, version, settings)
        _check_instance_directories_not_exist_or_empty(self)
        yield self
        check_instance(self)

    @classmethod
    def system_lookup(
        cls, name: str, version: PostgreSQLVersion, settings: Settings
    ) -> Self:
        """Build a PostgreSQLInstance by system lookup.

        :raises ~exceptions.InstanceNotFound: if the instance could not be
            found by system lookup.
        """
        try:
            self = cls(name, version, settings)
        except ValueError as e:
            raise exceptions.InstanceNotFound(f"{version}/{name}", str(e)) from e
        check_instance(self)
        return self

    @property
    def standby(self) -> Standby | None:
        return Standby.system_lookup(self)

    @classmethod
    def from_qualname(cls, value: str, settings: Settings) -> Self:
        """Lookup for an Instance by its qualified name."""
        try:
            version, name = value.split("-", 1)
        except ValueError:
            raise ValueError(f"invalid qualified name {value!r}") from None
        if not valid_postgresql_version(version):
            raise exceptions.InstanceNotFound(
                f"{version}/{name}", f"{version!r} is not a valid PostgreSQL version"
            )
        return cls.system_lookup(name, version, settings)

    def __str__(self) -> str:
        return f"{self.version}/{self.name}"

    @property
    def qualname(self) -> str:
        """Version qualified name, e.g. 13-main."""
        return f"{self.version}-{self.name}"

    def configuration(self, managed_only: bool = False) -> Configuration:
        """Read and return instance configuration."""
        return _postgresql_configuration(self.datadir, managed_only)

    @property
    def port(self) -> int:
        """TCP port the server listens on."""
        return conf.get_port(self.configuration())

    @property
    def socket_directory(self) -> str | None:
        """Directory path in which the socket should be.

        This is determined from 'unix_socket_directories' configuration entry,
        only considering the first item not starting with @. None if that
        setting is not defined.
        """
        if value := self.configuration().get("unix_socket_directories"):
            assert isinstance(value, str)
            for sdir in value.split(","):
                sdir = sdir.strip()
                if not sdir.startswith("@"):
                    return sdir
        return None

    @property
    def dumps_directory(self) -> Path:
        """Path to directory where database dumps are stored."""
        return Path(
            str(self._settings.postgresql.dumps_directory).format(
                version=self.version, name=self.name
            )
        )

    @property
    def psqlrc(self) -> Path:
        return self.datadir / ".psqlrc"

    @property
    def psql_history(self) -> Path:
        return self.datadir / ".psql_history"


@frozen
class Instance:
    """A PostgreSQL instance with satellite services."""

    postgresql: PostgreSQLInstance
    name: str = field(init=False)
    services: list[Any] = field()

    _settings: Settings = field(init=False, validator=instance_of(Settings), repr=False)

    @name.default
    def _default_name(self) -> str:
        return self.postgresql.name

    @services.validator
    def _validate_services(
        self, attribute: Attribute[list[Any]], value: list[Any]
    ) -> None:
        if len(set(map(type, value))) != len(value):
            raise ValueError(
                f"values for '{attribute.alias}' field must be of distinct types"
            )

    @services.default
    def _build_services(self) -> list[Any]:
        postgresql = self.postgresql
        settings = postgresql._settings
        return [
            s
            for s in hooks(settings, h.system_lookup, instance=postgresql)
            if s is not None
        ]

    @_settings.default
    def __settings_from_postgresql_(self) -> Settings:
        return self.postgresql._settings

    @classmethod
    def system_lookup(
        cls, name: str, version: PostgreSQLVersion, settings: Settings
    ) -> Self:
        postgresql = PostgreSQLInstance.system_lookup(name, version, settings)
        return cls.from_postgresql(postgresql)

    @classmethod
    def from_postgresql(cls, postgresql: PostgreSQLInstance) -> Self:
        return cls(postgresql=postgresql)

    def __str__(self) -> str:
        return self.postgresql.__str__()

    @property
    def qualname(self) -> str:
        return self.postgresql.qualname

    S = TypeVar("S")

    def service(self, stype: type[S]) -> S:
        """Return bound satellite service object matching requested type.

        :raises ValueError: if not found.
        """
        for s in self.services:
            if isinstance(s, stype):
                return s
        raise ValueError(stype)


@frozen
class DatabaseDump:
    id: str
    dbname: str
    date: datetime
    path: PurePath

    @classmethod
    def from_path(cls, path: PurePath) -> Self | None:
        """Build a DatabaseDump from a dump file path or return None if file
        name does not match expected format.
        """
        try:
            dbname, datestr = path.stem.rsplit("_", 1)
            date = datetime_fromisoformat(datestr)
        except ValueError:
            return None
        return cls.build(dbname, date, path)

    @classmethod
    def build(cls, dbname: str, date: datetime, path: PurePath) -> Self:
        """Build a DatabaseDump from dbname and date."""
        id = "_".join(
            [
                dbname,
                hashlib.blake2b(
                    (dbname + str(date)).encode("utf-8"), digest_size=5
                ).hexdigest(),
            ]
        )
        return cls(id=id, dbname=dbname, date=date, path=path)


@frozen
class PGSetting:
    """A column from pg_settings view."""

    query: ClassVar[str] = (
        "SELECT name, setting, context, pending_restart FROM pg_settings"
    )

    name: str
    setting: str
    context: str
    pending_restart: bool


@deps.use
def _check_instance_directories_not_exist_or_empty(
    instance: PostgreSQLInstance, *, fs: FileSystem = deps.Auto
) -> None:
    """Check that 'instance' directories do not already exist or are empty.

    :raises ~exceptions.InstanceAlreadyExists: otherwise.
    """
    for dtype, dpath in (("DATA", instance.datadir), ("WAL", instance.waldir)):
        if fs.exists(dpath) and not is_empty_dir(dpath):
            raise exceptions.InstanceAlreadyExists(
                f"{dtype} directory for instance {instance} already exists and is not empty"
            )


@deps.use
def check_instance(instance: PostgreSQLInstance, *, fs: FileSystem = deps.Auto) -> None:
    """Check if the instance exists and its configuration is valid.

    :raises ~exceptions.InvalidVersion: if PG_VERSION content does not
        match declared version
    :raises ~pglift.exceptions.InstanceNotFound: if PGDATA does not exist
    :raises ~pglift.exceptions.InstanceNotFound: if configuration cannot
        be read
    """
    notfound = partial(exceptions.InstanceNotFound, str(instance))
    if not fs.exists(instance.datadir):
        raise notfound("data directory does not exist")
    try:
        real_version = fs.read_text(instance.datadir / "PG_VERSION").splitlines()[0]
    except FileNotFoundError:
        raise notfound("PG_VERSION file not found") from None
    if real_version != instance.version:
        if not instance._settings.postgresql.data_paths_versioned():
            raise notfound(
                f"requested version {instance.version} is different from PG_VERSION ({real_version})"
            )
        raise exceptions.InvalidVersion(
            f"version mismatch ({real_version} != {instance.version})"
        )
    try:
        _postgresql_configuration(instance.datadir)
    except FileNotFoundError as e:
        raise notfound(str(e)) from e


def _postgresql_configuration(
    basedir: Path, managed_only: bool = False
) -> Configuration:
    """Return parsed PostgreSQL configuration reading files in 'basedir'.

    Refer to :func:`pglift.conf.read` for complete documentation.
    """
    try:
        return conf.read(basedir, managed_only=managed_only)
    except exceptions.FileNotFoundError:
        if managed_only:
            return Configuration()
        raise


@deps.use
def _is_standby(instance: PostgreSQLInstance, *, fs: FileSystem = deps.Auto) -> bool:
    """Return True if 'instance' is a standby."""
    return fs.exists(instance.datadir / "standby.signal")

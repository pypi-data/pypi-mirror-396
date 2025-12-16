# SPDX-FileCopyrightText: 2021 Dalibo
#
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

import abc
import enum
import re
import socket
import subprocess
import typing
from collections.abc import Iterator
from contextlib import contextmanager
from contextvars import ContextVar
from dataclasses import dataclass
from functools import cache
from pathlib import Path
from typing import (
    TYPE_CHECKING,
    Annotated,
    Any,
    ClassVar,
    Literal,
    Protocol,
    TypeAlias,
    TypedDict,
    TypeVar,
)

import humanize
import pgtoolkit.conf as pgconf
import psycopg.errors
import pydantic
from pydantic import SecretStr, create_model
from pydantic.fields import FieldInfo
from pydantic.types import StringConstraints

from ._compat import Self

if TYPE_CHECKING:
    CompletedProcess = subprocess.CompletedProcess[str]
    Popen = subprocess.Popen[str]
    from .models import interface
    from .pm import PluginManager
    from .settings import Settings
else:
    CompletedProcess = subprocess.CompletedProcess
    Popen = subprocess.Popen


Unspecified: Any = object()
#: A marker for parameters default value when None cannot be used.


Operation = Literal["create", "update"]


class ValidationContext(TypedDict, total=False):
    operation: Operation
    settings: Settings
    instance: interface.Instance | None


_validation_contextvar = ContextVar[ValidationContext]("_validation_contextvar")


@contextmanager
def validation_context(
    *,
    operation: Operation,
    settings: Settings | None = None,
    instance: interface.Instance | None = Unspecified,
) -> Iterator[None]:
    context = ValidationContext(operation=operation)
    if settings is not None:
        context["settings"] = settings
    if instance is not Unspecified:
        context["instance"] = instance
    token = _validation_contextvar.set(context)
    try:
        yield
    finally:
        _validation_contextvar.reset(token)


def info_data_get(info: pydantic.ValidationInfo, key: str, /) -> Any:
    """Try to get a value from ValidationInfo.data and turn KeyError
    into a meaningful validation error.

    >>> @dataclass
    ... class Info:
    ...     field_name: str | None
    ...     data: dict[str, Any]

    >>> info = Info("foo", {"baz": 1})

    >>> info_data_get(info, "bar")
    Traceback (most recent call last):
        ...
    ValueError: cannot validate 'foo': missing or invalid 'bar' field

    >>> info_data_get(info, "baz")
    1
    """
    try:
        return info.data[key]
    except KeyError as exc:
        msg = f"missing or invalid {exc} field"
        if info.field_name is not None:
            msg = f"cannot validate {info.field_name!r}: {msg}"
        raise ValueError(msg) from exc


class ConnectionString(str):
    pass


class ByteSizeType:
    human_readable = staticmethod(humanize.naturalsize)


ByteSize: TypeAlias = Annotated[int, ByteSizeType()]


class Status(enum.IntEnum):
    running = 0
    not_running = 3


ConfigChanges: TypeAlias = dict[str, tuple[pgconf.Value | None, pgconf.Value | None]]


BackupType = Literal["full", "incr", "diff"]
BACKUP_TYPES: tuple[BackupType] = typing.get_args(BackupType)
DEFAULT_BACKUP_TYPE: BackupType = "incr"


PostgreSQLStopMode = Literal["smart", "fast", "immediate"]


class Role(Protocol):
    @property
    def name(self) -> str: ...

    @property
    def password(self) -> SecretStr | None: ...

    @property
    def encrypted_password(self) -> SecretStr | None: ...


class NoticeHandler(Protocol):
    def __call__(self, diag: psycopg.errors.Diagnostic) -> Any: ...


_T = TypeVar("_T")


def field_annotation(field: FieldInfo, t: type[_T]) -> _T | None:
    """Return the annotation of type 't' in field, or None if not found."""
    assert not isinstance(field.annotation, typing.ForwardRef), (
        "field type is a ForwardRef"
    )
    for m in field.metadata:
        if isinstance(m, t):
            return m
    return None


class BaseModel(
    pydantic.BaseModel, frozen=True, extra="forbid", validate_assignment=True
):
    def __init__(self, /, **data: Any) -> None:
        self.__pydantic_validator__.validate_python(
            data,
            self_instance=self,
            context=_validation_contextvar.get(None),
        )


@dataclass(frozen=True)
class ComponentModel:
    """Representation of a component in a composite model used to build the
    field through pydantic.create_model().
    """

    name: str
    # Name of the attribute where the component will be attached to the
    # composite model.
    field_def: Any
    # Pydantic field definition for the component model, usually a 2-tuple
    # with an Annotated definition including a pydantic.Field() annotation and
    # the default value.
    validator: Any | None = None
    # Optional field validator for the component.


class CompositeModel(
    BaseModel,
    abc.ABC,
    # Allow extra fields to permit plugins to populate an object with
    # their specific data, following (hopefully) what's defined by
    # the "composite" model (see composite()).
    extra="allow",
):
    """A model type with extra fields from plugins."""

    @classmethod
    def composite(cls, pm: PluginManager) -> type[Self]:
        fields, validators = {}, {}
        for model in cls.component_models(pm):
            fields[model.name] = model.field_def
            if model.validator is not None:
                validators[f"{model.name}_validator"] = model.validator
        m = create_model(
            cls.__name__,
            __base__=cls,
            __doc__=cls.__doc__,
            __module__=__name__,
            __validators__=validators,
            **fields,
        )
        return m

    @classmethod
    @abc.abstractmethod
    def component_models(cls, pm: PluginManager) -> list[ComponentModel]: ...


class Service(BaseModel):
    __service__: ClassVar[str]

    def __init_subclass__(cls, *, service_name: str, **kwargs: Any) -> None:
        """Set a __name__ to subclasses.

        >>> class MyS(Service, service_name="my"):
        ...     x: str
        >>> s = MyS(x="y")
        >>> s.__class__.__service__
        'my'
        """
        super().__init_subclass__(**kwargs)
        cls.__service__ = service_name


class Runnable(Protocol):
    __service_name__: ClassVar[str]

    @property
    def name(self) -> str | None: ...

    def args(self) -> list[str]: ...

    def pidfile(self) -> Path: ...

    def logfile(self) -> Path | None: ...

    def env(self) -> dict[str, str] | None: ...


address_pattern = r"(?P<host>[^\s:?#]+):(?P<port>\d+)"


Address = Annotated[str, StringConstraints(pattern=address_pattern)]
#: Network address type <host or ip>:<port>.


def make_address(host: str, port: int) -> Address:
    return f"{host}:{port}"


def local_host() -> str:
    host = socket.gethostbyname(socket.gethostname())
    if host.startswith("127."):  # loopback addresses
        host = socket.getfqdn()
    return host


def local_address(port: int) -> Address:
    return make_address(local_host(), port)


def unspecified_address() -> Address:
    return Address()


address_rgx = re.compile(address_pattern)


@cache
def address_host(addr: Address) -> str:
    m = address_rgx.match(addr)
    assert m
    return m.group("host")


@cache
def address_port(addr: Address) -> int:
    m = address_rgx.match(addr)
    assert m
    return int(m.group("port"))


LogLevel = Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]

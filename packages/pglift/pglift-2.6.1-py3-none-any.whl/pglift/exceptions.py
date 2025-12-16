# SPDX-FileCopyrightText: 2021 Dalibo
#
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

import abc
import builtins
import subprocess
from collections.abc import Sequence
from pathlib import PurePath
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from .models import PostgreSQLInstance


class Error(Exception, metaclass=abc.ABCMeta):
    """Base class for operational error."""

    def __init__(self, message: str) -> None:
        super().__init__(message)


class Cancelled(Error):
    """Action cancelled."""


class SettingsError(Error):
    """An error about settings."""


class NotFound(Error, metaclass=abc.ABCMeta):
    """Base class for errors when an object with `name` is not found."""

    def __init__(self, name: str, hint: str | None = None) -> None:
        self.name = name
        self.hint = hint
        super().__init__(name)

    @abc.abstractproperty
    def object_type(self) -> str:
        """Type of object that's not found."""
        raise NotImplementedError

    def __str__(self) -> str:
        s = f"{self.object_type} {self.name!r} not found"
        if self.hint is not None:
            s = f"{s}: {self.hint}"
        return s


class InstanceNotFound(NotFound):
    """PostgreSQL instance not found or mis-configured."""

    object_type = "instance"


class RoleNotFound(NotFound):
    """PostgreSQL role not found."""

    object_type = "role"


class DatabaseNotFound(NotFound):
    """PostgreSQL database not found."""

    object_type = "database"


class DatabaseDumpNotFound(NotFound):
    """Database dump not found."""

    object_type = "dump"


class SchemaNotFound(NotFound):
    """PostgreSQL schema not found."""

    object_type = "schema"


class CommandError(subprocess.CalledProcessError, Error):
    """Execution of a command, in a subprocess, failed."""

    def __init__(
        self,
        returncode: int,
        cmd: Sequence[str],
        stdout: str | None = None,
        stderr: str | None = None,
    ) -> None:
        super().__init__(returncode, cmd, stdout, stderr)


class SystemError(Error, OSError):
    """Error (unexpected state) on target system."""


class FileExistsError(SystemError, builtins.FileExistsError):
    pass


class FileNotFoundError(SystemError, builtins.FileNotFoundError):
    pass


class InvalidVersion(Error, ValueError):
    """Invalid PostgreSQL version."""


class UnsupportedError(Error, RuntimeError):
    """Operation is unsupported."""


class InstanceAlreadyExists(Error, ValueError):
    """Instance with Name and version already exists"""


class InstanceStateError(Error, RuntimeError):
    """Unexpected instance state."""


class InstanceReadOnlyError(Error, RuntimeError):
    """Instance is a read-only standby."""

    def __init__(self, instance: PostgreSQLInstance):
        super().__init__(f"{instance} is a read-only standby instance")


class ConfigurationError(Error, LookupError):
    """A configuration entry is missing or invalid."""

    def __init__(self, path: PurePath, message: str) -> None:
        self.path = path  #: configuration file path
        super().__init__(message)

    def __str__(self) -> str:
        return f"{super().__str__()} (path: {self.path})"


class DependencyError(Error, RuntimeError):
    """Requested operation failed to due some database dependency."""


def safe_format(template: str, **kwargs: dict[str, Any]) -> str:
    """Return formatted template, by keeping placeholder as is if corresponding
    key is missing.

    >>> safe_format("{foo} {bar}", foo="something")
    "'something' 'bar'"
    >>> safe_format("{foo} {bar}", foo="something", bar="else")
    "'something' 'else'"
    """

    class Default(dict[str, Any]):
        def __missing__(self, key: str) -> str:
            return key

        def __getitem__(self, key: str) -> str:
            value = super().__getitem__(key)
            return f"'{value}'"

    return template.format_map(Default(**kwargs))


class MutuallyExclusiveError(ValueError):
    """Two fields or options mutually exclusive are used together."""

    def __init__(self, fields: tuple[str, str]) -> None:
        super().__init__(f"{{{fields[0]}}} and {{{fields[1]}}} can't be used together")

    def __str__(self) -> str:
        return safe_format(super().__str__())

    def format(self, kwargs: dict[str, Any]) -> str:
        return safe_format(self.args[0], **kwargs)

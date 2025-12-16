# SPDX-FileCopyrightText: 2021 Dalibo
#
# SPDX-License-Identifier: GPL-3.0-or-later

import dataclasses
import string
import warnings
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Final

import pydantic

from .. import types


def string_format_variables(fmt: str) -> set[str]:
    return {v for _, v, _, _ in string.Formatter().parse(fmt) if v is not None}


class BaseModel(pydantic.BaseModel, frozen=True, extra="forbid"):
    pass


@dataclass(frozen=True)
class TemplatedPath:
    """Validate that a Path field contains expected template variables."""

    required: set[str]
    optional: set[str] = dataclasses.field(default_factory=set)

    def __call__(self, value: Path) -> Path:
        """Validate 'value' with respect to required and known template variables.

        >>> v = TemplatedPath({"foo", "bar"}, {"baz"})
        >>> v("/mnt/{foo}/0/{bar}/1/{baz}")
        '/mnt/{foo}/0/{bar}/1/{baz}'
        >>> v("foo/{bar}-{baz}")
        Traceback (most recent call last):
            ...
        ValueError: value is missing template variable(s): foo
        >>> v("/tmp/{bar}-{foo}/...")
        '/tmp/{bar}-{foo}/...'
        >>> v("p/{bar}/a/{foo}/b/{quuz}/c/d")
        Traceback (most recent call last):
            ...
        ValueError: value contains unknown template variable(s): quuz
        """
        variables = string_format_variables(str(value))
        if missing := self.required - variables:
            raise ValueError(
                f"value is missing template variable(s): {', '.join(sorted(missing))}"
            )
        known = self.required | self.optional
        if unknown := variables - known:
            raise ValueError(
                f"value contains unknown template variable(s): {', '.join(sorted(unknown))}"
            )
        return value


def not_templated(value: Path, info: pydantic.ValidationInfo) -> Path:
    """Validation function checking that 'value' path does not contain template variables.

    >>> from pathlib import Path
    >>> from typing import Annotated
    >>> from pydantic import AfterValidator, BaseModel

    >>> class A(BaseModel):
    ...     x: Annotated[Path, AfterValidator(not_templated)]
    ...     y: Path

    >>> A(x="{x}", y="{y}")
    Traceback (most recent call last):
        ...
    pydantic_core._pydantic_core.ValidationError: 1 validation error for A
    x
      Value error, x accepts no template variable [type=value_error, input_value='{x}', input_type=str]
        ...

    >>> A(x="x", y="{y}")
    A(x=PosixPath('x'), y=PosixPath('{y}'))
    """
    if string_format_variables(str(value)):
        raise ValueError(f"{info.field_name} accepts no template variable")
    return value


@dataclass(frozen=True)
class PrefixedPath:
    basedir: Path = Path("")
    key: str = "prefix"

    def prefix(self, value: Path, prefix: str | Path) -> Path:
        """Return the path prefixed if is not yet absolute.

        >>> PrefixedPath(basedir=Path("alice")).prefix(Path("documents"), "/home")
        PosixPath('/home/alice/documents')
        >>> PrefixedPath(basedir=Path("/uh")).prefix(Path("/root"), Path("/whatever"))
        PosixPath('/root')
        """
        if value.is_absolute():
            return value
        assert Path(prefix).is_absolute(), (
            f"expecting an absolute prefix (got {prefix!r})",
        )
        return prefix / self.basedir / value


ConfigPath: Final = PrefixedPath(Path("etc"))
DataPath: Final = PrefixedPath(Path("srv"))
LogPath: Final = PrefixedPath(Path("log"))
RunPath: Final = PrefixedPath(Path(""), key="run_prefix")


def prefix_values(m: pydantic.BaseModel, prefixes: dict[str, Path]) -> dict[str, Any]:
    values = {}
    for key, field in m.__class__.model_fields.items():
        with warnings.catch_warnings():
            if field.deprecated:
                warnings.simplefilter("ignore", DeprecationWarning)
            value = getattr(m, key)
        if isinstance(value, Path):
            if p := types.field_annotation(field, PrefixedPath):
                value = p.prefix(value, prefixes[p.key])
        elif isinstance(value, pydantic.BaseModel):
            value = prefix_values(value, prefixes)
        values[key] = value
    return values


class ServerCert(BaseModel):
    """TLS certificate files for a server."""

    ca_cert: pydantic.FilePath | None = pydantic.Field(
        description="Certificate Authority certificate to verify client requests.",
        default=None,
    )
    cert: pydantic.FilePath = pydantic.Field(
        description="Certificate file for TLS encryption."
    )
    key: pydantic.FilePath = pydantic.Field(
        description="Private key for the certificate."
    )

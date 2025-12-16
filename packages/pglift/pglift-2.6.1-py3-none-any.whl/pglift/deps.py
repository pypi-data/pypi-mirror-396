# SPDX-FileCopyrightText: 2025 Dalibo
#
# SPDX-License-Identifier: GPL-3.0-or-later
"""Dependency injection machinery."""

from __future__ import annotations

import inspect
import typing
from collections.abc import Callable
from contextvars import ContextVar
from dataclasses import dataclass
from functools import wraps
from typing import Annotated, Any, Generic, ParamSpec, TypeVar

__all__ = [
    "Auto",
    "Dependency",
    "use",
]

V = TypeVar("V")
P = ParamSpec("P")
R = TypeVar("R")

Auto: Any = object()
#: A marker for the default value of a dependency, to be replaced by the
#  registered value at runtime.


@dataclass(frozen=True)
class Dependency(Generic[V]):
    """Annotation for a dependency on a ContextVar."""

    var: ContextVar[V]


def use(fn: Callable[P, R]) -> Callable[P, R]:
    """Inject registered dependencies decorated function's arguments, unless specified by caller.

    >>> TracerType = Callable[[str], None]
    >>> Tracer = ContextVar[TracerType]("Tracer", default=print)

    >>> @use
    ... def op(
    ...     value: str,
    ...     t: Annotated[TracerType, Dependency(Tracer)] = Auto,
    ... ) -> int:
    ...     t(f"* received {value}")
    ...     return len(value)

    >>> op("abc")
    * received abc
    3

    Changing the ContextVar changes the dependency target:

    >>> token = Tracer.set(lambda msg: None)
    >>> op("yz")
    2
    >>> Tracer.reset(token)
    >>> op("0")
    * received 0
    1

    When explicitly passed a value, the dependency uses it instead of the default value:

    >>> messages = []
    >>> op("foo", t=messages.append)
    3
    >>> messages
    ['* received foo']

    If decorated function has no dependent parameter, a TypeError is raised:
    >>> @use
    ... def nodep(x: int) -> int: ...  # doctest: +ELLIPSIS
    Traceback (most recent call last):
        ...
    TypeError: <function nodep at 0x...> has no dependent parameter
    """
    if not (depends := _get_depends(fn)):
        raise TypeError(f"{fn} has no dependent parameter")

    s = inspect.signature(fn)

    @wraps(fn)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
        b = s.bind_partial(*args, **kwargs)
        b.apply_defaults()
        for name, dep in depends.items():
            if b.arguments.get(name) is Auto:
                b.arguments[name] = dep.get()
        return fn(*b.args, **b.kwargs)

    return wrapper


def _get_depends(f: Callable[..., Any]) -> dict[str, ContextVar[Any]]:
    r"""Retrieve 'Dependency' annotations from 'f' callable mapped to parameters name.

    >>> def fn(
    ...     x: int,
    ...     y: Annotated[int, Dependency(ContextVar("v", default=1))],
    ...     z: Annotated[float, Dependency(ContextVar("z"))],
    ... ) -> None: ...
    >>> _get_depends(fn)
    {'y': <ContextVar name='v' default=1 at 0x...>, 'z': <ContextVar name='z' at 0x...>}

    >>> _get_depends(print)
    {}

    Currently, a parameter may only use at most one dependency:

    >>> def bad(
    ...     u: Annotated[
    ...         str,
    ...         Dependency(ContextVar("b")),
    ...         Dependency(ContextVar("ad")),
    ...     ],
    ... ) -> None: ...
    >>> _get_depends(bad)
    Traceback (most recent call last):
        ...
    AssertionError: invalid annotation for u: at most one dependency is allowed
    """
    depends = {}
    for name, annotation in typing.get_type_hints(f, include_extras=True).items():
        if name == "return":
            continue
        if typing.get_origin(annotation) is not Annotated:
            continue
        args = typing.get_args(annotation)[1:]
        dependencies = [a for a in args if isinstance(a, Dependency)]
        if not dependencies:
            continue
        assert len(dependencies) == 1, (
            f"invalid annotation for {name}: at most one dependency is allowed"
        )
        depends[name] = dependencies[0].var
    return depends

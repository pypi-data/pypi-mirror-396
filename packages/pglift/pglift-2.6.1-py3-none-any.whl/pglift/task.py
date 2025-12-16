# SPDX-FileCopyrightText: 2021 Dalibo
#
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

import collections
import contextlib
import functools
import inspect
from collections.abc import AsyncIterator, Callable, Iterator
from dataclasses import dataclass
from typing import Any, ClassVar, Generic, ParamSpec, TypeVar, overload

import pydantic

from . import __name__ as pkgname
from . import exceptions, util

logger = util.get_logger(pkgname)

P = ParamSpec("P")
T = TypeVar("T")
RP = ParamSpec("RP")
RT = TypeVar("RT")

Call = tuple["Task[Any, Any]", tuple[Any, ...], dict[str, Any]]


@dataclass
class RevertAction(Generic[RP, RT]):
    signature: inspect.Signature
    call: Callable[RP, RT]


class Task(Generic[P, T]):
    _calls: ClassVar[collections.deque[Call] | None] = None

    def __init__(self, title: str | None, action: Callable[P, T]) -> None:
        self.title = title
        self.action = action
        self.signature = inspect.signature(action)
        self.revert_action: RevertAction[Any, Any] | None = None
        functools.update_wrapper(self, action)

    def __repr__(self) -> str:
        return f"<Task {self.action.__name__!r} at 0x{id(self)}>"

    def __call__(self, *args: P.args, **kwargs: P.kwargs) -> T:
        if self._calls is not None:
            self._calls.append((self, args, kwargs))
        b = self.signature.bind(*args, **kwargs)
        b.apply_defaults()
        if self.title:
            logger.info(self.title.format(**b.arguments))
        return self.action(*args, **kwargs)

    def revert(self, revertfn: Callable[RP, RT], /) -> Callable[RP, RT]:
        """Decorator to register a 'revert' callback function.

        The revert function must accept a subset of the arguments of its
        respective action, though it can declare different parameters as long as
        they have a default value.
        """
        if inspect.iscoroutinefunction(self.action) and not inspect.iscoroutinefunction(
            revertfn
        ):
            raise TypeError(
                f"revert function '{revertfn.__module__}.{revertfn.__name__}' must be a coroutine function"
            )
        s = inspect.signature(revertfn)
        task_repr = f"{self.action.__module__}.{self.action.__name__}{self.signature}"
        revert_repr = f"{revertfn.__module__}.{revertfn.__name__}{s}"
        assert not (
            unknown := {
                n
                for n, p in s.parameters.items()
                if p.default is inspect.Parameter.empty
            }
            - set(self.signature.parameters)
        ), (
            f"{revert_repr} declares parameters unknown from {task_repr}: {', '.join(sorted(unknown))}"
        )
        assert not (
            incompatible := [
                k
                for k in set(s.parameters) & set(self.signature.parameters)
                if s.parameters[k] != self.signature.parameters[k]
            ]
        ), (
            f"{revert_repr} declares parameters incompatible with {task_repr}: {', '.join(sorted(incompatible))}"
        )
        self.revert_action = RevertAction(s, revertfn)
        return revertfn

    def rollback(self, *args: P.args, **kwargs: P.kwargs) -> Any:
        if self.revert_action is None:
            return
        b = self.signature.bind(*args, **kwargs)
        b.apply_defaults()
        if self.title:
            logger.warning("reverting: %s", self.title.format(**b.arguments))
        for arg in list(b.arguments):
            if arg not in self.revert_action.signature.parameters:
                del b.arguments[arg]
        return self.revert_action.call(*b.args, **b.kwargs)


@overload
def task(__func: Callable[P, T]) -> Task[P, T]: ...


@overload
def task(*, title: str | None) -> Callable[[Callable[P, T]], Task[P, T]]: ...


def task(
    __func: Callable[P, T] | None = None, *, title: str | None = None
) -> Task[P, T] | Callable[[Callable[P, T]], Task[P, T]]:
    def mktask(fn: Callable[P, T]) -> Task[P, T]:
        return functools.wraps(fn)(Task(title, fn))  # type: ignore[return-value]

    if __func is not None:
        return mktask(__func)
    return mktask


@contextlib.contextmanager
def transaction(revert_on_error: bool = True) -> Iterator[None]:
    """Context manager handling revert of run tasks, in case of failure."""
    if Task._calls is not None:
        raise RuntimeError("inconsistent task state")
    Task._calls = collections.deque()
    try:
        yield
    except BaseException as exc:
        # Only log internal errors, i.e. those not coming from user
        # cancellation or invalid input data.
        if isinstance(exc, KeyboardInterrupt):
            if Task._calls:
                logger.warning("%s interrupted", Task._calls[-1][0])
        elif not isinstance(exc, pydantic.ValidationError | exceptions.Cancelled):
            logger.warning(str(exc))
        assert Task._calls is not None
        while True:
            try:
                t, args, kwargs = Task._calls.pop()
            except IndexError:
                break
            if revert_on_error:
                r = t.rollback(*args, **kwargs)
                assert not inspect.isawaitable(r)
        raise exc
    finally:
        Task._calls = None


@contextlib.asynccontextmanager
async def async_transaction(revert_on_error: bool = True) -> AsyncIterator[None]:
    """Context manager handling revert of run tasks, in case of failure."""
    if Task._calls is not None:
        raise RuntimeError("inconsistent task state")
    Task._calls = collections.deque()
    try:
        yield
    except BaseException as exc:
        # Only log internal errors, i.e. those not coming from user
        # cancellation or invalid input data.
        if isinstance(exc, KeyboardInterrupt):
            if Task._calls:
                logger.warning("%s interrupted", Task._calls[-1][0])
        elif not isinstance(exc, pydantic.ValidationError | exceptions.Cancelled):
            logger.warning(str(exc))
        assert Task._calls is not None
        while True:
            try:
                t, args, kwargs = Task._calls.pop()
            except IndexError:
                break
            if revert_on_error:
                r = t.rollback(*args, **kwargs)
                if inspect.isawaitable(r):
                    await r
        raise exc
    finally:
        Task._calls = None

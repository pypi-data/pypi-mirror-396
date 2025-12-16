# SPDX-FileCopyrightText: 2021 Dalibo
#
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

import asyncio
import logging
import re
from collections.abc import Callable
from typing import Protocol

import pytest

from pglift import exceptions, task
from pglift._compat import assert_type


@task.task
def fwd(x: int, y: str) -> dict[str, str]:
    if not y:
        raise ValueError("empty y")
    return {"x": str(x + 1), "y": y}


def bad1(x: int, z: str, *, msg: str | None) -> None:
    pass


def bad2(x: int, y: int) -> None:
    pass


@pytest.mark.parametrize(
    ("fn", "msg"),
    [
        (bad1, r".+bad1.+ declares parameters unknown from .+fwd.+: msg, z"),
        (bad2, r".+bad2.+ declares parameters incompatible with .+fwd.+: y"),
    ],
)
def test_task_revert_bad_parameters(fn: Callable[..., None], msg: str) -> None:
    with pytest.raises(AssertionError, match=msg):
        fwd.revert(fn)


def test_task_revert_less_parameters() -> None:
    """A revert callback may be defined with less parameters than its task."""
    values: list[tuple[str, str]] = []

    @fwd.revert
    def bwd(x: int, msg: str = "reverted") -> None:
        values.append(("x", f"{msg}: {x - 1}"))

    with pytest.raises(ValueError, match="empty y"), task.transaction():
        fwd(1, "")

    assert values == [("x", "reverted: 0")]

    bwd(2, msg="direct call")

    assert values == [
        ("x", "reverted: 0"),
        ("x", "direct call: 1"),
    ]


def test_task_revert_typing() -> None:
    """The revert decorator preserves runtime and static typing of the callback."""

    @fwd.revert
    def bwd(x: int, *, offset: int = 1) -> str:
        return str(x - offset)

    class Expected(Protocol):
        def __call__(self, x: int, *, offset: int = ...) -> str: ...

    assert_type(bwd, Expected)

    with pytest.raises(TypeError):
        bwd("u", foo="bar")  # type: ignore[arg-type, call-arg]

    assert bwd(2, offset=2) == "0"


logger = logging.getLogger(__name__)


def test_task() -> None:
    @task.task(title="negate")
    def neg(x: int) -> int:
        return -x

    assert re.match(r"<Task 'neg' at 0x(\d+)>" "", repr(neg))

    assert neg(1) == -1
    assert neg.revert_action is None

    # Check static and runtime type error.
    with pytest.raises(TypeError):
        neg("1")  # type: ignore[arg-type]

    @neg.revert
    def revert_neg(x: int) -> int:
        return -x

    assert neg.revert_action
    assert neg.revert_action.call(-1) == 1


@pytest.mark.anyio
async def test_task_async() -> None:
    @task.task
    async def iamasync() -> int:
        return 1

    with pytest.raises(
        TypeError,
        match=r"revert function '.+\.iamnotasync' must be a coroutine function",
    ):

        @iamasync.revert
        def iamnotasync() -> int:
            return 99

    @iamasync.revert
    async def revert_iamasync() -> int:
        return 0

    assert await iamasync() == 1
    assert await revert_iamasync() == 0


def test_transaction_state() -> None:
    with pytest.raises(RuntimeError, match="inconsistent task state"):
        with task.transaction():
            with task.transaction():
                pass

    with pytest.raises(ValueError, match="expected"):
        with task.transaction():
            assert task.Task._calls is not None
            raise ValueError("expected")
    assert task.Task._calls is None


@pytest.mark.anyio
async def test_async_transaction_state() -> None:
    with pytest.raises(RuntimeError, match="inconsistent task state"):
        async with task.async_transaction():
            async with task.async_transaction():
                pass

    with pytest.raises(ValueError, match="expected"):
        async with task.async_transaction():
            assert task.Task._calls is not None
            raise ValueError("expected")
    assert task.Task._calls is None


def test_transaction(caplog: pytest.LogCaptureFixture) -> None:
    values = set()

    @task.task(title="add {x} to values")
    def add(x: int, fail: bool = False) -> None:
        values.add(x)
        if fail:
            raise RuntimeError("oups")

    add(1)
    assert values == {1}

    caplog.clear()
    with pytest.raises(RuntimeError, match="oups"):
        with caplog.at_level(logging.INFO, logger="pglift"):
            with task.transaction():
                add(2, fail=True)
    # no revert action
    assert values == {1, 2}
    assert caplog.messages == ["add 2 to values", "oups"]

    @add.revert
    def remove(x: int) -> None:
        try:
            values.remove(x)
        except KeyError:
            pass
        else:
            logger.info("removed %s from values", x)

    caplog.clear()
    with pytest.raises(RuntimeError, match="oups"):
        with (
            caplog.at_level(logging.INFO, logger="pglift"),
            caplog.at_level(logging.INFO, logger=__name__),
        ):
            with task.transaction():
                add(3, fail=False)
                add(4, fail=True)
    assert values == {1, 2}
    assert caplog.messages == [
        "add 3 to values",
        "add 4 to values",
        "oups",
        "reverting: add 4 to values",
        "removed 4 from values",
        "reverting: add 3 to values",
        "removed 3 from values",
    ]

    @add.revert
    def remove_fail(x: int, fail: bool = False) -> None:
        logger.info("remove numbers, failed")
        values.remove(x)
        if fail:
            raise ValueError("failed to fail")

    caplog.clear()
    with (
        pytest.raises(ValueError, match="failed to fail"),
        caplog.at_level(logging.WARNING),
    ):
        with task.transaction():
            add(3, fail=False)
            add(4, fail=True)
    assert values == {1, 2, 3}
    assert caplog.messages == [
        "oups",
        "reverting: add 4 to values",
    ]

    with pytest.raises(RuntimeError, match="oups"):
        with task.transaction(False):
            add(4, fail=True)
    assert values == {1, 2, 3, 4}

    @task.task
    def intr() -> None:
        raise KeyboardInterrupt

    caplog.clear()
    with pytest.raises(KeyboardInterrupt), caplog.at_level(logging.WARNING):
        with task.transaction():
            intr()
    assert caplog.messages == [f"{intr} interrupted"]

    @task.task
    def cancel() -> None:
        raise exceptions.Cancelled("forget about it")

    caplog.clear()
    with pytest.raises(exceptions.Cancelled):
        with task.transaction():
            cancel()
    assert not caplog.messages


@pytest.mark.anyio
async def test_transaction_async(caplog: pytest.LogCaptureFixture) -> None:
    values = set()

    @task.task(title="add {x} to values")
    async def add(x: int, fail: bool = False) -> None:
        await asyncio.sleep(0)
        values.add(x)
        if fail:
            raise RuntimeError("oups")

    await add(1)
    assert values == {1}

    caplog.clear()
    with pytest.raises(RuntimeError, match="oups"):
        with caplog.at_level(logging.INFO, logger="pglift"):
            async with task.async_transaction():
                await add(2, fail=True)
    # no revert action
    assert values == {1, 2}
    assert caplog.messages == ["add 2 to values", "oups"]

    @add.revert
    async def remove(x: int) -> None:
        await asyncio.sleep(0)
        try:
            values.remove(x)
        except KeyError:
            pass
        logger.info("removed %s from values", x)

    caplog.clear()
    with pytest.raises(RuntimeError, match="oups"):
        with (
            caplog.at_level(logging.INFO, logger="pglift"),
            caplog.at_level(logging.INFO, logger=__name__),
        ):
            async with task.async_transaction():
                await add(3, fail=False)
                await add(4, fail=True)
    assert values == {1, 2}
    assert caplog.messages == [
        "add 3 to values",
        "add 4 to values",
        "oups",
        "reverting: add 4 to values",
        "removed 4 from values",
        "reverting: add 3 to values",
        "removed 3 from values",
    ]

    @add.revert
    async def remove_fail(x: int, fail: bool = False) -> None:
        logger.info("remove numbers, failed")
        values.remove(x)
        if fail:
            raise ValueError("failed to fail")

    caplog.clear()
    with (
        pytest.raises(ValueError, match="failed to fail"),
        caplog.at_level(logging.WARNING),
    ):
        async with task.async_transaction():
            await add(3, fail=False)
            await add(4, fail=True)
    assert values == {1, 2, 3}
    assert caplog.messages == [
        "oups",
        "reverting: add 4 to values",
    ]

    with pytest.raises(RuntimeError, match="oups"):
        async with task.async_transaction(False):
            await add(4, fail=True)
    assert values == {1, 2, 3, 4}

    @task.task
    async def intr() -> None:
        raise KeyboardInterrupt

    caplog.clear()
    with pytest.raises(KeyboardInterrupt), caplog.at_level(logging.WARNING):
        async with task.async_transaction():
            await intr()
    assert caplog.messages == [f"{intr} interrupted"]

    @task.task
    async def cancel() -> None:
        raise exceptions.Cancelled("forget about it")

    caplog.clear()
    with pytest.raises(exceptions.Cancelled):
        async with task.async_transaction():
            await cancel()
    assert not caplog.messages

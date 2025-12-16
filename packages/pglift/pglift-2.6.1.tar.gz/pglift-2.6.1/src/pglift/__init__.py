# SPDX-FileCopyrightText: 2021 Dalibo
#
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

import sys
from collections.abc import Awaitable, Callable, Iterator, Mapping, Sequence
from contextlib import contextmanager
from functools import cache, singledispatch
from typing import Any, Final, ParamSpec, TypeVar, overload

import pluggy

from . import hookspecs as h
from . import pm, settings

__all__ = ["h", "hookimpl"]

# Declare type for hookimpl on our side until a version (> 1.0.0) is
# available.

F = TypeVar("F", bound=Callable[..., Any])


@overload
def hookimpl(__func: F) -> F: ...


@overload
def hookimpl(*, trylast: bool = ...) -> Callable[[F], F]: ...


def hookimpl(*args: Any, **kwargs: Any) -> Any:
    return pluggy.HookimplMarker(__name__)(*args, **kwargs)


@cache
def plugin_manager(s: settings.Settings) -> pm.PluginManager:
    return pm.PluginManager.get(s)


BeforeCall = Callable[[str, Sequence[pluggy.HookImpl], Mapping[str, Any]], None]
AfterCall = Callable[
    [Sequence[Any], str, Sequence[pluggy.HookImpl], Mapping[str, Any]], None
]

_HOOK_MONITOR: tuple[BeforeCall, AfterCall] | None = None


@contextmanager
def hook_monitoring(before: BeforeCall, after: AfterCall) -> Iterator[None]:
    """Register callbacks to be invoked (through hookexec()) upon hook calls."""
    global _HOOK_MONITOR
    assert _HOOK_MONITOR is None
    _HOOK_MONITOR = before, after
    try:
        yield
    finally:
        _HOOK_MONITOR = None


@contextmanager
def hookexec(
    hook_name: str, hook_impls: Sequence[pluggy.HookImpl], kwargs: Mapping[str, Any]
) -> Iterator[list[Any]]:
    """Context manager storing hook calls outcome and possibly invoking
    monitoring callbacks.
    """
    outcomes: list[Any] = []
    if _HOOK_MONITOR is not None:
        _HOOK_MONITOR[0](hook_name, hook_impls, kwargs)
    try:
        yield outcomes
    finally:
        if _HOOK_MONITOR is not None:
            _HOOK_MONITOR[1](outcomes, hook_name, hook_impls, kwargs)


R = TypeVar("R")
P = ParamSpec("P")


@singledispatch
def hooks(
    arg: pluggy.PluginManager | settings.Settings,
    spec: Callable[P, R],
    /,
    *args: P.args,
    **kwargs: P.kwargs,
) -> list[R]:
    """Invoke hook implementations matching 'spec' and return their result."""
    raise NotImplementedError


@hooks.register(pluggy.PluginManager)
def _(
    pm: pluggy.PluginManager, spec: Callable[P, R], /, *args: P.args, **kwargs: P.kwargs
) -> list[R]:
    assert not args
    opts = pm.parse_hookspec_opts(sys.modules[spec.__module__], spec.__name__)
    assert opts is None or not opts["firstresult"], (
        f"hook {spec.__name__!r} has firstresult=True"
    )
    hookcaller = getattr(pm.hook, spec.__name__)
    hook_impls = list(reversed(hookcaller.get_hookimpls()))
    with hookexec(spec.__name__, hook_impls, kwargs) as outcomes:
        for hook_impl in hook_impls:
            hook_kwargs = {name: kwargs[name] for name in hook_impl.argnames}
            r = hook_impl.function(**hook_kwargs)
            outcomes.append(r)
    return outcomes


@hooks.register(settings.Settings)
def _(
    s: settings.Settings, spec: Callable[P, R], /, *args: P.args, **kwargs: P.kwargs
) -> list[R]:
    return hooks(plugin_manager(s), spec, *args, **kwargs)


@singledispatch
async def async_hooks(
    arg: pluggy.PluginManager | settings.Settings,
    spec: Callable[P, Awaitable[R]],
    /,
    *args: P.args,
    **kwargs: P.kwargs,
) -> list[R]:
    """Invoke async hook implementations matching 'spec' and return their result."""
    raise NotImplementedError


@async_hooks.register(pluggy.PluginManager)
async def _(
    pm: pluggy.PluginManager,
    spec: Callable[P, Awaitable[R]],
    /,
    *args: P.args,
    **kwargs: P.kwargs,
) -> list[R]:
    assert not args
    opts = pm.parse_hookspec_opts(sys.modules[spec.__module__], spec.__name__)
    assert opts is None or not opts["firstresult"], (
        f"hook {spec.__name__!r} has firstresult=True"
    )
    hookcaller = getattr(pm.hook, spec.__name__)
    hook_impls = list(reversed(hookcaller.get_hookimpls()))
    with hookexec(spec.__name__, hook_impls, kwargs) as outcomes:
        for hook_impl in hook_impls:
            hook_kwargs = {name: kwargs[name] for name in hook_impl.argnames}
            r = await hook_impl.function(**hook_kwargs)
            outcomes.append(r)
    return outcomes


@async_hooks.register(settings.Settings)
async def _(
    s: settings.Settings,
    spec: Callable[P, Awaitable[R]],
    /,
    *args: P.args,
    **kwargs: P.kwargs,
) -> list[R]:
    return await async_hooks(plugin_manager(s), spec, *args, **kwargs)


@singledispatch
def hook(
    arg: pluggy.PluginManager | settings.Settings,
    spec: Callable[P, R],
    /,
    *args: P.args,
    **kwargs: P.kwargs,
) -> R | None:
    """Invoke hook implementations matching 'spec' and return the first result, if any."""
    raise NotImplementedError


@hook.register(pluggy.PluginManager)
def _(
    pm: pluggy.PluginManager, spec: Callable[P, R], /, *args: P.args, **kwargs: P.kwargs
) -> R | None:
    assert not args
    opts = pm.parse_hookspec_opts(sys.modules[spec.__module__], spec.__name__)
    assert opts is not None and opts["firstresult"], (
        f"hook {spec.__name__!r} hasn't firstresult=True"
    )
    hookcaller = getattr(pm.hook, spec.__name__)
    for hook_impl in reversed(hookcaller.get_hookimpls()):
        hook_kwargs = {name: kwargs[name] for name in hook_impl.argnames}
        if (result := hook_impl.function(**hook_kwargs)) is not None:
            return result  # type: ignore[no-any-return]
    return None


@hook.register(settings.Settings)
def _(
    s: settings.Settings, spec: Callable[P, R], /, *args: P.args, **kwargs: P.kwargs
) -> R | None:
    return hook(plugin_manager(s), spec, *args, **kwargs)


@singledispatch
async def async_hook(
    arg: pluggy.PluginManager | settings.Settings,
    spec: Callable[P, Awaitable[R]],
    /,
    *args: P.args,
    **kwargs: P.kwargs,
) -> R | None:
    """Invoke async hook implementations matching 'spec' and return the first result, if any."""
    raise NotImplementedError


@async_hook.register(pluggy.PluginManager)
async def _(
    pm: pluggy.PluginManager,
    spec: Callable[P, Awaitable[R]],
    /,
    *args: P.args,
    **kwargs: P.kwargs,
) -> R | None:
    assert not args
    opts = pm.parse_hookspec_opts(sys.modules[spec.__module__], spec.__name__)
    assert opts is not None and opts["firstresult"], (
        f"hook {spec.__name__!r} hasn't firstresult=True"
    )
    hookcaller = getattr(pm.hook, spec.__name__)
    for hook_impl in reversed(hookcaller.get_hookimpls()):
        hook_kwargs = {name: kwargs[name] for name in hook_impl.argnames}
        if (result := await hook_impl.function(**hook_kwargs)) is not None:
            return result  # type: ignore[no-any-return]
    return None


@async_hook.register(settings.Settings)
async def _(
    s: settings.Settings,
    spec: Callable[P, Awaitable[R]],
    /,
    *args: P.args,
    **kwargs: P.kwargs,
) -> R | None:
    return await async_hook(plugin_manager(s), spec, *args, **kwargs)


execpath: Final = (
    sys.executable
    if getattr(sys, "frozen", False)
    else f"{sys.executable} -m pglift_cli"
)

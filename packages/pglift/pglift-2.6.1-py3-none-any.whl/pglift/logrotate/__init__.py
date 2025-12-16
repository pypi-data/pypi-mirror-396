# SPDX-FileCopyrightText: 2021 Dalibo
#
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

from collections.abc import Iterator
from pathlib import Path

from .. import deps, h, hookimpl, hooks, util
from ..models import Instance
from ..settings import Settings, _logrotate
from ..system import FileSystem

logger = util.get_logger(__name__)


def register_if(settings: Settings) -> bool:
    return settings.logrotate is not None


def get_settings(settings: Settings) -> _logrotate.Settings:
    assert settings.logrotate is not None
    return settings.logrotate


def config_path(settings: _logrotate.Settings) -> Path:
    return settings.configdir / "logrotate.conf"


@hookimpl
async def site_configure_install(settings: Settings) -> None:
    _install(settings)


@deps.use
def _install(settings: Settings, *, fs: FileSystem = deps.Auto) -> None:
    s = get_settings(settings)
    fpath = config_path(s)
    if fs.exists(fpath):
        return
    if not fs.exists(s.configdir):
        logger.info("creating logrotate config directory")
        fs.mkdir(s.configdir, mode=0o750, exist_ok=True, parents=True)
    configs = [
        outcome
        for outcome in hooks(settings, h.logrotate_config, settings=settings)
        if outcome is not None
    ]
    if not configs:
        return
    with fs.open(fpath, "w") as f:
        logger.info("writing logrotate config")
        f.write("\n".join(configs))


@hookimpl
async def site_configure_uninstall(settings: Settings) -> None:
    _uninstall(get_settings(settings))


@deps.use
def _uninstall(settings: _logrotate.Settings, *, fs: FileSystem = deps.Auto) -> None:
    if fs.exists(settings.configdir):
        logger.info("deleting logrotate config directory")
        util.rmtree(settings.configdir)


@hookimpl
def site_configure_check(settings: Settings, log: bool) -> Iterator[bool]:
    yield _check(get_settings(settings), log)


@deps.use
def _check(
    settings: _logrotate.Settings, log: bool, *, fs: FileSystem = deps.Auto
) -> bool:
    fpath = config_path(settings)
    if not fs.exists(fpath):
        if log:
            logger.error("logrotate configuration '%s' missing", fpath)
        return False
    return True


@hookimpl
def site_configure_list(settings: Settings) -> Iterator[Path]:
    s = get_settings(settings)
    yield config_path(s)


def instance_configpath(settings: _logrotate.Settings, instance: Instance) -> Path:
    return settings.configdir / f"{instance.qualname}.conf"


@hookimpl
async def instance_dropped(instance: Instance) -> None:
    _remove_config(instance)


@deps.use
def _remove_config(instance: Instance, *, fs: FileSystem = deps.Auto) -> None:
    settings = get_settings(instance._settings)
    fs.unlink(instance_configpath(settings, instance), missing_ok=True)

# SPDX-FileCopyrightText: 2021 Dalibo
#
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

from collections.abc import Iterator
from pathlib import Path

from pgtoolkit.conf import Configuration

from .. import deps, h, hookimpl, hooks, postgresql, util
from ..models import interface
from ..settings import Settings, _rsyslog
from ..system import FileSystem

logger = util.get_logger(__name__)


def register_if(settings: Settings) -> bool:
    return settings.rsyslog is not None


def get_settings(settings: Settings) -> _rsyslog.Settings:
    assert settings.rsyslog is not None
    return settings.rsyslog


def config_path(settings: _rsyslog.Settings) -> Path:
    return settings.configdir / "rsyslog.conf"


@hookimpl
async def site_configure_install(settings: Settings) -> None:
    install(settings)


@deps.use
def install(settings: Settings, *, fs: FileSystem = deps.Auto) -> None:
    s = get_settings(settings)
    if fs.exists(fpath := config_path(s)):
        return
    util.check_or_create_directory(s.configdir, "rsyslog config", mode=0o750)
    configs = [
        outcome
        for outcome in hooks(settings, h.rsyslog_config, settings=settings)
        if outcome is not None
    ]
    if not configs:
        return
    with fs.open(fpath, "w") as f:
        logger.info("writing rsyslog config")
        f.write("\n".join(configs))


@hookimpl
async def site_configure_uninstall(settings: Settings) -> None:
    s = get_settings(settings)
    uninstall(s)


@deps.use
def uninstall(settings: _rsyslog.Settings, *, fs: FileSystem = deps.Auto) -> None:
    if fs.exists(settings.configdir):
        logger.info("deleting rsyslog config directory")
        util.rmtree(settings.configdir)


@hookimpl
def site_configure_check(settings: Settings, log: bool) -> Iterator[bool]:
    s = get_settings(settings)
    yield check(s, log)


@deps.use
def check(
    settings: _rsyslog.Settings, log: bool, *, fs: FileSystem = deps.Auto
) -> bool:
    if not fs.exists(fpath := config_path(settings)):
        if log:
            logger.error("rsyslog configuration file '%s' missing", fpath)
        return False
    return True


@hookimpl
def site_configure_list(settings: Settings) -> Iterator[Path]:
    s = get_settings(settings)
    yield config_path(s)


@hookimpl
def instance_settings(
    manifest: interface.PostgreSQLInstance,
) -> tuple[str, Configuration]:
    pgconfig = postgresql.template(manifest.version, "postgresql-rsyslog.conf").format(
        name=manifest.name,
        version=manifest.version,
    )
    config = Configuration()
    list(config.parse(pgconfig.splitlines()))
    return "rsyslog", config

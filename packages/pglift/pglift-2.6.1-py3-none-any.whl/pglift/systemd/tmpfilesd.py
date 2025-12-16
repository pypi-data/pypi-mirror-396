# SPDX-FileCopyrightText: 2025 Dalibo
#
# SPDX-License-Identifier: GPL-3.0-or-later

from collections.abc import Iterator
from pathlib import Path, PurePath

from .. import deps, h, hookimpl, hooks, systemd, util
from ..settings import Settings, _systemd
from ..system import Command, FileSystem

logger = util.get_logger(__name__)


def register_if(settings: Settings) -> bool:
    return settings.tmpfiles_manager == "systemd"


def config_path(name: str, settings: Settings) -> Path:
    assert settings.systemd
    return settings.systemd.tmpfilesd_conf_path / f"pglift-{name}.conf"


@deps.use
def install(
    name: str, content: str, settings: Settings, *, fs: FileSystem = deps.Auto
) -> bool:
    if fs.exists(path := config_path(name, settings)):
        return False
    fs.mkdir(path.parent, parents=True, exist_ok=True)
    fs.write_text(path, content)
    logger.info("installed %s systemd-tmpfiles.d configuration at %s", name, path)
    return True


@deps.use
def uninstall(name: str, settings: Settings, *, fs: FileSystem = deps.Auto) -> None:
    path = config_path(name, settings)
    fs.unlink(path, missing_ok=True)
    logger.info("removing %s systemd-tmpfiles.d configuration %s", name, path)


@deps.use
def installed(name: str, settings: Settings, *, fs: FileSystem = deps.Auto) -> bool:
    return fs.exists(config_path(name, settings))


@deps.use
async def systemd_tmpfiles_create(
    settings: _systemd.Settings, *, cmd: Command = deps.Auto
) -> None:
    cmd_args = [str(settings.systemd_tmpfiles), "--create"]
    if settings.user:
        cmd_args.append("--user")
    if settings.sudo:
        cmd_args.insert(0, "sudo")
    logger.info("creating ephemeral directories with systemd-tmpfiles")
    await cmd.run(cmd_args, check=True, env=None)


def should_manage_conf(run_prefix: PurePath, managed_dir: PurePath) -> bool:
    """Determine whether a systemd-tmpfiles configuration should be managed
    for a given directory.

    >>> should_manage_conf(PurePath("/run"), PurePath("/run"))
    False
    >>> should_manage_conf(PurePath("/toto"), PurePath("/run/pglift"))
    False
    >>> should_manage_conf(PurePath("/run"), PurePath("/run/pglift"))
    True
    >>> should_manage_conf(PurePath("/run"), PurePath("/run/pglift/machin"))
    True
    """
    return managed_dir.is_relative_to(run_prefix) and managed_dir != run_prefix


@hookimpl
async def site_configure_install(settings: Settings, header: str) -> None:
    changed = False
    for outcome in hooks(settings, h.systemd_tmpfilesd_managed_dir, settings=settings):
        for name, managed_dir in outcome:
            if should_manage_conf(settings.run_prefix, managed_dir):
                content = systemd.template("pglift-tmpfiles.d.conf").format(
                    path=managed_dir
                )
                if install(name, util.with_header(content, header), settings):
                    changed = True
    if changed:
        assert settings.systemd
        await systemd_tmpfiles_create(settings.systemd)


@hookimpl
async def site_configure_uninstall(settings: Settings) -> None:
    for outcome in hooks(settings, h.systemd_tmpfilesd_managed_dir, settings=settings):
        for name, _ in outcome:
            uninstall(name, settings)


@hookimpl
def site_configure_check(settings: Settings, log: bool) -> Iterator[bool]:
    for outcome in hooks(settings, h.systemd_tmpfilesd_managed_dir, settings=settings):
        for name, managed_dir in outcome:
            if should_manage_conf(settings.run_prefix, managed_dir):
                if not (i := installed(name, settings)) and log:
                    logger.error("missing systemd-tmpfiles configuration '%s'", name)
                yield i


@hookimpl
def site_configure_list(settings: Settings) -> Iterator[Path]:
    for outcome in hooks(settings, h.systemd_tmpfilesd_managed_dir, settings=settings):
        for name, managed_dir in outcome:
            if should_manage_conf(settings.run_prefix, managed_dir):
                yield config_path(name, settings)

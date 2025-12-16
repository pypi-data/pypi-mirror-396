# SPDX-FileCopyrightText: 2021 Dalibo
#
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

import configparser
import json
from pathlib import Path, PurePath

import pydantic
from pgtoolkit.conf import Configuration

from .. import async_hook, deps, exceptions, h, util
from ..models import PostgreSQLInstance
from ..settings import Settings, _temboard
from ..system import FileSystem, svc
from ..task import task
from .models import interface as i
from .models import system as s

logger = util.get_logger(__name__)


def available(settings: Settings) -> _temboard.Settings | None:
    return settings.temboard


def get_settings(settings: Settings) -> _temboard.Settings:
    """Return settings for temboard

    Same as `available` but assert that settings are not None.
    Should be used in a context where settings for the plugin are surely
    set (for example in hookimpl).
    """
    assert settings.temboard is not None
    return settings.temboard


@deps.use
def enabled(
    qualname: str, settings: _temboard.Settings, *, fs: FileSystem = deps.Auto
) -> bool:
    return fs.exists(_configpath(qualname, settings))


def _args(execpath: PurePath, configpath: PurePath) -> list[str]:
    return [str(execpath), "--config", str(configpath)]


def _configpath(qualname: str, settings: _temboard.Settings) -> Path:
    return Path(str(settings.configpath).format(name=qualname))


def _homedir(qualname: str, settings: _temboard.Settings) -> Path:
    return Path(str(settings.home).format(name=qualname))


def _pidfile(qualname: str, settings: _temboard.Settings) -> Path:
    return Path(str(settings.pid_file).format(name=qualname))


def _logfile(qualname: str, settings: _temboard.Settings) -> Path:
    return settings.logpath / f"temboard_agent_{qualname}.log"


@deps.use
def config_var(
    configpath: Path, *, name: str, section: str, fs: FileSystem = deps.Auto
) -> str:
    """Return temboardagent configuration value for given 'name' in 'section'."""
    cp = configparser.ConfigParser()
    try:
        with fs.open(configpath) as f:
            cp.read_file(f)
    except FileNotFoundError as e:
        raise exceptions.FileNotFoundError(
            f"temboard agent configuration file {configpath} not found: {e}"
        ) from e
    for sname, items in cp.items():
        if sname != section:
            continue
        try:
            return items[name]
        except KeyError:
            pass
    raise exceptions.ConfigurationError(
        configpath, f"{name} not found in {section} section"
    )


def port(qualname: str, settings: _temboard.Settings) -> int:
    configpath = _configpath(qualname, settings)
    return int(config_var(configpath, name="port", section="temboard"))


def password(qualname: str, settings: _temboard.Settings) -> str | None:
    configpath = _configpath(qualname, settings)
    try:
        return config_var(configpath, name="password", section="postgresql")
    except exceptions.ConfigurationError:
        return None


def system_lookup(
    name: str, settings: _temboard.Settings, *, warn: bool = True
) -> s.Service | None:
    try:
        p_ = port(name, settings)
        passwd_ = password(name, settings)
    except exceptions.FileNotFoundError as exc:
        if warn:
            logger.warning(
                "failed to read temboard-agent configuration %s: %s", name, exc
            )
        return None
    else:
        password_ = None
        if passwd_ is not None:
            password_ = pydantic.SecretStr(passwd_)
        return s.Service(name=name, settings=settings, port=p_, password=password_)


@task
@deps.use
async def setup(
    instance: PostgreSQLInstance,
    service: i.Service,
    settings: _temboard.Settings,
    instance_config: Configuration,
    *,
    fs: FileSystem = deps.Auto,
) -> None:
    """Setup temboardAgent"""
    configpath = _configpath(instance.qualname, settings)

    password_: str | None = None
    if not fs.exists(configpath):
        if service.password:
            password_ = service.password.get_secret_value()
    else:
        # Get the password from config file
        password_ = password(instance.qualname, settings)

    cp = configparser.ConfigParser()
    cp["temboard"] = {
        "port": str(service.port),
        "plugins": json.dumps(settings.plugins),
        "ssl_cert_file": str(settings.certificate.cert),
        "ssl_key_file": str(settings.certificate.key),
        "home": str(_homedir(instance.qualname, settings)),
        "ui_url": str(settings.ui_url),
        "signing_public_key": str(settings.signing_key),
    }
    if settings.certificate.ca_cert:
        cp["temboard"]["ssl_ca_cert_file"] = str(settings.certificate.ca_cert)

    cp["postgresql"] = {
        "user": settings.role,
        "instance": instance.qualname,
    }
    if "port" in instance_config:
        cp["postgresql"]["port"] = str(instance_config["port"])
    if "unix_socket_directories" in instance_config:
        pghost = instance_config.unix_socket_directories.split(",")[0]  # type: ignore[union-attr]
        cp["postgresql"]["host"] = pghost
    if password_:
        cp["postgresql"]["password"] = password_
    cp["logging"] = {
        "method": settings.logmethod,
        "level": settings.loglevel,
    }
    if settings.logmethod == "file":
        cp["logging"]["destination"] = str(_logfile(instance.qualname, settings))

    name = instance.qualname
    needs_restart = False
    if svc := system_lookup(name, settings, warn=False):
        cp_actual = configparser.ConfigParser()
        with fs.open(configpath) as f:
            cp_actual.read_file(f)
        if cp != cp_actual:
            logger.info("reconfiguring temboard agent %s", name)
            with fs.open(configpath, "w") as configfile:
                cp.write(configfile)
            needs_restart = True
    else:
        logger.info("configuring temboard agent %s", name)
        fs.mkdir(configpath.parent, mode=0o700, exist_ok=True, parents=True)
        fs.touch(configpath, mode=0o600)
        with fs.open(configpath, "w") as configfile:
            cp.write(configfile)

        homedir = _homedir(name, settings)
        fs.mkdir(homedir, mode=0o700, exist_ok=True, parents=True)

        pidfile = _pidfile(name, settings)
        fs.mkdir(pidfile.parent, mode=0o700, exist_ok=True, parents=True)

        svc = system_lookup(name, settings)
        assert svc is not None

    await async_hook(
        instance._settings,
        h.enable_service,
        settings=instance._settings,
        service=s.service_name,
        name=instance.qualname,
    )

    if needs_restart:
        await restart(instance._settings, svc)


@setup.revert
@deps.use
async def revert_setup(
    instance: PostgreSQLInstance,
    settings: _temboard.Settings,
    *,
    fs: FileSystem = deps.Auto,
) -> None:
    """Un-setup temboard"""
    logger.info("deconfiguring temboard argent")
    fs.unlink(_configpath(instance.qualname, settings), missing_ok=True)
    fs.unlink(_pidfile(instance.qualname, settings), missing_ok=True)
    fs.unlink(_logfile(instance.qualname, settings), missing_ok=True)
    homedir = _homedir(instance.qualname, settings)
    if fs.exists(homedir):
        util.rmtree(homedir)
    await async_hook(
        instance._settings,
        h.disable_service,
        settings=instance._settings,
        service=s.service_name,
        name=instance.qualname,
        now=True,
    )


async def start(
    settings: Settings, service: s.Service, *, foreground: bool = False
) -> None:
    logger.info("starting temboard-agent %s", service.name)
    await svc.start(settings, service, foreground=foreground)


async def stop(settings: Settings, service: s.Service) -> None:
    logger.info("stopping temboard-agent %s", service.name)
    await svc.stop(settings, service)


async def restart(settings: Settings, service: s.Service) -> None:
    logger.info("restarting temboard-agent %s", service.name)
    await svc.restart(settings, service)

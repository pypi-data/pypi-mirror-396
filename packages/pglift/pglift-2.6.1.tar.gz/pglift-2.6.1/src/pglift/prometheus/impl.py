# SPDX-FileCopyrightText: 2021 Dalibo
#
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

import re
import shlex
import urllib.parse
from pathlib import Path
from typing import Any
from urllib.parse import quote

import psycopg
import psycopg.conninfo
import pydantic
from dotenv import dotenv_values
from pgtoolkit.conf import Configuration

from .. import async_hook, deps, exceptions, h, util
from ..models import PostgreSQLInstance, interface
from ..settings import Settings, _prometheus
from ..system import FileSystem, svc
from ..task import task
from .models import interface as i
from .models import system as s

logger = util.get_logger(__name__)


def available(settings: Settings) -> _prometheus.Settings | None:
    return settings.prometheus


def get_settings(settings: Settings) -> _prometheus.Settings:
    """Return settings for prometheus

    Same as `available` but assert that settings are not None.
    Should be used in a context where settings for the plugin are surely
    set (for example in hookimpl).
    """
    assert settings.prometheus is not None
    return settings.prometheus


@deps.use
def enabled(
    qualname: str, settings: _prometheus.Settings, *, fs: FileSystem = deps.Auto
) -> bool:
    return fs.exists(_configpath(qualname, settings))


def _configpath(qualname: str, settings: _prometheus.Settings) -> Path:
    return Path(str(settings.configpath).format(name=qualname))


@deps.use
def _config(path: Path, *, fs: FileSystem = deps.Auto) -> s.Config:
    if not fs.exists(path):
        raise exceptions.FileNotFoundError(
            f"postgres_exporter configuration file {path} not found"
        )
    with fs.open(path) as f:
        # Might emit a WARNING log message, from 'dotenv.main' logger.
        variables = dotenv_values(stream=f)
    values = {k: v for k, v in variables.items() if v is not None}
    return s.Config(values=values, path=path)


listen_address_rgx = re.compile(r"--web\.listen-address[ =]([^ ]+)")


def _args(execpath: Path, config: s.Config) -> list[str]:
    varname = "POSTGRES_EXPORTER_OPTS"
    opts = config[varname]
    try:
        args = shlex.split(opts)
    except ValueError as e:
        raise exceptions.ConfigurationError(
            config.path, f"malformatted {varname} parameter: {opts!r}"
        ) from e
    la_varname = "PG_EXPORTER_WEB_LISTEN_ADDRESS"
    try:
        listen_address = config[la_varname]
    except exceptions.ConfigurationError:
        pass
    else:
        if listen_address_rgx.search(opts):
            raise exceptions.ConfigurationError(
                config.path,
                f"listen address appears to be defined both in {varname} and {la_varname}",
            )
        args += ["--web.listen-address", listen_address]
    return [str(execpath)] + args


def _env(config: s.Config) -> dict[str, str]:
    return {
        k: v
        for k, v in config.values.items()
        if v is not None
        and k not in ("POSTGRES_EXPORTER_OPTS", "PG_EXPORTER_WEB_LISTEN_ADDRESS")
    }


def _pidfile(qualname: str, settings: _prometheus.Settings) -> Path:
    return Path(str(settings.pid_file).format(name=qualname))


def port(config: s.Config) -> int:
    """Return postgres_exporter port read from configuration."""
    listen_address: str | None = None
    varname = "POSTGRES_EXPORTER_OPTS"
    try:
        opts = config[varname]
    except exceptions.ConfigurationError:
        pass
    else:
        if m := listen_address_rgx.search(opts):
            listen_address = m.group(1)
    if listen_address is None:
        la_varname = "PG_EXPORTER_WEB_LISTEN_ADDRESS"
        try:
            listen_address = config[la_varname]
        except exceptions.ConfigurationError:
            raise exceptions.ConfigurationError(
                config.path,
                f"listen-address not found in {varname} or {la_varname}",
            ) from None
        varname = la_varname
    try:
        _, value = listen_address.split(":", 1)
    except ValueError as e:
        raise exceptions.ConfigurationError(
            config.path, f"malformatted {varname} parameter"
        ) from e
    return int(value.strip())


def password(config: s.Config) -> pydantic.SecretStr | None:
    """Return postgres_exporter dsn password read from configuration."""
    varname = "DATA_SOURCE_NAME"
    dsn = config[varname]
    try:
        conninfo = psycopg.conninfo.conninfo_to_dict(dsn)
    except psycopg.ProgrammingError as e:
        raise exceptions.ConfigurationError(
            config.path, f"malformatted {varname} parameter"
        ) from e
    if (value := conninfo.get("password")) is not None:
        assert isinstance(value, str)
        return pydantic.SecretStr(value)
    return None


def make_uri(
    *,
    user: str = "",
    password: str = "",
    port: str = "5432",
    dbname: str = "",
    **kw: Any,
) -> str:
    """Return a libpq compatible uri for the given dsn object

    Note: key=value form DSN doesn't work with a unix socket host.
    Also for socket hosts, the host must be given in the uri params
    (after '?').

    >>> make_uri(**{"host": "/socket/path", "dbname": "somedb"})
    'postgresql://:5432/somedb?host=%2Fsocket%2Fpath'
    >>> make_uri(**{"host": "/socket/path"})
    'postgresql://:5432?host=%2Fsocket%2Fpath'
    >>> make_uri(
    ...     **{
    ...         "host": "/socket/path",
    ...         "user": "someone",
    ...         "dbname": "somedb",
    ...         "connect_timeout": "10",
    ...         "password": "secret",
    ...     }
    ... )
    'postgresql://someone:secret@:5432/somedb?host=%2Fsocket%2Fpath&connect_timeout=10'
    >>> make_uri(
    ...     **{
    ...         "host": "/socket/path",
    ...         "user": "someone",
    ...         "dbname": "somedb",
    ...         "password": "secret@!",
    ...     }
    ... )
    'postgresql://someone:secret%40%21@:5432/somedb?host=%2Fsocket%2Fpath'
    """
    userspec = user
    userspec += f":{quote(password)}" if password else ""
    userspec += "@" if userspec else ""
    netloc = f"{userspec}:{port}"
    query = urllib.parse.urlencode(kw)
    return urllib.parse.urlunsplit(("postgresql", netloc, dbname, query, None))


def system_lookup(
    name: str, settings: _prometheus.Settings, *, warn: bool = True
) -> s.Service | None:
    try:
        config = _config(_configpath(name, settings))
    except (exceptions.FileNotFoundError, exceptions.ConfigurationError) as exc:
        if warn:
            logger.warning(
                "failed to read postgres_exporter configuration %s: %s", name, exc
            )
        return None
    return s.Service(
        name=name, settings=settings, port=port(config), password=password(config)
    )


def exists(name: str, settings: _prometheus.Settings) -> bool:
    return system_lookup(name, settings, warn=False) is not None


@task
@deps.use
async def setup(
    name: str,
    settings: Settings,
    prometheus_settings: _prometheus.Settings,
    *,
    dsn: str = "",
    password: pydantic.SecretStr | None = None,
    port: int = i.default_port,
    fs: FileSystem = deps.Auto,
) -> s.Service:
    """Set up a Prometheus postgres_exporter service for an instance.

    :param name: a (locally unique) name for the service.
    :param dsn: connection info string to target instance.
    :param password: connection password.
    :param port: TCP port for the web interface and telemetry of postgres_exporter.
    """
    uri = make_uri(
        **psycopg.conninfo.conninfo_to_dict(  # type: ignore[arg-type]
            dsn, password=password.get_secret_value() if password is not None else None
        )
    )
    opts = " ".join(["--web.listen-address", f":{port}", "--log.level", "info"])
    config = [
        f"DATA_SOURCE_NAME={uri}",
        f"POSTGRES_EXPORTER_OPTS={opts!r}",
    ]

    configpath = _configpath(name, prometheus_settings)
    needs_restart = False
    if service := system_lookup(name, prometheus_settings, warn=False):
        if fs.read_text(configpath).splitlines() != config:
            logger.info("reconfiguring Prometheus postgres_exporter %s", name)
            fs.write_text(configpath, "\n".join(config))
            needs_restart = True
    else:
        logger.info("configuring Prometheus postgres_exporter %s", name)
        fs.mkdir(configpath.parent, mode=0o750, exist_ok=True, parents=True)
        fs.touch(configpath, mode=0o600)
        fs.write_text(configpath, "\n".join(config))
        service = system_lookup(name, prometheus_settings)
        assert service is not None

    await async_hook(
        settings, h.enable_service, settings=settings, service=s.service_name, name=name
    )

    if needs_restart:
        await restart(settings, service)
    return service


@setup.revert
@deps.use
async def revert_setup(
    name: str,
    settings: Settings,
    prometheus_settings: _prometheus.Settings,
    *,
    fs: FileSystem = deps.Auto,
) -> None:
    logger.info("deconfiguring Prometheus postgres_exporter %s", name)
    await async_hook(
        settings,
        h.disable_service,
        settings=settings,
        service=s.service_name,
        name=name,
        now=True,
    )
    fs.unlink(_configpath(name, prometheus_settings), missing_ok=True)


async def start(
    settings: Settings, service: s.Service, *, foreground: bool = False
) -> None:
    logger.info("starting Prometheus postgres_exporter %s", service.name)
    await svc.start(settings, service, foreground=foreground)


async def stop(settings: Settings, service: s.Service) -> None:
    logger.info("stopping Prometheus postgres_exporter %s", service.name)
    await svc.stop(settings, service)


async def restart(settings: Settings, service: s.Service) -> None:
    logger.info("restarting Prometheus postgres_exporter %s", service.name)
    await svc.restart(settings, service)


async def apply(
    postgres_exporter: i.PostgresExporter,
    settings: Settings,
    prometheus_settings: _prometheus.Settings,
) -> interface.ApplyResult:
    """Apply state described by specified interface model as a postgres_exporter
    service for a non-local instance.

    :raises exceptions.InstanceStateError: if the target instance exists on
    """
    try:
        PostgreSQLInstance.from_qualname(postgres_exporter.name, settings)
    except (ValueError, exceptions.InstanceNotFound):
        pass
    else:
        raise exceptions.InstanceStateError(
            f"instance {postgres_exporter.name!r} exists locally"
        )

    exists = enabled(postgres_exporter.name, prometheus_settings)
    if postgres_exporter.state == "absent":
        await drop(settings, postgres_exporter.name)
        return interface.ApplyResult(change_state="dropped" if exists else None)
    else:
        service = await setup(
            postgres_exporter.name,
            settings,
            prometheus_settings,
            dsn=postgres_exporter.dsn,
            password=postgres_exporter.password,
            port=postgres_exporter.port,
        )
        if postgres_exporter.state == "started":
            await start(settings, service)
        elif postgres_exporter.state == "stopped":
            await stop(settings, service)
        return interface.ApplyResult(
            change_state="created" if not exists else "changed"
        )


async def drop(settings: Settings, name: str) -> None:
    """Remove a postgres_exporter service."""
    logger.info("dropping postgres_exporter service '%s'", name)
    prometheus_settings = get_settings(settings)
    if (service := system_lookup(name, prometheus_settings)) is None:
        logger.warning("no postgres_exporter service '%s' found", name)
        return
    await stop(settings, service)
    await revert_setup(name, settings, prometheus_settings)


@deps.use
async def setup_local(
    instance: PostgreSQLInstance,
    service: i.Service,
    settings: _prometheus.Settings,
    instance_config: Configuration,
    *,
    fs: FileSystem = deps.Auto,
) -> None:
    """Setup Prometheus postgres_exporter for a local instance."""
    rolename = settings.role
    dsn = ["dbname=postgres"]
    if "port" in instance_config:
        dsn.append(f"port={instance_config.port}")
    if host := instance_config.get("unix_socket_directories"):
        dsn.append(f"host={host}")
    dsn.append(f"user={rolename}")
    if not instance_config.get("ssl", False):
        dsn.append("sslmode=disable")

    configpath = _configpath(instance.qualname, settings)
    password_: pydantic.SecretStr | None = None
    if service.password:
        password_ = service.password
    elif fs.exists(configpath):
        # Get the password from config file
        config = _config(configpath)
        password_ = password(config)

    await setup(
        instance.qualname,
        instance._settings,
        settings,
        dsn=" ".join(dsn),
        password=password_,
        port=service.port,
    )

# SPDX-FileCopyrightText: 2021 Dalibo
#
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

import asyncio
import logging
import socket
import ssl
import subprocess
import tempfile
import time
import urllib.parse
import warnings
from collections.abc import Iterator
from contextlib import contextmanager
from functools import partial
from pathlib import Path, PurePath
from typing import IO, Any, Literal

import httpx
import pgtoolkit.conf as pgconf
import tenacity
import yaml
from pydantic_core import to_jsonable_python

from .. import conf, deps, exceptions, postgresql, types, ui, util
from ..models import PostgreSQLInstance, interface
from ..models.system import check_instance
from ..settings import Settings, _patroni
from ..system import Command, FileSystem, svc
from ..task import task
from .models import Patroni, build
from .models import interface as i
from .models import system as s

logger = util.get_logger(__name__)


@util.cache
def template(*args: str) -> str:
    logger.debug("loading %s template", util.joinpath(*args))
    return util.template("patroni", *args)


def available(settings: Settings) -> _patroni.Settings | None:
    return settings.patroni


def get_settings(settings: Settings) -> _patroni.Settings:
    """Return settings for patroni

    Same as `available` but assert that settings are not None.
    Should be used in a context where settings for the plugin are surely
    set (for example in hookimpl).
    """
    assert settings.patroni is not None
    return settings.patroni


@deps.use
def enabled(
    qualname: str, settings: _patroni.Settings, *, fs: FileSystem = deps.Auto
) -> bool:
    return fs.exists(_configpath(qualname, settings))


def _configpath(qualname: str, settings: _patroni.Settings) -> Path:
    return Path(str(settings.configpath).format(name=qualname))


def logdir(qualname: str, settings: _patroni.Settings) -> Path:
    return settings.logpath / qualname


def validate_config(content: str, settings: _patroni.Settings) -> None:
    with tempfile.NamedTemporaryFile("w", suffix=".yaml") as f:
        f.write(content)
        f.seek(0)
        try:
            subprocess.run(  # nosec B603
                [str(settings.execpath), "--validate-config", f.name],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                check=True,
                text=True,
            )
        except subprocess.CalledProcessError as e:
            msg = "invalid Patroni configuration: %s"
            if settings.enforce_config_validation:
                raise exceptions.ConfigurationError(
                    PurePath(f.name), msg % e.stdout.strip()
                ) from e
            logging.warning(msg, e.stdout.strip())


@deps.use
def write_config(
    name: str,
    config: Patroni,
    settings: _patroni.Settings,
    *,
    validate: bool = False,
    fs: FileSystem = deps.Auto,
) -> None:
    """Write Patroni YAML configuration to disk after validation."""
    content = config.yaml()
    if validate:
        validate_config(content, settings)
    path = _configpath(name, settings)
    fs.mkdir(path.parent, mode=0o750, exist_ok=True, parents=True)
    fs.write_text(path, content)
    fs.chmod(path, 0o600)


async def maybe_backup_config(service: s.Service) -> None:
    """Make a backup of Patroni configuration for 'qualname' instance
    alongside the original file, if 'node' is the last member in 'cluster'
    or if the Patroni API is unreachable.
    """
    msg = "saving Patroni configuration file to %s; see %s for more information"
    doc = "https://pglift.readthedocs.io/en/latest/user/ops/ha.html#cluster-removal"

    # if API is unreachable, backup the configuration,
    if not await check_api_status(service.patroni):
        backup = _backup_config(service)
        logger.warning(msg, backup, doc)
        return

    # Otherwise check if this is the last node of the cluster before backup
    try:
        members = await cluster_members(service.patroni)
    except httpx.HTTPError as e:
        logger.error("failed to retrieve cluster members: %s", e)
    else:
        member_names = [m.name for m in members]
        node, cluster = service.node, service.cluster
        if not any(m for m in member_names if m != node):
            logger.debug(
                "members of cluster '%s': %s (node is '%s')",
                cluster,
                ", ".join(member_names),
                node,
            )
            backup = _backup_config(service)
            msg = "'%s' appears to be the last member of cluster '%s', " + msg
            logger.warning(msg, node, cluster, backup, doc)


@deps.use
def _backup_config(service: s.Service, *, fs: FileSystem = deps.Auto) -> Path:
    node, cluster, qualname = service.node, service.cluster, service.name
    configpath = _configpath(qualname, service.settings)
    backupname = f"{cluster}-{node}-{time.time()}"
    backuppath = configpath.parent / f"{backupname}.yaml"
    fs.write_text(
        backuppath,
        f"# Backup of Patroni configuration for instance {qualname!r}\n"
        + fs.read_text(configpath),
    )
    pgpass = build.pgpass(qualname, service.settings.postgresql)
    if fs.exists(pgpass):
        fs.write_text(configpath.parent / f"{backupname}.pgpass", fs.read_text(pgpass))
    return backuppath


def postgresql_changes(
    before: build.PostgreSQL | None,
    parameters_before: dict[str, Any] | None,
    after: build.PostgreSQL,
    parameters_after: dict[str, Any],
    /,
) -> types.ConfigChanges:
    """Return changes to PostgreSQL parameters between two 'postgresql'
    section of a Patroni configuration.
    """
    # Suppress serialization effects through a "round-trip".
    config_before: dict[str, Any] = {}
    if parameters_before:
        config_before |= to_jsonable_python(parameters_before, round_trip=True)
    if before:
        config_before |= {"port": types.address_port(before.listen)}
    config_after = to_jsonable_python(parameters_after, round_trip=True)
    config_after |= {"port": types.address_port(after.listen)}
    return conf.changes(config_before, config_after)


async def api_request(
    patroni: Patroni, method: str, path: str, **kwargs: Any
) -> httpx.Response:
    protocol = "http"
    verify: bool | ssl.SSLContext = True
    if patroni.restapi.cafile:
        protocol = "https"
        verify = ssl.create_default_context(cafile=str(patroni.restapi.cafile))
    if patroni.restapi.certfile and patroni.restapi.keyfile:
        protocol = "https"
        if not isinstance(verify, ssl.SSLContext):
            verify = ssl.create_default_context()
        verify.load_cert_chain(
            str(patroni.restapi.certfile), str(patroni.restapi.keyfile)
        )
    auth: httpx.BasicAuth | None = None
    if (b_auth := patroni.restapi.authentication) is not None:
        auth = httpx.BasicAuth(
            username=b_auth.username, password=b_auth.password.get_secret_value()
        )
    url = urllib.parse.urlunparse((protocol, patroni.restapi.listen, path, "", "", ""))
    async with httpx.AsyncClient(auth=auth, verify=verify) as client:
        try:
            r = await client.request(method, url, **kwargs)
        except httpx.ConnectError as e:
            logger.error("failed to connect to REST API server for %s: %s", patroni, e)
            await check_api_status(patroni)
            raise exceptions.SystemError(
                f"REST API server for {patroni} is unreachable; is the instance running?"
            ) from e
    r.raise_for_status()
    return r


@deps.use
def setup(
    instance: PostgreSQLInstance,
    manifest: interface.Instance,
    service: i.Service,
    settings: _patroni.Settings,
    configuration: pgconf.Configuration,
    *,
    fs: FileSystem = deps.Auto,
    _template: str | None = None,
) -> Patroni:
    """Return a fresh Patroni object for instance."""
    logger.info("setting up Patroni service")
    logpath = logdir(instance.qualname, settings)
    s = instance._settings
    dcs = settings.etcd.version
    templated_conf: dict[str, Any] = yaml.safe_load(
        template("patroni.yaml") if _template is None else _template
    )
    if not isinstance(templated_conf, dict):
        raise exceptions.SettingsError("invalid patroni.yaml template")

    is_local_pg_params = settings.configuration_mode.parameters == "local"
    pg_params = build.parameters_managed(configuration, {}, is_local_pg_params)

    managed_conf: dict[str, Any] = {
        "scope": service.cluster,
        "name": service.node,
        "log": build.Log(dir=logpath),
        "bootstrap": build.bootstrap(
            settings,
            postgresql.initdb_options(manifest, s.postgresql),
            hba=(
                None
                if settings.configuration_mode.auth == "local"
                else postgresql.pg_hba(manifest, s).splitlines()
            ),
            pg_ident=(
                None
                if settings.configuration_mode.auth == "local"
                else postgresql.pg_ident(manifest, s).splitlines()
            ),
            parameters=None if is_local_pg_params else pg_params,
        ),
        dcs: build.etcd(service.etcd, settings),
        "postgresql": build.postgresql(
            instance,
            manifest,
            configuration,
            service.postgresql,
            None if not is_local_pg_params else pg_params,
        ),
        "restapi": build.restapi(service.restapi, settings.restapi),
        "ctl": settings.ctl,
    }
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", DeprecationWarning)
        if settings.watchdog is not None:
            managed_conf |= {"watchdog": settings.watchdog}

    conf = util.deep_update(templated_conf, managed_conf)

    patroni = Patroni.model_validate(conf)

    fs.mkdir(logpath, exist_ok=True, parents=True)

    return patroni


def update(
    actual: Patroni,
    /,
    service: i.Service,
    settings: _patroni.Settings,
    configuration: pgconf.Configuration,
    parameters: dict[str, Any] | None = None,
) -> Patroni:
    """Return a Patroni object, updated from 'actual' and instance data."""
    logger.info("updating Patroni service")
    args = actual.model_dump()
    args["postgresql"] = _update_postgresql_args(
        actual.postgresql, service.postgresql, configuration, parameters
    )
    if service.restapi:
        args["restapi"] = util.deep_update(
            actual.restapi.model_dump(), service.restapi.model_dump()
        )
    if service.etcd:
        dcs = settings.etcd.version
        args[dcs] |= build.export_model(service.etcd)
    patroni = Patroni.model_validate(args)

    return patroni


def update_hba(
    actual: Patroni, qualname: str, /, settings: _patroni.Settings, hba: list[str]
) -> None:
    """Update the pg_hba section of a Patroni configuration and write the new
    configuration.
    """
    args = actual.model_dump(exclude={"postgresql"}) | {
        "postgresql": actual.postgresql.model_dump(exclude={"pg_hba"}) | {"pg_hba": hba}
    }
    patroni = Patroni.model_validate(args)
    write_config(qualname, patroni, settings)


def _update_postgresql_args(
    value: build.PostgreSQL,
    postgresql_options: i.PostgreSQL | None,
    configuration: pgconf.Configuration,
    parameters: dict[str, Any] | None,
) -> dict[str, Any]:
    """Return a dict to construct a build.PostgreSQL object with values
    updated from Patroni-specific PostgreSQL options and general PostgreSQL
    configuration
    """
    # remove the parameters, they will be re-added (if needed - when not None)
    # by postgresql_managed()
    base = value.model_dump(exclude={"parameters"})
    updates = build.postgresql_managed(
        configuration, postgresql_options, parameters=parameters
    )

    return util.deep_update(base, updates)  # type: ignore[arg-type]


@deps.use
def upgrade(
    instance: PostgreSQLInstance,
    manifest: interface.Instance,
    actual: Patroni,
    /,
    postgresql_options: i.PostgreSQL | None,
    settings: _patroni.Settings,
    configuration: pgconf.Configuration,
    parameters: dict[str, Any] | None = None,
    *,
    fs: FileSystem = deps.Auto,
) -> Patroni:
    """Return a Patroni object, upgraded from 'actual' and instance data."""
    assert manifest.upgrading_from
    # Mapping of file operations to perform at exit; target path -> origin
    # path, if target *file* needs to be copied or None, if target *directory*
    # needs be created.
    file_ops: dict[Path, Path | None] = {}

    logger.info("upgrading Patroni service")
    postgresql_args = _update_postgresql_args(
        actual.postgresql, postgresql_options, configuration, parameters
    ) | build.postgresql_upgrade_from(actual.postgresql, instance, manifest)
    args = actual.model_dump(exclude={"postgresql"}) | {"postgresql": postgresql_args}

    if (log := actual.log) and log.dir:
        logpath = logdir(instance.qualname, settings)
        args["log"] = log.model_dump(exclude={"dir"}) | {"dir": logpath}
        file_ops[logpath] = None

    if actual.postgresql.pgpass:
        assert args["postgresql"]["pgpass"]
        file_ops[args["postgresql"]["pgpass"]] = actual.postgresql.pgpass

    dynamic_config_name = "patroni.dynamic.json"
    file_ops[instance.datadir / dynamic_config_name] = (
        manifest.upgrading_from.datadir / dynamic_config_name
    )

    patroni = Patroni.model_validate(args)

    for target, origin in file_ops.items():
        if origin is None:
            logger.debug("creating %s directory", target)
            fs.mkdir(target, exist_ok=True, parents=True)
        elif fs.exists(origin):
            fs.mkdir(target.parent, exist_ok=True, parents=True)
            logger.debug("copying %s to %s", origin, target)
            fs.copy(origin, target)
    return patroni


@task(title="bootstrapping PostgreSQL with Patroni")
async def init(
    instance: PostgreSQLInstance, patroni: Patroni, service: s.Service
) -> None:
    """Call patroni for bootstrap.

    Then wait for Patroni to bootstrap by checking that (1) the postgres
    instance exists, (2) that it's up and running and, (3) that Patroni REST
    API is ready.

    At each retry, log new lines found in Patroni and PostgreSQL logs to our
    logger.
    """

    @tenacity.retry(
        retry=tenacity.retry_if_exception_type(exceptions.FileNotFoundError),
        wait=tenacity.wait_exponential(multiplier=1, min=1, max=10),
        stop=tenacity.stop_after_attempt(5),
        before_sleep=tenacity.before_sleep_log(logger, logging.DEBUG),
        reraise=True,
    )
    @deps.use
    def wait_logfile(
        instance: PostgreSQLInstance,
        settings: _patroni.Settings,
        *,
        fs: FileSystem = deps.Auto,
    ) -> Path:
        logf = logfile(instance.qualname, settings)
        if not fs.exists(logf):
            raise exceptions.FileNotFoundError("Patroni log file not found (yet)")
        logger.debug("Patroni log file found %s", logf)
        return logf

    @contextmanager
    @deps.use
    def postgres_logfile(
        instance: PostgreSQLInstance,
        position: int,
        *,
        fs: FileSystem = deps.Auto,
    ) -> Iterator[IO[str] | None]:
        try:
            postgres_logpath = next(postgresql.logfile(instance, timeout=0))
        except exceptions.FileNotFoundError:
            # File current_logfiles not found
            yield None
            return
        logger.debug("reading current PostgreSQL logs from %s", postgres_logpath)
        try:
            with fs.open(postgres_logpath) as f:
                f.seek(position)
                yield f
        except OSError as e:
            # Referenced file not created yet or gone?
            logger.warning(
                "failed to open PostgreSQL log file %s (%s)", postgres_logpath, e
            )
            yield None
            return

    def log_process(f: IO[str], level: int, *, execpath: PurePath) -> int:
        for line in f:
            logger.log(level, "%s: %s", execpath, line.rstrip())
        return f.tell()

    await start(instance._settings, service, foreground=False)

    patroni_settings = service.settings
    logger.debug("waiting for Patroni log file creation")
    logf = wait_logfile(instance, patroni_settings)
    log_patroni = partial(log_process, execpath=patroni_settings.execpath)
    log_postgres = partial(
        log_process, execpath=postgresql.bindir(instance) / "postgres"
    )

    retry_ctrl = tenacity.AsyncRetrying(
        retry=(
            tenacity.retry_if_exception_type(exceptions.InstanceNotFound)
            | tenacity.retry_if_exception_type(exceptions.InstanceStateError)
            | tenacity.retry_if_exception_type(httpx.HTTPError)
        ),
        # Retry indefinitely (no 'stop' option), waiting exponentially until
        # the 10s delay gets reached (and then waiting fixed).
        wait=tenacity.wait_exponential(multiplier=1, min=1, max=10),
        before_sleep=tenacity.before_sleep_log(logger, logging.DEBUG),
    )

    logger.info("waiting for instance %s creation by Patroni", instance)

    with logstream(logf) as f:
        postgres_log_end = 0
        pginstance_created = False
        try:
            async for attempt in retry_ctrl:
                with attempt:
                    level = logging.DEBUG
                    if not await check_api_status(patroni):
                        level = logging.WARNING
                    log_patroni(f, level)

                    if not pginstance_created:
                        check_instance(instance)
                        pginstance_created = True
                        logger.info(
                            "PostgreSQL instance %s created by Patroni", instance
                        )

                    with postgres_logfile(instance, postgres_log_end) as postgres_logf:
                        if postgres_logf is not None:
                            postgres_log_end = log_postgres(postgres_logf, level)

                    if not await postgresql.is_ready(instance):
                        raise exceptions.InstanceStateError(f"{instance} not ready")

                    logger.debug("checking Patroni readiness")
                    await api_request(patroni, "GET", "readiness")

        except tenacity.RetryError as retry_error:
            if ui.confirm("Patroni failed to start, abort?", default=False):
                raise exceptions.Cancelled(
                    f"Patroni {instance} start cancelled"
                ) from retry_error.last_attempt.result()
        finally:
            if postgres_logf:
                postgres_logf.close()

    logger.info("instance %s successfully created by Patroni", instance)


@init.revert
async def revert_init(instance: PostgreSQLInstance, service: s.Service) -> None:
    """Call patroni for bootstrap."""
    await delete(instance._settings, service)


@deps.use
async def delete(
    settings: Settings, service: s.Service, *, fs: FileSystem = deps.Auto
) -> None:
    """Remove Patroni configuration for 'instance'."""
    await maybe_backup_config(service)
    await stop(settings, service)
    logger.info("deconfiguring Patroni service")
    fs.unlink(_configpath(service.name, service.settings), missing_ok=True)
    fs.unlink(build.pgpass(service.name, service.settings.postgresql), missing_ok=True)
    fs.unlink(logfile(service.name, service.settings), missing_ok=True)


async def start(
    settings: Settings,
    service: s.Service,
    *,
    foreground: bool = False,
) -> None:
    logger.info("starting Patroni %s", service.name)
    await svc.start(settings, service, foreground=foreground)


async def is_paused(patroni: Patroni) -> bool | None:
    """Determine if the Patroni cluster is in pause mode. Return None if the
    cluster pause mode cannot be retrieved (e.g., if the Patroni API is
    unreachable).
    """
    try:
        r = await api_request(patroni, "GET", path="/")
    except (httpx.HTTPError, exceptions.SystemError):
        logger.warning(
            "REST API is unreachable; could not determine if '%s' is in pause mode",
            patroni.name,
        )
        return None
    return r.json().get("pause", False) is True


async def stop(settings: Settings, service: s.Service) -> None:
    logger.info("stopping Patroni %s", service.name)
    if await is_paused(service.patroni):
        logger.info(
            "Patroni '%s' is in pause mode, PostgreSQL server will not be stopped",
            service.name,
        )
    await svc.stop(settings, service)
    logger.debug("waiting for Patroni %s REST API to terminate", service.name)
    await wait_api_down(service.patroni)
    logger.debug("Patroni %s REST API terminated", service.name)


async def restart(patroni: Patroni, timeout: int = 3) -> None:
    logger.info("restarting %s", patroni)
    await api_request(patroni, "POST", "restart", json={"timeout": timeout})


async def reload(patroni: Patroni) -> None:
    logger.info("reloading %s", patroni)
    await api_request(patroni, "POST", "reload")


async def cluster_members(patroni: Patroni) -> list[i.ClusterMember]:
    """Return the list of members of the Patroni cluster which 'instance' is member of."""
    r = await api_request(patroni, "GET", "cluster")
    return [i.ClusterMember(**item) for item in r.json()["members"]]


async def cluster_leader(patroni: Patroni) -> str | None:
    for m in await cluster_members(patroni):
        if m.role == "leader":
            return m.name
    return None


@deps.use
async def remove_cluster(service: s.Service, *, cmd: Command = deps.Auto) -> None:
    config = _configpath(service.name, service.settings)
    logger.info("removing '%s' cluster state from DCS", service.cluster)
    await cmd.run(
        [str(service.settings.ctlpath), "-c", str(config), "remove", service.cluster],
        check=True,
        input=f"{service.cluster}\nYes I am aware\n{service.node}\n",
    )


async def check_api_status(
    patroni: Patroni, *, logger: logging.Logger | None = logger
) -> bool:
    """Return True if the REST API of Patroni with 'name' is listening."""
    api_address = patroni.restapi.listen
    if logger:
        logger.debug("checking status of REST API for %s at %s", patroni, api_address)
    try:
        _, writer = await asyncio.open_connection(
            types.address_host(api_address),
            types.address_port(api_address),
            family=socket.AF_INET,
        )
        writer.close()
        await writer.wait_closed()
    except OSError as exc:
        if logger:
            logger.error(
                "REST API for %s not listening at %s: %s", patroni, api_address, exc
            )
        return False
    return True


@tenacity.retry(
    retry=tenacity.retry_if_exception_type(exceptions.Error),
    wait=tenacity.wait_fixed(1),
    before_sleep=tenacity.before_sleep_log(logger, logging.DEBUG),
)
async def wait_api_down(patroni: Patroni) -> None:
    if await check_api_status(patroni, logger=None):
        raise exceptions.Error("Patroni REST API still running")


@contextmanager
@deps.use
def logstream(logpath: Path, *, fs: FileSystem = deps.Auto) -> Iterator[IO[str]]:
    with fs.open(logpath) as f:
        yield f


def logfile(name: str, settings: _patroni.Settings) -> Path:
    return logdir(name, settings) / "patroni.log"


@deps.use
def logs(
    name: str, settings: _patroni.Settings, *, fs: FileSystem = deps.Auto
) -> Iterator[str]:
    logf = logfile(name, settings)
    if not fs.exists(logf):
        raise exceptions.FileNotFoundError(f"no Patroni logs found at {logf}")
    with logstream(logf) as f:
        yield from f


ConfigureOperationContext = (
    tuple[Literal["create", "convert"], None]
    | tuple[Literal["update", "upgrade"], Patroni]
)


def _configure_postgresql(
    settings: _patroni.Settings,
    configuration: pgconf.Configuration,
    instance: PostgreSQLInstance,
    manifest: interface.Instance,
    context: ConfigureOperationContext,
    parameters: dict[str, Any] | None = None,
) -> Patroni | None:
    service_manifest = manifest.service(i.Service)
    op, actual = context
    if op == "create":
        return None
    elif op == "convert":
        patroni = setup(instance, manifest, service_manifest, settings, configuration)
    elif op == "upgrade":
        assert actual is not None
        patroni = upgrade(
            instance,
            manifest,
            actual,
            service_manifest.postgresql,
            settings,
            configuration,
            parameters,
        )
    else:
        # Instance "alter".
        assert actual is not None
        patroni = update(actual, service_manifest, settings, configuration, parameters)
    # then write the configuration file
    write_config(instance.qualname, patroni, settings, validate=False)
    return patroni

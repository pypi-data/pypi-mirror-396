# SPDX-FileCopyrightText: 2021 Dalibo
#
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

import concurrent.futures
import getpass
import logging
import platform
import shutil
import socket
import subprocess
import typing
from collections.abc import AsyncIterator, Awaitable, Iterator, Mapping, Sequence
from datetime import datetime
from pathlib import Path
from textwrap import dedent
from typing import TYPE_CHECKING, Any, Protocol, TypeAlias, TypeVar

import pgtoolkit.conf as pgconf
import psycopg.conninfo
import pytest
import yaml
from anyio.pytest_plugin import FreePortFactory
from typing_extensions import assert_never

from pglift import (
    hook_monitoring,
    instances,
    manager,
    pgbackrest,
    plugin_manager,
    postgresql,
)
from pglift.backup import BACKUP_SERVICE_NAME, BACKUP_TIMER_NAME
from pglift.models import interface, system
from pglift.pgbackrest.models import system as pgbackrest_models
from pglift.postgresql import POSTGRESQL_SERVICE_NAME
from pglift.settings import (
    POSTGRESQL_VERSIONS,
    PostgreSQLVersion,
    Settings,
    _pgbackrest,
    _postgresql,
    _systemd,
)
from pglift.system import command, install
from pglift.types import local_host
from pglift.util import deep_update

from . import AuthType, PostgresLogger, cmd, execute
from .pgbackrest import (
    PgbackrestRepoHost,
    PgbackrestRepoHostSSH,
    PgbackrestRepoHostTLS,
    ServerSSH,
)
from .ssh import SSHKeys, add_to_known_hosts

if TYPE_CHECKING:
    from pglift.fixtures.etcd import Etcd
    from pglift.fixtures.types import CertFactory

try:
    default_pg_bindir_template, default_pg_version = (
        _postgresql._postgresql_bindir_version()
    )
except OSError as e:
    pytest.fail(str(e))


pytest_plugins = [
    "pglift.fixtures",
    "pglift.fixtures.functional",
]


def pytest_addoption(parser: Any) -> None:
    parser.addoption(
        "--pg-version",
        choices=POSTGRESQL_VERSIONS,
        default=default_pg_version,
        help="Run tests with specified PostgreSQL version (default: %(default)s)",
    )
    parser.addoption(
        "--pg-auth",
        choices=typing.get_args(AuthType),
        default="peer",
        help="Run tests with PostgreSQL authentication method (default: %(default)s)",
    )
    parser.addoption(
        "--surole-name",
        default="postgres",
        help="Run tests with a specific surole name",
    )
    parser.addoption(
        "--no-version-in-path-settings",
        action="store_true",
        default=False,
        help="Define postgresql.{datadir,waldir} setting without a '{version}' template variable",
    )
    parser.addoption(
        "--systemd",
        action="store_true",
        default=False,
        help="Run tests with systemd as service manager/tmpfiles manager/scheduler",
    )
    if shutil.which("pgbackrest") is not None:
        parser.addoption(
            "--pgbackrest-repo-host",
            choices=["tls", "ssh"],
            default=None,
            help="Use a dedicated repository host for pgbackrest",
        )


def pytest_report_header(config: Any) -> list[str]:
    pg_version = config.option.pg_version
    systemd = config.option.systemd
    pg_auth = config.option.pg_auth
    surole_name = config.option.surole_name
    pgbackrest_repo_host = config.getoption("pgbackrest_repo_host", False)
    no_version_in_path_settings = config.getoption("no_version_in_path_settings")
    return [
        f"postgresql: {pg_version}",
        f"auth method: {pg_auth}",
        f"version in path settings: {not no_version_in_path_settings}",
        f"surole name: {surole_name}",
        f"systemd: {systemd}",
        f"pgbackrest repo host: {pgbackrest_repo_host}",
    ]


def pytest_configure(config: Any) -> None:
    config.addinivalue_line(
        "markers", "standby: mark test as concerning standby instance"
    )


@pytest.fixture(scope="package")
def anyio_backend() -> str:
    return "asyncio"


@pytest.fixture(scope="package")
def logger() -> logging.Logger:
    testlogger = logging.getLogger("pglift-tests")
    testlogger.setLevel(logging.DEBUG)
    return testlogger


@pytest.fixture(scope="package", autouse=True)
def supervisor(systemd_requested: bool, logger: logging.Logger) -> Iterator[None]:
    """Supervisor fixture for background processes started by pglift to
    cleanup possible zombies.
    """
    if systemd_requested:
        yield
        return
    else:
        cmd.procs.clear()
        token = command.set(cmd)

        yield

        command.reset(token)

        for proc, args in cmd.procs:
            if proc.returncode is None:
                logger.warning("terminating zombie process %d: %s", proc.pid, args)
                try:
                    proc.terminate()
                except ProcessLookupError:
                    pass
            else:
                logger.debug(
                    "process %s: %s, exited with rc=%d", proc, args, proc.returncode
                )
            proc.wait()


@pytest.fixture(autouse=True)
def journalctl(systemd_requested: bool) -> Iterator[None]:
    journalctl = shutil.which("journalctl")
    if not systemd_requested or journalctl is None:
        yield
        return
    with subprocess.Popen([journalctl, "--user", "-f", "-n0"]) as proc:
        yield
        proc.terminate()


@pytest.fixture(scope="package")
def systemd_available() -> bool:
    try:
        subprocess.run(
            ["systemctl", "--user", "status"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=True,
        )
    except (FileNotFoundError, subprocess.CalledProcessError):
        return False
    return True


@pytest.fixture(scope="package")
def postgres_logger(logger: logging.Logger) -> Iterator[PostgresLogger]:
    """Register an 'instance' to stream its log to the test logger."""
    executor = concurrent.futures.ThreadPoolExecutor()

    def submit(instance: system.PostgreSQLInstance) -> None:
        def postgres_logs(instance: system.PostgreSQLInstance) -> None:
            for line in postgresql.logs(instance):
                logger.debug("%s: %s", instance, line.rstrip())

        executor.submit(postgres_logs, instance)

    yield submit

    executor.shutdown(wait=False, cancel_futures=True)


@pytest.fixture(scope="package")
def powa_available(no_plugins: bool, pg_bindir: Path) -> bool:
    if no_plugins:
        return False
    pg_config = pg_bindir / "pg_config"
    result = subprocess.run(
        [pg_config, "--pkglibdir"], stdout=subprocess.PIPE, check=True, text=True
    )
    pkglibdir = Path(result.stdout.strip())
    return (
        (pkglibdir / "pg_qualstats.so").exists()
        and (pkglibdir / "pg_stat_kcache.so").exists()
        and (pkglibdir / "powa.so").exists()
    )


@pytest.fixture(scope="package")
def systemd_requested(request: Any, systemd_available: bool) -> bool:
    value = request.config.option.systemd
    assert isinstance(value, bool)
    if value and not systemd_available:
        raise pytest.UsageError("systemd is not available on this system")
    return value


@pytest.fixture(scope="package")
def postgresql_auth(request: Any) -> AuthType:
    return request.config.option.pg_auth  # type: ignore[no-any-return]


@pytest.fixture(scope="package")
def no_version_in_path_settings(request: pytest.FixtureRequest) -> bool:
    opt = request.config.option.no_version_in_path_settings
    assert isinstance(opt, bool)
    return opt


def ssh_command(path: Path, key: Path) -> Path:
    cmdfile = path / "sshcmd"
    with cmdfile.open("w") as f:
        f.write(
            dedent(
                f"""\
                #!/bin/sh
                /usr/bin/ssh -i {key} -o StrictHostKeyChecking=no "$@"
                """
            )
        )
    cmdfile.chmod(0o700)
    return cmdfile


@pytest.fixture(scope="package")
def pgbackrest_repo_host(
    request: Any,
    postgresql_auth: AuthType,
    pgbackrest_execpath: Path | None,
    ca_cert: Path,
    cert_factory: CertFactory,
    tmp_path_factory: pytest.TempPathFactory,
    free_tcp_port_factory: FreePortFactory,
    logger: logging.Logger,
) -> Iterator[PgbackrestRepoHost | None]:
    option = request.config.option.pgbackrest_repo_host
    if not option:
        yield None
        return

    assert pgbackrest_execpath is not None
    repo_path = tmp_path_factory.mktemp("pgbackrest-repo")
    logpath = repo_path / "logs"
    logpath.mkdir()
    hostname = socket.getfqdn()
    if option == "tls":
        repo_cert = cert_factory(common_name=hostname)
        with PgbackrestRepoHostTLS(
            client_configpath=repo_path / "pgbackrest.conf",
            server_configpath=repo_path / "server.conf",
            logpath=logpath,
            port=free_tcp_port_factory(),
            path=repo_path / "backups",
            repo_cn=hostname,
            dbhost_cn=hostname,
            ca_file=ca_cert,
            repo_certfile=repo_cert.path,
            repo_keyfile=repo_cert.private_key,
            logger=logger,
        ) as r:
            yield r
    elif option == "ssh":
        if postgresql_auth != "peer":
            pytest.skip("pgbackrest SSH repository requires 'peer' authentication mode")
        dbhost_port = free_tcp_port_factory()
        dbhost_ssh_path = tmp_path_factory.mktemp("pgbackrest-client") / "ssh"

        # exchange keys
        dbhost_keys = SSHKeys.make(dbhost_ssh_path)
        repo_keys = SSHKeys.make(repo_path)
        (dbhost_ssh_path / "authorized_keys").write_text(
            "no-agent-forwarding,no-X11-forwarding,no-port-forwarding,"
            f"command=\"sh -c '{pgbackrest_execpath} ${{SSH_ORIGINAL_COMMAND#* }}'\" "
            f"{repo_keys.public_key.read_text()}"
        )
        (repo_path / "authorized_keys").write_text(
            "no-agent-forwarding,no-X11-forwarding,no-port-forwarding,"
            f"command=\"sh -c '{pgbackrest_execpath} ${{SSH_ORIGINAL_COMMAND#* }}'\" "
            f"{dbhost_keys.public_key.read_text()}"
        )

        with ServerSSH(
            host_keyfile=dbhost_keys.host_key,
            port=dbhost_port,
            ssh_path=dbhost_ssh_path,
        ):
            add_to_known_hosts(repo_path, hostname, dbhost_port)
            repo_port = free_tcp_port_factory()
            with PgbackrestRepoHostSSH(
                client_configpath=repo_path / "pgbackrest.conf",
                host_keyfile=repo_keys.host_key,
                user_keyfile=repo_keys.private_key,
                logpath=logpath,
                port=repo_port,
                ssh_path=repo_path,
                cmd_ssh=ssh_command(repo_path, repo_keys.private_key),
                dbhost_port=dbhost_port,
                dbhost_user_keyfile=dbhost_keys.private_key,
                dbhost_cmd_ssh=ssh_command(dbhost_ssh_path, dbhost_keys.private_key),
                path=repo_path / "backups",
                dbhost_host=hostname,
                logger=logger,
            ) as r:
                add_to_known_hosts(dbhost_ssh_path, hostname, repo_port)
                yield r
    else:
        assert_never(option)


@pytest.fixture(scope="package")
def config_dir(tmp_path_factory: pytest.TempPathFactory) -> Path:
    """An empty PGLIFT_CONFIG_DIR, to prevent usage of user's site configuration."""
    return tmp_path_factory.mktemp("pglift-config-dir")


@pytest.fixture(autouse=True, scope="package")
def config_env(config_dir: Path) -> Iterator[Path]:
    """Setup pglift environment (e.g. PGLIFT_CONFIG_DIR) for tests."""
    with pytest.MonkeyPatch.context() as mp:
        mp.setenv("PGLIFT_CONFIG_DIR", str(config_dir))
        yield config_dir


@pytest.fixture(scope="package", autouse=True)
def config_templates(postgresql_auth: AuthType, config_dir: Path) -> None:
    """Copy test-local (and PostgreSQL auth-type specific) templates to PGLIFT_CONFIG_DIR."""
    name = "peer" if postgresql_auth == "peer" else "base"
    shutil.copytree(
        Path(__file__).parent / "data" / name, config_dir, dirs_exist_ok=True
    )


@pytest.fixture(scope="package")
def postgresql_settings(
    tmp_path_factory: pytest.TempPathFactory,
    postgresql_auth: AuthType,
    surole_name: str,
    surole_password: str | None,
    pgbackrest_password: str | None,
    pg_back_execpath: Path | None,
    no_version_in_path_settings: bool,
) -> _postgresql.Settings:
    """Factory to create a _postgresql.Settings instance with distinct files
    (.pgpass or password_command file) from other instances.
    """
    auth: dict[str, Any] = {
        "local": "password",
        "passfile": None,
    }
    surole: dict[str, Any] = {"name": surole_name}
    backuprole: dict[str, Any] = {"name": "backup"}
    if postgresql_auth == "peer":
        pass
    elif postgresql_auth == "password_command":
        passcmdfile = tmp_path_factory.mktemp("home") / "passcmd"
        auth["password_command"] = [str(passcmdfile), "{instance}", "{role}"]
        with passcmdfile.open("w") as f:
            f.write(
                dedent(
                    f"""\
                    #!/bin/sh
                    instance=$1
                    role=$2
                    if [ ! "$instance" ]
                    then
                        echo "no instance given!!" >&2
                        exit 1
                    fi
                    if [ ! "$role" ]
                    then
                        echo "no role given!!" >&2
                        exit 1
                    fi
                    if [ "$role" = {surole["name"]} ]
                    then
                        echo "retrieving password for $role for $instance..." >&2
                        echo {surole_password}
                        exit 0
                    fi
                    if [ "$role" = {backuprole["name"]} ]
                    then
                        echo "retrieving password for $role for $instance..." >&2
                        echo {pgbackrest_password}
                        exit 0
                    fi
                    """
                )
            )
        passcmdfile.chmod(0o700)
    elif postgresql_auth == "pgpass":
        passfile = tmp_path_factory.mktemp("home") / ".pgpass"
        passfile.touch(mode=0o600)
        auth["passfile"] = str(passfile)
        surole["pgpass"] = True
        backuprole["pgpass"] = True
    else:
        raise AssertionError(f"unexpected {postgresql_auth}")
    obj: dict[str, Any] = {
        "auth": auth,
        "surole": surole,
        "backuprole": backuprole,
        "replrole": "replication",
    }
    if pg_back_execpath is not None:
        obj["dump_commands"] = [
            [
                str(pg_back_execpath),
                "-B",
                "{bindir}",
                "-b",
                "{path}",
                "-d",
                "{conninfo}",
                "{dbname}",
                "-K",
                "7",
                "-P",
                "7",
            ]
        ]
    if no_version_in_path_settings:
        pgsql_data = tmp_path_factory.mktemp("pgsql-data")
        obj |= {
            "datadir": pgsql_data / "{name}" / "data",
            "waldir": pgsql_data / "{name}" / "wal",
        }
    return _postgresql.Settings.model_validate(obj)


@pytest.fixture(scope="package")
def passfile(
    postgresql_auth: AuthType, postgresql_settings: _postgresql.Settings
) -> Path:
    if postgresql_auth != "pgpass":
        pytest.skip(f"not applicable for auth:{postgresql_auth}")
    p = postgresql_settings.auth.passfile
    assert p is not None
    return p


@pytest.fixture(scope="package")
def settings(
    tmp_path_factory: pytest.TempPathFactory,
    postgresql_settings: _postgresql.Settings,
    systemd_requested: bool,
    patroni_execpaths: tuple[Path, Path] | None,
    etcd_host: Etcd | None,
    pgbackrest_execpath: Path | None,
    pgbackrest_repo_host: PgbackrestRepoHost | None,
    ca_cert: Path,
    cert_factory: CertFactory,
    prometheus_execpath: Path | None,
    powa_available: bool,
    temboard_execpath: Path | None,
    free_tcp_port_factory: FreePortFactory,
) -> Settings:
    prefix = tmp_path_factory.mktemp("prefix")
    (prefix / "run" / "postgresql").mkdir(parents=True)
    run_prefix = tmp_path_factory.mktemp("run")
    obj = {
        "prefix": str(prefix),
        "run_prefix": str(run_prefix),
        "postgresql": postgresql_settings.model_dump(),
    }
    if systemd_requested:
        obj.update({"systemd": {}})

    if patroni_execpaths and etcd_host:
        host = local_host()
        restapi_cert = cert_factory(host)
        ctl_cert = cert_factory(host)
        patroni, patronictl = patroni_execpaths
        obj["patroni"] = {
            "execpath": patroni,
            "ctlpath": patronictl,
            "etcd": {
                "hosts": [etcd_host.endpoint],
                "protocol": "https",
                "cacert": ca_cert,
            },
            "postgresql": {
                "connection": {
                    "ssl": {
                        "mode": "verify-ca",
                        "rootcert": ca_cert,
                    },
                },
            },
            "restapi": {
                "cafile": ca_cert,
                "certfile": restapi_cert.path,
                "keyfile": restapi_cert.private_key,
                "verify_client": "required",
            },
            "ctl": {
                "certfile": ctl_cert.path,
                "keyfile": ctl_cert.private_key,
            },
        }

    if pgbackrest_execpath is not None:
        hostname = socket.getfqdn()
        if isinstance(pgbackrest_repo_host, PgbackrestRepoHostTLS):
            pgbackrest_dbhost_cert = cert_factory(
                common_name=pgbackrest_repo_host.dbhost_cn
            )
            pgbackrest_repository = {
                "mode": "host-tls",
                "pid_file": str(run_prefix / "pgbackrest" / "pgbackrest.pid"),
                "host": hostname,
                "host_port": pgbackrest_repo_host.port,
                "host_config": pgbackrest_repo_host.client_configpath,
                "cn": pgbackrest_repo_host.repo_cn,
                "certificate": {
                    "ca_cert": ca_cert,
                    "cert": pgbackrest_dbhost_cert.path,
                    "key": pgbackrest_dbhost_cert.private_key,
                },
                "port": free_tcp_port_factory(),
            }
        elif isinstance(pgbackrest_repo_host, PgbackrestRepoHostSSH):
            pgbackrest_repository = {
                "mode": "host-ssh",
                "host": hostname,
                "host_port": pgbackrest_repo_host.port,
                "host_config": pgbackrest_repo_host.client_configpath,
                "host_user": getpass.getuser(),
                "cmd_ssh": pgbackrest_repo_host.dbhost_cmd_ssh,
            }
        else:
            assert pgbackrest_repo_host is None
            pgbackrest_repository = {
                "mode": "path",
                "path": tmp_path_factory.mktemp("pgbackrest") / "backups",
            }
        obj["pgbackrest"] = {
            "execpath": pgbackrest_execpath,
            "repository": pgbackrest_repository,
        }

    if prometheus_execpath:
        obj["prometheus"] = {"execpath": prometheus_execpath}

    if powa_available:
        obj["powa"] = {}

    if temboard_execpath:
        temboard_signing_key = (
            tmp_path_factory.mktemp("temboard-agent") / "signing-public.pem"
        )
        temboard_cert = cert_factory("0.0.0.0")
        obj["temboard"] = {
            "execpath": temboard_execpath,
            "ui_url": "https://0.0.0.0:8888",
            "signing_key": temboard_signing_key,
            "certificate": {
                "ca_cert": ca_cert,
                "cert": temboard_cert.path,
                "key": temboard_cert.private_key,
            },
            "logmethod": "file",
        }
        temboard_signing_key.write_text(
            "-----BEGIN PUBLIC KEY-----\n"
            "MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQChaZFhzRuFgNDLgAJ2+WQsVQ75\n"
            "G9UswuVxTfltxP4mc+ou8lyj7Ck73+M3HkFE2r623g6DZcNYCXqpyNpInsBo68kD\n"
            "IDgwHKaQBTPyve0VhNjkJyqoKIC6AJKv/wixEwsHUm/rNU8cXnY7WCNGjCV+JrEm\n"
            "ekHBWP1X4hFfPKcvvwIDAQAB\n"
            "-----END PUBLIC KEY-----"
        )

    return Settings.model_validate(obj)


@pytest.fixture
def pgbackrest_settings(
    pgbackrest_available: bool, settings: Settings
) -> _pgbackrest.Settings:
    """pgBackRest settings, if pgBackRest is enabled; skipping otherwise."""
    if not pgbackrest_available:
        pytest.skip("pgbackrest is not available")
    assert settings.pgbackrest is not None
    return settings.pgbackrest


@pytest.fixture
def systemd_settings(settings: Settings) -> _systemd.Settings:
    if settings.systemd is None:
        pytest.skip("not applicable, systemd is not enabled")
    return settings.systemd


@pytest.fixture(scope="package")
def require_systemd_scheduler(settings: Settings) -> None:
    if settings.scheduler != "systemd":
        pytest.skip("not applicable for scheduler method other than 'systemd'")


@pytest.fixture(scope="package")
def require_systemd_tmpfiles_manager(settings: Settings) -> None:
    if settings.tmpfiles_manager != "systemd":
        pytest.skip("not applicable for tmpfiles_manager method other than 'systemd'")


@pytest.fixture(scope="package")
def require_pgbackrest_localrepo(
    settings: Settings, pgbackrest_repo_host: PgbackrestRepoHost | None
) -> None:
    if not settings.pgbackrest:
        pytest.skip("not applicable if pgbackrest is not activated")
    elif pgbackrest_repo_host:
        pytest.skip("not applicable for pgbackrest repository host")


@pytest.fixture(scope="package", autouse=True)
def _hook_logger(logger: logging.Logger) -> Iterator[None]:
    hook_level = logging.DEBUG - 1
    logging.addLevelName(hook_level, "HOOK")
    logger.setLevel(hook_level)

    def before(
        hook_name: str, hook_impls: Sequence[Any], kwargs: Mapping[str, Any]
    ) -> None:
        if not hook_impls:
            return

        def p(value: Any) -> str:
            s = str(value)
            if len(s) >= 20:
                s = f"{s[:17]}..."
            return s

        logger.log(
            hook_level,
            "calling hook %s(%s) with implementations: %s",
            hook_name,
            ", ".join(f"{k}={p(v)}" for k, v in kwargs.items()),
            ", ".join(i.plugin_name for i in hook_impls),
        )

    def after(
        outcome: Any,
        hook_name: str,
        hook_impls: Sequence[Any],
        kwargs: Mapping[str, Any],
    ) -> None:
        if not hook_impls:
            return
        logger.log(hook_level, "outcome of %s: %s", hook_name, outcome)

    logger.log(hook_level, "activating hookcall monitoring")
    with hook_monitoring(before, after):
        yield None


@pytest.fixture(scope="package", autouse=True)
async def _installed(
    settings: Settings,
    systemd_requested: bool,
    config_env: Path,
    override_systemd_unit_start_limit: None,
    create_tmpfilesd_dir: None,
    supervisor: None,
) -> AsyncIterator[None]:
    if systemd_requested:
        assert settings.service_manager == "systemd"

    (config_env / "settings.yaml").write_text(
        yaml.dump(settings.model_dump(mode="json"))
    )

    if install.check(settings, partial=True):
        pytest.fail("pglift is (possibly partially) configured on site")

    await install.do(
        settings,
        header=f"# ** Test run on {platform.node()} at {datetime.now().isoformat()} **",
    )
    yield
    await install.undo(settings)


@pytest.fixture(scope="package")
def create_tmpfilesd_dir(systemd_requested: bool, settings: Settings) -> Iterator[None]:
    if not systemd_requested:
        yield
        return
    assert settings.systemd
    if (tmpfilesd_conf_dir := settings.systemd.tmpfilesd_conf_path).exists():
        yield
        return
    tmpfilesd_conf_dir.mkdir(parents=True)
    yield
    shutil.rmtree(tmpfilesd_conf_dir)


@pytest.fixture(scope="package")
def override_systemd_unit_start_limit(systemd_requested: bool) -> Iterator[None]:
    """Override the systemd configuration for the instance to prevent
    errors when too many starts happen in a short amount of time
    """
    if not systemd_requested:
        yield
        return
    units = [
        POSTGRESQL_SERVICE_NAME,
        BACKUP_SERVICE_NAME,
        BACKUP_TIMER_NAME,
    ]
    overrides_dir = Path("~/.config/systemd/user").expanduser()
    overrides = [overrides_dir / f"{unit}.d" / "override.conf" for unit in units]
    for override in overrides:
        override.parent.mkdir(parents=True, exist_ok=True)
        content = """
        [Unit]
        StartLimitIntervalSec=0
        """
        override.write_text(dedent(content))

    yield

    for override in overrides:
        shutil.rmtree(override.parent)


@pytest.fixture(scope="package")
def pg_version(request: pytest.FixtureRequest) -> PostgreSQLVersion:
    return request.config.option.pg_version  # type: ignore[no-any-return]


@pytest.fixture(scope="package")
def pg_bindir(pg_version: PostgreSQLVersion) -> Path:
    return Path(default_pg_bindir_template.format(version=pg_version))


@pytest.fixture(scope="package")
def surole_name(request: Any) -> str:
    return str(request.config.option.surole_name)


@pytest.fixture(scope="package")
def surole_password(postgresql_auth: AuthType) -> str | None:
    if postgresql_auth == "peer":
        return None
    return "s3kret p@Ssw0rd!"


@pytest.fixture(scope="package")
def replrole_password() -> str:
    return "r3pl p@Ssw0rd!"


@pytest.fixture(scope="package")
def prometheus_password() -> str:
    # TODO: use a password with blanks when
    # https://github.com/prometheus-community/postgres_exporter/issues/393 is fixed
    return "prom3th3us-p@Ssw0rd!"


@pytest.fixture(scope="package")
def temboard_password() -> str:
    return "tembo@rd p@Ssw0rd!"


@pytest.fixture(scope="package")
def powa_password() -> str:
    return "P0w4 p@Ssw0rd!"


@pytest.fixture(scope="package")
def pgbackrest_password(postgresql_auth: AuthType) -> str | None:
    if postgresql_auth == "peer":
        return None
    return "b4ckup p@Ssw0rd!"


T_co = TypeVar("T_co", covariant=True)


class Factory(Protocol[T_co]):
    def __call__(
        self, s: Settings, name: str, state: str = ..., **kwargs: Any
    ) -> T_co: ...


ManifestFactory: TypeAlias = Factory[interface.Instance]


@pytest.fixture(scope="package")
def instance_manifest_factory(
    pg_version: PostgreSQLVersion,
    surole_password: str | None,
    replrole_password: str,
    pgbackrest_password: str | None,
    prometheus_password: str,
    temboard_password: str,
    powa_password: str,
    free_tcp_port_factory: FreePortFactory,
) -> ManifestFactory:
    def factory(
        s: Settings, name: str, state: str = "stopped", **kwargs: Any
    ) -> interface.Instance:
        port = free_tcp_port_factory()
        services = {}
        if s.prometheus:
            services["prometheus"] = {
                "port": free_tcp_port_factory(),
                "password": prometheus_password,
            }
        if s.powa:
            services["powa"] = {"password": powa_password}
        if s.temboard:
            services["temboard"] = {
                "password": temboard_password,
                "port": free_tcp_port_factory(),
            }
        if s.pgbackrest:
            services["pgbackrest"] = {
                "password": pgbackrest_password,
                "stanza": f"mystanza-{name}",
            }
        m = {
            "name": name,
            "version": pg_version,
            "state": state,
            "port": port,
            "auth": {
                "host": "trust",
            },
            "settings": {
                "shared_preload_libraries": "passwordcheck",
            },
            "surole_password": surole_password,
            "replrole_password": replrole_password,
            "restart_on_changes": True,
            **services,
        }
        m = deep_update(m, kwargs)
        pm = plugin_manager(s)
        return interface.Instance.composite(pm).model_validate(m)

    return factory


@pytest.fixture(scope="package")
def replication_slot() -> str:
    return "standby"


@pytest.fixture(scope="package")
def instance_manifest(
    settings: Settings,
    instance_manifest_factory: ManifestFactory,
    replication_slot: str,
) -> interface.Instance:
    return instance_manifest_factory(
        settings,
        "test",
        state="started",
        replication_slots=[replication_slot],
    )


InstanceFactory: TypeAlias = Factory[
    Awaitable[tuple[interface.Instance, system.Instance]]
]


@pytest.fixture
async def instance_factory(
    instance_manifest_factory: ManifestFactory,
) -> AsyncIterator[InstanceFactory]:
    values: dict[str, system.PostgreSQLInstance] = {}

    async def factory(
        s: Settings, name: str, state: str = "stopped", **kwargs: Any
    ) -> tuple[interface.Instance, system.Instance]:
        assert name not in values, f"{name} already used"
        m = instance_manifest_factory(s, name, state=state, **kwargs)
        result = await instances.apply(s, m)
        assert result.change_state == "created"
        i = system.PostgreSQLInstance.system_lookup(m.name, m.version, s)
        values[name] = i
        return m, system.Instance.from_postgresql(i)

    yield factory

    for i in values.values():
        await _drop_instance_if_exists(i)


@pytest.fixture(scope="package")
async def instance(
    settings: Settings,
    instance_manifest: interface.Instance,
    pgbackrest_repo_host: PgbackrestRepoHost | None,
    pgbackrest_password: str | None,
    postgres_logger: PostgresLogger,
) -> AsyncIterator[system.Instance]:
    assert await instances.apply(settings, instance_manifest)
    instance = system.Instance.system_lookup(
        instance_manifest.name, instance_manifest.version, settings
    )
    pg_instance = instance.postgresql
    if settings.pgbackrest and pgbackrest_repo_host is not None:
        svc = instance.service(pgbackrest_models.Service)
        pgbackrest_repo_host.add_stanza(svc.stanza, pg_instance)
        await pgbackrest.check(
            pg_instance, svc, settings.pgbackrest, pgbackrest_password
        )
    # Limit postgresql.conf to uncommented entries to reduce pytest's output
    # due to --show-locals.
    postgresql_conf = pg_instance.datadir / "postgresql.conf"
    postgresql_conf.write_text(
        "\n".join(
            line
            for line in postgresql_conf.read_text().splitlines()
            if line.strip() and not line.strip().startswith("#")
        )
    )
    postgres_logger(pg_instance)
    yield instance
    await _drop_instance_if_exists(pg_instance)


@pytest.fixture(scope="package")
def pg_instance(instance: system.Instance) -> system.PostgreSQLInstance:
    return instance.postgresql


@pytest.fixture(scope="package")
async def instance_primary_conninfo(
    settings: Settings, pg_instance: system.PostgreSQLInstance
) -> str:
    return psycopg.conninfo.make_conninfo(
        host=str(settings.postgresql.socket_directory),
        port=pg_instance.port,
        user=settings.postgresql.replrole,
    )


@pytest.fixture(scope="package")
async def standby_manifest(
    settings: Settings,
    surole_password: str | None,
    replrole_password: str,
    instance_primary_conninfo: str,
    instance_manifest: interface.Instance,
    instance_manifest_factory: ManifestFactory,
    replication_slot: str,
) -> interface.Instance:
    extras = {}
    if settings.pgbackrest:
        extras = {"pgbackrest": {"stanza": f"mystanza-{instance_manifest.name}"}}
    return instance_manifest_factory(
        settings,
        "standby",
        state="started",
        surole_password=surole_password,
        standby={
            "primary_conninfo": instance_primary_conninfo,
            "password": replrole_password,
            "slot": replication_slot,
        },
        **extras,
    )


@pytest.fixture(scope="package")
async def standby_instance(
    settings: Settings,
    standby_manifest: interface.Instance,
    instance: system.Instance,
    pgbackrest_repo_host: PgbackrestRepoHost | None,
    pgbackrest_password: str | None,
    postgres_logger: PostgresLogger,
) -> AsyncIterator[system.Instance]:
    pg_instance = instance.postgresql
    assert await postgresql.is_running(pg_instance)
    await instances.apply(settings, standby_manifest)
    stdby_instance = system.Instance.system_lookup(
        standby_manifest.name, standby_manifest.version, settings
    )
    stdby_pg_instance = stdby_instance.postgresql
    if settings.pgbackrest and pgbackrest_repo_host is not None:
        svc = stdby_instance.service(pgbackrest_models.Service)
        primary_svc = instance.service(pgbackrest_models.Service)
        assert svc.stanza == primary_svc.stanza
        assert svc.path == primary_svc.path
        assert svc.index == 2
        async with postgresql.running(stdby_pg_instance):
            pgbackrest_repo_host.add_stanza(svc.stanza, stdby_pg_instance, index=2)
            await pgbackrest.check(
                stdby_pg_instance, svc, settings.pgbackrest, pgbackrest_password
            )
    postgres_logger(stdby_pg_instance)
    yield stdby_instance
    await _drop_instance_if_exists(stdby_pg_instance)


@pytest.fixture(scope="package")
def standby_pg_instance(standby_instance: system.Instance) -> system.PostgreSQLInstance:
    return standby_instance.postgresql


@pytest.fixture(scope="package")
def to_be_upgraded_manifest(
    settings: Settings, instance_manifest_factory: ManifestFactory
) -> interface.Instance:
    return instance_manifest_factory(settings, "to_be_upgraded")


@pytest.fixture(scope="package")
async def to_be_upgraded_instance(
    settings: Settings,
    to_be_upgraded_manifest: interface.Instance,
    pgbackrest_repo_host: PgbackrestRepoHost | None,
    pgbackrest_password: str | None,
) -> AsyncIterator[system.Instance]:
    m = to_be_upgraded_manifest
    assert await instances.apply(settings, m)
    instance = system.Instance.system_lookup(m.name, m.version, settings)
    pg_instance = instance.postgresql
    if settings.pgbackrest and pgbackrest_repo_host is not None:
        svc = instance.service(pgbackrest_models.Service)
        async with postgresql.running(pg_instance):
            pgbackrest_repo_host.add_stanza(svc.stanza, pg_instance)
            await pgbackrest.check(
                pg_instance, svc, settings.pgbackrest, pgbackrest_password
            )
    yield instance
    await _drop_instance_if_exists(pg_instance)


@pytest.fixture(scope="package")
async def upgraded_instance(
    settings: Settings,
    pg_version: PostgreSQLVersion,
    to_be_upgraded_instance: system.Instance,
    free_tcp_port_factory: FreePortFactory,
    pgbackrest_repo_host: PgbackrestRepoHost | None,
    pgbackrest_password: str | None,
) -> AsyncIterator[system.Instance]:
    pm = plugin_manager(settings)
    port = free_tcp_port_factory()
    instance = await instances.upgrade(
        to_be_upgraded_instance,
        name="upgraded",
        version=pg_version,
        port=port,
        _instance_model=interface.Instance.composite(pm),
    )
    pg_instance = instance.postgresql
    if settings.pgbackrest and pgbackrest_repo_host is not None:
        svc = instance.service(pgbackrest_models.Service)
        old_svc = to_be_upgraded_instance.service(pgbackrest_models.Service)
        assert (
            svc.stanza == old_svc.stanza
            and svc.path == old_svc.path
            and svc.index == old_svc.index
            and svc.datadir == pg_instance.datadir
        )
        with pgbackrest_repo_host.edit_config() as cfg:
            cfg[svc.stanza]["pg1-path"] = str(svc.datadir)
            cfg[svc.stanza]["pg1-port"] = str(port)
        async with postgresql.running(pg_instance):
            pgbackrest_repo_host.run(
                "stanza-upgrade", "--stanza", svc.stanza, "--no-online"
            )
            await pgbackrest.check(
                pg_instance, svc, settings.pgbackrest, pgbackrest_password
            )
    yield instance
    await _drop_instance_if_exists(pg_instance)


async def _drop_instance(instance: system.PostgreSQLInstance) -> pgconf.Configuration:
    config = instance.configuration()
    await _drop_instance_if_exists(instance)
    return config


async def _drop_instance_if_exists(instance: system.PostgreSQLInstance) -> None:
    if instances.exists(instance.name, instance.version, instance._settings):
        # Rebuild the Instance in order to get the list of services refreshed.
        i = system.Instance.from_postgresql(instance)
        await instances.drop(i)


@pytest.fixture(scope="package")
async def instance_dropped(
    pg_instance: system.PostgreSQLInstance,
) -> pgconf.Configuration:
    return await _drop_instance(pg_instance)


@pytest.fixture(scope="package")
async def standby_instance_dropped(
    standby_pg_instance: system.PostgreSQLInstance,
) -> pgconf.Configuration:
    return await _drop_instance(standby_pg_instance)


@pytest.fixture(scope="package")
async def to_be_upgraded_instance_dropped(
    to_be_upgraded_instance: system.Instance,
) -> pgconf.Configuration:
    return await _drop_instance(to_be_upgraded_instance.postgresql)


@pytest.fixture(scope="package")
async def upgraded_instance_dropped(
    upgraded_instance: system.Instance,
) -> pgconf.Configuration:
    return await _drop_instance(upgraded_instance.postgresql)


class RoleFactory(Protocol):
    def __call__(
        self, name: str, *options: str, owns_objects_in: Sequence[str] = ()
    ) -> None: ...


@pytest.fixture
def role_factory(
    pg_instance: system.PostgreSQLInstance, logger: logging.Logger
) -> Iterator[RoleFactory]:
    roles: dict[str, list[str]] = {}

    def factory(name: str, *options: str, owns_objects_in: Sequence[str] = ()) -> None:
        if name in roles:
            raise ValueError(f"{name!r} name already taken")
        stmt = f"CREATE ROLE {name}"
        if options:
            stmt += " " + " ".join(options)
        execute(pg_instance, stmt, fetch=False)
        roles[name] = list(owns_objects_in)

    yield factory

    for name, databases in roles.items():
        logger.debug("dropping role %s", name)
        for dbname in databases:
            logger.debug("dropping database %s (owned by %s)", dbname, name)
            execute(
                pg_instance, f"DROP OWNED BY {name} CASCADE", fetch=False, dbname=dbname
            )
        execute(pg_instance, f"DROP ROLE IF EXISTS {name}", fetch=False)


class TablespaceFactory(Protocol):
    def __call__(self, name: str) -> None: ...


@pytest.fixture
def tablespace_factory(
    pg_instance: system.PostgreSQLInstance,
    tmp_path_factory: pytest.TempPathFactory,
    logger: logging.Logger,
) -> Iterator[TablespaceFactory]:
    names = set()

    def factory(name: str) -> None:
        location = tmp_path_factory.mktemp(f"tablespace-{name}")
        execute(
            pg_instance,
            f"CREATE TABLESPACE {name} LOCATION '{location}'",
            fetch=False,
        )
        names.add((name, location))

    yield factory

    for name, location in names:
        logger.debug("dropping tablespace %s (%s)", name, location)
        if content := list(location.iterdir()):
            logger.warning(
                "tablespace %s is not empty: %s", name, ", ".join(map(str, content))
            )
        execute(pg_instance, f"DROP TABLESPACE IF EXISTS {name}", fetch=False)


class DatabaseFactory(Protocol):
    def __call__(self, name: str, *, owner: str | None = None) -> None: ...


@pytest.fixture
def database_factory(
    pg_instance: system.PostgreSQLInstance, logger: logging.Logger
) -> Iterator[DatabaseFactory]:
    datnames = set()

    def factory(name: str, *, owner: str | None = None) -> None:
        if name in datnames:
            raise ValueError(f"{name!r} name already taken")
        sql = f"CREATE DATABASE {name}"
        if owner:
            sql += f" OWNER {owner}"
        execute(pg_instance, sql, fetch=False)
        datnames.add(name)

    yield factory

    for name in datnames:
        logger.debug("dropping database %s", name)
        execute(pg_instance, f"DROP DATABASE IF EXISTS {name}", fetch=False)


# This fixture is defined as async because mixing sync and async fixtures does
# not work pretty well with ContextVar, more information:
# https://github.com/agronholm/anyio/issues/614
@pytest.fixture(scope="package", autouse=True)
async def instance_managers() -> AsyncIterator[None]:
    # Use postgresql by default, we will adapt it on specific package / module
    # if needed
    with (
        manager.instance.use(postgresql),
        manager.hba.use(postgresql),
        manager.configuration.use(postgresql),
    ):
        yield

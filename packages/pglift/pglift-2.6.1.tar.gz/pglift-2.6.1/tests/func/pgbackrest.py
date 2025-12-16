# SPDX-FileCopyrightText: 2021 Dalibo
#
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

import configparser
import getpass
import logging
import shlex
import subprocess
from abc import ABC, abstractmethod, abstractproperty
from collections.abc import Iterator
from contextlib import contextmanager
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from pglift._compat import Self
from pglift.models import PostgreSQLInstance
from pglift.settings import _pgbackrest


@dataclass
class PgbackrestRepoHost(ABC):
    logpath: Path
    port: int
    path: Path
    client_configpath: Path

    logger: logging.Logger

    # Use low timeout values to avoid getting stuck long.
    archive_timeout: int = field(default=2, init=False)
    io_timeout: int = field(default=1, init=False)
    db_timeout: int = field(default=1, init=False)

    @contextmanager
    def edit_config(self) -> Iterator[configparser.ConfigParser]:
        cp = configparser.ConfigParser(strict=True)
        if self.client_configpath.exists():
            with self.client_configpath.open() as f:
                cp.read_file(f)
        yield cp
        with self.client_configpath.open("w") as f:
            cp.write(f)

    @abstractmethod
    def add_stanza(
        self, name: str, instance: PostgreSQLInstance, index: int = 1
    ) -> None: ...

    def check_stanza(self, stanza: str) -> None:
        self.run(
            "check",
            "--stanza",
            stanza,
            "--no-archive-check",
            "--io-timeout",
            str(self.io_timeout),
            "--db-timeout",
            str(self.db_timeout),
        )

    def cmd(self, *args: str) -> list[str]:
        """Build a pgbackrest client command."""
        return ["pgbackrest", "--config", str(self.client_configpath)] + list(args)

    def run(self, *args: str) -> subprocess.CompletedProcess[str]:
        """Run a pgbackrest client command from the repository."""
        cmd = self.cmd(*args)
        return self.run_command(cmd)

    def run_command(self, cmd: list[str]) -> subprocess.CompletedProcess[str]:
        self.logger.debug("running: %s", shlex.join(cmd))
        with subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        ) as p:
            assert p.stderr is not None
            stderr = []
            for errline in p.stderr:
                self.logger.debug("%s: %s", cmd[0], errline.rstrip())
                stderr.append(errline)
            assert p.stdout is not None
            stdout = p.stdout.read()
        if p.returncode != 0:
            raise subprocess.CalledProcessError(p.returncode, p.args)
        return subprocess.CompletedProcess(
            p.args, p.returncode, stdout=stdout, stderr="".join(stderr)
        )


@dataclass
class _Server(ABC):
    proc: subprocess.Popen[str] | None = field(default=None, init=False)

    @abstractproperty
    def server_command(self) -> list[str]: ...

    def __enter__(self) -> Self:
        assert self.proc is None, "process already started"
        self.proc = subprocess.Popen(self.server_command, text=True)
        self.proc.__enter__()
        return self

    def __exit__(self, *args: Any) -> None:
        assert self.proc is not None, "process not started"
        self.proc.terminate()
        self.proc.__exit__(*args)
        self.proc = None


@dataclass
class PgbackrestRepoHostTLS(PgbackrestRepoHost, _Server):
    server_configpath: Path
    dbhost_cn: str
    ca_file: Path
    repo_cn: str
    repo_certfile: Path
    repo_keyfile: Path

    @property
    def server_command(self) -> list[str]:
        return ["pgbackrest", "server", "--config", str(self.server_configpath)]

    def __post_init__(self) -> None:
        cp = configparser.ConfigParser(strict=True)
        cp.add_section("global")
        cp["global"] = {
            "repo1-path": str(self.path),
            "repo1-retention-full": "2",
            "tls-server-address": "*",
            "tls-server-ca-file": str(self.ca_file),
            "tls-server-cert-file": str(self.repo_certfile),
            "tls-server-key-file": str(self.repo_keyfile),
            "tls-server-auth": f"{self.dbhost_cn}=*",
            "tls-server-port": str(self.port),
            "log-level-console": "off",
            "log-level-file": "detail",
            "log-level-stderr": "info",
            "log-path": str(self.logpath),
        }
        with self.server_configpath.open("w") as f:
            cp.write(f)

        with self.edit_config() as cp:
            cp.add_section("global")
            cp["global"] = {
                "repo1-path": str(self.path),
                "repo1-retention-full": "2",
                "repo1-bundle": "y",
                "repo1-block": "y",
                "start-fast": "y",
                "archive-timeout": str(self.archive_timeout),
                "log-level-console": "off",
                "log-level-file": "detail",
                "log-level-stderr": "info",
                "log-path": str(self.logpath),
            }

    def add_stanza(
        self, name: str, instance: PostgreSQLInstance, index: int = 1
    ) -> None:
        settings = instance._settings
        pgbackrest_settings = settings.pgbackrest
        assert pgbackrest_settings is not None
        host_config_path = pgbackrest_settings.configpath
        assert isinstance(pgbackrest_settings.repository, _pgbackrest.TLSHostRepository)
        host_port = pgbackrest_settings.repository.port
        user = settings.postgresql.backuprole.name
        socket_path = settings.postgresql.socket_directory
        pg = f"pg{index}"
        with self.edit_config() as cp:
            if not cp.has_section(name):
                cp.add_section(name)
            cp[name].update(
                {
                    f"{pg}-host": self.dbhost_cn,
                    f"{pg}-host-port": str(host_port),
                    f"{pg}-host-type": "tls",
                    f"{pg}-host-config-path": str(host_config_path),
                    f"{pg}-host-ca-file": str(self.ca_file),
                    f"{pg}-host-cert-file": str(self.repo_certfile),
                    f"{pg}-host-key-file": str(self.repo_keyfile),
                    f"{pg}-path": str(instance.datadir),
                    f"{pg}-port": str(instance.port),
                    f"{pg}-user": user,
                    f"{pg}-socket-path": str(socket_path),
                }
            )
        self.run(
            "server-ping",
            "--io-timeout",
            str(self.io_timeout),
            "--tls-server-address",
            self.dbhost_cn,
            "--tls-server-port",
            str(host_port),
        )
        self.run("stanza-create", "--stanza", name, "--no-online")
        self.run("verify", "--stanza", name)
        self.run("repo-ls")
        self.check_stanza(name)


@dataclass
class ServerSSH(_Server):
    ssh_path: Path
    host_keyfile: Path
    port: int

    @property
    def server_command(self) -> list[str]:
        return [
            "/usr/sbin/sshd",
            "-D",
            "-e",
            "-o",
            f"AuthorizedKeysFile={self.ssh_path / 'authorized_keys'}",
            "-o",
            "AuthenticationMethods=publickey",
            "-o",
            "PidFile=no",
            "-o",
            "StrictModes=no",
            "-h",
            str(self.host_keyfile),
            "-p",
            str(self.port),
        ]


@dataclass
class PgbackrestRepoHostSSH(PgbackrestRepoHost, ServerSSH):
    host_keyfile: Path
    user_keyfile: Path
    cmd_ssh: Path
    dbhost_host: str
    dbhost_port: int
    dbhost_user_keyfile: Path
    dbhost_cmd_ssh: Path

    def __post_init__(self) -> None:
        current_user = getpass.getuser()
        with self.edit_config() as cp:
            cp.add_section("global")
            cp["global"] = {
                "repo1-path": str(self.path),
                "repo1-retention-full": "2",
                "repo1-host-user": current_user,
                "start-fast": "y",
                "archive-timeout": str(self.archive_timeout),
                "log-level-console": "info",
                "log-level-file": "detail",
                "log-level-stderr": "info",
                "log-path": str(self.logpath),
                "cmd-ssh": str(self.cmd_ssh),
            }

    def add_stanza(
        self, name: str, instance: PostgreSQLInstance, index: int = 1
    ) -> None:
        settings = instance._settings
        pgbackrest_settings = settings.pgbackrest
        assert pgbackrest_settings is not None
        host_config_path = pgbackrest_settings.configpath
        assert isinstance(pgbackrest_settings.repository, _pgbackrest.SSHHostRepository)
        socket_path = settings.postgresql.socket_directory
        pg = f"pg{index}"
        current_user = getpass.getuser()
        user = settings.postgresql.backuprole.name
        with self.edit_config() as cp:
            if not cp.has_section(name):
                cp.add_section(name)
            cp[name].update(
                {
                    f"{pg}-host": self.dbhost_host,
                    f"{pg}-host-port": str(self.dbhost_port),
                    f"{pg}-host-type": "ssh",
                    f"{pg}-host-user": current_user,
                    f"{pg}-host-config-path": str(host_config_path),
                    f"{pg}-path": str(instance.datadir),
                    f"{pg}-port": str(instance.port),
                    f"{pg}-user": user,
                    f"{pg}-socket-path": str(socket_path),
                }
            )
        self.ping_ssh(
            f"{current_user}@{self.dbhost_host}",
            "-p",
            str(self.dbhost_port),
            "-i",
            str(self.user_keyfile),
            "-o",
            "StrictHostKeyChecking=no",
        )
        self.ping_ssh(
            f"{current_user}@{self.dbhost_host}",
            "-p",
            str(self.port),
            "-i",
            str(self.dbhost_user_keyfile),
            "-o",
            "StrictHostKeyChecking=no",
        )
        self.run(
            "stanza-create",
            "--stanza",
            name,
            "--no-online",
            "--log-level-console=debug",
        )
        self.run("verify", "--stanza", name)
        self.run("repo-ls")
        self.check_stanza(name)

    def ping_ssh(self, *args: str) -> subprocess.CompletedProcess[str]:
        """Check SSH connection from/to the repository."""
        cmd = ["ssh"] + list(args)
        return self.run_command(cmd)

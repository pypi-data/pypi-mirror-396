# SPDX-FileCopyrightText: 2021 Dalibo
#
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

import logging
import shlex
import socket
import ssl
import subprocess
from collections.abc import Iterator, Sequence
from contextlib import contextmanager
from dataclasses import dataclass, field
from pathlib import Path

import tenacity
from trustme import CA, LeafCert
from typing_extensions import Self

logger = logging.getLogger(__name__)


@dataclass
class Etcd:
    execdir: Path
    name: str
    basedir: Path
    client_port: int
    peer_port: int
    ca: CA
    host: str = "127.0.0.1"
    datadir: Path = field(init=False)
    server_certificate: LeafCert = field(init=False)
    proc: subprocess.Popen[bytes] | None = field(init=False, default=None)

    def __post_init__(self) -> None:
        self.datadir = self.basedir / "data"
        self.datadir.mkdir(mode=0o700)
        self.server_certificate = self.ca.issue_cert(self.host)

    @property
    def endpoint(self) -> str:
        return f"{self.host}:{self.client_port}"

    @tenacity.retry(
        retry=tenacity.retry_if_exception_type(ConnectionRefusedError),
        wait=tenacity.wait_fixed(1),
        stop=tenacity.stop_after_attempt(5),
        reraise=True,
    )
    def try_connect(self) -> None:
        context = ssl.create_default_context()
        self.ca.configure_trust(context)
        logger.debug("trying to connect to etcd")
        with (
            socket.create_connection((self.host, self.client_port), timeout=5) as sock,
            context.wrap_socket(sock, server_hostname=self.host) as ssock,
        ):
            logger.info("successfully connected to etcd (%s)", ssock.version())

    def setup_auth(
        self, *, credentials: tuple[str, str], role: str, prefixes: Sequence[str]
    ) -> None:
        etcdctl = self.execdir / "etcdctl"
        r = subprocess.run(  # nosec
            [etcdctl, "version"], check=True, capture_output=True, text=True
        )
        version = tuple(
            int(v) for v in r.stdout.splitlines()[0].split(": ", 1)[1].split(".")
        )
        caopt = "--cacert" if version >= (3, 4) else "--ca-file"
        username, password = credentials
        with self.ca.cert_pem.tempfile() as cacert:
            ctl = [str(etcdctl), "--endpoints", self.endpoint, caopt, cacert]
            for args in (
                ["role", "add", role],
                *(
                    [
                        "role",
                        "grant-permission",
                        role,
                        "--prefix=true",
                        "readwrite",
                        prefix,
                    ]
                    for prefix in prefixes
                ),
                ["user", "add", "root:rootpw"],
                ["user", "grant-role", "root", "root"],
                ["user", "add", f"{username}:{password}"],
                ["user", "grant-role", username, role],
                ["user", "list"],
                ["auth", "enable"],
                # Make sure authentication works with the new user.
                *(
                    ["--user", f"{username}:{password}", "get", prefix]
                    for prefix in prefixes
                ),
            ):
                cmd = ctl + args
                logger.debug("%s", shlex.join(cmd))
                r = subprocess.run(  # nosec
                    cmd, stdin=subprocess.DEVNULL, capture_output=True, text=True
                )
                for outline in r.stdout.rstrip().splitlines():
                    logger.debug("%s: %s", ctl[0], outline)
                for outline in r.stderr.rstrip().splitlines():
                    logger.error("%s: %s", ctl[0], outline)
                r.check_returncode()

    @contextmanager
    def running(self) -> Iterator[Self]:
        client_url = f"https://{self.endpoint}"
        ssldir = self.basedir / "ssl"
        ssldir.mkdir(mode=0o700, exist_ok=True)
        with (
            self.server_certificate.cert_chain_pems[0].tempfile(
                str(ssldir)
            ) as certfile,
            self.server_certificate.private_key_pem.tempfile(str(ssldir)) as keyfile,
        ):
            cmd = [
                str(self.execdir / "etcd"),
                "--name",
                self.name,
                "--data-dir",
                str(self.datadir),
                "--cert-file",
                str(certfile),
                "--key-file",
                str(keyfile),
                "--listen-peer-urls",
                f"http://{self.host}:{self.peer_port}",
                "--listen-client-urls",
                client_url,
                "--advertise-client-urls",
                client_url,
            ]
            assert self.proc is None, "already started"
            logger.info("starting etcd with command: %s", cmd)
            with subprocess.Popen(  # nosec
                cmd, stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL
            ) as proc:
                self.try_connect()
                self.proc = proc
                try:
                    yield self
                finally:
                    logger.info("terminating etcd process %d", proc.pid)
                    proc.terminate()
                    self.proc = None

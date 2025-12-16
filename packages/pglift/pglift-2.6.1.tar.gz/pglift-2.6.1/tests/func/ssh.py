# SPDX-FileCopyrightText: 2021 Dalibo
#
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

import socket
import subprocess
from dataclasses import dataclass
from pathlib import Path

import tenacity
from typing_extensions import Self


@dataclass
class SSHKeys:
    host_key: Path
    private_key: Path
    public_key: Path

    @classmethod
    def make(cls, path: Path) -> Self:
        (path / "etc" / "ssh").mkdir(parents=True, exist_ok=True)
        subprocess.run(
            ["ssh-keygen", "-A", "-f", path], check=True, capture_output=True
        )
        host_key = path / "etc" / "ssh" / "ssh_host_rsa_key"

        private_key = path / "id_rsa"
        subprocess.run(
            [
                "ssh-keygen",
                "-f",
                str(private_key),
                "-t",
                "rsa",
                "-b",
                "2048",
                "-N",
                "",
            ],
            check=True,
            capture_output=True,
        )
        public_key = path / "id_rsa.pub"

        return cls(host_key, private_key, public_key)


def add_to_known_hosts(path: Path, hostname: str, port: int) -> None:
    @tenacity.retry(
        retry=tenacity.retry_if_exception_type(ConnectionRefusedError),
        wait=tenacity.wait_fixed(1),
        stop=tenacity.stop_after_attempt(5),
    )
    def try_connect(hostname: str, port: int) -> None:
        with socket.socket() as s:
            s.connect((hostname, port))

    with open(path / "known_hosts", "w") as f:
        try_connect(hostname, port)
        subprocess.run(["ssh-keyscan", "-p", str(port), hostname], stdout=f, check=True)

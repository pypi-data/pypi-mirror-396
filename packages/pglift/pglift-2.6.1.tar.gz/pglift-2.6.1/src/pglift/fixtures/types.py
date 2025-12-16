# SPDX-FileCopyrightText: 2021 Dalibo
#
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Protocol


@dataclass
class Certificate:
    path: Path
    private_key: Path

    def __post_init__(self) -> None:
        if not self.path.exists():
            raise ValueError(f"path={self.path} does not exist")
        if not self.private_key.exists():
            raise ValueError(f"private_key={self.private_key} does not exist")


class CertFactory(Protocol):
    def __call__(
        self, *identities: str, common_name: str | None = None
    ) -> Certificate: ...

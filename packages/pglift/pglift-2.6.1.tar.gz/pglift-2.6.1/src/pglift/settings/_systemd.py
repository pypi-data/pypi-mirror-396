# SPDX-FileCopyrightText: 2021 Dalibo
#
# SPDX-License-Identifier: GPL-3.0-or-later

import os
import shutil
from pathlib import Path
from typing import Annotated, Any, ClassVar

from pydantic import AfterValidator, Field, ValidationInfo, model_validator

from .. import util
from .base import BaseModel


def default_systemd_unit_path(uid: int) -> Path:
    """Return the default systemd unit path for 'uid'.

    >>> default_systemd_unit_path(0)
    PosixPath('/etc/systemd/system')
    >>> default_systemd_unit_path(42)  # doctest: +ELLIPSIS
    PosixPath('/.../.local/share/systemd/user')
    """
    if uid == 0:
        return Path("/etc/systemd/system")
    return util.xdg_data_home() / "systemd" / "user"


def default_systemd_tmpfilesd_config_path(uid: int) -> Path:
    """Return the default systemd-tmpfiles.d configuration path for 'uid'.

    >>> default_systemd_tmpfilesd_config_path(0)
    PosixPath('/etc/tmpfiles.d')
    >>> default_systemd_tmpfilesd_config_path(42)  # doctest: +ELLIPSIS
    PosixPath('/.../user-tmpfiles.d')
    """
    if uid == 0:
        return Path("/etc/tmpfiles.d")
    return util.xdg_config_home() / "user-tmpfiles.d"


def check_sudo_and_user(value: bool, info: ValidationInfo) -> bool:
    if value and info.data.get("user"):
        raise ValueError("cannot be used with 'user' mode")
    return value


class Settings(BaseModel):
    """Systemd settings."""

    systemctl: ClassVar[Path]
    systemd_tmpfiles: ClassVar[Path]

    @model_validator(mode="before")
    @classmethod
    def __systemctl_systemd_tmpfiles_(cls, values: dict[str, Any]) -> dict[str, Any]:
        if not hasattr(cls, "systemctl"):
            if (systemctl := shutil.which("systemctl")) is None:
                raise ValueError("systemctl command not found")
            cls.systemctl = Path(systemctl)
        if not hasattr(cls, "systemd_tmpfiles"):
            if (systemd_tmpfiles := shutil.which("systemd-tmpfiles")) is None:
                raise ValueError("systemd-tmpfiles command not found")
            cls.systemd_tmpfiles = Path(systemd_tmpfiles)
        return values

    unit_path: Annotated[
        Path, Field(description="Base path where systemd units will be installed.")
    ] = default_systemd_unit_path(os.getuid())

    tmpfilesd_conf_path: Annotated[
        Path,
        Field(
            description="Base path where systemd tmpfiles.d configuration will be installed."
        ),
    ] = default_systemd_tmpfilesd_config_path(os.getuid())

    user: Annotated[
        bool,
        Field(
            description="Use the system manager of the calling user, by passing --user to systemctl calls."
        ),
    ] = True

    sudo: Annotated[
        bool,
        Field(
            description="Run systemctl command with sudo; only applicable when 'user' is unset."
        ),
        AfterValidator(check_sudo_and_user),
    ] = False

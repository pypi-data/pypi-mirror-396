# SPDX-FileCopyrightText: 2021 Dalibo
#
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

import os
import subprocess
from typing import Any

import psycopg.conninfo

from .. import exceptions, util
from ..models import PostgreSQLInstance
from ..types import ConnectionString

logger = util.get_logger(__name__)


def environ(
    instance: PostgreSQLInstance, role: str, *, base: dict[str, str] | None = None
) -> dict[str, str]:
    """Return a dict with libpq environment variables for authentication."""
    auth = instance._settings.postgresql.auth
    if base is None:
        env = os.environ.copy()
    else:
        env = base.copy()
    if auth.passfile is not None:
        env.setdefault("PGPASSFILE", str(auth.passfile))
    if auth.password_command and "PGPASSWORD" not in env:
        try:
            cmd_args = [
                c.format(instance=instance, role=role) for c in auth.password_command
            ]
        except ValueError as e:
            raise exceptions.SettingsError(
                f"failed to format auth.password_command: {e}"
            ) from None
        logger.debug("getting password for '%s' role from password_command", role)
        password = subprocess.run(  # nosec
            cmd_args, check=True, capture_output=True, text=True
        ).stdout.strip()
        if password:
            env["PGPASSWORD"] = password
    return env


def dsn(instance: PostgreSQLInstance, **kwargs: Any) -> ConnectionString:
    for badarg in ("port", "passfile", "host"):
        if badarg in kwargs:
            raise TypeError(f"unexpected {badarg!r} argument")

    kwargs["port"] = instance.port
    if socket_directory := instance.socket_directory:
        kwargs["host"] = socket_directory
    if (passfile := instance._settings.postgresql.auth.passfile) is not None:
        kwargs["passfile"] = str(passfile)
    kwargs.setdefault("dbname", "postgres")

    assert "dsn" not in kwargs
    return ConnectionString(psycopg.conninfo.make_conninfo(**kwargs))


def obfuscate_conninfo(conninfo: str, **kwargs: Any) -> str:
    """Return an obfuscated connection string with password hidden.

    >>> obfuscate_conninfo("user=postgres password=foo")
    'user=postgres password=********'
    >>> obfuscate_conninfo("user=postgres", password="secret")
    'user=postgres password=********'
    >>> obfuscate_conninfo("port=5444")
    'port=5444'
    >>> obfuscate_conninfo("postgres://dba:secret@dbserver/appdb")
    'user=dba password=******** dbname=appdb host=dbserver'
    """
    params = psycopg.conninfo.conninfo_to_dict(conninfo, **kwargs)
    if "password" in params:
        params["password"] = "*" * 8
    return psycopg.conninfo.make_conninfo("", **params)

# SPDX-FileCopyrightText: 2021 Dalibo
#
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

import asyncio
import io
import time
from collections.abc import AsyncIterator, Iterator
from contextlib import asynccontextmanager
from decimal import Decimal
from functools import cache
from pathlib import Path
from typing import IO

import psycopg
import psycopg.rows
import tenacity
from async_lru import alru_cache
from pgtoolkit import ctl
from psycopg.conninfo import conninfo_to_dict

from .. import conf, deps, exceptions, sql, util
from ..models import PostgreSQLInstance
from ..settings import POSTGRESQL_VERSIONS
from ..system import Command, FileSystem, db
from ..types import Status
from . import pq
from .models import WALReplayPauseState, WALSenderState

logger = util.get_logger(__name__)

WAIT_TIMEOUT: int = 10


@deps.use
@alru_cache(maxsize=len(POSTGRESQL_VERSIONS) + 1)
async def pg_ctl(bindir: Path, *, cmd: Command = deps.Auto) -> ctl.AsyncPGCtl:
    return await ctl.AsyncPGCtl.get(bindir, run_command=cmd.run)


@cache
def bindir(instance: PostgreSQLInstance, /) -> Path:
    settings = instance._settings.postgresql
    version = instance.version
    # Per validation of PostgreSQLInstance.version, the following next()
    # call would return.
    return next(v.bindir for v in settings.versions if v.version == version)


@deps.use
async def is_ready(instance: PostgreSQLInstance, *, cmd: Command = deps.Auto) -> bool:
    """Return True if the instance is ready per pg_isready."""
    logger.debug("checking if PostgreSQL instance %s is ready", instance)
    pg_isready = str(bindir(instance) / "pg_isready")
    user = instance._settings.postgresql.surole.name
    dsn = pq.dsn(instance, user=user)
    env = pq.environ(instance, user)
    r = await cmd.run([pg_isready, "-d", dsn], env=env, log_stdout=True)
    if r.returncode == 0:
        return True
    assert r.returncode in (
        1,
        2,
    ), f"Unexpected exit status from pg_isready {r.returncode}: {r.stdout}, {r.stderr}"
    return False


async def wait_ready(
    instance: PostgreSQLInstance, *, timeout: int = WAIT_TIMEOUT
) -> None:
    async for attempt in tenacity.AsyncRetrying(
        retry=tenacity.retry_if_exception_type(exceptions.InstanceStateError),
        wait=tenacity.wait_exponential(multiplier=1, min=1, max=timeout),
        stop=tenacity.stop_after_delay(timeout),
    ):
        with attempt:
            if not await is_ready(instance):
                raise exceptions.InstanceStateError(f"{instance} not ready")


async def status(instance: PostgreSQLInstance) -> Status:
    """Return the status of an instance.

    :raises ~exceptions.InstanceNotFound: if ``pg_ctl status`` command exits
        with status code 4 (data directory not found).
    """
    logger.debug("get status of PostgreSQL instance %s", instance)
    pgstatus = await (await pg_ctl(bindir(instance))).status(instance.datadir)
    try:
        return Status(pgstatus.value)
    except ValueError as e:
        raise exceptions.InstanceNotFound(
            str(instance), hint=f"'pg_ctl status' exited with code {pgstatus}"
        ) from e


async def is_running(instance: PostgreSQLInstance) -> bool:
    """Return True if the instance is running based on its status."""
    try:
        return (await status(instance)) == Status.running
    except exceptions.InstanceNotFound:
        return False


async def check_status(instance: PostgreSQLInstance, expected: Status) -> None:
    """Check actual instance status with respected to `expected` one.

    :raises ~exceptions.InstanceStateError: in case the actual status is not expected.
    """
    if (st := await status(instance)) != expected:
        raise exceptions.InstanceStateError(f"instance is {st.name}")


async def get_data_checksums(instance: PostgreSQLInstance) -> bool:
    """Return True/False if data_checksums is enabled/disabled on instance."""
    controldata = await (await pg_ctl(bindir(instance))).controldata(instance.datadir)
    try:
        return controldata["Data page checksum version"] != "0"
    except KeyError as e:
        logger.warning(
            "failed to get data_checksums status: %s not found in controldata", e
        )
        return False


@deps.use
async def set_data_checksums(
    instance: PostgreSQLInstance, enabled: bool, *, cmd: Command = deps.Auto
) -> None:
    """Enable/disable data checksums on instance.

    The instance MUST NOT be running.
    """
    action = "enable" if enabled else "disable"
    await cmd.run(
        [
            str(bindir(instance) / "pg_checksums"),
            f"--{action}",
            "--pgdata",
            str(instance.datadir),
        ],
        check=True,
    )


@deps.use
def logfile(
    instance: PostgreSQLInstance,
    *,
    timeout: float | None = None,
    poll_interval: float = 0.1,
    fs: FileSystem = deps.Auto,
) -> Iterator[Path]:
    """Yield the current log file by polling current_logfiles for changes.

    :raises ~exceptions.FileNotFoundError: if the current log file, matching
        first configured log_destination, is not found.
    :raises ~exceptions.SystemError: if the current log file cannot be opened
        for reading.
    :raises ValueError: if no record matching configured log_destination is
        found in current_logfiles (this indicates a misconfigured instance).
    :raises TimeoutError: if no new log file was polled from current_logfiles
        within specified 'timeout'.
    """
    config = instance.configuration()
    log_destination = conf.get_str(config, "log_destination", "stderr")
    destinations = [v.strip() for v in log_destination.split(",")]
    current_logfiles = instance.datadir / "current_logfiles"
    if not fs.exists(current_logfiles):
        raise exceptions.FileNotFoundError(
            f"file 'current_logfiles' for instance {instance} not found"
        )

    @tenacity.retry(
        retry=tenacity.retry_if_exception_type(FileNotFoundError),
        stop=tenacity.stop_after_attempt(2),
        reraise=True,
    )
    def logf() -> Path:
        """Get the current log file, matching configured log_destination.

        Retry in case the 'current_logfiles' file is unavailable for reading,
        which might happen as postgres typically re-creates it upon update.
        """
        with fs.open(current_logfiles) as f:
            for line in f:
                destination, location = line.strip().split(None, maxsplit=1)
                if destination in destinations:
                    break
            else:
                raise ValueError(
                    f"no record matching {log_destination!r} log destination found for instance {instance}"
                )
        fpath = Path(location)
        if not fpath.is_absolute():
            fpath = instance.datadir / fpath
        return fpath

    current_logfile = None
    start_time = time.monotonic()
    while True:
        f = logf()
        if f == current_logfile:
            if timeout is not None:
                if time.monotonic() - start_time >= timeout:
                    raise TimeoutError("timed out waiting for a new log file")
            time.sleep(poll_interval)
            continue
        current_logfile = f
        start_time = time.monotonic()
        yield current_logfile


@deps.use
def logs(
    instance: PostgreSQLInstance,
    *,
    timeout: float | None = None,
    poll_interval: float = 0.1,
    fs: FileSystem = deps.Auto,
) -> Iterator[str]:
    """Return the content of current log file as an iterator."""
    for fpath in logfile(instance, timeout=timeout, poll_interval=poll_interval):
        logger.info("reading logs of instance %s from %s", instance, fpath)
        try:
            with fs.open(fpath) as f:
                yield from f
        except OSError as e:
            raise exceptions.SystemError(
                f"failed to read {fpath} on instance {instance}"
            ) from e


@asynccontextmanager
@deps.use
async def log(
    instance: PostgreSQLInstance, *, fs: FileSystem = deps.Auto
) -> AsyncIterator[None]:
    """Context manager forwarding PostgreSQL log messages (emitted during the
    context) to our logger.

    If no PostgreSQL log file is found, do nothing.
    """
    try:
        logpath = next(logfile(instance, timeout=0))
    except exceptions.FileNotFoundError:
        yield None
        return

    # Log PostgreSQL messages, read from current log file, using a
    # thread to avoid blocking.
    def logpg(f: IO[str], execpath: Path) -> None:
        """Log lines read from 'f', until it gets closed."""
        while True:
            try:
                line = f.readline()
            except ValueError:  # I/O operation on closed file
                break
            if line:
                logger.debug("%s: %s", execpath, line.rstrip())

    with fs.open(logpath) as logf:
        logf.seek(0, io.SEEK_END)
        # TODO: use asyncio.TaskGroup from Python 3.11
        task = asyncio.create_task(
            asyncio.to_thread(logpg, logf, bindir(instance) / "postgres")
        )
        try:
            yield None
        finally:
            logf.close()  # Would terminate the threaded task.
            await task


async def replication_lag(instance: PostgreSQLInstance) -> Decimal | None:
    """Return the replication lag of a standby instance.

    The instance must be running; if the primary is not running, None is
    returned.

    :raises TypeError: if the instance is not a standby.
    """
    standby = instance.standby
    if standby is None:
        raise TypeError(f"{instance} is not a standby")

    try:
        async with await db.primary_connect(standby) as cnx:
            primary_lsn = await db.one(
                cnx,
                "SELECT pg_current_wal_lsn()",
                row_factory=psycopg.rows.scalar_row,
            )
    except psycopg.OperationalError as e:
        logger.warning("failed to connect to primary: %s", e)
        return None

    if (user := standby.user) is None:
        user = instance._settings.postgresql.replrole
        assert user is not None
    password = (
        standby.password.get_secret_value()
        if standby.password
        else pq.environ(instance, user).get("PGPASSWORD")
    )
    dsn = pq.dsn(instance, dbname="template1", user=user, password=password)
    async with await db.connect_dsn(dsn) as cnx:
        return await db.one(
            cnx,
            "SELECT %s::pg_lsn - pg_last_wal_replay_lsn()",
            (primary_lsn,),
            row_factory=psycopg.rows.scalar_row,
        )


async def wal_sender_state(
    instance: PostgreSQLInstance,
) -> WALSenderState | None:
    """Return the state of the WAL sender process (on the primary) connected
    to standby 'instance'.

    This queries pg_stat_replication view on the primary, filtered by
    application_name assuming that the standby instance name is used there.
    We retrieve application_name if set in primary_conninfo, use cluster_name
    otherwise or fall back to instance name.
    """
    assert instance.standby is not None, f"{instance} is not a standby"
    primary_conninfo = conninfo_to_dict(instance.standby.primary_conninfo)
    try:
        application_name = primary_conninfo["application_name"]
    except KeyError:
        application_name = conf.get_str(
            instance.configuration(), "cluster_name", instance.name
        )

    try:
        async with await db.primary_connect(instance.standby) as cnx:
            return await db.fetchone(
                cnx,
                "SELECT state FROM pg_stat_replication WHERE application_name = %s",
                (application_name,),
                row_factory=psycopg.rows.scalar_row,
            )
    except psycopg.OperationalError as e:
        logger.warning("failed to connect to primary: %s", e)
        return None


async def wal_replay_pause_state(instance: PostgreSQLInstance) -> WALReplayPauseState:
    """Return whether WAL recovery pause has been requested."""
    async with db.connect(instance) as cnx:
        return await db.one(
            cnx,
            sql.query("get_wal_replay_pause_state"),
            row_factory=psycopg.rows.scalar_row,
        )

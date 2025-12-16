# SPDX-FileCopyrightText: 2021 Dalibo
#
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

import json
import logging
import re
import shutil
from pathlib import Path

import pytest
import tenacity
from pgtoolkit import pgpass

from pglift import instances, pgbackrest, postgresql
from pglift.models import system
from pglift.pgbackrest import repo_path
from pglift.pgbackrest.models import Service
from pglift.settings import Settings, _pgbackrest

from . import AuthType, execute, postgresql_stopped
from .conftest import InstanceFactory, ManifestFactory
from .pgbackrest import PgbackrestRepoHost, PgbackrestRepoHostTLS

pytestmark = pytest.mark.anyio


@pytest.fixture(scope="session", autouse=True)
def _pgbackrest_available(pgbackrest_available: bool) -> None:
    if not pgbackrest_available:
        pytest.skip("pgbackrest is not available")


async def test_configure(
    settings: Settings,
    instance: system.Instance,
    postgresql_auth: AuthType,
    pgbackrest_repo_host: PgbackrestRepoHost | None,
) -> None:
    pg_instance = instance.postgresql
    instance_config = pg_instance.configuration()
    assert instance_config
    instance_port = instance_config.port

    stanza = f"mystanza-{instance.name}"
    pgbackrest_settings = pgbackrest.get_settings(settings)
    stanza_configpath = pgbackrest_settings.configpath / "conf.d" / f"{stanza}.conf"
    assert stanza_configpath.exists()
    lines = stanza_configpath.read_text().splitlines()
    assert f"pg1-port = {instance_port}" in lines
    assert "pg1-user = backup" in lines

    if pgbackrest_repo_host is None:
        assert isinstance(pgbackrest_settings.repository, _pgbackrest.PathRepository)
        assert (
            pgbackrest_settings.repository.path / "archive" / stanza / "archive.info"
        ).exists()

        assert (pgbackrest_settings.logpath / f"{stanza}-stanza-create.log").exists()

    if postgresql_auth == "pgpass":
        assert settings.postgresql.auth.passfile is not None
        lines = settings.postgresql.auth.passfile.read_text().splitlines()
        assert any(line.startswith(f"*:{pg_instance.port}:*:backup:") for line in lines)

    pgconfigfile = pg_instance.datadir / "postgresql.conf"
    pgconfig = [
        line.split("#", 1)[0].strip() for line in pgconfigfile.read_text().splitlines()
    ]
    assert (
        f"archive_command = '{pgbackrest_settings.execpath}"
        f" --config-path={pgbackrest_settings.configpath}"
        f" --stanza={stanza}"
        f" --pg1-path={pg_instance.datadir}"
        " archive-push %p'"
    ) in pgconfig


@pytest.mark.anyio
async def test_check(
    settings: Settings,
    instance: system.Instance,
    pgbackrest_repo_host: PgbackrestRepoHost | None,
    pgbackrest_password: str | None,
) -> None:
    """Run a 'pgbackrest check' on database host, when in remote repository setup."""
    if pgbackrest_repo_host is None:
        pytest.skip("not applicable for local repository")
    pgbackrest_settings = pgbackrest.get_settings(settings)
    service = instance.service(Service)
    async with postgresql.running(instance.postgresql, timeout=5):
        await pgbackrest.check(
            instance.postgresql, service, pgbackrest_settings, pgbackrest_password
        )
        pgbackrest_repo_host.run("check", f"--stanza={service.stanza}")
    assert await pgbackrest.backup_info(service, pgbackrest_settings)


@pytest.mark.anyio
async def test_iterbackups_empty(
    instance: system.Instance,
    settings: Settings,
    pgbackrest_repo_host: PgbackrestRepoHost | None,
) -> None:
    if pgbackrest_repo_host is not None:
        pytest.skip("only applicable for local repository")
    pgbackrest_settings = pgbackrest.get_settings(settings)
    stanza = f"mystanza-{instance.name}"
    assert [
        _ async for _ in pgbackrest.iter_backups(instance, pgbackrest_settings)
    ] == []
    assert isinstance(pgbackrest_settings.repository, _pgbackrest.PathRepository)
    repopath = pgbackrest_settings.repository.path
    latest_backup = repopath / "backup" / stanza / "latest"

    assert (repopath / "backup" / stanza / "backup.info").exists()
    assert not latest_backup.exists()


@pytest.mark.anyio
async def test_standby(
    settings: Settings,
    instance: system.Instance,
    standby_instance: system.Instance,
    pgbackrest_repo_host: PgbackrestRepoHost | None,
    logger: logging.Logger,
) -> None:
    pgbackrest_settings = pgbackrest.get_settings(settings)

    stanza = "mystanza-test"
    stanza_path = pgbackrest_settings.configpath / "conf.d" / f"{stanza}.conf"
    assert stanza_path.exists()
    assert not (
        pgbackrest_settings.configpath
        / "conf.d"
        / f"mystanza-{standby_instance.name}.conf"
    ).exists()

    service = instance.service(Service)
    standby_service = standby_instance.service(Service)
    assert service.index == 1
    assert standby_service.index == 2

    assert await postgresql.is_running(instance.postgresql)
    assert await postgresql.is_running(standby_instance.postgresql)
    logger.info(
        "WAL sender state: %s",
        await postgresql.wal_sender_state(standby_instance.postgresql),
    )
    if pgbackrest_repo_host:
        rbck = pgbackrest_repo_host.run(
            "backup", "--stanza", stanza, "--backup-standby"
        )
    else:
        rbck = await repo_path.backup(standby_instance, pgbackrest_settings)
    info = await pgbackrest.backup_info(
        service, pgbackrest.get_settings(instance._settings)
    )
    standby_info = await pgbackrest.backup_info(standby_service, pgbackrest_settings)
    assert standby_info == info
    assert len(info["backup"]) == 1
    assert info["status"]["message"] == "ok"

    assert re.findall(r"INFO: wait for replay on the standby to reach", rbck.stderr)
    assert re.findall(r"INFO: replay on the standby reached", rbck.stderr)


@pytest.mark.anyio
async def test_backup_restore(
    logger: logging.Logger,
    instance_factory: InstanceFactory,
    settings: Settings,
    pgbackrest_repo_host: PgbackrestRepoHost | None,
    surole_password: str | None,
) -> None:
    """Check 'backup' and 'restore' operations.

    Do this on a dedicated instance in order to avoid putting
    the standby out of sync w.r.t. to the primary 'instance'.
    """
    pgbackrest_settings = pgbackrest.get_settings(settings)
    stanza = "restoreme"
    manifest, instance = await instance_factory(
        settings,
        "restoreme",
        state="started",
        surole_password=surole_password,
        pgbackrest={"stanza": stanza},
    )
    pg_instance = instance.postgresql
    if pgbackrest_repo_host is not None:
        pgbackrest_repo_host.add_stanza(stanza, pg_instance)

    execute(pg_instance, "CREATE DATABASE backrest", fetch=False)
    execute(
        pg_instance,
        "CREATE TABLE t AS (SELECT 'created' as s)",
        dbname="backrest",
        fetch=False,
    )
    rows = execute(pg_instance, "SELECT * FROM t", dbname="backrest")
    assert rows == [{"s": "created"}]

    latest_backup: Path
    if pgbackrest_repo_host is None:
        await repo_path.backup(instance, pgbackrest_settings, type="full")
        assert isinstance(pgbackrest_settings.repository, _pgbackrest.PathRepository)
        repopath = pgbackrest_settings.repository.path
        latest_backup = repopath / "backup" / stanza / "latest"
    else:
        pgbackrest_repo_host.run("backup", "--stanza", stanza, "--type", "full")
        pgbackrest_repo_host.run("expire", "--stanza", stanza)
        latest_backup = pgbackrest_repo_host.path / "backup" / stanza / "latest"
    assert latest_backup.exists() and latest_backup.is_symlink()

    backup1 = await pgbackrest.iter_backups(instance, pgbackrest_settings).__anext__()
    assert backup1.type == "full"
    assert set(backup1.databases) & {"backrest", "postgres"}
    assert backup1.date_stop > backup1.date_start

    if isinstance(pgbackrest_repo_host, PgbackrestRepoHostTLS):
        # PgbackrestRepoHostTLS has repo-block=y, thus the backup set size is
        # not returned.
        assert backup1.repo_size is None
    else:
        assert backup1.repo_size

    execute(
        pg_instance,
        "INSERT INTO t(s) VALUES ('backup1')",
        dbname="backrest",
        fetch=False,
    )

    # Sleep 1s so that the previous backup gets sufficiently old to be picked
    # upon restore later on.
    execute(pg_instance, "SELECT pg_sleep(1)", fetch=False)
    (record,) = execute(pg_instance, "SELECT current_timestamp", fetch=True)
    before_drop = record["current_timestamp"]
    execute(
        pg_instance,
        "INSERT INTO t(s) VALUES ('before-drop')",
        dbname="backrest",
        fetch=False,
    )

    execute(pg_instance, "DROP DATABASE backrest", fetch=False)

    @tenacity.retry(
        reraise=True,
        wait=tenacity.wait_fixed(1),
        stop=tenacity.stop_after_attempt(5),
        before=tenacity.before_log(logger, logging.DEBUG),
    )
    def check_not_in_recovery() -> None:
        (r,) = execute(pg_instance, "SELECT pg_is_in_recovery() as in_recovery")
        assert not r["in_recovery"], "instance still in recovery"

    # With no target (date or label option), restore *and* apply WALs, thus
    # getting back to the same state as before the restore, i.e. 'backrest'
    # database dropped.
    async with postgresql_stopped(pg_instance):
        await pgbackrest.restore(instance, pgbackrest_settings)
    check_not_in_recovery()
    rows = execute(pg_instance, "SELECT datname FROM pg_database")
    assert "backrest" not in [r["datname"] for r in rows]

    # With a date target, WALs are applied until that date.
    async with postgresql_stopped(pg_instance):
        await pgbackrest.restore(instance, pgbackrest_settings, date=before_drop)
    check_not_in_recovery()
    rows = execute(pg_instance, "SELECT datname FROM pg_database")
    assert "backrest" in [r["datname"] for r in rows]
    rows = execute(pg_instance, "SELECT * FROM t", dbname="backrest")
    assert {r["s"] for r in rows} == {"created", "backup1"}

    # With a label target, WALs are not replayed, just restore instance state
    # at specified backup.
    async with postgresql_stopped(pg_instance):
        await pgbackrest.restore(instance, pgbackrest_settings, label=backup1.label)
    check_not_in_recovery()
    rows = execute(pg_instance, "SELECT datname FROM pg_database")
    assert "backrest" in [r["datname"] for r in rows]
    rows = execute(pg_instance, "SELECT * FROM t", dbname="backrest")
    assert rows == [{"s": "created"}]


@pytest.mark.anyio
async def test_upgrade(
    settings: Settings,
    to_be_upgraded_instance: system.Instance,
    upgraded_instance: system.Instance,
    pgbackrest_repo_host: PgbackrestRepoHost | None,
) -> None:
    pgbackrest_settings = pgbackrest.get_settings(settings)
    # Upgraded instance use the stanza of the original instance.
    assert (
        pgbackrest_settings.configpath
        / "conf.d"
        / f"mystanza-{to_be_upgraded_instance.name}.conf"
    ).exists()
    assert not (
        pgbackrest_settings.configpath
        / "conf.d"
        / f"mystanza-{upgraded_instance.name}.conf"
    ).exists()

    if pgbackrest_repo_host is not None:
        stanza = f"mystanza-{to_be_upgraded_instance.name}"
        r = pgbackrest_repo_host.run("info", "--stanza", stanza, "--output", "json")
        (info,) = json.loads(r.stdout)
        assert not info["backup"]
        assert info["status"]["message"] == "no valid backups"

        async with postgresql.running(upgraded_instance.postgresql, timeout=5):
            pgbackrest_repo_host.run("backup", "--stanza", stanza)

        r = pgbackrest_repo_host.run("info", "--stanza", stanza, "--output", "json")
        (info,) = json.loads(r.stdout)
        assert info["backup"]
        assert info["status"]["message"] == "ok"


@pytest.mark.anyio
async def test_standby_instance_restore_from_backup(
    instance: system.Instance,
    instance_primary_conninfo: str,
    instance_factory: InstanceFactory,
    replrole_password: str,
    settings: Settings,
    surole_password: str | None,
    pgbackrest_repo_host: PgbackrestRepoHost | None,
    caplog: pytest.LogCaptureFixture,
    logger: logging.Logger,
) -> None:
    """Test a standby instance can be created from a pgbackrest backup"""
    pg_instance = instance.postgresql
    # create slot on primary
    slot = "standby_restored"
    execute(
        pg_instance,
        f"SELECT true FROM pg_create_physical_replication_slot({slot!r})",
        fetch=False,
    )
    stanza = f"mystanza-{instance.name}"
    if pgbackrest_repo_host is not None:
        pgbackrest_repo_host.run("backup", "--stanza", stanza, "--type", "full")
    else:
        pgbackrest_settings = pgbackrest.get_settings(settings)
        await repo_path.backup(instance, pgbackrest_settings, type="full")
    caplog.clear()
    instance_name = "standby_from_pgbackrest"
    manifest, standby = await instance_factory(
        settings,
        instance_name,
        surole_password=surole_password,
        standby={
            "primary_conninfo": instance_primary_conninfo,
            "password": replrole_password,
            "slot": slot,
        },
        pgbackrest={
            "stanza": stanza,
        },
    )
    assert "restoring from a pgBackRest backup" in caplog.messages
    async with postgresql.running(standby.postgresql, timeout=5):
        replrole = manifest.replrole(settings)
        assert execute(
            standby.postgresql,
            "SELECT * FROM pg_is_in_recovery()",
            role=replrole,
            dbname="template1",
        ) == [{"pg_is_in_recovery": True}]

        @tenacity.retry(
            reraise=True,
            wait=tenacity.wait_fixed(1),
            stop=tenacity.stop_after_attempt(5),
            before=tenacity.before_log(logger, logging.DEBUG),
        )
        def check_is_streaming() -> None:
            assert execute(
                pg_instance,
                f"SELECT usename, state FROM pg_stat_replication WHERE application_name = {instance_name!r}",
            ) == [
                {
                    "usename": "replication",
                    "state": "streaming",
                }
            ]

        check_is_streaming()


@pytest.mark.anyio
async def test_create_primary_instance_from_stanza(
    instance_factory: InstanceFactory,
    passfile: Path,
    settings: Settings,
    pgbackrest_repo_host: PgbackrestRepoHost | None,
    instance_manifest_factory: ManifestFactory,
    pgbackrest_password: str | None,
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Test the creation of an instance from a pgBackRest backup when PGDATA is
    not available, for example after a disaster (ie. filesystem lost)."""
    name = "to_be_restored"
    stanza = f"mystanza-{name}"
    manifest, instance = await instance_factory(
        settings,
        name,
        pgbackrest={"stanza": stanza},
        state="started",
    )
    pg_instance = instance.postgresql
    if settings.pgbackrest and pgbackrest_repo_host is not None:
        svc = instance.service(Service)
        pgbackrest_repo_host.add_stanza(svc.stanza, pg_instance)
        await pgbackrest.check(
            pg_instance, svc, settings.pgbackrest, pgbackrest_password
        )
    version = pg_instance.version

    # Create some data
    execute(pg_instance, "CREATE DATABASE backrest;", fetch=False)
    execute(
        pg_instance,
        "CREATE TABLE t AS (SELECT 'created' as s)",
        dbname="backrest",
        fetch=False,
    )
    rows = execute(pg_instance, "SELECT * FROM t", dbname="backrest")
    assert rows == [{"s": "created"}]

    async with postgresql.running(pg_instance, timeout=5):
        if pgbackrest_repo_host is not None:
            pgbackrest_repo_host.run("backup", "--stanza", stanza, "--type", "full")
        else:
            pgbackrest_settings = pgbackrest.get_settings(settings)
            await repo_path.backup(instance, pgbackrest_settings, type="full")

    caplog.clear()
    shutil.rmtree(pg_instance.datadir)
    shutil.rmtree(pg_instance.waldir)
    # Also manually remove entries from .pgpass to avoid tests failing at drop stage
    if passfile:
        assert manifest.port
        with passfile.open() as f:
            pf = pgpass.parse(f)
        pf.remove(port=manifest.port)
        with passfile.open("w") as f:
            pf.save(f)

    assert not instances.exists(name, version, settings)
    m = instance_manifest_factory(
        settings, name, state="started", pgbackrest={"stanza": stanza}
    )
    await instances.apply(settings, m)
    assert "restoring from a pgBackRest backup" in caplog.messages

    # Check that data exists in newly restored instance
    rows = execute(pg_instance, "SELECT * FROM t", dbname="backrest")
    assert rows == [{"s": "created"}]

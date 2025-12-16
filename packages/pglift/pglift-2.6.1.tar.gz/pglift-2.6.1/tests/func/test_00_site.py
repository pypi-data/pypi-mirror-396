# SPDX-FileCopyrightText: 2021 Dalibo
#
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

import subprocess

import pytest

from pglift import systemd
from pglift.settings import Settings
from pglift.settings._pgbackrest import TLSHostRepository
from pglift.system import install

from .pgbackrest import PgbackrestRepoHost, PgbackrestRepoHostTLS

pytestmark = pytest.mark.anyio


async def test_site_configure_check(settings: Settings) -> None:
    assert install.check(settings)


async def test_pgbackrest_repo_tls_service(
    pgbackrest_repo_host: PgbackrestRepoHost | None, settings: Settings
) -> None:
    if pgbackrest_repo_host is None or not isinstance(
        pgbackrest_repo_host, PgbackrestRepoHostTLS
    ):
        pytest.skip("only applicable for pgbackrest TLS repo host")
    if settings.systemd is None or settings.service_manager != "systemd":
        pytest.skip("only applicable for systemd service manager")
    assert await systemd.is_enabled(settings.systemd, "pglift-pgbackrest")


@pytest.mark.usefixtures("require_systemd_tmpfiles_manager")
async def test_systemd_tmpfiles_configuration(settings: Settings) -> None:
    if settings.systemd is None or settings.service_manager != "systemd":
        pytest.skip("only applicable for systemd tmpfiles manager")

    tmpfilesd_managed_dir = [settings.postgresql.socket_directory]
    conf_dir = settings.systemd.tmpfilesd_conf_path
    assert (conf_dir / "pglift-postgresql.conf").exists()

    if settings.patroni is not None:
        tmpfilesd_managed_dir.append(settings.patroni.pid_file.parent)
        assert (conf_dir / "pglift-patroni.conf").exists()
    if settings.temboard is not None:
        tmpfilesd_managed_dir.append(settings.temboard.pid_file.parent)
        assert (conf_dir / "pglift-temboard.conf").exists()
    if settings.pgbackrest is not None and isinstance(
        settings.pgbackrest.repository, TLSHostRepository
    ):
        tmpfilesd_managed_dir.append(settings.pgbackrest.repository.pid_file.parent)
        assert (conf_dir / "pglift-pgbackrest.conf").exists()

    # simulate reboot by removing the socket_directory and pid_file parents and
    # then run systemd-tmpfiles which is usually run at start-up; So no need to
    # re-run site-configure to create those files.
    #
    for d in tmpfilesd_managed_dir:
        d.rmdir()
    assert not all(d.exists() for d in tmpfilesd_managed_dir)
    subprocess.run(["systemd-tmpfiles", "--user", "--create"], check=True)
    assert all((d.exists() and d.is_dir()) for d in tmpfilesd_managed_dir)

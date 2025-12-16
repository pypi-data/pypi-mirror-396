# SPDX-FileCopyrightText: 2021 Dalibo
#
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

from pathlib import Path

import pytest

from pglift import exceptions, systemd
from pglift.models import Instance
from pglift.settings import PostgreSQLVersion, Settings, _temboard
from pglift.systemd import tmpfilesd
from pglift.temboard import (
    get,
    systemd_tmpfilesd_managed_dir,
    systemd_unit_templates,
    systemd_units,
)
from pglift.temboard import impl as temboard
from pglift.temboard.models.system import Service
from pglift.testutil import model_copy_validate


@pytest.fixture
def temboard_settings(settings: Settings) -> _temboard.Settings:
    assert settings.temboard is not None
    return settings.temboard


def test_systemd_units() -> None:
    assert systemd_units() == ["pglift-temboard_agent@.service"]


def test_systemd_unit_templates(
    settings: Settings, temboard_execpath: Path | None
) -> None:
    assert temboard_execpath
    ((name, content),) = list(systemd_unit_templates(settings=settings))
    assert name == "pglift-temboard_agent@.service"
    lines = content.splitlines()
    assert (
        f"ExecStart={temboard_execpath} -c {settings.prefix}/etc/temboard-agent/temboard-agent-%i.conf"
        in lines
    )


def test_install_systemd_tmpfiles_template(settings: Settings) -> None:
    ((name, managed_dir),) = list(systemd_tmpfilesd_managed_dir(settings))
    assert name == "temboard"
    assert managed_dir == settings.run_prefix / "temboard-agent"
    content = systemd.template("pglift-tmpfiles.d.conf").format(path=managed_dir)
    assert content == f"d   {settings.run_prefix}/temboard-agent  0750    -   -   -\n"


def test_manage_systemd_tmpfiles_conf(settings: Settings) -> None:
    assert settings.temboard
    assert settings.systemd
    temboard_conf = settings.systemd.tmpfilesd_conf_path / "pglift-temboard.conf"
    temboard_s = settings.temboard.model_dump()
    temboard_s["pid_file"] = settings.run_prefix / "{name}" / "temboard" / "pid_file"
    s = model_copy_validate(settings, {"temboard": temboard_s})
    assert temboard_conf in list(tmpfilesd.site_configure_list(s))
    temboard_s["pid_file"] = Path("/{name}/temboard/pid_file")
    s = model_copy_validate(settings, {"temboard": temboard_s})
    assert temboard_conf not in list(tmpfilesd.site_configure_list(s))


def test_port(temboard_settings: _temboard.Settings, instance: Instance) -> None:
    with pytest.raises(exceptions.FileNotFoundError):
        temboard.port("nosuchinstance", temboard_settings)

    port = temboard.port(instance.qualname, temboard_settings)
    assert port == 2345

    configpath = Path(str(temboard_settings.configpath).format(name="wrong"))
    configpath.write_text("[empty section]\n")
    with pytest.raises(LookupError, match="port not found in temboard section"):
        temboard.port("wrong", temboard_settings)


def test_password(temboard_settings: _temboard.Settings, instance: Instance) -> None:
    with pytest.raises(exceptions.FileNotFoundError):
        temboard.password("nosuchinstance", temboard_settings)

    password = temboard.password(instance.qualname, temboard_settings)
    assert password == "dorade"

    configpath = Path(str(temboard_settings.configpath).format(name="nopw"))
    configpath.write_text("[postgresql]\n")
    assert temboard.password("nopw", temboard_settings) is None


def test_service(instance: Instance, pg_version: PostgreSQLVersion) -> None:
    s = instance.service(Service)
    assert s is not None
    assert s.name == instance.qualname
    assert s.port == 2345
    logfile = s.logfile()
    assert (
        logfile is not None and logfile.name == f"temboard_agent_{pg_version}-test.log"
    )


@pytest.mark.anyio
async def test_get(instance: Instance) -> None:
    assert (svc := await get(instance)) is not None
    assert (
        svc.port == 2345
        and svc.password is not None
        and svc.password.get_secret_value() == "dorade"
    )

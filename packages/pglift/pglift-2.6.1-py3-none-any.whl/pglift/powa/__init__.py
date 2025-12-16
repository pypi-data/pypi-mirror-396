# SPDX-FileCopyrightText: 2021 Dalibo
#
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

from typing import Annotated

from pgtoolkit.conf import Configuration
from pydantic import Field

from .. import hookimpl, types, util
from ..models import interface
from ..settings import Settings
from .impl import POWA_EXTENSIONS, POWA_LIBRARIES
from .impl import available as available
from .models import interface as i

logger = util.get_logger(__name__)


def register_if(settings: Settings) -> bool:
    return available(settings) is not None


@hookimpl
def instance_settings() -> tuple[str, Configuration]:
    conf = Configuration()
    conf["shared_preload_libraries"] = ", ".join(POWA_LIBRARIES)
    return "powa", conf


@hookimpl
def instance_model() -> types.ComponentModel:
    return types.ComponentModel(
        i.Service.__service__,
        (
            Annotated[
                i.Service,
                Field(
                    description="Configuration for the PoWA service, if enabled in site settings.",
                    validate_default=True,
                ),
            ],
            i.Service(),
        ),
    )


@hookimpl
async def get() -> i.Service:
    return i.Service()


@hookimpl
def rolename(settings: Settings) -> str:
    assert settings.powa
    return settings.powa.role


@hookimpl
def role(settings: Settings, manifest: interface.Instance) -> interface.Role | None:
    name = rolename(settings)
    service_manifest = manifest.service(i.Service)
    return interface.Role(
        name=name, password=service_manifest.password, login=True, superuser=True
    )


@hookimpl
def database(settings: Settings) -> interface.Database | None:
    assert settings.powa
    return interface.Database(
        name=settings.powa.dbname,
        extensions=[{"name": item} for item in POWA_EXTENSIONS],
    )

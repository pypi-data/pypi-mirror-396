# SPDX-FileCopyrightText: 2025 Dalibo
#
# SPDX-License-Identifier: GPL-3.0-or-later
from __future__ import annotations

from collections.abc import Iterator
from contextlib import contextmanager

from .. import patroni, postgresql
from ..models import PostgreSQLInstance, interface
from ..patroni import dcs as dcs_manager
from ..settings import Settings
from . import configuration as configuration_manager
from . import hba as hba_manager
from . import instance as instance_manager
from .configuration import ConfigurationManager as ConfigurationManager
from .hba import HbaManager as HbaManager
from .instance import InstanceManager as InstanceManager


@contextmanager
def from_instance(instance: PostgreSQLInstance) -> Iterator[None]:
    """Alter the ContextVars defining the module (patroni or postgresql) to
    configure, manage the HBA and operate (start, stop, restart,...) the
    instance.
    """
    yield from _set_managers(instance, instance._settings)


@contextmanager
def from_manifest(manifest: interface.Instance, settings: Settings) -> Iterator[None]:
    """Alter the ContextVars defining the module (patroni or postgresql) to
    configure and manage the instance.
    """
    yield from _set_managers(manifest, settings)


def _set_managers(
    instance: PostgreSQLInstance | interface.Instance, settings: Settings
) -> Iterator[None]:
    """Set the managers to patroni if Patroni is available (in settings)
    and managing the instance.
    """
    mngr = (
        patroni
        if patroni.available(settings) and patroni.is_managed(instance)
        else postgresql
    )

    hba_mngr = mngr
    config_mngr = mngr
    if patroni.available(settings) and patroni.is_managed(instance):
        assert settings.patroni
        hba_mngr = (
            patroni
            if settings.patroni.configuration_mode.auth == "local"
            else dcs_manager
        )
        config_mngr = (
            patroni
            if settings.patroni.configuration_mode.parameters == "local"
            else dcs_manager
        )

    with (
        instance_manager.use(mngr),
        hba_manager.use(hba_mngr),
        configuration_manager.use(config_mngr),
    ):
        yield

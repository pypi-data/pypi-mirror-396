# SPDX-FileCopyrightText: 2021 Dalibo
#
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

import importlib
from types import ModuleType
from typing import Any

import pluggy

from . import __name__ as pkgname
from . import hookspecs, settings
from ._compat import Self


class PluginManager(pluggy.PluginManager):
    ns = pkgname
    modules: tuple[str, ...] = (
        "postgresql",
        "databases",
        "passfile",
        "backup",
        "logrotate",
        "pgbackrest",
        "patroni",
        "pgbackrest.repo_host_tls",
        "pgbackrest.repo_host_ssh",
        "pgbackrest.repo_path",
        "prometheus",
        "powa",
        "rsyslog",
        "temboard",
        "systemd.service_manager",
        "systemd.scheduler",
        "systemd.tmpfilesd",
        "hba",
    )

    @classmethod
    def all(cls, specs: ModuleType = hookspecs) -> Self:
        """Return a PluginManager with all modules registered."""
        self = cls(cls.ns)
        self.add_hookspecs(specs)
        for hname in cls.modules:
            hm = importlib.import_module(f"{cls.ns}.{hname}")
            self.register(hm)
        self.check_pending()
        return self

    @classmethod
    def get(cls, settings: settings.Settings, specs: ModuleType = hookspecs) -> Self:
        """Return a PluginManager based on 'settings'."""
        self = cls(cls.ns)
        self.add_hookspecs(specs)
        for hname in cls.modules:
            hm = importlib.import_module(f"{cls.ns}.{hname}")
            if not hasattr(hm, "register_if") or hm.register_if(settings):
                self.register(hm)
        self.check_pending()
        return self

    def register(self, plugin: Any, name: str | None = None) -> Any:
        rv = super().register(plugin, name)
        assert self.get_hookcallers(plugin), f"{plugin} has no hook caller"
        return rv

    def unregister_all(self) -> list[object]:
        unregistered = []
        for __, plugin in self.list_name_plugin():
            self.unregister(plugin)
            unregistered.append(plugin)
        return unregistered

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, self.__class__):
            return NotImplemented
        return self.get_plugins() == other.get_plugins()

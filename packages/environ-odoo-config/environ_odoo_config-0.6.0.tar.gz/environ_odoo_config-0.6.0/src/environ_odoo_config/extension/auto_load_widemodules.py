from functools import cached_property

import importlib_metadata as md
from typing_extensions import Callable, Dict, Set

from environ_odoo_config.config_section.api import (
    CSVKey,
)
from environ_odoo_config.environ import Environ
from environ_odoo_config.odoo_config import OdooConfigExtension, OdooEnvConfig
from environ_odoo_config.utils import NOT_INI_CONFIG

__all__ = ["AutoLoadServerWideModuleExtension", "AutoLoadEntryPoints"]


def _auto_load_entry_point() -> Dict[str, Callable[[Environ], bool]]:
    result: Dict[str, Callable[[Environ], bool]] = {}
    for entry_point in md.entry_points().select(group=_AutoLoadEntryPoints.GROUP_NAME):
        result[entry_point.name] = entry_point.load()
    return result


class _AutoLoadEntryPoints:
    GROUP_NAME = "environ_odoo_config.auto_server_wide_module"

    @cached_property
    def auto_load_ep(self) -> Dict[str, Callable[[Environ], bool]]:
        return _auto_load_entry_point()


AutoLoadEntryPoints = _AutoLoadEntryPoints()


class AutoLoadServerWideModuleExtension(OdooConfigExtension):
    _exclude_auto_load: Set[str] = CSVKey(
        "ODOO_ENV2CONFIG_EXCLUDE_EP_LOAD",
        info="Allow to exclude auto loading server wide module",
        ini_dest=NOT_INI_CONFIG,
    )

    def apply_extension(self, environ: Environ, odoo_config: OdooEnvConfig):
        super().apply_extension(environ, odoo_config)
        for name, auto_load_callback in AutoLoadEntryPoints.auto_load_ep.items():
            if name not in self._exclude_auto_load and auto_load_callback(environ):
                odoo_config.wide_modules.add_module(name)

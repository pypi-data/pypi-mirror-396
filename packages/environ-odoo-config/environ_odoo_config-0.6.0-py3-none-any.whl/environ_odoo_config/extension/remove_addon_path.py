from __future__ import annotations

import logging

from environ_odoo_config.config_section.api import RepeatableKey
from environ_odoo_config.environ import Environ
from environ_odoo_config.odoo_config import OdooConfigExtension, OdooEnvConfig

_logger = logging.getLogger(__name__)

ODOO_DEFAULT_MAX_CONN = 64


class RemoveAddonPathExtension(OdooConfigExtension):
    _order = 999
    _file_name_exclude: set[str] = RepeatableKey("EXCLUDE_ADDON_PATH")

    def apply_extension(self, environ: Environ, odoo_config: "OdooEnvConfig"):
        super().apply_extension(environ, odoo_config)
        odoo_config.addons_path.addons_path = self.filter_exclude_path(odoo_config.addons_path.addons_path)

    def filter_exclude_path(self, base_addon_path):
        valid_addon_path = set()
        _file_name_exclude = self._file_name_exclude or {"EXCLUDE"}
        for addon_path in base_addon_path:
            if not addon_path.exists():
                _logger.info("Ignore %s path don't exist", addon_path)
                continue
            if any((addon_path / exc_fname).exists() for exc_fname in _file_name_exclude):
                # EXCLUDE not exclude submodule discover
                # Only exclude this module from the addon-path
                _logger.info("Ignore %s contains on file %s", addon_path, _file_name_exclude)
                continue
            valid_addon_path.add(addon_path)
        return valid_addon_path

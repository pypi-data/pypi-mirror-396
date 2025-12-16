from __future__ import annotations

import importlib
import logging

from environ_odoo_config.environ import Environ
from environ_odoo_config.odoo_config import OdooConfigExtension, OdooEnvConfig

_logger = logging.getLogger(__name__)

ODOO_DEFAULT_MAX_CONN = 64


class AutoOdooDirNameAddonsToAddonsPath(OdooConfigExtension):
    """
    Automatically add /addons from ODOO_PATH env var.
    This path exist if odoo is installed from a git clone.
    In that case the addons in `$ODOO_PATH/addons` or not added in the current virtual env.

    If Odoo is installed from tar.gs / zip then all the addons are in the venv, we don't need to do that.
    """

    def apply_extension(self, environ: Environ, odoo_config: "OdooEnvConfig"):
        super().apply_extension(environ, odoo_config)
        if (
            odoo_config.misc.odoo_path
            and odoo_config.misc.odoo_path.exists()
            and not importlib.util.find_spec("odoo.addons.web")
        ):
            # here we assume addon `web` is in /addons dir, but not in the current venv
            official_addon_path = odoo_config.misc.odoo_path / "addons"
            if official_addon_path.exists() and official_addon_path.is_dir() and (official_addon_path / "web").exists():
                # This is a addon path we want, then we add it
                odoo_config.addons_path.addons_path.add(official_addon_path)

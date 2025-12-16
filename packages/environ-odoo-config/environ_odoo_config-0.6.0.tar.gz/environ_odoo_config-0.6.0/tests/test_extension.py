import unittest

from environ_odoo_config.entrypoints import EntryPoints
from environ_odoo_config.config_section.http import ConfigConverterHttp
from environ_odoo_config.extension.remove_addon_path import RemoveAddonPathExtension
from environ_odoo_config.odoo_config import OdooEnvConfig, OdooConfigExtension
from environ_odoo_config.environ import Environ
from environ_odoo_config.config_section.api import SimpleKey
from environ_odoo_config.extension.db_max_conn_auto import AutoMaxDatabaseConnExtension
from environ_odoo_config.extension.auto_load_widemodules import AutoLoadServerWideModuleExtension
from environ_odoo_config.extension.auto_odoo_addon_path import AutoOdooDirNameAddonsToAddonsPath


class HttpConverterForce(OdooConfigExtension):

    force_http:bool = SimpleKey("FORCE_ENABLE_HTTP", py_default=False)

    def apply_extension(self, env:Environ, full_config: OdooEnvConfig) -> None:
        self.parse_env(env)
        full_config.http.enable = self.force_http or False
        full_config.http.port = 1234
        full_config.http.interface = "1.2.3.4"


class TestExtensionConverter(unittest.TestCase):

    def test_extension_order(self):
        self.assertEqual([AutoLoadServerWideModuleExtension, AutoOdooDirNameAddonsToAddonsPath, AutoMaxDatabaseConnExtension, RemoveAddonPathExtension], EntryPoints.extension)

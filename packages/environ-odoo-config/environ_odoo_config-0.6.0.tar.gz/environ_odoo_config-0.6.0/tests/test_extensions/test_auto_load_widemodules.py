import unittest
from unittest.mock import MagicMock, patch

from environ_odoo_config.extension.auto_load_widemodules import AutoLoadServerWideModuleExtension
from environ_odoo_config.extension.db_max_conn_auto import AutoMaxDatabaseConnExtension
from environ_odoo_config.odoo_config import OdooEnvConfig
from environ_odoo_config.config_section.database import ConfigConverterDatabase
from environ_odoo_config.environ import Environ

class TestAutoLoadServerWideModule(unittest.TestCase):

    def test_autoload(self):
        environ = Environ({
            "ODOO_ENV2CONFIG_EXCLUDE_EP_LOAD": "",
        })
        config = OdooEnvConfig(environ)
        self.assertFalse(config.wide_modules.loads)
        config.apply_extension(AutoLoadServerWideModuleExtension)
        self.assertSetEqual({"base", "web"}, config.wide_modules.loads)

import unittest
from pathlib import Path

from environ_odoo_config.extension.remove_addon_path import RemoveAddonPathExtension
from environ_odoo_config.odoo_config import OdooEnvConfig
from environ_odoo_config.environ import Environ

class TestRemoveAddonPathExtension(unittest.TestCase):

    def setUp(self):
        self.lib_path = Path(__file__).parent.parent.parent
        self.lib_path_src = self.lib_path / "src"

    def test_normal_addon_path(self):
        addon_path = self.lib_path_src / "odoo" / "addons"
        addon_path_no_exist = self.lib_path_src / "odoo" / "addons" / "not_exist"
        self.assertTrue(addon_path.exists())
        self.assertFalse(addon_path_no_exist.exists())
        conf = OdooEnvConfig(Environ({
            "ADDON_PATH_LOCAL": str(addon_path),
            "ADDON_PATH_LOCAL2": str(addon_path_no_exist)
            }
        ), use_os_environ=False)
        self.assertEqual({addon_path, addon_path_no_exist}, conf.addons_path.addons_path)
        conf.apply_extension(RemoveAddonPathExtension)
        self.assertEqual({addon_path}, conf.addons_path.addons_path, "Remove addon path if not exist on local")

    def test_with_exclude(self):
        addon_path = self.lib_path_src / "odoo" / "addons" / "environ_odoo_config"
        self.assertTrue(addon_path.exists())
        self.assertTrue((addon_path / "__manifest__.py").exists())
        conf = OdooEnvConfig(Environ({
            "ADDON_PATH_LOCAL": str(addon_path),
            "EXCLUDE_ADDON_PATH_FNAME_MANIFEST": "__manifest__.py",
            }
        ), use_os_environ=False)
        self.assertEqual({addon_path}, conf.addons_path.addons_path)
        conf.apply_extension(RemoveAddonPathExtension)
        self.assertFalse(conf.addons_path.addons_path, msg="Rule to exclude path if contain __manifest__.py")

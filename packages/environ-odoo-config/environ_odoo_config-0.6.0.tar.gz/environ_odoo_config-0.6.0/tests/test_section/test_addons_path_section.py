import unittest
from pathlib import Path

from environ_odoo_config.config_writer import CliOption
from environ_odoo_config.environ import Environ
from environ_odoo_config.config_section.addons_path import ConfigConverterAddonsPath
from tests._decorators import MultiOdooVersion


class TestDatabaseOdooConfigSection(unittest.TestCase):
    @MultiOdooVersion.without_args
    def test_default(self):
        conf = ConfigConverterAddonsPath()
        self.assertFalse(conf.addons_path)
        self.assertFalse(CliOption.from_groups(conf))

    @MultiOdooVersion.with_args
    def test_global(self, version):
        conf = ConfigConverterAddonsPath(
            Environ(
                {
                    "ODOO_VERSION": str(version),
                    "ADDON_PATH_LOCAL": "/path/to/module",
                    "ADDON_PATH_LOCAL2": "/path/to/module2",
                }
            )
        )
        flags = CliOption.from_groups(conf)
        self.assertIn("--addons-path", flags)
        self.assertEqual(2, len(conf.addons_path))
        self.assertIn(Path("/path/to/module"), flags["--addons-path"])
        self.assertIn(Path("/path/to/module2"), flags["--addons-path"])

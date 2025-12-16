import unittest
from pathlib import Path

from environ_odoo_config.config_writer import CliOption
from environ_odoo_config.environ import Environ
from environ_odoo_config.config_section.misc import ConfigConverterMisc


class TestConfigConverterMisc(unittest.TestCase):
    def test_default(self):
        conf = ConfigConverterMisc()
        self.assertFalse(conf.unaccent)
        self.assertFalse(conf.with_demo)
        self.assertFalse(conf.stop_after_init)
        self.assertFalse(conf.save_config_file)
        self.assertFalse(CliOption.from_groups(conf))

    def test_global(self):
        conf = ConfigConverterMisc(
            Environ(
                {
                    "UNACCENT": str(True),
                    "STOP_AFTER_INIT": str(True),
                    "SAVE_CONFIG_FILE": str(True),
                    "DATA_DIR": "data",
                }
            )
        )
        self.assertTrue(conf.unaccent)
        self.assertFalse(conf.with_demo)
        self.assertTrue(conf.stop_after_init)
        self.assertTrue(conf.save_config_file)

        flags = CliOption.from_groups(conf)
        self.assertIn("--unaccent", flags)
        self.assertTrue(flags["--unaccent"])

        self.assertIn("--save", flags)
        self.assertTrue(flags["--save"])

        self.assertIn("--stop-after-init", flags)
        self.assertTrue(flags["--stop-after-init"])

        self.assertIn("--data-dir", flags)
        self.assertEqual(flags["--data-dir"], Path("data"))

    def test_datadir_sub_ODOO_PATH(self):
        conf = ConfigConverterMisc(
            Environ(
                {
                    "ODOO_PATH": "/odoo",
                    "DATA_DIR": "data",
                }
            )
        )
        self.assertEqual(conf.data_dir, Path("/odoo/data"))
        flags = CliOption.from_groups(conf)
        self.assertIn("--data-dir", flags)
        self.assertEqual(flags["--data-dir"], Path("/odoo/data"))

    def test_without_demo_FALSE(self):
        conf = ConfigConverterMisc(
            Environ(
                {
                    "WITH_DEMO": "False",
                }
            )
        )
        self.assertFalse(conf.with_demo)
        flags = CliOption.from_groups(conf)
        self.assertNotIn("--without-demo", flags)

    def test_without_demo_True(self):
        """
        Env WITHOUT_DEMO=True handle as --without-demo=all
        Returns:

        """
        conf = ConfigConverterMisc(
            Environ(
                {
                    "WITHOUT_DEMO": "True",
                }
            )
        )
        self.assertSetEqual({"all"}, conf.without_demo)
        flags = CliOption.from_groups(conf)
        self.assertIn("--without-demo", flags)
        self.assertSetEqual({"all"}, flags["--without-demo"])

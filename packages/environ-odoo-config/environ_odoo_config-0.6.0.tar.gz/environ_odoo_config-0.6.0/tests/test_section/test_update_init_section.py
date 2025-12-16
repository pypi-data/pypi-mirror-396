import unittest

from environ_odoo_config.config_writer import CliOption
from environ_odoo_config.environ import Environ
from environ_odoo_config.config_section.update_init import ConfigConverterUpdateInit
from tests._decorators import MultiOdooVersion


class TestUpdateInitSection(unittest.TestCase):
    @MultiOdooVersion.without_args
    def test_default(self):
        conf = ConfigConverterUpdateInit()
        self.assertEqual(set(), conf.install)
        self.assertEqual(set(), conf.update)
        self.assertFalse(CliOption.from_groups(conf))

    @MultiOdooVersion.with_args
    def test_value(self, version: int):
        conf = ConfigConverterUpdateInit(
            Environ(
                {
                    "ODOO_VERSION": str(version),
                    "INIT": " module1 , module2, module3 , module1 ",
                    "UPDATE": " module_a , module_b , module_c, module_b ",
                }
            )
        )
        flags = CliOption.from_groups(conf)

        self.assertSetEqual({"module1", "module2", "module3"}, conf.install)
        self.assertIn("--init", flags)
        self.assertSetEqual({"module1", "module2","module3"}, flags["--init"])

        self.assertSetEqual({"module_a", "module_b", "module_c"}, conf.update)
        self.assertIn("--update", flags)
        self.assertSetEqual({"module_a","module_b","module_c"}, flags["--update"])

    @MultiOdooVersion.with_args
    def test_value_repeat(self, version: int):
        conf = ConfigConverterUpdateInit(
            Environ(
                {
                    "ODOO_VERSION": str(version),
                    "INIT": "module0, module3",
                    "INIT_MODULE1": "True",
                    "INIT_MODULE2": "module2",
                    "UPDATE": " module_a , module_b ,  ",
                    "UPDATE_MODULE_C": "module_c, module_b"
                }
            )
        )
        flags = CliOption.from_groups(conf)

        self.assertSetEqual({"module0", "module1", "module2", "module3"}, conf.install)
        self.assertIn("--init", flags)
        self.assertEqual({"module0", "module1", "module2", "module3"}, flags["--init"])

        self.assertSetEqual({"module_a", "module_b", "module_c"}, conf.update)
        self.assertIn("--update", flags)
        self.assertEqual({"module_a", "module_b", "module_c"}, flags["--update"])

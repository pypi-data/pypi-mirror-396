import unittest

from environ_odoo_config.config_writer import CliOption
from environ_odoo_config.environ import Environ
from environ_odoo_config.config_section.wide_modules import ConfigConverterServerWideModule

class TestHttpOdooConfigSection(unittest.TestCase):

    def test_serer_wide_modules_key(self):
        conf = ConfigConverterServerWideModule(
            Environ({"SERVER_WIDE_MODULES": "module1,module2"})
        )
        self.assertEqual({"module1", "module2"}, conf.loads)
        conf = ConfigConverterServerWideModule(
            Environ({"SERVER_WIDE_MODULES": "module1,module2,module1,base"})
        )
        # Assert no duplicate module and order is keeped
        self.assertEqual({"module1", "module2", "base"}, conf.loads)

    def test_module_name(self):
        conf = ConfigConverterServerWideModule(
            Environ(
                {
                    "LOAD_MODULE_A": str(True),
                    "LOAD_MODULE_0": str(1),
                    "LOAD_MODULE_1": str(False),
                    "LOAD_MODULE_2": str(0),
                }
            )
        )
        # Assert "True" or "1" is valid activate value, and the sort is alpha
        self.assertSetEqual({"module_a", "module_0"}, conf.loads)
        conf = ConfigConverterServerWideModule(
            Environ(
                {
                    "LOAD_QUEUE_JOB": "my_custom_module",
                }
            )
        )
        self.assertSetEqual({"my_custom_module"}, conf.loads)
        conf = ConfigConverterServerWideModule(
            Environ(
                {
                    "LOAD_aslkaskalds": "queue_job",
                }
            )
        )
        self.assertSetEqual({"queue_job"}, conf.loads)
        self.assertEqual({"--load": {'queue_job'}}, CliOption.from_groups(conf))


    def test_serer_wide_modules_mix(self):
        conf = ConfigConverterServerWideModule(
            Environ({
                "SERVER_WIDE_MODULES": "module1,module2",
                "LOAD_QUEUE_JOB": "my_custom_module",
                "LOAD_MODULE1": "True",
            })
        )
        self.assertEqual({"my_custom_module", "module1", "module2"}, conf.loads)
        self.assertEqual({"my_custom_module", "module1", "module2"}, conf.loads)

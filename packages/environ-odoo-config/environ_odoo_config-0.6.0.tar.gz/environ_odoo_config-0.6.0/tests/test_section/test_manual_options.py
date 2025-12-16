import unittest

from environ_odoo_config.config_writer import IniFileConfigWriter

from environ_odoo_config.config_writer import CliOption
from .. import OdooConfigTest
from environ_odoo_config.environ import Environ
from environ_odoo_config.config_section.other_option import ConfigConverterOtherOption
from typing import cast


class TestOdooOptSection(unittest.TestCase):
    def test_default(self):
        conf = ConfigConverterOtherOption()
        self.assertFalse(CliOption.from_groups(conf))

    def test_global(self):
        conf = self._prepare_conf()
        self.assertTrue(conf._other_options)
        self.assertDictEqual(conf._other_options, {
            "MODULES_AUTO_INSTALL_DISABLED": "partner_autocomplete,iap,mail_bot",
            "MODULES_AUTO_INSTALL_ENABLED": "web_responsive",
        })

    def test_write_to_config(self):
        conf = self._prepare_conf()
        config = OdooConfigTest()
        config.options.update({"db_port": "5469"})

        writer = IniFileConfigWriter()
        writer.process_config_group(conf)
        writer.store_data(config)

        self.assertEqual("partner_autocomplete,iap,mail_bot", config["modules_auto_install_disabled"])
        self.assertEqual("web_responsive", config["modules_auto_install_enabled"])
        self.assertEqual("5469", config["db_port"], "pas de changements")

    def _prepare_conf(self) -> ConfigConverterOtherOption:
        return ConfigConverterOtherOption(
            Environ(
                {
                    "OPT_ODOO_MODULES_AUTO_INSTALL_DISABLED": "partner_autocomplete,iap,mail_bot",
                    "OPT_ODOO_MODULES_AUTO_INSTALL_ENABLED": "web_responsive",
                }
            )
        )

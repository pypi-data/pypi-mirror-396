from __future__ import annotations

import logging
import optparse
import os
import unittest

from environ_odoo_config.environ import Environ
from environ_odoo_config.odoo_config import OdooEnvConfig
from environ_odoo_config.odoo_version import OdooVersion, OdooVersionRange
from environ_odoo_config.utils import NOT_INI_CONFIG
from tests import _decorators
try:
    from odoo.tools import config
except ImportError:
    config = None

_logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)

@_decorators.SkipUnless.env_odoo
class TestAllCliValid(unittest.TestCase):
    def setUp(self):
        self.possible_keys = {}
        self.possible_dest = {}
        for group in config.parser.option_groups:
            for option in group.option_list:
                if option.help == optparse.SUPPRESS_HELP:
                    continue

                self.possible_keys[option.get_opt_string()] = option
                if option.dest not in config.blacklist_for_save:
                    self.possible_dest[option.dest] = option


    def test_all_cli_valid(self):
        current_version = Environ(os.environ).odoo_version_type
        allconfig = OdooEnvConfig()
        not_exist = []
        _logger.info("======================================")
        converters = {
            type(allconfig.http) : allconfig.http,
            type(allconfig.addons_path) : allconfig.addons_path,
            type(allconfig.database) : allconfig.database,
            type(allconfig.geoip) : allconfig.geoip,
            type(allconfig.gevent) : allconfig.gevent,
            type(allconfig.i18n) : allconfig.i18n,
            type(allconfig.misc) : allconfig.misc,
            type(allconfig.other_option) : allconfig.other_option,
            type(allconfig.process_limit) : allconfig.process_limit,
            type(allconfig.smtp) : allconfig.smtp,
            type(allconfig.test) : allconfig.test,
            type(allconfig.update_init) : allconfig.update_init,
            type(allconfig.wide_modules) : allconfig.wide_modules,
            type(allconfig.workers) : allconfig.workers,
            type(allconfig.logging) : allconfig.logging,
        }
        for converter_type, converter_inst in converters.items():
            for field_name, key in converter_type.get_fields().items():
                version_key = key.get_by_version(current_version)
                if not version_key:
                    _logger.info("%s : '%s#%s' not valid", current_version, converter_type, field_name)
                    continue
                cli_used = version_key.cli_used()
                if cli_used:
                    valid = self.possible_keys.pop(cli_used, False)
                    _logger.info("%s : Key '%s#%s' process -> %s", current_version, converter_type, field_name, cli_used)
                    if not valid:
                        not_exist.append(f"L'option cli '{cli_used}' n'existe pas dans la version {current_version}. {converter_type}#{field_name}")
                else:
                    _logger.info("%s : Key '%s#%s' no cli", current_version, converter_type, field_name)

                if version_key.ini_section == "options":
                    ini_dest = version_key.ini_dest
                    if ini_dest and ini_dest != NOT_INI_CONFIG:
                        valid = self.possible_dest.pop(ini_dest, False)
                        if not valid:
                            not_exist.append(f"L'option ini '{ini_dest}' or key {version_key} n'existe pas dans la version {current_version}. {converter_type}#{field_name}")
                    else:
                        _logger.info("%s : Key '%s#%s' no ini_dest", current_version, converter_type, field_name)

        _logger.info("======================================")
        if OdooVersionRange(vmin=OdooVersion.V14, vmax=OdooVersion.V16).is_valid(current_version):
            # This options is a deprecated option, and odoo copy it to transient_age_limit
            self.possible_dest.pop("osv_memory_age_limit")
            self.possible_keys.pop("--osv-memory-age-limit")
        if OdooVersionRange(vmin=OdooVersion.V16, vmax=OdooVersion.V17).is_valid(current_version):
            # This options is a deprecated option, and odoo copy it to transient_age_limit
            self.possible_dest.pop("longpolling_port", None)
            self.possible_keys.pop("--longpolling-port")

        self.assertTrue(len(not_exist) == 0, msg="\n".join(not_exist))

        self.assertTrue(len(self.possible_dest) == 0, msg="\n".join(self.possible_dest.keys()))
        self.assertTrue(len(self.possible_keys) == 0, msg="\n".join(self.possible_keys.keys()))

# -*- coding: utf8 -*-
import sys
import unittest
from argparse import ArgumentParser
from unittest.mock import MagicMock, patch

from environ_odoo_config.config_writer import OdooConfigWrapper
from environ_odoo_config.environ import Environ
from environ_odoo_config.odoo_config import OdooEnvConfig
from environ_odoo_config.config_writer import OdooCliWriter
from tests._decorators import MultiOdooVersion

@patch("argparse.ArgumentParser.exit", new=MagicMock)
class TestOdooConfig(unittest.TestCase):

    @MultiOdooVersion.with_env
    def test_args_database(self, environ: Environ):
        db_host = "my-host.com"
        db_name = "my-db"
        db_port = str(5253)
        db_user = "my-user"
        db_password = "py-password"
        environ.mutate({
            "DB_NAME": db_name,
            "DB_HOST": db_host,
            "DB_PORT": db_port,
            "DB_USER": db_user,
            "DB_PASSWORD": db_password,
        })
        odoo_config = OdooEnvConfig(environ, use_os_environ=False)
        odoo_config_mock = MagicMock()
        wrapper = OdooConfigWrapper(
            odoo_config=odoo_config_mock,
            odoo_version=environ.odoo_version_type,
            reset=False # MagickMock Don't need to be reset
        )
        wrapper.write_env_config(odoo_config, writer_type=OdooCliWriter)
        wanted = {
                "--db_host=" + db_host,
                "--db_port=" + db_port,
                "--db_user=" + db_user,
                "--db_password=" + db_password,
                "--database=" + db_name,
        }
        self.assertEqual(len(odoo_config_mock.mock_calls), 1)
        func_name, _args, _kwargs = odoo_config_mock.mock_calls[0]
        self.assertEqual('_parse_config', func_name)
        self.assertFalse(_kwargs)
        self.assertSetEqual(set(_args[0]), wanted | set(_args[0]))

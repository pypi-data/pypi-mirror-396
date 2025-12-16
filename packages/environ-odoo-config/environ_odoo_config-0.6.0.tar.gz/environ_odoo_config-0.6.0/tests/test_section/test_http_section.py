import unittest

from environ_odoo_config.config_section.gevent import ConfigConverterGevent
from environ_odoo_config.odoo_version import OdooVersion
from environ_odoo_config.environ import Environ
from environ_odoo_config.config_writer import CliOption
from environ_odoo_config.config_section.http import ConfigConverterHttp


class TestHttpOdooConfigSection(unittest.TestCase):
    def test_default(self):
        conf = ConfigConverterHttp()
        self.assertIsNone(conf.interface)
        self.assertEqual(0, conf.port)
        self.assertFalse(conf.enable)
        self.assertEqual(CliOption({"--no-http": True}), CliOption.from_groups(conf))

        conf = ConfigConverterGevent()
        self.assertEqual(0, conf.port)
        self.assertEqual(CliOption(), CliOption.from_groups(conf))

    def test_disable(self):
        conf = ConfigConverterHttp()
        conf.enable = True
        self.assertEqual(CliOption(), CliOption.from_groups(conf))
        self.assertIsNone(conf.interface)
        self.assertEqual(0, conf.port)
        self.assertTrue(conf.enable)
        conf = ConfigConverterGevent()
        self.assertEqual(0, conf.longpolling_port)

    def test_global_http_key(self):
        env = Environ(
            {
                "GEVENT_PORT": "4040",
                "HTTP_INTERFACE": "0.1.2.3",
                "HTTP_PORT": "8080",
                "HTTP_ENABLE": "True",
            }
        )
        gevent = ConfigConverterGevent(env)
        http = ConfigConverterHttp(env)
        self.assertEqual("0.1.2.3", http.interface)
        self.assertEqual(8080, http.port)
        self.assertTrue(http.enable)
        self.assertEqual(4040, gevent.longpolling_port)


    def test_enable(self):
        conf = ConfigConverterHttp(
            Environ(
                {
                    "HTTP_ENABLE": "True",
                }
            )
        )
        self.assertEqual(CliOption(), CliOption.from_groups(conf))
        self.assertIsNone(conf.interface)
        self.assertEqual(0, conf.port)
        self.assertTrue(conf.enable)
        conf = ConfigConverterHttp(
            Environ(
                {
                    "HTTP_ENABLE": "False",
                }
            )
        )
        self.assertEqual(CliOption({"--no-http": True}), CliOption.from_groups(conf))
        self.assertIsNone(conf.interface)
        self.assertEqual(0, conf.port)
        self.assertFalse(conf.enable)

    def test_longpolling_port_before_v16(self):
        for odoo_version in OdooVersion.V15.max():
            with self.subTest(odoo_version):
                env = Environ(
                    {
                        "ODOO_VERSION": int(odoo_version),
                        "GEVENT_PORT": "4040",
                        "HTTP_INTERFACE": "0.1.2.3",
                        "HTTP_PORT": "8080",
                        "HTTP_ENABLE": "True",
                    }
                )
                http = ConfigConverterHttp(env)
                gevent = ConfigConverterGevent(env)
                self.assertEqual("0.1.2.3", http.interface)
                self.assertEqual(8080, http.port)
                self.assertTrue(http.enable)
                self.assertEqual(4040, gevent.longpolling_port)
                self.assertDictEqual(
                    CliOption(
                        {
                            "--longpolling-port": 4040,
                            "--http-port": 8080,
                            "--http-interface": "0.1.2.3",
                        }
                    ),
                    CliOption.from_groups(gevent, http),
                 msg=f"Error option in version {env.odoo_version}")

    def test_longpolling_port_after_v16(self):
        for odoo_version in OdooVersion.V16.min():
            with self.subTest(odoo_version):
                env = Environ(
                    {
                        "ODOO_VERSION": int(odoo_version),
                        "GEVENT_PORT": "4040",
                        "HTTP_INTERFACE": "0.1.2.3",
                        "HTTP_PORT": "8080",
                        "HTTP_ENABLE": "True",
                    }
                )
                http = ConfigConverterHttp(env)
                gevent = ConfigConverterGevent(env)
                self.assertEqual("0.1.2.3", http.interface)
                self.assertEqual(8080, http.port)
                self.assertTrue(http.enable)
                self.assertEqual(4040, gevent.longpolling_port)
                self.assertDictEqual(
                    CliOption(
                        {
                            "--gevent-port": 4040,
                            "--http-port": 8080,
                            "--http-interface": "0.1.2.3",
                        }
                    ),
                    CliOption.from_groups(gevent, http),
                )

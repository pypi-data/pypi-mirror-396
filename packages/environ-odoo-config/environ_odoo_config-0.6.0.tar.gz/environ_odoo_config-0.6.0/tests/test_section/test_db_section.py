import unittest

from environ_odoo_config.config_section.database import ConfigConverterDatabase
from environ_odoo_config.environ import Environ

class TestDatabaseOdooConfigSection(unittest.TestCase):
    def test_default(self):
        conf = ConfigConverterDatabase()
        self.assertIsNone(conf.name)
        self.assertIsNone(conf.host)
        self.assertEqual(0, conf.max_conn)
        self.assertIsNone(conf.filter)
        self.assertIsNone(conf.user)
        self.assertEqual(0, conf.port)
        self.assertIsNone(conf.password)
        self.assertTrue(conf.show)

    def test_global(self):
        conf = ConfigConverterDatabase(
            Environ(
                {
                    "DB_FILTER": "db_filter.*",
                    "DB_NAME": "db_name",
                    "DB_HOST": "db_host",
                    "DB_MAX_CONN": "20",
                    "DB_PORT": "1234",
                    "DB_USER": "db_user",
                    "DB_PASSWORD": "db_password",
                    "LIST_DB": "True",
                }
            )
        )
        self.assertEqual("db_filter.*", conf.filter)
        self.assertEqual("db_host", conf.host)
        self.assertEqual(20, conf.max_conn)
        self.assertEqual("db_name", conf.name)
        self.assertEqual("db_user", conf.user)
        self.assertEqual(1234, conf.port)
        self.assertEqual("db_password", conf.password)
        self.assertTrue(conf.show)

    def test_db_name(self):
        """
        If a <DB_NAME> is filled and no  <DB_FILTER> then <DB_FILTER> is set to <DB_NAME>
        and DatabaseOdooConfigSection#show is set to false
        """
        conf = ConfigConverterDatabase(
            Environ(
                {
                    "DB_NAME": "db_name",
                }
            )
        )
        self.assertEqual("db_name", conf.name)
        self.assertIsNone(conf.filter)
        self.assertTrue(conf.show)

        self.assertIsNone(conf.host)
        self.assertIsNone(conf.user)
        self.assertEqual(0, conf.port)
        self.assertIsNone(conf.password)
        self.assertEqual(0, conf.max_conn)

    def test_db_filter(self):
        """
        If <DB_FILTER> is set but no <DB_NAME> then :
        - DatabaseOdooConfigSection#name is None
        - DatabaseOdooConfigSection#show is True
        """
        conf = ConfigConverterDatabase(
            Environ(
                {
                    "DB_FILTER": "db_filter.*",
                }
            )
        )
        self.assertEqual("db_filter.*", conf.filter)
        self.assertTrue(conf.show)
        self.assertIsNone(conf.name)

        self.assertIsNone(conf.host)
        self.assertIsNone(conf.user)
        self.assertEqual(0, conf.port)
        self.assertIsNone(conf.password)
        self.assertEqual(0, conf.max_conn)

    def test_db_name_with_show(self):
        """
        If <DB_NAME> is set but no <DB_FILTER> and <SHOW_DB> then:
        - DatabaseOdooConfigSection#name eq <DB_NAME>
        - DatabaseOdooConfigSection#filter eq <DB_NAME> + '.*'
        - DatabaseOdooConfigSection#show is True
        """
        conf = ConfigConverterDatabase(
            Environ(
                {
                    "DB_NAME": "db_name",
                    "LIST_DB": "True",
                }
            )
        )
        self.assertEqual("db_name", conf.name)
        self.assertIsNone(conf.filter)
        self.assertTrue(conf.show)

        self.assertIsNone(conf.host)
        self.assertIsNone(conf.user)
        self.assertEqual(0, conf.port)
        self.assertIsNone(conf.password)
        self.assertEqual(0, conf.max_conn)

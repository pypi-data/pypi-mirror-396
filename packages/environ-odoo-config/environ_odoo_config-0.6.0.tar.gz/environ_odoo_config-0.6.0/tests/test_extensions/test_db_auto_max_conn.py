import unittest
from unittest.mock import MagicMock, patch

from environ_odoo_config.extension.db_max_conn_auto import AutoMaxDatabaseConnExtension
from environ_odoo_config.odoo_config import OdooEnvConfig
from environ_odoo_config.config_section.database import ConfigConverterDatabase
from environ_odoo_config.environ import Environ

class TestDatabaseAutoMaxConnectionExtension(unittest.TestCase):

    def test_max_con_auto(self):
        """
        By default there 3 workers
        If <DB_MAX_CONN_MODE> is set to "AUTO" and a <DB_MAX_CONN> is provided then:
        if <DB_MAX_CONN> superior to AUTO computed value
        - DatabaseOdooConfigSection#max_conn eq <DB_MAX_CONN>
        """
        conf = OdooEnvConfig(Environ({
                "DB_MAX_CONN": 100,
                "AUTO_DB_MAX_CONN": str(False),
                # "AUTO_DB_MAX_CONN_THRESHOLD": 100,
                # "AUTO_DB_MAX_CONN_WORKER": 100,
            }
        ), use_os_environ=False)
        conf.apply_extension(AutoMaxDatabaseConnExtension)
        self.assertEqual(100, conf.database.max_conn)

    def test_max_conn_auto_psycopg2_no_connect(self):
        conf = OdooEnvConfig(Environ({
            # "DB_MAX_CONN": 100,
            # "AUTO_DB_MAX_CONN": str(False),
            # "AUTO_DB_MAX_CONN_THRESHOLD": 100,
            # "AUTO_DB_MAX_CONN_WORKER": 100,
        }
        ), use_os_environ=False)
        try:
            # Force patch psycopg2.connect if package exist in venv
            # in case the test are run with odoo dependencies
            import psycopg2
            with patch("psycopg2.connect", new=MagicMock(side_effect=ValueError())):
                conf.apply_extension(AutoMaxDatabaseConnExtension)
        except ImportError:
            conf.apply_extension(AutoMaxDatabaseConnExtension)

        self.assertEqual(0, conf.database.max_conn)

    def test_max_conn_auto_psycopg2(self):
        conf = OdooEnvConfig(Environ({
            "DB_MAX_CONN": 100,
            # "AUTO_DB_MAX_CONN": str(False),
            # "AUTO_DB_MAX_CONN_THRESHOLD": 100,
            # "AUTO_DB_MAX_CONN_WORKER": 100,
        }
        ), use_os_environ=False)
        with patch("environ_odoo_config.extension.db_max_conn_auto.AutoMaxDatabaseConnExtension._get_maxconn_psycopg", new=MagicMock(return_value=45)):
            conf.apply_extension(AutoMaxDatabaseConnExtension)

        self.assertEqual(42, conf.database.max_conn)

    def test_threshold_25(self):
        conf = OdooEnvConfig(Environ({
            # "DB_MAX_CONN": 100,
            # "AUTO_DB_MAX_CONN": str(False),
            "AUTO_DB_MAX_CONN_THRESHOLD": 25,
            # "AUTO_DB_MAX_CONN_WORKER": 100,
        }
        ), use_os_environ=False)
        with patch("environ_odoo_config.extension.db_max_conn_auto.AutoMaxDatabaseConnExtension._get_maxconn_psycopg", new=MagicMock(return_value=50)):
            conf.apply_extension(AutoMaxDatabaseConnExtension)

        self.assertEqual(37, conf.database.max_conn)

    def test_threshold_more_than_50(self):
        conf = OdooEnvConfig(Environ({
            # "DB_MAX_CONN": 100,
            # "AUTO_DB_MAX_CONN": str(False),
            "AUTO_DB_MAX_CONN_THRESHOLD": 75,
            # "AUTO_DB_MAX_CONN_WORKER": 100,
        }
        ), use_os_environ=False)
        with patch("environ_odoo_config.extension.db_max_conn_auto.AutoMaxDatabaseConnExtension._get_maxconn_psycopg", new=MagicMock(return_value=50)):
            conf.apply_extension(AutoMaxDatabaseConnExtension)

        self.assertEqual(25, conf.database.max_conn, msg="Max threshold is 50%, ")

    def test_max_conn_worker_1(self):
        conf = OdooEnvConfig(Environ({
            "WORKER_HTTP": 2,
            "AUTO_DB_MAX_CONN_BY_WORKER": 10, # Set a max of 9 conn per worker
            # "AUTO_DB_MAX_CONN": str(False),
            # "AUTO_DB_MAX_CONN_THRESHOLD": 75,
            # "AUTO_DB_MAX_CONN_WORKER": 100,
        }
        ), use_os_environ=False)
        with patch("environ_odoo_config.extension.db_max_conn_auto.AutoMaxDatabaseConnExtension._get_maxconn_psycopg", new=MagicMock(return_value=50)):
            conf.apply_extension(AutoMaxDatabaseConnExtension)
        self.assertEqual(9, conf.database.max_conn, msg="50 - 5% / 5 (http + 2 cron + 1 gevent) = 9 > 10")

    def test_max_conn_worker_min(self):
        conf = OdooEnvConfig(Environ({
            "WORKER_HTTP": 9,
            # "DB_MAX_CONN": 100,
            # "AUTO_DB_MAX_CONN": str(False),
            # "AUTO_DB_MAX_CONN_THRESHOLD": 75,
            # "AUTO_DB_MAX_CONN_WORKER": 100,
        }
        ), use_os_environ=False)
        with patch("environ_odoo_config.extension.db_max_conn_auto.AutoMaxDatabaseConnExtension._get_maxconn_psycopg", new=MagicMock(return_value=50)):
            conf.apply_extension(AutoMaxDatabaseConnExtension)
        self.assertEqual(3, conf.database.max_conn, msg="50 - 5% / 12 (9 http + 2 cron + 1 gevent) = 2 < 3 (min to work)")

    def test_max_conn_worker_force(self):
        conf = OdooEnvConfig(Environ({
            "WORKER_HTTP": 20,
            # "AUTO_DB_MAX_CONN_WORKER": 2,
            # "AUTO_DB_MAX_CONN": str(False),
            # "AUTO_DB_MAX_CONN_THRESHOLD": 75,
            # "AUTO_DB_MAX_CONN_WORKER": 100,
        }
        ), use_os_environ=False)
        with patch("environ_odoo_config.extension.db_max_conn_auto.AutoMaxDatabaseConnExtension._get_maxconn_psycopg", new=MagicMock(return_value=50)):
            conf.apply_extension(AutoMaxDatabaseConnExtension)
        self.assertEqual(3, conf.database.max_conn, msg="50 - 5% / 12 (9 http + 2 cron + 1 gevent) but AUTO_DB_MAX_CONN_BY_WORKER=5")

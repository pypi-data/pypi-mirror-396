import unittest

from environ_odoo_config.config_writer import CliOption
from environ_odoo_config.environ import Environ
from environ_odoo_config.config_section.workers import ConfigConverterWorkers


class TestConfigConverterWorkers(unittest.TestCase):
    def test_default(self):
        conf = ConfigConverterWorkers()
        self.assertEqual(0, conf.worker_http)
        self.assertEqual(0, conf.cron)
        self.assertEqual(0, conf.total)
        conf.parse_env(Environ())
        self.assertEqual(0, conf.worker_http)
        self.assertEqual(0, conf.cron)
        self.assertEqual(0, conf.total)
        self.assertFalse(CliOption.from_groups(conf))

    def test_WORKER_HTTP(self):
        conf = ConfigConverterWorkers()
        self.assertEqual(0, conf.worker_http)
        self.assertEqual(0, conf.cron)
        self.assertEqual(0, conf.total)
        conf.parse_env(Environ({"WORKER_HTTP": str(10)}))
        self.assertEqual(10, conf.worker_http)
        self.assertEqual(0, conf.cron)
        self.assertEqual(10, conf.total)
        self.assertEqual(CliOption({"--workers": 10}), CliOption.from_groups(conf))

    def test_priority(self):
        conf = ConfigConverterWorkers(
            Environ(
                {
                    "WORKER_HTTP": str(2),
                    "WORKER_JOB": str(3),
                }
            )
        )
        self.assertEqual(2, conf.worker_http)
        self.assertEqual(0, conf.cron)  # default value
        self.assertEqual(2, conf.total)

    def test_usecase_worker(self):
        conf = ConfigConverterWorkers(
            Environ(
                {
                    "WORKER_HTTP": str(2),
                    "WORKER_JOB": str(3),
                    "WORKER_CRON": str(1),
                }
            )
        )
        self.assertEqual(2, conf.worker_http)
        self.assertEqual(1, conf.cron)
        self.assertEqual(3, conf.total)
        self.assertEqual(
            CliOption({"--workers": 2, "--max-cron-threads": 1}), CliOption.from_groups(conf)
        )

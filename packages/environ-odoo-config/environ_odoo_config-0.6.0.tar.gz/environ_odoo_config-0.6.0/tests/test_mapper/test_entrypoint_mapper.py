from unittest import TestCase
from environ_odoo_config.entrypoints import EntryPoints

class TestEntrypointMapper(TestCase):

    def test_load(self):
        self.assertEqual(len(EntryPoints.mappers), 3, "2 postgrsql + 1 compatibility")
        self.assertEqual(len(EntryPoints.extension), 4, msg="auto_load + max_conn + remove_addon")

# -*- coding: utf8 -*-
import unittest

from environ_odoo_config.entrypoints import EntryPoints
from environ_odoo_config.environ import Environ, new_environ
from environ_odoo_config.extension import postgresql_mapper


class TestPostgresqlMapper(unittest.TestCase):
    maxDiff=None

    def test_empty(self):
        """
        Assert By default the mapper don't add default value
        """
        result = postgresql_mapper.postgresql_env_libpq(Environ())
        for key_result, value in result.items():
            self.assertIsNone(value, "Value of key [%s] is not None" % key_result)
        result = postgresql_mapper.postgresql_env_docker(Environ())
        for key_result, value in result.items():
            self.assertIsNone(value, "Value of key [%s] is not None" % key_result)

    def test_libpq_mapper(self):
        """
        The Mappers d'ont have _order defined like extension.
        So the order is only alphabetical, base on the name of the entrypoint

        We ensure here, we have the expected behavior
        """
        base_environ = Environ({
            "PGHOST": "__PGHOST",
            "PGPORT": "__PGPORT",
            "PGDATABASE": "__PGDATABASE",
            "PGUSER": "__PGUSER",
            "PGPASSWORD": "__PGPASSWORD",
            "PGAPPNAME": "__PGAPPNAME",
            "PGSSLMODE": "__PGSSLMODE",
        })
        environ = postgresql_mapper.postgresql_env_libpq(base_environ)
        self.assertDictEqual(environ, {**base_environ, **{
        "DB_HOST": "__PGHOST",
        "DB_PORT": "__PGPORT",
        "DB_NAME": "__PGDATABASE",
        "DB_USER": "__PGUSER",
        "DB_PASSWORD": "__PGPASSWORD",
        "DB_APP_NAME": "__PGAPPNAME",
        "DB_SSL_MODE": "__PGSSLMODE",
    }})

    def test_docker_mapper(self):
        """
        The Mappers d'ont have _order defined like extension.
        So the order is only alphabetical, base on the name of the entrypoint

        We ensure here, we have the expected behavior
        """
        base_environ = Environ({
            "POSTGRES_DB": "__POSTGRES_DB",
            "POSTGRES_USER": "__POSTGRES_USER",
            "POSTGRES_PASSWORD": "__POSTGRES_PASSWORD",
        })
        environ = postgresql_mapper.postgresql_env_docker(base_environ)
        self.assertDictEqual(environ, {**base_environ, **{
        "DB_NAME": "__POSTGRES_DB",
        "DB_USER": "__POSTGRES_USER",
        "DB_PASSWORD": "__POSTGRES_PASSWORD",
    }})

    def test_postgres_mapper(self):
        """
        The Mappers d'ont have _order defined like extension.
        So the order is only alphabetical, base on the name of the entrypoint

        We ensure here, we have the expected behavior
        """
        base_environ = {
            "PGHOST": "__PGHOST",
            "PGPORT": "__PGPORT",
            # "PGDATABASE": "__PGDATABASE", Don't set this value to use POSTGRES_DB
            "PGUSER": "__PGUSER",
            "PGPASSWORD": "__PGPASSWORD",
            "PGAPPNAME": "__PGAPPNAME",
            "PGSSLMODE": "__PGSSLMODE",
            "POSTGRES_DB": "__POSTGRES_DB",
            "POSTGRES_USER": "__POSTGRES_USER",
            "POSTGRES_PASSWORD": "__POSTGRES_PASSWORD",
        }
        environ = Environ.new(base_environ, use_os_environ=False, apply_mapper=True)
        self.assertDictEqual(environ, {**environ, **{
            "DB_HOST": "__PGHOST",
            "DB_PORT": "__PGPORT",
            "DB_NAME": "__POSTGRES_DB",
            "DB_USER": "__PGUSER",
            "DB_PASSWORD": "__PGPASSWORD",
            "DB_APP_NAME": "__PGAPPNAME",
            "DB_SSL_MODE": "__PGSSLMODE",
    }})

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from environ_odoo_config.environ import Environ


def postgresql_env_libpq(curr_env: "Environ") -> "Environ":
    """
    Map environ supported by the official postgresql libpq env vars
    Taken from : https://www.postgresql.org/docs/current/libpq-envars.html

    """
    return curr_env + {
        "DB_HOST": curr_env.gets("DB_HOST", "PGHOST"),
        "DB_PORT": curr_env.gets("DB_PORT", "PGPORT"),
        "DB_NAME": curr_env.gets("DB_NAME", "PGDATABASE"),
        "DB_USER": curr_env.gets("DB_USER", "PGUSER"),
        "DB_PASSWORD": curr_env.gets("DB_PASSWORD", "PGPASSWORD"),
        "DB_APP_NAME": curr_env.gets("DB_APP_NAME", "PGAPPNAME"),
        "DB_SSL_MODE": curr_env.gets("DB_SSL_MODE", "PGSSLMODE"),
    }


def postgresql_env_docker(curr_env: "Environ") -> "Environ":
    """
    Map environ supported by the official postgresql service to odoo standard config
    Taken from : https://hub.docker.com/_/postgres#environment-variables
    """
    return curr_env + {
        "DB_NAME": curr_env.gets("DB_NAME", "POSTGRES_DB"),
        "DB_USER": curr_env.gets("DB_USER", "POSTGRES_USER"),
        "DB_PASSWORD": curr_env.gets("DB_PASSWORD", "POSTGRES_PASSWORD"),
    }

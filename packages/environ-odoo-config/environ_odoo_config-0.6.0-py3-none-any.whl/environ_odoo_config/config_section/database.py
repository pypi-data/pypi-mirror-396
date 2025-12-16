import enum
from pathlib import Path

from environ_odoo_config.odoo_version import OdooVersion

from .api import CliOnly, EnumKey, OdooConfigGroup, SimpleKey


class DbSslMode(enum.Enum):
    DISABLE = "disable"
    ALLOW = "allow"
    PREFER = "prefer"
    REQUIRE = "require"
    VERIFY_CA = "verify-ca"
    VERIFY_FULL = "verify-full"


class ConfigConverterDatabase(OdooConfigGroup):
    """
    convert environment variable related to the PostgreSQL database
    """

    _name = "database"
    _opt_group = "Database Configuration"
    pg_path: Path = CliOnly("--pg_path", info="specify the pg executable path")
    # DB Section
    name: str = SimpleKey("DB_NAME", cli=["-d", "--database"], info="specify the database name", ini_dest="db_name")
    host: str = SimpleKey("DB_HOST", cli="--db_host", info="specify the database host", ini_dest="db_host")
    port: int = SimpleKey("DB_PORT", cli=["--db_port"], info="specify the database port", ini_dest="db_port")
    user: str = SimpleKey("DB_USER", cli=["-r", "--db_user"], info="specify the database user name", ini_dest="db_user")
    password: str = SimpleKey(
        "DB_PASSWORD", cli=["-w", "--db_password"], info="specify the database password", ini_dest="db_password"
    )
    app_name: str = SimpleKey(
        "DB_APP_NAME",
        cli=["--db_app_name"],
        info="specify the application name in the database, {pid} is substituted by the process pid",
        ini_dest="db_app_name",
        odoo_version=OdooVersion.V19.min(),
    )
    max_conn: int = SimpleKey(
        "DB_MAX_CONN",
        cli="--db_maxconn",
        info="specify the maximum number of physical connections to PostgreSQL",
        ini_dest="db_maxconn",
    )

    replica_host: str = SimpleKey(
        "DB_REPLICA_HOST",
        cli="--db_replica_host",
        info="specify the replica host. Specify an empty db_replica_host to use the default unix socket.",
        odoo_version=OdooVersion.V18.min(),
        ini_dest="db_replica_host",
    )
    replica_port: int = SimpleKey(
        "DB_REPLICA_PORT",
        cli="--db_replica_port",
        info="specify the replica port",
        odoo_version=OdooVersion.V18.min(),
        ini_dest="db_replica_port",
    )
    template: str = SimpleKey(
        "DB_TEMPLATE",
        cli="--db-template",
        info="specify a custom database template to create a new database",
        ini_dest="db_template",
    )
    sslmode: DbSslMode = EnumKey(
        DbSslMode,
        "DB_SSL_MODE",
        cli="--db_sslmode",
        info="specify the database ssl connection mode (see PostgreSQL documentation)",
        ini_dest="db_sslmode",
    )
    # Security-related options
    list_db: bool = SimpleKey(
        "LIST_DB",
        cli=["--no-database-list"],
        info="""Disable the ability to obtain or view the list of databases.
        Also disable access to the database manager and selector,
        so be sure to set a proper --database parameter first""",
        py_default=True,
    )
    filter: str = SimpleKey(
        "DB_FILTER",
        cli="--db-filter",
        info="""Regular expressions for filtering available databases for Web UI.
        The expression can use %d (domain) and %h (host) placeholders.""",
        ini_dest="dbfilter",
    )

    @property
    def show(self) -> bool:
        return self.list_db

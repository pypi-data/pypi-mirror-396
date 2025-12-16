import logging

from environ_odoo_config.config_section.api import SimpleKey
from environ_odoo_config.environ import Environ
from environ_odoo_config.odoo_config import OdooConfigExtension, OdooEnvConfig

_logger = logging.getLogger(__name__)

ODOO_DEFAULT_MAX_CONN = 64


class AutoMaxDatabaseConnExtension(OdooConfigExtension):
    _order = 999
    auto_db_max_conn: bool = SimpleKey("AUTO_DB_MAX_CONN", py_default=True)
    auto_db_max_conn_threshold: int = SimpleKey("AUTO_DB_MAX_CONN_THRESHOLD", py_default=5)
    auto_db_max_conn_by_worker: int = SimpleKey("AUTO_DB_MAX_CONN_BY_WORKER", py_default=5)
    _compute_max_conn: int = 0

    def _get_maxconn_psycopg(self, odoo_config: OdooEnvConfig):
        try:
            import psycopg2

            dbname = odoo_config.database.name or "postgres"
            user = odoo_config.database.user
            password = odoo_config.database.password
            host = odoo_config.database.host
            port = odoo_config.database.port
            with psycopg2.connect(dbname=dbname, user=user, password=password, port=port, host=host) as conn:
                conn.set_session(readonly=True)
                with conn.cursor() as cursor:
                    cursor.execute("""select "setting" from pg_settings where name='max_connections'""")
                    (value,) = cursor.fetchone()
            return int(value)
        except Exception:
            _logger.info("Can't fetch max_connections from pg_settings ")
        return -1

    def _get_maxconn_worker(self, max_conn, odoo_config: OdooEnvConfig):
        # in worker mode, then the number of connection is used for each worker
        # Add 1 for gevent
        nb_worker = odoo_config.workers.worker_http + (odoo_config.workers.worker_cron or 2) + 1
        _logger.info(
            "Max conn global is %s to dispatch for :  %s workers (%s http + %s cron + 1 gevent)",
            max_conn,
            nb_worker,
            odoo_config.workers.worker_http,
            odoo_config.workers.worker_cron or 2,
        )
        _logger.info("Worker Mode => max connection are for each pid")
        return int(max(min(self.auto_db_max_conn_by_worker, max_conn // nb_worker), 3))

    def apply_extension(self, environ: Environ, odoo_config: OdooEnvConfig):
        super().apply_extension(environ, odoo_config)
        if not self.auto_db_max_conn:
            return
        initial_max_conn = odoo_config.database.max_conn
        # Get max_conn from postgresql database
        max_conn = self._get_maxconn_psycopg(odoo_config)
        max_conn = self._apply_threshold(max_conn) if max_conn else initial_max_conn

        if odoo_config.workers.worker_http > 0:
            max_conn = self._get_maxconn_worker(max_conn, odoo_config)
        odoo_config.database.max_conn = max_conn or initial_max_conn

    def _apply_threshold(self, max_conn: int):
        if not max_conn:
            return max_conn
        auto_db_max_conn_threshold = min(self.auto_db_max_conn_threshold, 50)
        # apply threshold, (pg_activity, metrics, other) default 5%
        return int(max_conn * (1 - auto_db_max_conn_threshold / 100))

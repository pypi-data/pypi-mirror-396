import enum

from environ_odoo_config.config_section.api import EnumKey
from environ_odoo_config.environ import Environ
from environ_odoo_config.odoo_config import OdooConfig, OdooConfigExtension


class MaxConnMode(enum.Enum):
    """
    Mode to compute the max_conn attribute
    Attributes:
        AUTO: the max_conn is compute from the number of worker defined
        in [`WorkerConfig`][odoo_env_config.section.worker_section]
        FIXED: the value is taken from `"DB_MAX_CONN"` is [][os.environ]
    """

    AUTO = "AUTO"
    FIXED = "FIXED"


def compute_auto_maxconn(curr_env: Environ) -> int:
    """
    Compute the current maxconn based on the number of worker
    Odoo recomendation is ~= Number of worker * 1.5.
    Args:
        curr_env: The current Env

    Returns:
        The number of worker * 1.5
    """
    # nb_workers = ConfigConverterWorkers(curr_env).workers
    nb_workers = 1
    return nb_workers + int(nb_workers // 2)


class AutoLoadServerWideModule(OdooConfigExtension):
    _max_connections_mode: MaxConnMode = EnumKey(MaxConnMode, "DB_MAX_CONN_MODE", py_default=MaxConnMode.FIXED)

    def apply_extension(self, environ: Environ, odoo_config: OdooConfig):
        """
        Compute the current maxconn based on the number of worker
        Odoo recomendation is ~= Number of worker * 1.5.
        """
        if self._max_connections_mode == MaxConnMode.AUTO and odoo_config.worker_http:
            nb_workers = odoo_config.worker_http + int(odoo_config.worker_http // 2)
            self.max_conn = max(self.max_conn, nb_workers)

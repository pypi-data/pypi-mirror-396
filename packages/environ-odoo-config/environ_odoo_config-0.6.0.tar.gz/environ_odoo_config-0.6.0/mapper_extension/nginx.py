from environ_odoo_config.config_section.api import SimpleKey
from environ_odoo_config.environ import Environ
from environ_odoo_config.odoo_config import OdooConfigExtension, OdooEnvConfig


class AutoLoadServerWideModule(OdooConfigExtension):
    _activate_nginx: bool = SimpleKey("ACTIVATE_NGINX", py_default=False)

    def apply_extension(self, environ: Environ, odoo_config: OdooEnvConfig):
        if self._activate_nginx:
            odoo_config.gevent.port = 8072
            odoo_config.http.port = 8069
            odoo_config.http.interface = "127.0.0.1"
            odoo_config.http.proxy_mode = True

from typing_extensions import Union

from environ_odoo_config.config_writer import CliOption
from environ_odoo_config.odoo_version import OdooVersion

from .api import (
    OdooConfigGroup,
    SimpleKey,
)


class ConfigConverterHttp(OdooConfigGroup):
    """
    convert environment variable related to the Odoo Http configuration
    """

    _opt_group = "Http Configuration"

    enable: bool = SimpleKey(
        "HTTP_ENABLE",
        cli="--no-http",
        ini_dest="http_enable",
        # cli_use_filter=negate_bool,
        info="Disable the HTTP and Longpolling services entirely",
        py_default=False,
        ini_default=True,
    )

    _http_enable_exist: bool = SimpleKey("HTTP_ENABLE")
    interface: str = SimpleKey(
        "HTTP_INTERFACE",
        cli="--http-interface",
        ini_dest="http_interface",
        info="Listen interface address for HTTP services. Keep empty to listen on all interfaces (0.0.0.0)",
    )
    port: int = SimpleKey(
        "HTTP_PORT",
        cli="--http-port",
        ini_dest="http_port",
        info="Listen port for the main HTTP service. Keep empty to listen on all interfaces (0.0.0.0)",
    )
    proxy_mode: bool = SimpleKey(
        "PROXY_MODE",
        cli="--proxy-mode",
        info="""Activate reverse proxy WSGI wrappers (headers rewriting).
        Only enable this when running behind a trusted web proxy!""",
    )
    x_sendfile: bool = SimpleKey(
        "X_SENDFILE",
        cli="--x-sendfile",
        info="""Activate X-Sendfile (apache) and X-Accel-Redirect (nginx)
        HTTP response header to delegate the delivery of large
        files (assets/attachments) to the web server.""",
        odoo_version=OdooVersion.V16.min(),
    )

    def _get_cli_option(self) -> Union["CliOption", None]:
        if not self.enable:
            return CliOption({"--no-http": True})
        return super()._get_cli_option()

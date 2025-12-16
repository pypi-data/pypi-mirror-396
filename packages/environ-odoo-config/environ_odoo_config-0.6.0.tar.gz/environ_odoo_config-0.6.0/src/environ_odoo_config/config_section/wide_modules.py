from typing_extensions import Callable, Dict, Set

from environ_odoo_config.environ import Environ

from .api import (
    CSVKey,
    OdooConfigGroup,
    RepeatableKey,
)


class ConfigConverterServerWideModule(OdooConfigGroup):
    """
    convert environment variable related to the server_wide_module configuration
    """

    _opt_group = "Server wide module Configuration"
    __auto_load: Dict[str, Callable[[Environ], bool]] = {}

    _legacy_load: Set[str] = CSVKey("SERVER_WIDE_MODULES", info="old version of the list of the server-wide modules")
    loads: Set[str] = RepeatableKey(
        "LOAD", cli=["--load"], ini_dest="server_wide_modules", info="list of server-wide modules."
    )

    def _post_parse_env(self, environ: Environ):
        self.loads = self.loads | self._legacy_load

    # @property
    # def server_wide_modules(self) -> Set[str]:
    #     return self._legacy_load | self.loads | {"base", "web"}

    def add_module(self, module_name: str):
        self.loads.add(module_name)

from typing import Any, Dict, Set, Type, Union

from .config_section.addons_path import ConfigConverterAddonsPath
from .config_section.api import OdooConfigGroup
from .config_section.database import ConfigConverterDatabase
from .config_section.geo_ip_db import ConfigConverterGeoIPDb
from .config_section.gevent import ConfigConverterGevent
from .config_section.http import ConfigConverterHttp
from .config_section.i18n import ConfigConverterI18n
from .config_section.log import ConfigConverterLogging
from .config_section.misc import ConfigConverterMisc
from .config_section.other_option import ConfigConverterOtherOption
from .config_section.process_limit import ConfigConverterLimit
from .config_section.smtp import ConfigConverterSmtp
from .config_section.test import ConfigConverterTest
from .config_section.update_init import ConfigConverterUpdateInit
from .config_section.wide_modules import ConfigConverterServerWideModule
from .config_section.workers import ConfigConverterWorkers
from .entrypoints import EntryPoints
from .environ import Environ, new_environ


class OdooConfigExtension(OdooConfigGroup):
    _order: int = 10

    def __init__(self) -> None:
        super().__init__(None)

    def apply_extension(self, environ: Environ, odoo_config: "OdooEnvConfig"):
        self.parse_env(environ)


class OdooEnvConfig:
    """
    Main entry point of `environ_odoo_config`.
    This class allow you to create and change an odoo config file before using it by odoo.
    This class can be used to change the Odoo config `odoo.tools.config` in your custom odoo cli
    """

    __extension_registry: Set["OdooConfigExtension"] = set()

    http: ConfigConverterHttp
    addons_path: ConfigConverterAddonsPath
    database: ConfigConverterDatabase
    geoip: ConfigConverterGeoIPDb
    gevent: ConfigConverterGevent
    i18n: ConfigConverterI18n
    misc: ConfigConverterMisc
    other_option: ConfigConverterOtherOption
    process_limit: ConfigConverterLimit
    smtp: ConfigConverterSmtp
    test: ConfigConverterTest
    update_init: ConfigConverterUpdateInit
    wide_modules: ConfigConverterServerWideModule
    workers: ConfigConverterWorkers
    logging: ConfigConverterLogging

    def __init__(
        self,
        environ: Union[Environ, None, Dict[str, Any]] = None,
        use_os_environ: bool = True,
    ) -> None:
        self._env = new_environ(environ, use_os_environ=use_os_environ, apply_mapper=True)
        self.http = ConfigConverterHttp(self.environ)
        self.addons_path = ConfigConverterAddonsPath(self.environ)
        self.database = ConfigConverterDatabase(self.environ)
        self.geoip = ConfigConverterGeoIPDb(self.environ)
        self.gevent = ConfigConverterGevent(self.environ)
        self.i18n = ConfigConverterI18n(self.environ)
        self.misc = ConfigConverterMisc(self.environ)
        self.other_option = ConfigConverterOtherOption(self.environ)
        self.process_limit = ConfigConverterLimit(self.environ)
        self.smtp = ConfigConverterSmtp(self.environ)
        self.test = ConfigConverterTest(self.environ)
        self.update_init = ConfigConverterUpdateInit(self.environ)
        self.wide_modules = ConfigConverterServerWideModule(self.environ)
        self.workers = ConfigConverterWorkers(self.environ)
        self.logging = ConfigConverterLogging(self.environ)

    @property
    def environ(self) -> Environ:
        return self._env

    def apply_all_extension(self):
        for extension in EntryPoints.extension:
            self.apply_extension(extension)

    def apply_extension(self, extension_type: Type[OdooConfigExtension]):
        ext: OdooConfigExtension = extension_type()
        ext.parse_env(self.environ)
        ext.apply_extension(self.environ, self)

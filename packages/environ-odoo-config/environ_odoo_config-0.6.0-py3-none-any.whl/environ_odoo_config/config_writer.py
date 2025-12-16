import abc
from pathlib import Path
from typing import Dict, Iterator, List, Mapping, Type

from typing_extensions import TYPE_CHECKING, Any, Protocol, Self

from environ_odoo_config import utils
from environ_odoo_config.odoo_utils import GETTER_KEY_COMPAT
from environ_odoo_config.odoo_version import OdooVersion

if TYPE_CHECKING:
    from environ_odoo_config.config_section.api import OdooConfigGroup
    from environ_odoo_config.odoo_config import OdooEnvConfig

import logging

_logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    pass


class ConfigWriter(abc.ABC):
    @abc.abstractmethod
    def process_config_group(self, config_group: "OdooConfigGroup"):
        raise NotImplementedError()

    @abc.abstractmethod
    def store_data(self, odoo_config: "OdooConfig"):
        raise NotImplementedError()


class OdooConfig(Protocol):
    options: Dict[str, Any]
    misc: Dict[str, Dict[str, Any]]

    def set_admin_password(self, value: str): ...

    def get(self, key, default=None): ...

    def pop(self, key, default=None): ...

    def get_misc(self, sect, key, default=None): ...

    def __setitem__(self, key, value): ...

    def __getitem__(self, key): ...


class OdooConfigWrapper:
    def __init__(self, odoo_config: OdooConfig, odoo_version: OdooVersion, reset: bool = False):
        self._odoo_config = odoo_config
        self._odoo_version = odoo_version
        if reset:
            self._odoo_config.__init__()

    def write_env_config(self, env_config: "OdooEnvConfig", *, writer_type: Type[ConfigWriter]):
        writer = writer_type()
        writer.process_config_group(env_config.http)
        writer.process_config_group(env_config.addons_path)
        writer.process_config_group(env_config.database)
        writer.process_config_group(env_config.geoip)
        writer.process_config_group(env_config.gevent)
        writer.process_config_group(env_config.i18n)
        writer.process_config_group(env_config.misc)
        writer.process_config_group(env_config.process_limit)
        writer.process_config_group(env_config.smtp)
        writer.process_config_group(env_config.test)
        writer.process_config_group(env_config.update_init)
        writer.process_config_group(env_config.wide_modules)
        writer.process_config_group(env_config.workers)
        writer.process_config_group(env_config.logging)
        writer.process_config_group(env_config.other_option)
        writer.store_data(self._odoo_config)
        return writer

    def set_admin_password(self, value: str):
        self._odoo_config.set_admin_password(value)

    def save_odoo_config(self):
        try:
            self._odoo_config.save()
        except Exception as e:
            _logger.exception("Can't  save options %s", self._odoo_config.options, exc_info=e)

    def set_config_file(self, config_path: Path):
        if OdooVersion.V19.min().is_valid(self._odoo_version):
            # The path to config must be in _default_options to work in Odoo19
            self._odoo_config._default_options["config"] = utils.normalize_path(config_path)
        else:
            self._odoo_config.config_file = config_path
            self._odoo_config.rcfile = config_path

    def __getitem__(self, item) -> Any:
        config_compat_getter = GETTER_KEY_COMPAT.get(item)
        if config_compat_getter:
            return config_compat_getter(self._odoo_config)
        return self._odoo_config[item]

    def __setitem__(self, key: str, value: Any):
        self._odoo_config[key] = value

    def __str__(self):
        from pprint import pformat

        d = {"options": self._odoo_config.options}
        if OdooVersion.V19.min().is_valid(self._odoo_version) and self._odoo_config.misc:
            d.update(self._odoo_config.misc)
        return pformat(d)


class IniFileConfigWriter(ConfigWriter):
    """
    Allow to persist the configuration converter without using cli argument
    Usefull for non-standard options or not cli option in the odoo config ini file.
    """

    def __init__(self):
        self.data = {"options": {}}

    def set(self, key: str, value: str):
        """
        Manual set a key to Odoo Config instance
        Args:
            key: The key in `options` section
            value: The value to set properly formated
        """
        self.data["options"][key] = value

    def process_config_group(self, config_group: "OdooConfigGroup"):
        for key, value in config_group._get_custom_ini_options().items():  # noqa
            self.set(key, value)

    def store_data(self, odoo_config: "OdooConfig"):
        for section, datas in self.data.items():
            if section == "options":
                for key, value in datas.items():
                    odoo_config[key] = value
            else:
                misc_sec_data = odoo_config.misc.setdefault(section, {})
                for key, value in datas.items():
                    misc_sec_data[key] = value


class CliOption(dict, Mapping[str, Any]):
    def __setitem__(self, __key, __value):
        super().__setitem__(utils.add_dash(__key), __value)

    def set(self, key: str, value: Any, force_set: bool = False) -> Self:
        if value or force_set:
            self[key] = value
        return self

    def set_all(self, values: Dict[str, Any], force_set: bool = False) -> Self:
        for key, value in values.items():
            self.set(key, value, force_set)
        return self

    def to_args(self) -> List[str]:
        result = []
        clean_values = utils.DictUtil.clean_none_env_value(self)
        clean_values = utils.DictUtil.clean_dict(clean_values)
        for key, value in clean_values.items():
            if not value:
                continue
            key = utils.add_dash(key)
            if value == str(True):
                result.append(key)
            else:
                result.append(f"{key}={value}")
        return result

    @classmethod
    def from_groups(cls, *config_groups: "OdooConfigGroup") -> "CliOption":
        force_result = CliOption()
        for config_group in config_groups:
            result = config_group._get_cli_option()  # noqa
            if result:
                force_result.update(result)
        if force_result:
            return force_result

        writer = OdooCliWriter()
        for config_group in config_groups:
            writer.process_config_group(config_group)
        return writer.get_cli_option()

    def __iter__(self) -> Iterator[str]:
        return iter(self.to_args())


class OdooCliWriter(ConfigWriter):
    def __init__(self):
        self._result = CliOption()

    def get_cli_option(self) -> CliOption:
        return self._result

    def process_config_group(self, config_group: "OdooConfigGroup"):
        result = CliOption()
        for field_name, env_key in config_group.get_fields().items():
            value = getattr(config_group, field_name, utils.ODOO_DEFAULT)
            version_env_key = env_key.get_by_version(config_group._for_version)
            if not version_env_key:
                _logger.debug("Unsupported config %s for Odoo version %s", env_key.field_name, env_key.odoo_version)
                continue
            cli_used = version_env_key.cli_used()
            _logger.debug("convert to cli %s -> %s=%s", field_name, cli_used, value)
            if cli_used and value != utils.ODOO_DEFAULT and version_env_key.cli_use_filter(value):
                result.set(cli_used, value)
        if result:
            self._result.update(result)

    def store_data(self, odoo_config: "OdooConfig"):
        odoo_config._parse_config(self._result.to_args())  # noqa

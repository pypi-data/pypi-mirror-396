from __future__ import annotations

import enum
import sys

from typing_extensions import (
    TYPE_CHECKING,
    Any,
    Callable,
    Collection,
    Dict,
    Generic,
    LiteralString,
    Set,
    Type,
    TypeVar,
    Union,
)

if TYPE_CHECKING:
    from environ_odoo_config.config_writer import CliOption

from environ_odoo_config.environ import Environ
from environ_odoo_config.odoo_version import OdooVersion, OdooVersionRange

if sys.version_info >= (3, 10):
    from inspect import get_annotations
else:
    from get_annotations import get_annotations

import logging
from pathlib import Path

from environ_odoo_config import utils

__all__ = ["OdooConfigGroup", "SimpleKey", "EnumKey", "CSVKey", "CliOnly", "RepeatableKey", "RepeatableDictKey"]

OUT_TYPE = TypeVar("OUT_TYPE")
IN_TYPE = TypeVar("IN_TYPE")

_logger = logging.getLogger(__name__)
SHORTCUT_CLI_LENGTH = 2  # Length of 1 dash and 1 lettre for cli. `-i` or `-d`


def _reset_fields(cls):
    for field_name, env_key in cls.get_fields().items():
        setattr(cls, field_name, env_key.py_default)


class OdooConfigGroup:
    _opt_group: str = ""
    _ini_section: str = "options"

    def __init__(self, env: Environ | None = None, **kwargs: Dict[str, Any]) -> None:
        self._for_version: OdooVersion = OdooVersion.NO_VERSION
        if env is not None:
            self.parse_env(env)
        for field_name, value in kwargs.items():
            setattr(self, field_name, value)

    @staticmethod
    def __new__(cls, *args, **kwargs):
        if cls.get_fields():
            _reset_fields(cls)
            return object.__new__(cls)
        _logger.info("Load : %s", cls._opt_group or cls.__name__)
        cls._process_cls_fields()
        _reset_fields(cls)
        return object.__new__(cls)

    @classmethod
    def _process_cls_fields(cls):
        _cls_fields = {}
        for name, _type in get_annotations(cls).items():
            f = getattr(cls, name, None)
            if not isinstance(f, _ConfigKey):
                _logger.debug("Exclude field %s%s, not a EnvKey", f, type(f))
                continue
            f.set_python_info(name, _type)
            if f.ini_section == utils.DEFAULT:
                f.ini_section = cls._ini_section
            if utils.DEFAULT in (f.from_environ_value, f.py_default):
                msg = f"Unsupported field type: {_type} for field '{name}' of type {type(f)}"
                raise ValueError(msg)

            f.propagate_field_to_other_version()
            _cls_fields[name] = f
        setattr(cls, f"_{cls.__name__}_cls_fields", _cls_fields)
        cls._post_load()

    @classmethod
    def _post_load(cls):
        pass

    @property
    def for_version(self) -> OdooVersion:
        return self._for_version

    def __str__(self):
        return self._opt_group or str(type(self))

    @classmethod
    def get_fields(cls) -> Dict[str, _ConfigKey]:
        return getattr(cls, f"_{cls.__name__}_cls_fields", {})

    def parse_env(self, environ: Environ) -> None:
        self._for_version = environ.odoo_version_type
        for field_name, env_key in self.get_fields().items():
            version_env_key = env_key.get_by_version(self._for_version)
            if not version_env_key:
                _logger.debug("Unsupported config for Odoo version %s", environ.odoo_version)
                continue
            value = env_key.get_value(environ)
            if value == utils.ODOO_DEFAULT:
                continue
            setattr(self, field_name, value)
        self._post_parse_env(environ)

    def _post_parse_env(self, environ: Environ):
        pass

    def _get_cli_option(self) -> Union["CliOption", None]:
        return None

    def _get_custom_ini_options(self) -> Dict[str, Any]:
        return {}


class _ConfigKey(Generic[OUT_TYPE]):
    from_environ_value: Callable[[str | None], OUT_TYPE | utils.ODOO_DEFAULT | None]
    """Convert the env string value to OUT_TYPE"""
    field_name: str
    """Name of the field in the OdooConfigClass"""
    py_type: Type[OUT_TYPE]
    """Type of the field in the OdooConfigClass"""
    cli: list[str]
    """The Odoo cli argparse values can be short or long version"""
    cli_use_filter: Callable[[OUT_TYPE], bool]
    """Tell if the cli should be use depends of the value found from env."""
    info: str
    """Help string"""
    ini_dest: str
    """Name of the field in the `ini` file"""
    ini_section: str
    """Name of section of the ini_dest field in the `ini` file"""
    odoo_version: OdooVersionRange
    """Supported odoo version of this fields. Used when an Odoo cli change over version"""
    other_version: Collection[_ConfigKey[OUT_TYPE]]
    """Other supported odoo version of this fields. Used when the odoo cli change over time"""

    def __init__(  # noqa: PLR0913
        self,
        env_key: LiteralString,
        *,
        from_environ_value: Callable[[str], OUT_TYPE] = utils.DEFAULT,
        cli: list[LiteralString] | LiteralString = utils.DEFAULT,
        cli_use_filter: Callable[[OUT_TYPE], bool] = utils.DEFAULT,
        info: LiteralString = utils.DEFAULT,
        ini_dest: Union[LiteralString, utils.NOT_INI_CONFIG] = utils.DEFAULT,
        ini_section: LiteralString = utils.DEFAULT,
        ini_default: OUT_TYPE = utils.DEFAULT,
        ini_converter: Callable[[OUT_TYPE], Any] = utils.DEFAULT,
        odoo_version: OdooVersionRange = utils.DEFAULT,
        other_version: list[_ConfigKey[OUT_TYPE]] = utils.DEFAULT,
        py_default: OUT_TYPE = utils.DEFAULT,
    ):
        assert cli != utils.DEFAULT or env_key, "Keys should have a env key or a cli"

        self.field_name: str = utils.DEFAULT  # noqa
        self.py_type = Any
        self.py_default: OUT_TYPE | None = py_default

        self.from_environ_value = from_environ_value
        self.key = env_key
        self.cli = cli
        self.cli_use_filter = cli_use_filter
        self.info = info
        self.ini_dest = ini_dest
        self.ini_section = ini_section
        self.ini_default = ini_default
        self.odoo_version = odoo_version
        self.other_version = other_version
        self.ini_converter = ini_converter
        self._post__init__()

    def _post__init__(self):
        if self.other_version == utils.DEFAULT:
            self.other_version: list[_ConfigKey[OUT_TYPE]] = []
        if self.cli != utils.DEFAULT and not isinstance(self.cli, list):
            self.cli = [self.cli]
        if self.odoo_version == utils.DEFAULT:
            self.odoo_version = OdooVersion.latest.max()
        if self.ini_default == utils.DEFAULT:
            self.ini_default = utils.ODOO_DEFAULT
        for other_version in self.other_version:
            assert other_version.other_version != utils.DEFAULT, "Version Keys can't have sub version"

    def propagate_field_to_other_version(self):  # noqa: C901
        dest_names = set()

        for other_version in self.other_version:
            assert other_version.other_version != utils.DEFAULT, "Version Keys can't have sub version"
            assert type(other_version) is CliOnly, "OnlyCli type is supported"
            other_version.from_environ_value = self.from_environ_value
            other_version.cli_use_filter = self.cli_use_filter
            if other_version.key == utils.DEFAULT:
                other_version.key = self.key
            if other_version.cli == utils.DEFAULT:
                other_version.cli = self.cli
            if other_version.info == utils.DEFAULT:
                other_version.info = self.info
            if other_version.py_default == utils.DEFAULT:
                other_version.py_default = self.py_default
            if other_version.ini_default == utils.DEFAULT:
                other_version.ini_default = self.ini_default
            if other_version.ini_converter == utils.DEFAULT:
                other_version.ini_converter = self.ini_converter
            if other_version.ini_dest == utils.DEFAULT:
                other_version.ini_dest = self.ini_dest
            if other_version.ini_section == utils.DEFAULT:
                other_version.ini_section = self.ini_section
            if other_version.field_name == utils.DEFAULT:
                other_version.field_name = self.field_name
            dest_names.add(other_version.ini_dest)
        dest_names -= {self.ini_dest}
        if dest_names:
            self.info += f"For prior version see {','.join(dest_names)}"

    def set_python_info(self, field_name: str, python_type: Any):
        self.py_type = python_type
        self.field_name = field_name
        if field_name.startswith("_"):
            self.ini_dest = utils.NOT_INI_CONFIG
            self.ini_section = utils.NOT_INI_CONFIG
        if self.ini_dest == utils.DEFAULT:
            self.ini_dest = field_name
        if python_type in (Any, "Any"):
            self.from_environ_value = utils.no_change
            self.ini_converter = utils.no_change
            self.cli_use_filter = utils.if_not_none

    def get_by_version(self, current_version: OdooVersion) -> "_ConfigKey[OUT_TYPE]|None":
        if current_version == OdooVersion.NO_VERSION or self.odoo_version.is_valid(current_version):
            return self
        if self.other_version:
            for supported_version in self.other_version:
                if supported_version.odoo_version.is_valid(current_version):
                    return supported_version
        return None

    def get_value(self, env: dict[str, str]) -> Union[OUT_TYPE, utils.ODOO_DEFAULT, None]:
        if self.key == utils.DEFAULT:
            msg = f"The key {self.field_name} don't have environ key to search"
            raise ValueError(msg)
        value = env.get(self.key)
        if not value:
            return self.ini_default
        return self.from_environ_value(value)

    def cli_used(self) -> str | None:
        if not self.cli or self.cli == utils.DEFAULT:
            return None
        more_than_2length = list(filter(lambda it: len(it) > SHORTCUT_CLI_LENGTH, self.cli))
        if more_than_2length:
            return more_than_2length[0]
        return self.cli[0]

    def __str__(self):
        return f"{type(self)}({self.field_name, self.py_type})"


def bool_to_str(v):
    return str(utils.to_bool(v))


class SimpleKey(_ConfigKey[OUT_TYPE]):
    def set_python_info(self, field_name: str, python_type: Any):  # noqa: C901
        super().set_python_info(field_name, python_type)
        _from_environ_value = utils.DEFAULT
        _py_default = utils.DEFAULT
        _ini_converter = utils.false_if_not
        if python_type in (str, "str"):
            _from_environ_value = str
            _py_default = None
        elif python_type in (float, "float"):
            _from_environ_value = utils.to_float
            _py_default = 0.0
        elif python_type in ("int", int):
            _from_environ_value = utils.to_int
            _py_default = 0
        elif python_type in ("bool", bool):
            _from_environ_value = utils.to_bool
            _ini_converter = bool_to_str
            _py_default = False
            if (
                self.cli != utils.DEFAULT
                and self.cli_use_filter == utils.DEFAULT
                and all(c.startswith("--no-") for c in self.cli)
            ):
                self.cli_use_filter = utils.negate_bool
        elif python_type in (Path, "Path"):
            _from_environ_value = Path
            _py_default = None
            _ini_converter = str

        if self.from_environ_value == utils.DEFAULT and _from_environ_value != utils.DEFAULT:
            self.from_environ_value = _from_environ_value
        if self.py_default == utils.DEFAULT and _py_default != utils.DEFAULT:
            self.py_default = _py_default
        if self.cli_use_filter == utils.DEFAULT:
            self.cli_use_filter = utils.if_not_none
        if self.ini_converter == utils.DEFAULT:
            self.ini_converter = _ini_converter


ENUM_TYPE = TypeVar("ENUM_TYPE", bound=Type[enum.Enum])


def _enum_to_str(v) -> str | utils.ODOO_DEFAULT:
    if v not in (None, utils.DEFAULT, utils.ODOO_DEFAULT):
        return v.value.lower()
    return utils.ODOO_DEFAULT


class EnumKey(_ConfigKey[ENUM_TYPE]):
    def __init__(  # noqa: PLR0913
        self,
        enum_type: ENUM_TYPE,
        env_key: LiteralString = utils.DEFAULT,
        *,
        from_environ_value: Callable[[str], OUT_TYPE] = utils.DEFAULT,
        cli: list[LiteralString] | LiteralString = utils.DEFAULT,
        cli_use_filter: Callable[[OUT_TYPE], bool] = utils.DEFAULT,
        info: LiteralString = utils.DEFAULT,
        ini_dest: LiteralString = utils.DEFAULT,
        ini_section: LiteralString = utils.DEFAULT,
        ini_default: OUT_TYPE = utils.DEFAULT,
        odoo_version: OdooVersionRange = utils.DEFAULT,
        other_version: list[SimpleKey[OUT_TYPE]] = utils.DEFAULT,
        py_default: OUT_TYPE = utils.DEFAULT,
    ):
        super().__init__(
            env_key,
            from_environ_value=from_environ_value,
            cli=cli,
            cli_use_filter=cli_use_filter,
            info=info,
            ini_section=ini_section,
            ini_dest=ini_dest,
            ini_default=ini_default,
            odoo_version=odoo_version,
            other_version=other_version,
            py_default=py_default,
        )
        self.py_type = enum_type
        if self.from_environ_value == utils.DEFAULT:
            self.from_environ_value = enum_type.__getitem__
        if self.py_default == utils.DEFAULT:
            self.py_default = None
        if self.ini_converter == utils.DEFAULT:
            self.ini_converter = _enum_to_str
        if self.cli_use_filter == utils.DEFAULT:
            self.cli_use_filter = _enum_to_str


def to_csv(value: OUT_TYPE) -> Union[str, utils.ODOO_DEFAULT]:
    if isinstance(value, Collection):
        return ",".join(value)
    return utils.ODOO_DEFAULT


class CSVKey(_ConfigKey[Set[OUT_TYPE]]):
    csv_converter: Callable[[str], Collection[str]]

    def __init__(  # noqa: PLR0913
        self,
        env_key: LiteralString = utils.DEFAULT,
        *,
        from_environ_value: Callable[[str], OUT_TYPE] = utils.DEFAULT,
        cli: list[LiteralString] | LiteralString = utils.DEFAULT,
        cli_use_filter: Callable[[OUT_TYPE], bool] = utils.DEFAULT,
        info: LiteralString = utils.DEFAULT,
        ini_dest: LiteralString = utils.DEFAULT,
        ini_section: LiteralString = utils.DEFAULT,
        ini_default: OUT_TYPE = utils.DEFAULT,
        odoo_version: OdooVersionRange = utils.DEFAULT,
        other_version: list[SimpleKey[OUT_TYPE]] = utils.DEFAULT,
        csv_converter: Callable[[str], Collection[str]] = utils.DEFAULT,
    ):
        super().__init__(
            env_key,
            from_environ_value=from_environ_value,
            cli=cli,
            cli_use_filter=cli_use_filter,
            info=info,
            ini_section=ini_section,
            ini_dest=ini_dest,
            ini_default=ini_default,
            odoo_version=odoo_version,
            other_version=other_version,
        )
        self.py_default = set()
        if csv_converter == utils.DEFAULT:
            csv_converter = utils.csv_set_value
        self.csv_converter = csv_converter
        if self.ini_converter == utils.DEFAULT:
            self.ini_converter = to_csv
        if self.cli_use_filter == utils.DEFAULT:
            self.cli_use_filter = utils.if_not_empty

    def get_value(self, env: dict[str, str]) -> Union[set[OUT_TYPE], utils.ODOO_DEFAULT]:
        if self.key == utils.DEFAULT:
            return utils.ODOO_DEFAULT
        direct_value = env.get(self.key)
        if not direct_value:
            return set()  # Avoid side effect
        set_value = self.csv_converter(direct_value)
        return {self.from_environ_value(v) for v in set_value}

    def set_python_info(self, field_name: str, python_type: Any):
        super().set_python_info(field_name, set)
        if python_type in (Set[str], "set[str]"):
            self.from_environ_value = str
        elif python_type in (Set[int], "set[int]"):
            self.from_environ_value = utils.to_int
        elif python_type in (Set[float], "set[float]"):
            self.from_environ_value = utils.to_float
        elif python_type in (Set[bool], "set[bool]"):
            self.from_environ_value = utils.to_bool
        elif python_type in (Set[Path], "set[Path]"):
            self.from_environ_value = Path


class CliOnly(SimpleKey[OUT_TYPE]):
    def __init__(  # noqa: PLR0913
        self,
        *cli: LiteralString,
        cli_use_filter: Callable[[OUT_TYPE], bool] = utils.DEFAULT,
        info: LiteralString = utils.DEFAULT,
        ini_dest: LiteralString = utils.DEFAULT,
        ini_section: LiteralString = utils.DEFAULT,
        ini_default: OUT_TYPE = utils.DEFAULT,
        odoo_version: OdooVersion.Range = utils.DEFAULT,
        other_version: list[SimpleKey[OUT_TYPE]] = utils.DEFAULT,
    ):
        super().__init__(
            env_key=utils.DEFAULT,
            cli=list(cli),
            cli_use_filter=cli_use_filter,
            info=info,
            ini_dest=ini_dest,
            ini_section=ini_section,
            ini_default=ini_default,
            odoo_version=odoo_version,
            other_version=other_version,
        )
        self.from_environ_value = lambda it: None
        self.py_default = None

    def get_value(self, env: dict[str, str]) -> Union[Any, utils.ODOO_DEFAULT, None]:
        return None


class RepeatableKey(CSVKey[OUT_TYPE]):
    def get_value(self, env: dict[str, str]) -> Union[set[OUT_TYPE], utils.ODOO_DEFAULT]:
        if self.key == utils.DEFAULT:
            return utils.ODOO_DEFAULT
        result = super().get_value(env)
        if result == utils.ODOO_DEFAULT:
            result = set()
        r_copy = result.copy()
        key_r = self.key + "_"
        for env_key in env:
            if env_key.startswith(key_r):
                key_suffix = env_key[len(key_r) :]
                str_value = env[env_key]

                if utils.is_boolean(str_value):
                    if utils.to_bool(str_value):
                        r_copy.add(key_suffix.lower())
                else:
                    r_copy.update({self.from_environ_value(v) for v in self.csv_converter(env[env_key])})
        return r_copy


class RepeatableDictKey(_ConfigKey[Dict[str, OUT_TYPE]]):
    csv_converter: Callable[[str], Collection[str]]

    def _post__init__(self):
        super()._post__init__()
        if self.py_default == utils.DEFAULT:
            self.py_default = dict()
        if self.ini_converter == utils.DEFAULT:
            self.ini_converter = to_csv
        if self.cli_use_filter == utils.DEFAULT:
            self.cli_use_filter = utils.if_not_empty

    def set_python_info(self, field_name: str, python_type: Any):
        super().set_python_info(field_name, python_type)
        if self.from_environ_value != utils.DEFAULT:
            return
        _logger.debug("Try find `from_environ_value` factory from types")
        if python_type in (Dict[str, str], "dict[str, str]"):
            self.from_environ_value = str
        elif python_type in (Dict[str, int], "dict[str, int]"):
            self.from_environ_value = utils.to_int
        elif python_type in (Dict[str, float], "dict[str, float]"):
            self.from_environ_value = utils.to_float
        elif python_type in (Dict[str, bool], "dict[str, bool]"):
            self.from_environ_value = utils.to_bool
        elif python_type in (Dict[str, Path], "dict[str, Path]"):
            self.from_environ_value = Path
        else:
            _logger.warning("Can't find type for key %s, set `from_environ_value` or a supported type types", self)
            self.from_environ_value = str

    def get_value(self, env: dict[str, str]) -> Union[Dict[str, OUT_TYPE], utils.ODOO_DEFAULT]:
        if self.key == utils.DEFAULT:
            return utils.ODOO_DEFAULT
        r_copy = {}
        key_r = self.key + "_"
        for env_key in env:
            if env_key.startswith(key_r):
                key_suffix = env_key[len(key_r) :]
                str_value = env[env_key]
                r_copy[key_suffix] = self.from_environ_value(str_value)
        return r_copy

from __future__ import annotations

import enum
import logging
import os
from collections import OrderedDict
from typing import Any, TypeVar

from typing_extensions import (
    List,
    Mapping,
    Self,
    Tuple,
    Type,
    Union,
    cast,
)

from . import utils
from .entrypoints import EntryPoints
from .odoo_version import OdooVersion

_logger = logging.getLogger(__name__)
SHORTCUT_CLI_LENGHT = 2  # Lenght of 1 dash and 1 lettre for cli. `-i` or `-d`


ET = TypeVar("ET", bound=enum.Enum)


class Environ(dict, Mapping[str, str]):
    """
    A mapping class on steroid, used to manipulate the current Odoo environ.
    Base factory is `from_os_environ`.
    """

    @classmethod
    def new(
        cls, base_environ: dict[str, Any] | None = None, *, use_os_environ: bool = True, apply_mapper: bool = True
    ) -> "Environ":
        """
        Create a new Environ from base_environ and os.environ if asked
        Args:
            base_environ: runtime environ varaible to add
            use_os_environ: include in the new Environ os.environ
            apply_mapper: Load and apply project.entry-points."environ_odoo_config.mapper" found

        Returns: a new Environ

        """
        environ = cls(base_environ or {})
        if use_os_environ:
            environ.update(dict(os.environ))
        if apply_mapper:
            environ.update(apply_environ_mapper(environ))
        return environ

    def copy(self) -> "Environ":
        return Environ(self)

    @property
    def odoo_version(self) -> int:
        """
        Returns:
            `env:ODOO_VERSION` as [int][int]
        """
        return self.odoo_version_type.value

    @property
    def odoo_version_type(self) -> OdooVersion:
        """
        Try to find the version with importing `odoo.release`, otherwise use `ODOO_VERSION` from current self..
        Returns:
            `env:ODOO_VERSION` as OdooVersion otherwise OdooVersion.NO_VERSION is returned
        """
        int_version = self.get_int("ODOO_VERSION")
        if not int_version:
            try:
                import odoo.release

                int_version = odoo.release.version_info[0]
            except ImportError:
                pass

        return OdooVersion(max(int_version, OdooVersion.NO_VERSION.value))

    def mutate(self, *arg, **kwargs) -> Self:
        """
        Same as [dict.update][dict.update] but return `self`
        Returns:
            current self after the `update`
        """
        self.update(*arg, **kwargs)
        return self

    def get_bool(self, *keys: str, default: bool = False) -> bool:
        return utils.to_bool(self.gets(*keys, default=str(default)))

    def get_int(self, *keys: str, default: int = 0) -> int:
        return utils.to_int(self.gets(*keys, default=str(default)))

    def get_enum(self, key: str, enum_type: Type[ET], *, default: ET) -> ET:
        value = self.get(key)
        if not value or value not in enum_type.__members__:
            return default
        return enum_type[value]

    def is_boolean(self, *keys: str) -> bool:
        return utils.is_boolean(self.gets(*keys))

    def get_list(self, key: str, separator=",", allow_duplicate: bool = False) -> List[str]:
        value = self.get(key)
        if self.is_boolean(key) and not self.get_bool(key):
            return []
        if not value:
            return []
        if allow_duplicate:
            return [u.strip() for u in value.strip().split(separator)]
        res = OrderedDict()
        for value in value.strip().split(separator):
            res[value.strip()] = None
        return list(res.keys())

    def gets(self, *keys: str, default: str = None, none_if_false: bool = True) -> Union[str, None]:
        """
        Returns:
            The first not false value found from keys (in keys orders) or the default
        """
        return utils.get_value(self, *keys, default=default, if_all_falsy_return_none=none_if_false)

    def get_start_with(self, prefix) -> List[Tuple[str, str]]:
        result = {}
        for key, value in self.items():
            if key.startswith(prefix):
                result[key[len(prefix) :]] = value
        return cast(List[Tuple[str, str]], list(result.items()))

    def __add__(self, other: Mapping[str, Any]) -> "Environ":
        result = self.copy()
        result.update(other)
        return result


def apply_environ_mapper(environ: Environ) -> Environ:
    curr_env = environ.copy()
    for mapper in EntryPoints.mappers:
        curr_env.update(mapper(curr_env.copy()))
    return curr_env.copy()


def new_environ(
    base_environ: dict[str, Any] | None = None, use_os_environ: bool = True, apply_mapper: bool = True
) -> Environ:
    return Environ.new(base_environ=base_environ, use_os_environ=use_os_environ, apply_mapper=apply_mapper)


odoo_log_levels = [
    "info",
    "debug_rpc",
    "warn",
    "test",
    "critical",
    "runbot",
    "debug_sql",
    "error",
    "debug",
    "debug_rpc_answer",
    "notset",
]

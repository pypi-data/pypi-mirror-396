import os
from functools import cached_property
from typing import TYPE_CHECKING, Callable, Dict, List, Tuple, Type

import importlib_metadata as md

if TYPE_CHECKING:
    from .environ import Environ
    from .odoo_config import OdooConfigExtension

__all__ = ["EntryPoints"]


def _oenv2config_compatibility(curr_env: "Environ") -> "Environ":
    """ """
    return curr_env + {
        "PROXY_MODE": curr_env.gets("PROXY_MODE", "PROXY_ENABLE"),
        "ADMIN_PASSWORD": curr_env.gets("ADMIN_PASSWORD", "ADMIN_PASSWD"),
        "WORKER_HTTP": curr_env.gets("WORKER_HTTP", "WORKERS"),
        "WORKER_CRON": curr_env.gets("WORKER_CRON", "CRON_THREAD", "MAX_CRON_THREADS"),
        "HTTP_INTERFACE": curr_env.gets("HTTP_INTERFACE", "XMLRPC_INTERFACE"),
        "HTTP_PORT": curr_env.gets("HTTP_PORT", "XMLRPC_PORT"),
        "HTTP_ENABLE": curr_env.gets("HTTP_ENABLE", "XMLRPC_ENABLE"),
        "GEVENT_PORT": curr_env.gets("GEVENT_PORT", "LONGPOLLING_PORT"),
        "SERVER_WIDE_MODULES": curr_env.gets("SERVER_WIDE_MODULES", "LOAD"),
        "GEOIP_CITY_DB": curr_env.gets("GEOIP_CITY_DB", "GEOIP_DB"),
        "TRANSIENT_AGE_LIMIT": curr_env.gets("TRANSIENT_AGE_LIMIT", "OSV_MEMORY_AGE_LIMIT"),
        "TRANSIENT_COUNT_LIMIT": curr_env.gets("TRANSIENT_COUNT_LIMIT", "OSV_MEMORY_COUNT_LIMIT"),
        "INIT": curr_env.gets("INIT", "INSTALL"),
        **{"INIT_" + k: v for k, v in curr_env.get_start_with("INSTALL_")},
    }


class _Entrypoints:
    @cached_property
    def mappers(self):
        return self._load_mappers()

    @cached_property
    def extension(self):
        return self._load_config_extension()

    def _load_mappers(self) -> List[Callable[["Environ"], "Environ"]]:
        exclude_mappers = set(k.strip() for k in os.getenv("ODOO_ENV_CONFIG_EXCLUDE_MAPPERS", "").split(",") if k)
        mappers: list[Callable[[Environ], Environ]] = [
            _oenv2config_compatibility,
        ]
        for entry_point in md.entry_points(group="environ_odoo_config.mapper"):
            # If no distro is specified, use first to come up.
            if entry_point.name in exclude_mappers:
                continue
            mappers.append(entry_point.load())
        return mappers

    def _load_config_extension(self) -> List[Type["OdooConfigExtension"]]:
        exclude_ = set(k.strip() for k in os.getenv("ODOO_ENV_CONFIG_EXCLUDE_EXT", "").split(",") if k)
        result: Dict[Tuple[int, str], Type["OdooConfigExtension"]] = {}
        for entry_point in md.entry_points(group="environ_odoo_config.extension"):
            # If no distro is specified, use first to come up.
            if entry_point.name in exclude_:
                continue
            converter_cls: Type["OdooConfigExtension"] = entry_point.load()
            result[(converter_cls._order, entry_point.name)] = converter_cls

        return [result[key] for key in sorted(result.keys())]


EntryPoints = _Entrypoints()  # noqa

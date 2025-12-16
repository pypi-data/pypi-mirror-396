from pathlib import Path
from typing import Any, Callable, Dict, List


def get_config_db_names(odoo_config) -> List[str]:
    """assure la compatibilité V12-V19"""
    conf_db_name = odoo_config["db_name"]
    if isinstance(conf_db_name, bool):
        return []
    if isinstance(conf_db_name, str):
        conf_db_name = conf_db_name.split(",")
    return sorted(db.strip() for db in conf_db_name)


def get_addon_path(odoo_config) -> List[Path]:
    """
    Return the addons_path list.
    - In Odoo 19 this is already a list
    - before it's only a csv string
    """
    addons_path = odoo_config["addons_path"]
    if isinstance(addons_path, bool):
        return []
    if isinstance(addons_path, str):
        return [Path(ap) for ap in addons_path.split(",")]
    return addons_path


GETTER_KEY_COMPAT: Dict[str, Callable[[Any], Any]] = {
    "db_name": get_config_db_names,
    "addons_path": get_addon_path,
}

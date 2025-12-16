from pathlib import Path
from typing import Set

from environ_odoo_config.odoo_version import OdooVersion

from ..utils import NOT_INI_CONFIG
from .api import (
    OdooConfigGroup,
    RepeatableKey,
)


class ConfigConverterUpdateInit(OdooConfigGroup):
    """
    convert environment variable used to update or init modules
    """

    _opt_group = "Update or Install Configuration"
    init: Set[str] = RepeatableKey(
        "INIT", cli=["-i", "--init"], info="Initialise (install/re-install) odoo modules.", ini_dest=NOT_INI_CONFIG
    )
    reinit: Set[str] = RepeatableKey(
        "REINIT",
        cli=["--reinit"],
        info="Initialise (install/re-install) odoo modules.",
        ini_dest=NOT_INI_CONFIG,
        odoo_version=OdooVersion.V19.min(),
    )
    update: Set[str] = RepeatableKey(
        "UPDATE", cli=["-u", "--update"], info="Update odoo modules.", ini_dest=NOT_INI_CONFIG
    )
    upgrade_path: Set[Path] = RepeatableKey(
        "UPGRADE_PATH",
        cli="--upgrade-path",
        info="specify an additional upgrade path.",
        odoo_version=OdooVersion.V13.min(),
    )
    pre_upgrade_scripts: Set[Path] = RepeatableKey(
        "PRE_UPGRADE_SCRIPTS",
        cli="--pre-upgrade-scripts",
        odoo_version=OdooVersion.V16.min(),
        info="Run specific upgrade scripts before loading any module when -u is provided.",
    )

    @property
    def install(self) -> Set[str]:
        return self.init

from typing_extensions import Dict

from environ_odoo_config.utils import NOT_INI_CONFIG

from .api import (
    OdooConfigGroup,
    RepeatableDictKey,
)


class ConfigConverterOtherOption(OdooConfigGroup):
    """
    convert environment variable to config without parsing.
    """

    _opt_group = "Manual Odoo Options"
    _other_options: Dict[str, str] = RepeatableDictKey(
        "OPT_ODOO", info="Allow to set non official config without dedicated converter", ini_dest=NOT_INI_CONFIG
    )

    def _get_custom_ini_options(self):
        return {key.lower().strip(): value for key, value in self._other_options.items()}

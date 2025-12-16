from __future__ import annotations

import logging
from pathlib import Path

from .api import (
    OdooConfigGroup,
    RepeatableKey,
)

_logger = logging.getLogger(__name__)


class ConfigConverterAddonsPath(OdooConfigGroup):
    """
    convert environment variable using `ADDONS_GIT_` or `ADDONS_LOCAL_`
    """

    _opt_group = "Addons Path Configuration"

    addons_path: set[Path] = RepeatableKey(
        "ADDON_PATH", cli="--addons-path", info="specify additional addons paths", ini_dest="addons_path"
    )

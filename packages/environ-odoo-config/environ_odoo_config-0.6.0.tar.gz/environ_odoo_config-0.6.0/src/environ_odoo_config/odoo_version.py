from __future__ import annotations

import enum
import logging
from typing import Iterator, TypeVar

from typing_extensions import (
    Union,
)

_logger = logging.getLogger(__name__)
SHORTCUT_CLI_LENGHT = 2  # Lenght of 1 dash and 1 lettre for cli. `-i` or `-d`


ET = TypeVar("ET", bound=enum.Enum)


class OdooVersion(enum.IntEnum):
    NO_VERSION = 0  # Special value
    # V11 = 11
    V12 = 12
    V13 = 13
    V14 = 14
    V15 = 15
    V16 = 16
    V17 = 17
    V18 = 18
    V19 = 19
    # Special Value, change it manually to max supported version
    latest = V19

    def max(self) -> "OdooVersionRange":
        return OdooVersionRange(vmin=OdooVersion.V12, vmax=self)

    def min(self) -> "OdooVersionRange":
        return OdooVersionRange(vmin=self, vmax=OdooVersion.latest)


class OdooVersionRange:
    def __init__(self, *, vmin: Union[OdooVersion, None] = None, vmax: Union[OdooVersion, None] = None) -> None:
        """
        A range of version (included)
        Args:
            vmin: The minimal supported version (included) or V12 by default
            vmax: The maximal supported version (included) or latest by default
        """
        self._min = vmin or OdooVersion.V12
        self._max = vmax or OdooVersion.latest

    def is_valid(self, version: OdooVersion) -> bool:
        return self._min <= version <= self._max

    def __adoc__(self) -> str:
        if self._min == self._max:
            return f"Only Odoo version {float(self._min.value)} is supported"
        return f"Supported Odoo version from {float(self._min.value)} until {float(self._max.value)}"

    def __iter__(self) -> Iterator[OdooVersion]:
        return (OdooVersion(o) for o in range(self._min.value, min(self._max.value + 1, OdooVersion.latest.value)))

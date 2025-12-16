from pathlib import Path

from environ_odoo_config.odoo_version import OdooVersion

from .api import (
    CliOnly,
    OdooConfigGroup,
    SimpleKey,
)


class ConfigConverterGeoIPDb(OdooConfigGroup):
    """
    convert environment variable related to the Odoo Geo IP configuration
    """

    _opt_group = "Geo IP Database Configuration"
    geoip_city_db: Path = SimpleKey(
        "GEOIP_CITY_DB",
        cli=["--geoip-city-db"],
        info="Absolute path to the GeoIP City database file.",
        odoo_version=OdooVersion.V17.min(),
        other_version=[CliOnly("--geoip-db", ini_dest="geoip_database", odoo_version=OdooVersion.V16.max())],
    )
    geoip_country_db: Path = SimpleKey(
        "GEOIP_COUNTRY_DB",
        cli="--geoip-country-db",
        odoo_version=OdooVersion.V17.min(),
        info="Absolute path to the GeoIP Country database file.",
    )

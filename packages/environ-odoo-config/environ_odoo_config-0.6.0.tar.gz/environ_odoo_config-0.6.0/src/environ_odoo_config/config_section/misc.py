from pathlib import Path

from typing_extensions import Any, Self, Set

from environ_odoo_config import utils
from environ_odoo_config.environ import Environ
from environ_odoo_config.odoo_version import OdooVersion, OdooVersionRange
from environ_odoo_config.utils import NOT_INI_CONFIG, ODOO_DEFAULT, csv_set_value

from .api import (
    CliOnly,
    OdooConfigGroup,
    RepeatableKey,
    SimpleKey,
)


def csv_not_false(value) -> Set[str]:
    return {v for v in csv_set_value(value) if not (utils.is_boolean(v) and not utils.to_bool(value))}


def always_false(x: Any) -> bool:
    return False


class ConfigConverterMisc(OdooConfigGroup):
    _opt_group = "Misc Odoo Options"

    odoo_path: Path = SimpleKey("ODOO_PATH", ini_dest=NOT_INI_CONFIG)
    config_file: Path = SimpleKey(
        "ODOO_RC",
        cli=["-c", "--config"],
        info="specify alternate config file",
        cli_use_filter=always_false,
        ini_dest=NOT_INI_CONFIG,
    )
    import_partial: bool = SimpleKey(
        "IMPORT_PARTIAL",
        cli=["-P", "--import-partial"],
        info="""Use this for big data importation, if it crashes you will be able to continue at the current state.
         Provide a filename to store intermediate importation states.""",
    )
    pidfile: Path = SimpleKey("PIDFILE", cli="--pidfile", info="file where the server pid will be stored")
    _pidfile_auto: bool = SimpleKey("PIDFILE", info="Auto set a pid file in `/tmp/odoo.pid` if the key equal `True`")

    unaccent: bool = SimpleKey(
        "UNACCENT", cli="--unaccent", info="Try to enable the unaccent extension when creating new databases."
    )
    without_demo: Set[str] = RepeatableKey(
        "WITHOUT_DEMO",
        cli="--without-demo",
        info="""disable loading demo data for modules to be installed (comma-separated, use "all" for all modules).
        Requires -d and -i. Default is %default""",
        csv_converter=csv_not_false,
        odoo_version=OdooVersion.V18.max(),
    )
    with_demo: bool = SimpleKey(
        "WITH_DEMO",
        cli="--with-demo",
        info="""install demo data in new databases""",
        odoo_version=OdooVersion.V19.min(),
    )
    without_demo_all: bool = SimpleKey(
        "WITHOUT_DEMO",
        # from_environ_value=lambda it: not utils.to_bool(it),
        info="""disable loading demo data for all modules if equal to true""",
        ini_dest=NOT_INI_CONFIG,
    )
    stop_after_init: bool = SimpleKey(
        "STOP_AFTER_INIT",
        cli="--stop-after-init",
        info="stop the server after its initialization",
        ini_dest=NOT_INI_CONFIG,
    )
    save_config_file: bool = SimpleKey(
        "SAVE_CONFIG_FILE", cli=["-s", "--save"], info="Save the generated config. Always True", ini_dest=NOT_INI_CONFIG
    )
    admin_password: str = SimpleKey(
        "ADMIN_PASSWORD", info="The Admin password for database management", ini_dest=NOT_INI_CONFIG
    )
    skip_auto_install: bool = SimpleKey(
        "SKIP_AUTO_INSTALL",
        cli="--skip-auto-install",
        info="Skip the automatic installation of modules marked as auto_install",
        odoo_version=OdooVersionRange(vmin=OdooVersion.V17, vmax=OdooVersion.V18),
    )
    data_dir: Path = SimpleKey("DATA_DIR", cli=["-D", "--data-dir"], info="Directory where to store Odoo data")

    dev_mode: bool = CliOnly("--dev", ini_dest=NOT_INI_CONFIG)
    shell_interface: str = CliOnly("--shell-interface", ini_dest=NOT_INI_CONFIG)

    def parse_env(self, curr_env: Environ) -> Self:
        super().parse_env(curr_env)
        if self.for_version >= OdooVersion.V19:
            if self.with_demo == ODOO_DEFAULT and self.without_demo_all != ODOO_DEFAULT:
                self.with_demo = not self.without_demo_all
        elif self.without_demo_all:
            # When WITHOUT_DEMO="True", then we set to `all`
            self.without_demo = {"all"}

        # curr_env["WITHOUT_DEMO"] = "all"
        if self.odoo_path and self.data_dir:
            self.data_dir = self.odoo_path / self.data_dir.expanduser()
        if self._pidfile_auto and not self.pidfile:
            self.pidfile = Path("/tmp/odoo.pid")
        return self

    # def write_to_config(self, config: OdooConfig):
    #     if self.admin_password:
    #         config.set_admin_password(self.admin_password)

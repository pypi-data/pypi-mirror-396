"""
Python file containing all the function used by the cli.
`odoo_env_confi` expose a script command when installed.
>>> odoo - env2config - h

This command allow to run this libraray inside an odoo command (See `odoo.cli.Command`
"""

import argparse
import contextlib
import logging
import os
import sys
from pathlib import Path

import dotenv

from .config_writer import IniFileConfigWriter, OdooCliWriter, OdooConfigWrapper
from .odoo_config import OdooEnvConfig


def init_logger():
    _logger_level = getattr(logging, os.environ.get("NDP_SERVER_LOG_LEVEL", "INFO"), logging.INFO)
    _logger = logging.getLogger(__name__)
    _logger.setLevel(logging.DEBUG)
    _logger.addHandler(logging.StreamHandler())


class SplitArgs(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        # start or ending comma removed to avoid empty value in list
        setattr(
            namespace,
            self.dest,
            getattr(namespace, self.dest, []) + list(filter(None, values.split(","))),
        )


def get_odoo_cmd_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser()
    p.add_argument("--dest", dest="config_dest", help="Path to odoo configuration file", default="odoo-config.ini")
    p.add_argument("--show", dest="print_config", action="store_true", help="Generate the config and log out (stderr)")
    p.add_argument(
        "--no-environ",
        dest="use_environ",
        action="store_false",
        help="Disable parsing `os.environ` only use stdin",
        default=True,
    )
    p.add_argument("--stdin", help="Use `--stdin` to take env to parse from stdin", action="store_true")
    p.set_defaults(func=lambda _: sys.exit(p.format_help()))
    return p


def cli_main(cmdargs=None):
    parser = get_odoo_cmd_parser()
    if cmdargs:
        # Removing blank sub_args
        # Is called with "$ENV_VAR" but ENV_VAR isn't set, then `sub_args` contains `['']
        # So we remove empty string from it
        cmdargs = [s for s in cmdargs if s.split()]
    ns, other_args = parser.parse_known_args(cmdargs)
    if other_args:
        raise ValueError("Args %s not supported" % other_args)
    extra_env = {}
    if ns.stdin:
        extra_env = dotenv.dotenv_values(stream=sys.stdin)
    config_converter = OdooEnvConfig(environ=extra_env, use_os_environ=ns.use_environ)
    config_converter.apply_all_extension()
    if ns.config_dest:
        config_converter.misc.config_file = Path(ns.config_dest)
    wrapper = cli_save_env_config(config_converter, auto_save=not ns.print_config, setup_logging=False)

    if ns.print_config:
        print("Config :", file=sys.stderr)
        print(wrapper, file=sys.stderr)


def cli_save_env_config(
    odoo_env_config: OdooEnvConfig, *, setup_logging: bool = True, auto_save: bool = True
) -> OdooConfigWrapper:
    """
    Entrypoint of the command

    1. First we parse `args`
    2. Then we load `--profiles` if some are provided
    3. And finally we execute [odoo_env_config][odoo_env_config.entry.env_to_odoo_args] and save it to the dest file

    Args:
        odoo_module: The Odoo module imported
        force_odoo_args: Other args to pass to odoo_module config
        config_dest: The dest file to store the config generated
        other_env: The environment where the config is extracted
        auto_save: determine is the config is actually writtent to the dest file
    """
    import odoo as odoo_module

    with contextlib.suppress(Exception):
        odoo_module.netsvc.init_logger()

    wrapper = OdooConfigWrapper(
        odoo_config=odoo_module.tools.config, odoo_version=odoo_env_config.environ.odoo_version_type, reset=True
    )
    if odoo_env_config.misc.config_file:
        wrapper.set_config_file(odoo_env_config.misc.config_file)
    wrapper.write_env_config(odoo_env_config, writer_type=OdooCliWriter)
    wrapper.write_env_config(odoo_env_config, writer_type=IniFileConfigWriter)
    if odoo_env_config.misc.admin_password:
        wrapper.set_admin_password(odoo_env_config.misc.admin_password)
    if auto_save:
        wrapper.save_odoo_config()
    if setup_logging:
        odoo_module.netsvc.init_logger()
    if wrapper["addons_path"]:
        # Addons path probably change, then I need to override initialize_sys_path
        odoo_module.modules.module.initialize_sys_path()
    return wrapper

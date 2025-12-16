import configparser
import os
import unittest
import uuid
from os.path import join as pjoin
from pathlib import Path
from typing import Any, Dict, List

import dotenv

from environ_odoo_config.odoo_config import OdooEnvConfig
from environ_odoo_config import cli
from environ_odoo_config.environ import Environ


def create_config(
    env_files: List[str] = None, odoo_rc: str = None, extra_odoo_args: List[str] = None
) -> configparser.ConfigParser:
    """
    This function create a config file using the subprocess launching odoo of the version

    Args:
        env_files: The profile you want to add
        odoo_rc: To force where the odoo-rc is generated
        extra_odoo_args: Extra Odoo Args you want to add instead of Env var
    Returns:
        The odoo-rc generated if success
    Raises:
        ValueError: if the subprocess calling oenv2config failed
    """
    rand = str(uuid.uuid4()).split("-")[0]
    odoo_rc = odoo_rc or f"/tmp/odoo_rc-{rand}.ini"
    print("rc file in ", odoo_rc)
    if os.path.exists(odoo_rc):
        os.remove(odoo_rc)  # Remove to sure no file exist
    other_envs = Environ({})
    for env_file in env_files or []:
        efile = pjoin(os.path.dirname(__file__), "profiles", f"{env_file}.env")
        if os.path.exists(efile):
            other_envs.update(dotenv.dotenv_values(efile))
        efile_v = pjoin(
            os.path.dirname(__file__), "profiles", f"{env_file}-{other_envs.odoo_version}.env"
        )
        if os.path.exists(efile_v):
            other_envs.update(dotenv.dotenv_values(efile_v))
    odoo_config = OdooEnvConfig(environ=other_envs, use_os_environ=False)
    odoo_config.misc.config_file = Path(odoo_rc)
    cli.cli_save_env_config(odoo_config, auto_save=True)
    parser = configparser.ConfigParser()
    parser.read(odoo_rc)
    return parser


def assertParser(
    case: unittest.TestCase,
    parser: configparser.ConfigParser,
    expected_values: Dict[str, Any],
    section="options",
):
    """
    Assert the parser comparing the expectedValue.
    Do some typing converstion based on the type of the value of the key in expected_values
    If the value in `expected_values` to compare to the same key in parser is:
    - bool, the `parser.getboolean` is used with `assertEqual`
    - int, the `parser.getint` is used with `assertEqual`
    - float, the function `parser.getfloat` is used with `assertEqual`
    - List, a split on `,` if applied and `assertListEqual`
    - other `assertEqual` without conversion

    Args:
        case: The test case
        parser: The parser to assert
        expected_values: The key, value to assert
        section: If you want to assert an another section
    """
    case.assertTrue(parser)
    case.assertTrue(expected_values)
    dict_compare = {}
    for key, value in expected_values.items():
        pvalue = parser.get(section, key)
        if isinstance(value, bool):
            try:
                pvalue = parser.getboolean(section, key)
            except ValueError:
                case.fail(
                    f"{section}.{key}, not an 'boolean' value, {parser.get(section, key)}"
                )
        elif isinstance(value, int):
            try:
                pvalue = parser.getint(section, key)
            except ValueError:
                case.fail(
                    f"{section}.{key}, not an 'int' value, '{parser.get(section, key)}'"
                )
        elif isinstance(value, float):
            try:
                pvalue = parser.getfloat(section, key)
            except ValueError:
                case.fail(
                    f"{section}.{key}, not an 'float' value, {parser.get(section, key)}"
                )

        elif isinstance(value, list):
            pvalue = parser.get(section, key).split(",")
        case.assertEqual(pvalue, value, f"{section}.{key}, not equal")
        dict_compare[key] = pvalue
    case.assertDictEqual(expected_values, dict_compare)

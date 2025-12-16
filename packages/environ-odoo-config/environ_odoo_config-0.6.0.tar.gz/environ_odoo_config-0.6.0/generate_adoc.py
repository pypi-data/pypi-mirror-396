from __future__ import annotations

import io
import os
from pathlib import Path

from typing_extensions import Any

from environ_odoo_config.config_section.api import (
    EnumKey,
    CliOnly as OnlyCli,
    RepeatableKey,
    CSVKey as SimpleCSVKey,
    SimpleKey,
)
from string import Template

from environ_odoo_config.odoo_config import OdooEnvConfig
from environ_odoo_config.utils import DEFAULT, NOT_INI_CONFIG

header_tmpl = Template("""= ${opt_group}

This config section ${class_doc} to valid odoo CLI.

include::partial$$converters/${fname}[]

""")

field_tmpl = {
    SimpleKey: Template("""[[option_${init_dest}]]
== ${init_dest}
${f_help}

TIP: $odoo_version

The environment variable `${env_key}` is used and expect a xref:ROOT:type_var.adoc#env_var_value_type_${f_type}[${f_type}].

${cli_used}
"""),
    RepeatableKey: Template("""[[option_${init_dest}]]
== ${init_dest}
NOTE: ${f_help}

${cli_used}

The environment variable `${env_key}` is xref:ROOT:type_var.adoc#env_var_value_type_repeatable[repeatable]. +
This mean a suffix can be added after an **single** `_`.
For example `${env_key}_value`, the suffix is `value` not `_value`

"""),
    SimpleCSVKey: Template("""[[option_${init_dest}]]
== ${init_dest}
NOTE: ${f_help}

${cli_used}

The environment variable `${env_key}` is used and expect a xref:ROOT:type_var.adoc#env_var_value_type_csv[`csv`] value.

.Example
****
Possible values :

* `${env_key}="value1,value2"`
* `${env_key}="value1"`

[TIP]
====
The value are automatically deduplicated. +
`${env_key}="value1,value2"` and `${env_key}="value2,value1,value2"` are the same.
====

****

"""),
    EnumKey: Template("""[[option_${init_dest}]]
== ${init_dest}
NOTE: ${f_help}

${cli_used}

The environment variable `${env_key}` is used and expect a `str`.
${cli_used}
${list_value}
"""),
}

special_tmpl = Template("""
[[env_${env_key}]]
=== ${env_key}
${f_help}

TIP: $odoo_version

The environment variable `${env_key}` is used and expect a `${f_type}`.

${cli_used}
""")

subversion_key_tmpl = Template("""[NOTE]
====
${odoo_version} this key used the cli ${cli_used}
====
""")

class CSVKeyAdoc:
    template = Template("""[[option_${init_dest}]]
== ${init_dest}
NOTE: ${f_help}

${cli_used}

The environment variable `${env_key}` is used and expect a xref:ROOT:type_var.adoc#env_var_value_type_csv[`csv`] value.

.Example
****
Possible values :

* `${env_key}="value1,value2"`
* `${env_key}="value1"`
****

""")
    def create_page(self, key: SimpleCSVKey[Any]):
        return self.template.substitute()

only_cli_tmpl = Template("""=== ${f_help}""")


allconfig = OdooEnvConfig()
converters = {
        type(allconfig.http) : allconfig.http,
        type(allconfig.addons_path) : allconfig.addons_path,
        type(allconfig.database) : allconfig.database,
        type(allconfig.geoip) : allconfig.geoip,
        type(allconfig.gevent) : allconfig.gevent,
        type(allconfig.i18n) : allconfig.i18n,
        type(allconfig.misc) : allconfig.misc,
        type(allconfig.other_option) : allconfig.other_option,
        type(allconfig.process_limit) : allconfig.process_limit,
        type(allconfig.smtp) : allconfig.smtp,
        type(allconfig.test) : allconfig.test,
        type(allconfig.update_init) : allconfig.update_init,
        type(allconfig.wide_modules) : allconfig.wide_modules,
        type(allconfig.workers) : allconfig.workers,
        type(allconfig.logging) : allconfig.logging,
    }
Converters = list(converters.keys())
ROOT_ADOC = Path(__file__).parent / Path("modules/generated")
ROOT_PAGES = ROOT_ADOC / Path("pages")
ROOT_PARTIAL = ROOT_ADOC / Path("partials")

ROOT_ADOC.mkdir(parents=True, exist_ok=True)
ROOT_PAGES.mkdir(parents=True, exist_ok=True)
ROOT_PARTIAL.mkdir(parents=True, exist_ok=True)


class SubVersionKey:
    def __init__(self, origin: EnumKey[Any], sub: OnlyCli[Any]):
        self.origin = origin
        self.sub = sub


def get_adoc(obj: Any) -> str:
    if hasattr(obj, "__adoc__"):
        return obj.__adoc__()
    if obj is Path:
        return "https://docs.python.org/3/library/os.html#os.PathLike[Path]"
    if obj is bool:
        return "https://docs.python.org/3/library/stdtypes.html#boolean-type-bool[bool]"
    if obj is set:
        return "https://docs.python.org/3/library/stdtypes.html#set[set]"
    if obj is str:
        return "https://docs.python.org/3/library/stdtypes.html#str[str]"
    if obj is int:
        return "https://docs.python.org/3/library/functions.html#int[int]"
    if obj is int:
        return "https://docs.python.org/3/library/functions.html#float[float]"
    return obj.__doc__


def get_class_doc_link(ttype):
    if isinstance(ttype, EnumKey):
        return "xref:ROOT:type_var.adoc#env_var_value_type_enum[Enum]"
    if isinstance(ttype, SimpleCSVKey):
        return "xref:ROOT:type_var.adoc#env_var_value_type_csv[CSV]"
    if isinstance(ttype, RepeatableKey):
        return "xref:ROOT:type_var.adoc#env_var_value_type_repeatable[Repeatable]"
    if isinstance(ttype, SimpleKey):
        if ttype.py_type is str:
            return "xref:ROOT:type_var.adoc#env_var_value_type_str[String]"
        if ttype.py_type is int:
            return "xref:ROOT:type_var.adoc#env_var_value_type_int[Int]"
        if ttype.py_type is float:
            return "xref:ROOT:type_var.adoc#env_var_value_type_float[Float]"
        if ttype.py_type is Path:
            return "xref:ROOT:type_var.adoc#env_var_value_type_Path[Path]"
        if ttype.py_type is bool:
            return ("xref:ROOT:type_var.adoc#env_var_value_type_bool[Bool]")
        return f"xref:ROOT:type_var.adoc[SimpleKey({type(ttype.py_type)})]"
    if isinstance(ttype, OnlyCli):
        return "No Environ variables"
    return f"xref:ROOT:type_var.adoc[{type(ttype)}]"


def convert_field(env_key):
    list_value = None
    if type(env_key) is EnumKey:
        list_value = "\n* ".join(["Possible value are:\n"] + list(env_key.py_type._value2member_map_.keys()))
    if isinstance(env_key, SubVersionKey):
        return subversion_key_tmpl.substitute(
            init_dest="QQQQ1",
            f_help="QQQQ2",
            cli_used=f"`{env_key.sub.cli_used()}`",
            env_key=env_key.origin.key,
            f_type="QQQQ4",
            list_value="QQQQ5",
            odoo_version=get_adoc(env_key.sub.odoo_version),
        )
    return field_tmpl[type(env_key)].substitute(
        init_dest=env_key.ini_dest,
        f_help=_get_generic_info(env_key),
        cli_used="\n* ".join(["Odoo cli used:\n"] + env_key.cli),
        env_key=env_key.key,
        f_type=env_key.py_type.__name__,
        list_value=list_value,
        odoo_version=get_adoc(env_key.odoo_version),
    )


def _get_generic_info(env_key: EnvKey[Any]) -> str:
    if env_key.info == DEFAULT:
        if env_key.ini_dest == DEFAULT and env_key.cli == DEFAULT:
            raise ValueError("No ini dest or cli for %s" % env_key)

        info = "Convert"
        if env_key.key != DEFAULT:
            info += f" environ key={env_key.key}"
        if env_key.cli != DEFAULT:
            info += f" cli args={env_key.cli}"
        if env_key.ini_dest != DEFAULT and env_key.cli != DEFAULT:
            info += f" to {env_key.ini_dest}"

        return info
    return env_key.info


def generate_doc_converters():
    converter_pages = ROOT_PAGES / Path("converters")
    partials_pages = ROOT_PARTIAL / Path("converters")
    converter_pages.mkdir(parents=True, exist_ok=True)
    partials_pages.mkdir(parents=True, exist_ok=True)
    navs = []
    allconfig = OdooEnvConfig()

    for c in converters.keys():
        doc_single_line = "convert environment variable related to " + c._opt_group.lower()
        fname = c.__module__.split(".")[-1] + ".adoc"
        adoc_file: Path = converter_pages / fname
        adoc_file.touch(exist_ok=True)
        (partials_pages / fname).touch(exist_ok=True)
        parts = [
            header_tmpl.substitute(
                opt_group=c._opt_group, class_name=c.__qualname__, class_doc=doc_single_line, fname=fname
            )
        ]
        special_field = []
        onlycli_field = []
        for field_name, env_key in c.get_fields().items():
            if isinstance(env_key, OnlyCli):
                onlycli_field.append((field_name, env_key))
                continue
            if env_key.ini_dest == NOT_INI_CONFIG or env_key.cli_used() in (DEFAULT, None):
                special_field.append((field_name, env_key))
                continue
            try:
                parts.append(convert_field(env_key))
                for other_version in env_key.other_version:
                    parts.append(convert_field(SubVersionKey(env_key, other_version)))
            except Exception as e:
                print("Failed top render doc for", field_name, env_key)
                raise e
        if special_field:
            parts.extend(["\n", "== Other environment keys", "\n"])
            for field_name, env_key in special_field:
                parts.append(
                    special_tmpl.substitute(
                        init_dest=env_key.ini_dest,
                        f_help=_get_generic_info(env_key),
                        cli_used="NOTE: No cli argument exist for this key",
                        env_key=env_key.key,
                        f_type=getattr(env_key.py_type, "__name__", "FFFFFFFFFFFFF"),
                        odoo_version=get_adoc(env_key.odoo_version),
                    )
                )
        if onlycli_field:
            parts.extend(["\n", "== Only CLI args", "\n"])
            for field_name, env_key in onlycli_field:
                parts.append(
                    only_cli_tmpl.substitute(
                        init_dest=env_key.ini_dest,
                        f_help=_get_generic_info(env_key),
                        cli_used="None",
                        env_key=env_key.key,
                        f_type=getattr(env_key.py_type, "__name__", "XXXXXX"),
                        odoo_version=get_adoc(env_key.odoo_version),
                    )
                )
        with adoc_file.open(mode="w") as fopen:
            fopen.write("\n".join(parts))
        navs.append(f"** xref:converters/{fname}[]")
    return navs


Index_tmpl = Template("""= Index ${odoo_version_str}

include::partial$$${partial_fname}.adoc[]

""")


class AdocFile:
    def __init__(self, fname: str, title: str = None, title_lvl: int = 1):
        self._fname = fname
        self.title = title
        self.title_lvl = title_lvl
        self._content = []

    def include(self, file):
        self._content.append(str)


class AdocTableColumn:
    def __init__(self, name):
        self._name = name

    def __adoc__(self) -> str:
        return self._name


class AdocTable:
    def __init__(self, col_names: list[str], *, name: str | None = None, **table_opt):
        self._name = name
        self._cols = [AdocTableColumn(col) for col in col_names or []]
        self._table_opt = table_opt
        self._lines = []

    def add_column(self, *col_name: str):
        self._cols.extend([AdocTableColumn(col) for col in col_name])

    def add_line(self, *data: str):
        assert len(self._cols) == len(data)
        self._lines.append([str(d) for d in data])

    def extend_lines(self, *data: list[str]):
        self._lines.extend(list(data))

    def __adoc__(self) -> str:
        buff = io.StringIO()
        if self._name:
            print(f".{self._name}", file=buff)
        print("|===", file=buff)
        print("|" + "| ".join([c.__adoc__() for c in self._cols]), file=buff)
        buff.write("\n")
        for line in self._lines:
            # TODO expand to follow number of column
            print("|" + "| ".join(line), file=buff)
        print("|===", file=buff)
        return buff.getvalue()


Table_index_tmpl = Template(""".${converter_name}
|===
| Env Var name | Type | Doc

${table_content}
|===""")

Table_index_line_tmpl = Template("""| ${name} | ${type_var} | ${doc_link}""")


def generate_index_env():
    pages = ROOT_PAGES / Path("environ")
    partial = ROOT_PARTIAL / Path("environ")
    if not pages.exists():
        os.mkdir(pages)
    if not partial.exists():
        os.mkdir(partial)
    fname = "index.adoc"
    adoc_file: Path = pages / fname
    adoc_file.touch(exist_ok=True)
    (partial / f"{fname}").touch(exist_ok=True)

    page_buff = io.StringIO()
    print("= Index Supported Environ variable", file=page_buff)
    print("", file=page_buff)

    for c in Converters:
        converter_fname = c.__module__.split(".")[-1] + ".adoc"
        print("==", c._opt_group, file=page_buff)
        print("", file=page_buff)

        table = AdocTable(col_names=["Env Var name", "Type", "Doc", "Version Supported"])
        for field_name, env_key in c.get_fields().items():
            if isinstance(env_key, OnlyCli):
                continue
            if not env_key:
                continue
            if env_key.ini_dest == NOT_INI_CONFIG:
                continue
            adoc_xref = f"xref:converters/{converter_fname}#option_{env_key.ini_dest}[{env_key.ini_dest}]"
            if env_key.ini_dest == NOT_INI_CONFIG or env_key.cli_used() in (DEFAULT, None):
                adoc_xref = f"xref:converters/{converter_fname}#env_{env_key.key}[{env_key.key}]"

            table.add_line(
                env_key.key,
                get_class_doc_link(env_key),
                adoc_xref,
                get_adoc(env_key.odoo_version),
            )
        print(get_adoc(table), file=page_buff)

        with adoc_file.open(mode="w") as fopen:
            fopen.write(page_buff.getvalue())
    return [f"** xref:environ/{fname}[]"]


if __name__ == "__main__":
    nav_file = ROOT_ADOC / "nav.adoc"
    if not nav_file.exists():
        nav_file.touch()

    page_buff = io.StringIO()
    print(".Index", file=page_buff)
    for nav in generate_index_env():
        print(nav, file=page_buff)
    print("", file=page_buff)
    print(".Converter to Odoo config", file=page_buff)
    for nav in generate_doc_converters():
        print(nav, file=page_buff)
    with nav_file.open(mode="w") as fopen:
        fopen.write(page_buff.getvalue())

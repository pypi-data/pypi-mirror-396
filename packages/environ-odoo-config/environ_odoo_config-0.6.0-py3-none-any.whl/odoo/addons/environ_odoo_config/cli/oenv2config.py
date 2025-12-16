from environ_odoo_config import _odoo_command, cli


class _OEnv2Config(_odoo_command.OdooCommand):
    """
    [Deprecated] alias of `generate_config`
    """

    # The attribute EnvironConfigGenerate (exactly the same of the current class name) is for old odoo version
    name = "oenv2config"

    # @property
    # def prog(self):
    #     return super().prog

    @property
    def parser(self):
        return cli.get_odoo_cmd_parser()

    def run(self, cmdargs):
        return cli.cli_main(cmdargs)

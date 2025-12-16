from environ_odoo_config import _odoo_command, cli


class _GenerateConfig(_odoo_command.OdooCommand):
    """
    Generate an odoo config file from environ variable.
    """

    # The attribute EnvironConfigGenerate (exactly the same of the current class name) is for old odoo version
    name = "generate_config"

    # @property
    # def prog(self):
    #     return super().prog

    @property
    def parser(self):
        return cli.get_odoo_cmd_parser()

    def run(self, cmdargs):
        return cli.cli_main(cmdargs)

import odoo

if odoo.release.version >= "16.0":  # Prior to 16.0, change the cli name was buggy. Backport code
    from odoo.cli import Command as OdooCommand
else:
    import odoo.cli.command

    class OdooCommand:
        name = None

        def __init_subclass__(cls):
            cls.name = cls.name or cls.__name__.lower()
            odoo.cli.command.commands[cls.name] = cls

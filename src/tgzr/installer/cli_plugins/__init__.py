from tgzr.cli.utils import TGZRCliGroup

from .install_cli import install_cmd, help_cmd


def install_cli_plugins(group: TGZRCliGroup):
    group.add_command(install_cmd)
    cmd, kwargs, setter_name = group.get_default_command()
    if cmd is None:
        group.set_default_command(install_cmd, "tgzr.installer")

    help = group.find_group("help")
    if help is not None:
        help.add_command(help_cmd)

import click
import rich
from rich.console import Console
from rich.markdown import Markdown
from rich.table import Table

from .._version import __version__
from ..install import gui_install, headless_install


@click.command("install")
@click.option(
    "-H",
    "--home",
    help="Path to install to. Default to current dir. Created if needed.",
)
@click.option("-C", "--connection", default="tgzr://alpha", help="Where to connect to.")
@click.option(
    "-U",
    "--userid",
    help="The userid to use for connection (only applicable for some connection plugins).",
)
@click.option(
    "-p",
    "--python-version",
    default="3.12",
    help="The python version to use. Defaults to 3.12 which in the minimum (3.14 is known to cause issue with nicegui on windows for now)",
)
@click.option(
    "--default-index",
    default="https://pi.alpha.tgzr.net/tgzr/alpha-prod",
    help="The URL of the default package index (Default is the url of the official TGZR Package Index).",
)
@click.option(
    "-f",
    "--find-links",
    # default="https://pypi.org/simple",
    help="path a folder containing packages to install. Usefull in no-internet situations.",
)
@click.option(
    "--allow-prerelease",
    is_flag=True,
    help="Allow installing tgzr using pre-release packages. Defaults to False.",
)
@click.option(
    "--no-cache",
    is_flag=True,
    help="Disable uv cache (mostly for testing). Defaults to False.",
)
@click.option(
    "--headless",
    is_flag=True,
    help="No not use GUI. This is way faster, but you need to provide all options on the command line.",
)
@click.option(
    "-K",
    "--keep-temp-files",
    is_flag=True,
    help="Do not cleanup temp file. Usefull when debugging the installer.",
)
@click.option(
    "-X",
    "--exists-ok",
    is_flag=True,
    help="Override instead of failing if the installation already exist.",
)
@click.option(
    "-i",
    "--info",
    is_flag=True,
    help="Show info about the installer.",
)
def install_cmd(
    home: str | None,
    connection: str | None,
    userid: str | None,
    python_version: str | None,
    default_index: str | None = None,
    find_links: str | None = None,
    allow_prerelease: bool = False,
    no_cache: bool = False,
    headless: bool = False,
    keep_temp_files: bool = False,
    exists_ok: bool = False,
    info: bool = False,
):
    """
    Create or Update a TGZR Installation.
    """
    if info:
        import tgzr.cli._version
        import sys
        import uv

        table = Table(
            "Name",
            "Version",
            show_lines=True,
            show_header=False,
            title="Installer Info",
        )
        table.add_row("tgzr.installer", __version__)
        table.add_row("tgzr.cli", tgzr.cli._version.__version__)
        table.add_row("python version", sys.version)
        table.add_row("executable", sys.executable)
        table.add_row("UV bin", uv.find_uv_bin())

        rich.print(table)
        return

    if not headless:
        gui_install(
            home=home,
            connection_url=connection,
            userid=userid,
            python_version=python_version,
            default_index=default_index,
            find_links=find_links,
            allow_prerelease=allow_prerelease,
            no_cache=no_cache,
            keep_temp_files=keep_temp_files,
            exists_ok=exists_ok,
            echo=rich.print,
        )
    else:
        if home is None:
            raise click.UsageError(
                "You need to specify the home path for headless installations."
            )
        if connection is None:
            raise click.UsageError(
                "You need to specify the connection url for headless installations."
            )

        headless_install(
            home=home,
            connection_url=connection,
            userid=userid,
            python_version=python_version,
            default_index=default_index,
            find_links=find_links,
            allow_prerelease=allow_prerelease,
            no_cache=no_cache,
            keep_temp_files=keep_temp_files,
            exists_ok=exists_ok,
            echo=rich.print,
        )


HELP = """
.

## TGZR Installation

In order to start TGZR you need an `connection url` telling
where you want to connect to. 

Once connected, you need a folder to install your apps. 
This folder is known as the TGZR `home folder`.

The process of installing tgzr boils down to creating the `home folder`
and save the `connection url` inside it.

You can install TGZR as many times as you need to. Common reasons to 
do so are:
- You want to separate work done with different Studios in different 
home folders.
- You use several TGZR identities, so you need several home folders
- You are developing apps and tools and need to use a TGZR instance
dedicated to your tests, beta release, etc... so you need different 
connection urls
- You love TGZR so much you just cant stop installing it everywhere ^_^

### Install

`Double-Click` the installer, or execute `tgzr-installer-xxx install`.

Once the preparation is done, the Installer GUI will show up.

This GUI will let you specify all install options.
You can use the command line arguments to provide default values, use
`tgzr-installer-xxx -h` to see the list of arguments.

### Headless install

When you want to automate the installation, pass all the arguments
to the installer and include `--headless`.


Here are a few examples:
- installing to a directory, with default connection: `tgzr-install-xxx install -D D:/TGZR`
- installing here, using a specified connection: `tgzr-install-xxx install -D . -C tgzr://alpha`
- don't install, just test a connection: `tgzr-install-xxx install -C file://D:/path/to/tgzr_connection_info.json`


Use `tgzr-install-xxx install -h` for details on available options.

Happy installing! ✨

### Advanced Options

During installation, tgzr will fetch packages from PyPI.

If you need to use custom packages instead of official ones, 
you can override the default package index with 
`--default-index` and/or specify an local folder containing the
packages to use with `-f` or `--find-links`.

Do note that if you're trying to install dev/beta/pre packages with 
`--find-links` you will also need to use `--allow-prerelease` !

.
"""


@click.command("install")
def help_cmd():
    """Help on installing tgzr"""

    console = Console()
    md = Markdown(HELP)
    console.print(md)
    return

from __future__ import annotations
from typing import Callable

import os
from pathlib import Path
import tempfile
import platform
import subprocess

import uv


def execute(cmd: list[str], echo, raises: bool = False, exits: bool = True) -> bool:
    cmd_str = " ".join(cmd)
    print(f"EXEC: {cmd_str}")
    echo(f"EXEC: {cmd_str}")
    # ret = os.system(cmd)
    try:
        ret = subprocess.check_call(cmd)
    except Exception as err:
        if raises:
            raise
        else:
            echo(f"!ERROR! Cmd exception 😬: {err}")
            return False
    if ret:
        if raises:
            raise ChildProcessError(f"Error creating venv with cmd: {cmd}")
        echo("!ERROR! Cmd returned non-zero 😬")
        return False
    return True


def create_temp_venv(
    python_version: str | None,
    default_index: str | None,
    find_links: str | None,
    allow_prerelease: bool,
    no_cache: bool,
    requirements: list[str],
    echo,
) -> str | None:

    #
    # Clean up PATH
    #

    # (we've seen situations where things in the PATH would mess up the installation)
    PATH = os.environ.get("PATH", "")
    path = PATH.split(os.pathsep)
    banned_words = ["python", ".poetry"]
    clean_path = []
    for i in path:
        keep = True
        for word in banned_words:
            if word in i.lower():
                keep = False
                break
        if keep:
            clean_path.append(i)
    os.environ["PATH"] = os.pathsep.join(clean_path)

    #
    # Locate UV
    #

    try:
        # NOTE: this works when we're a pysintaller binary thanks to the
        # data arg of the Analysis arg in the pyinstall spec file:
        # it keeps the uv executable installed in your current venv
        # (it exists because we have uv in the project requirement)
        # and place it in a "bin" folder inside the pysintaller archive.
        # This bin folder is looked up by uv.find_uv_bin() so we're
        # good.
        uv_exe = uv.find_uv_bin()
    except Exception as err:
        # This should not occur ¯\\_(ツ)_/¯
        echo(f"Oops, could not find uv: {err}")

    #
    # Create Temp venv
    #

    venv_path = tempfile.mkdtemp(prefix="tgzr_install_tmp_venv")
    echo(f"Creating temp venv: {venv_path}")

    cmd = [
        uv_exe,
        "venv",
        "-p",
        python_version,
        "--prompt",
        "TGZR-Installer",
        venv_path,
    ]
    if not execute(cmd, echo):
        return None

    #
    # Install requirements
    #

    default_index_options = []
    if default_index:
        # default_index_options = f"--default-index {default_index} --index https://pypi.org/simple  --index-strategy unsafe-best-match"
        default_index_options = ["--index", default_index]

    find_links_options = []
    if find_links:
        find_links_options = ["--find-links", find_links]

    prerelease_options = []
    if allow_prerelease:
        # We are automatically disabling cache when using pre-releases
        # because cache f*cks my brain.
        # If too anoying, we'll add a separate option like '--use-case-with-prerelease'
        prerelease_options = ["--prerelease=allow"]

    no_cache_options = []
    if no_cache:
        no_cache_options = ["--no-cache"]

    # cmd = f"{uv_exe} pip install {default_index_options} {find_links_options} {no_cache_options} {prerelease_options} --python {venv_path} {requirements}"
    cmd = [
        uv_exe,
        "pip",
        "install",
        *default_index_options,
        *find_links_options,
        *no_cache_options,
        *prerelease_options,
        "--python",
        venv_path,
        *requirements,
    ]

    if not execute(cmd, echo):
        return None

    return venv_path


def create_home_folder(
    home_path: Path,
    connection_url: str,
    userid: str | None,
    venv_path: str,
    python_version: str | None,
    default_index: str | None,
    find_links: str | None,
    allow_prerelease: bool,
    no_cache: bool,
    echo,
):
    if platform.system() == "Windows":
        tgzr_exe = f"{venv_path}/Scripts/tgzr.exe"
    else:
        tgzr_exe = f"{venv_path}/bin/tgzr"

    more_options = []
    if python_version:
        more_options.extend([f"--python-version", python_version])
    if default_index:
        more_options.extend([f"--default-index", default_index])
    if find_links:
        more_options.extend(
            [
                f"--find-links",
                find_links,
            ]
        )
    if allow_prerelease:
        more_options.extend(["--allow-prerelease"])

    if no_cache:
        more_options.extend(["--no-cache"])

    if userid:
        more_options.extend([f"--userid", userid])

    cmd = [
        tgzr_exe,
        "session",
        "create",
        "--home",
        str(home_path),
        "--connection",
        connection_url,
        *more_options,
    ]

    if not execute(cmd, echo):
        echo("Could not create home folder :/")
        return


def gui_install(
    home: Path | str | None = None,
    connection_url: str | None = None,
    userid: str | None = None,
    python_version: str | None = None,
    default_index: str | None = None,
    find_links: str | None = None,
    allow_prerelease: bool = False,
    no_cache: bool = False,
    keep_temp_files: bool = False,
    exists_ok: bool = False,
    echo: Callable[[str], None] | None = None,
):
    if home is not None:
        home = str(Path(home).resolve())
    echo = echo or print
    echo("- GUI INSTALL -")

    print(f"-> {home=}")
    print(f"-> {connection_url=}")
    print(f"-> {userid=}")
    print(f"-> {python_version=}")
    print(f"-> {default_index=}")
    print(f"-> {find_links=}")
    print(f"-> {allow_prerelease=}")
    print(f"-> {no_cache=}")
    print(f"-> {exists_ok=}")
    print(f"-> {keep_temp_files=}")

    venv_path = create_temp_venv(
        python_version=python_version,
        default_index=default_index,
        find_links=find_links,
        allow_prerelease=allow_prerelease,
        no_cache=no_cache,
        requirements=["tgzr.session", "tgzr.cli", "tgzr.apps.installer"],
        echo=echo,
    )
    if venv_path is None:
        echo("Could not create tmp venv :/")
        return

    if platform.system() == "Windows":
        tgzr_exe = f"{venv_path}/Scripts/tgzr.exe"
    else:
        tgzr_exe = f"{venv_path}/bin/tgzr"

    more_options = []
    if python_version is not None:
        more_options.extend(
            ["--python-version", python_version],
        )
    if default_index is not None:
        more_options.extend(
            ["--default-index", default_index],
        )
    if find_links is not None:
        more_options.extend(
            ["--find-links", find_links],
        )
    if allow_prerelease:
        more_options.extend(["--allow-prerelease"])
    if no_cache:
        more_options.extend(["--no-cache"])
    if userid is not None:
        more_options.extend(["--userid", userid])

    cmd = [
        tgzr_exe,
        "app",
        "gui_install",
        "--home",
        home or str(Path.cwd()),
        "--connection",
        connection_url,
        *more_options,
    ]

    if not execute(cmd, echo):
        echo("Could not launch GUI installer")
        return


def headless_install(
    home: Path | str,
    connection_url: str,
    userid: str | None = None,
    python_version: str | None = None,
    default_index: str | None = None,
    find_links: str | None = None,
    allow_prerelease: bool = False,
    no_cache: bool = False,
    keep_temp_files: bool = False,
    exists_ok: bool = False,
    echo: Callable[[str], None] | None = None,
):
    """
    Install TGZR by creating a tmp venv with tgzr.session and
    execute `tgzr.session..

    May raise: FileExistsError, ChildProcessError.
    """

    echo = echo or print
    echo("- HEADLESS INSTALL -")

    if 1:
        print(f"-> {home=}")
        print(f"-> {connection_url=}")
        print(f"-> {userid=}")
        print(f"-> {python_version=}")
        print(f"-> {default_index=}")
        print(f"-> {find_links=}")
        print(f"-> {allow_prerelease=}")
        print(f"-> {no_cache=}")
        print(f"-> {exists_ok=}")
        print(f"-> {keep_temp_files=}")

    home = Path(home)
    if home.exists() and not exists_ok:
        raise FileExistsError(
            f"The path {home} already exists. Use -X to install over it. Aborting."
        )

    echo(f"Installing tgzr at {home}")

    venv_path = create_temp_venv(
        python_version=python_version,
        default_index=default_index,
        find_links=find_links,
        allow_prerelease=allow_prerelease,
        no_cache=no_cache,
        requirements=["tgzr.session", "tgzr.cli"],
        echo=echo,
    )
    if venv_path is None:
        echo("Cound not create temp venv")
        return

    #
    # Create the home folder using tgzr.session
    #
    create_home_folder(
        home_path=home,
        connection_url=connection_url,
        userid=userid,
        venv_path=venv_path,
        python_version=python_version,
        default_index=default_index,
        no_cache=no_cache,
        find_links=find_links,
        allow_prerelease=allow_prerelease,
        echo=echo,
    )

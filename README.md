# tgzr.installer
TGZR Installer

# Generatet the installer

You need to install the package with the `dev` extra requirements:
`uv pip install tgzr.installer[dev]`

Then you can generate the installer with: `uv run --extra dev pyinstaller pyinstaller_specs/tgzr-<platform>.spec`

The `tgzr-<platform>` executable will be generated in the `dist/` folder
import sys

if __name__ == "__main__":
    # This is executed by the pyinstaller binary.
    # NB: we need a absolute imports here for pyinstaller to work
    # NB2: we did need to setup the pyinstaller spec metadata in order
    # for entry-points to load.

    from tgzr.cli.main_cli import tgzr_cli

    sys.exit(tgzr_cli())

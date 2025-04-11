#!@PYTHON@
"""A launcher for the application."""

import gettext
import locale
import sys

BASE_ID = "@BASE_ID@"
PKG_DATA_DIR = "@pkgdatadir@"
LOCALE_DIR = "@localedir@"

sys.path.insert(1, PKG_DATA_DIR)

locale.bindtextdomain(BASE_ID, LOCALE_DIR)
locale.textdomain(BASE_ID)
gettext.bindtextdomain(BASE_ID, LOCALE_DIR)
gettext.textdomain(BASE_ID)


def main() -> int:
    """Entry point for the application."""
    from cys403_project.ui.main import main_ui

    main_ui(sys.argv)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

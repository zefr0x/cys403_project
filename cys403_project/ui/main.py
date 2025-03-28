"""Main file for the GUI."""

import contextlib
from collections.abc import Sequence

import gi

from cys403_project.__about__ import APP_ID, APP_NAME

from .main_window import Cys403ProjectMainWindow

gi.require_version("Adw", "1")
from gi.repository import (  # noqa: E402
    Adw,
    Gio,
    GLib,
)


class Cys403Project(Adw.Application):
    """The Main application class."""

    def __init__(self) -> None:
        """Initialize the application."""
        super().__init__(
            application_id=APP_ID,
            flags=Gio.ApplicationFlags.HANDLES_OPEN,
        )
        GLib.set_application_name(APP_NAME)

    def do_open(self, files: Sequence[Gio.File], _count: int, _hint: str) -> None:  # type: ignore[override]
        """Handle CLI args."""
        self.files = files

        self.activate()

    def do_activate(self) -> None:
        """Handle activate event."""
        Adw.Application.do_activate(self)

        self.window = self.props.active_window

        if not self.window:
            self.window = Cys403ProjectMainWindow(self)

        self.window.present()

        # Pass CLI args to the main window
        with contextlib.suppress(AttributeError, KeyError):
            self.window.open_files(self.files)  # type: ignore[attr-defined]


def main_ui(argv: Sequence[str]) -> int:
    """Launch the UI with arguments."""
    app = Cys403Project()
    return app.run(list(argv))

"""Main application window."""

import logging
from collections.abc import Sequence
from gettext import gettext as _

import gi

from cys403_project.__about__ import (
    APP_ARTISTS_LIST,
    APP_AUTHOR,
    APP_DEVELOPERS_LIST,
    APP_ID,
    APP_VERSION,
    BUG_REPORT_URL,
    BUILD_PROFILE,
    PROJECT_HOME_PAGE_URL,
)

from .image_page import ImagePage
from .rsa_page import RsaPage

gi.require_version("Adw", "1")
gi.require_version("Gtk", "4.0")
from gi.repository import (  # noqa: E402
    Adw,
    Gio,
    Gtk,
)

logger = logging.getLogger(__name__)


class Cys403ProjectMainWindow(Adw.ApplicationWindow):
    """Main window."""

    def __init__(self, application: Adw.Application) -> None:
        """Initialize main window."""
        super().__init__(
            application=application,
            title=_("CYS-403 Project"),
        )
        self.set_size_request(500, 800)

        if BUILD_PROFILE == "development":
            self.add_css_class("devel")

        # Main layout
        main_layout = Adw.ToolbarView()
        self.set_content(main_layout)

        # View switcher
        view_switcher = Adw.ViewSwitcher()
        view_switcher.set_policy(Adw.ViewSwitcherPolicy.WIDE)

        # View stack
        view_stack = Adw.ViewStack()
        view_switcher.set_stack(view_stack)

        self._rsa_page = RsaPage(self)
        self._image_page = ImagePage(self)

        view_stack.add_titled_with_icon(
            self._rsa_page, "rsa", _("RSA"), "network-wireless-encrypted-symbolic"
        )
        view_stack.add_titled_with_icon(
            self._image_page,
            "image",
            _("Image"),
            "image-x-generic-symbolic",
        )

        # Window header
        header = self.__build_header()
        header.set_title_widget(view_switcher)
        main_layout.add_top_bar(header)

        # Main Overlay
        self._overlay = Adw.ToastOverlay(child=view_stack)
        main_layout.set_content(self._overlay)

        # Bottom bar
        view_switcher_bar = Adw.ViewSwitcherBar()
        view_switcher_bar.set_stack(view_stack)

        main_layout.add_bottom_bar(view_switcher_bar)

        # BreakPoint
        break_point = Adw.Breakpoint(
            condition=Adw.breakpoint_condition_parse("max-width: 700px")
        )
        self.add_breakpoint(break_point)
        break_point.add_setter(self._sidebar_toggle_button, "visible", value=True)
        break_point.add_setter(self._rsa_page.split_view, "collapsed", value=True)
        break_point.add_setter(self._image_page.split_view, "collapsed", value=True)

    def __build_header(self) -> Adw.HeaderBar:
        """Create the header bar for the application."""
        header = Adw.HeaderBar()

        # About application button
        about_button = Gtk.Button(icon_name="help-about-symbolic")
        header.pack_end(about_button)
        about_button.connect("clicked", self.__show_about_dialog)

        self._sidebar_toggle_button = Gtk.ToggleButton(
            icon_name="sidebar-show-symbolic", visible=False
        )
        header.pack_start(self._sidebar_toggle_button)

        self._sidebar_toggle_button.connect(
            "toggled", self._on_sidebar_toggle_button_toggled
        )
        return header

    def _on_sidebar_toggle_button_toggled(self, button: Gtk.ToggleButton) -> None:
        """Hnalde sidebar button toggled."""
        self._rsa_page.split_view.set_show_sidebar(button.props.active)
        self._image_page.split_view.set_show_sidebar(button.props.active)

    def open_files(self, files: Sequence[Gio.File]) -> None:
        """
        Open files.

        Used to pass input from the CLI.
        """
        # TODO: Implement opening files from CLI.

    def show_error(self, msg: str) -> None:
        """Display an error toast."""
        self._overlay.dismiss_all()  # type: ignore[attr-defined]
        self._overlay.add_toast(
            Adw.Toast(
                custom_title=Gtk.Label(
                    label=_("<b>ERROR: %s</b>") % msg,
                    css_classes=("error",),
                    use_markup=True,
                    wrap=True,
                )
            )
        )

    def __show_about_dialog(self, _button: Gtk.Button) -> None:
        """Present the app's about dialog."""
        about_window = Adw.AboutDialog(
            application_icon=APP_ID,
            application_name=self.get_title() or "",
            developer_name=APP_AUTHOR,
            developers=APP_DEVELOPERS_LIST,
            artists=APP_ARTISTS_LIST,
            # TRANSLATORS: The string may contain email addresses and URLs.
            translator_credits=_("translator-credits"),
            copyright="© 2024 " + APP_AUTHOR,
            issue_url=BUG_REPORT_URL,
            license_type=Gtk.License.GPL_3_0_ONLY,
            version=APP_VERSION,
            website=PROJECT_HOME_PAGE_URL,
        )

        about_window.add_acknowledgement_section(
            _("External Libraries"),
            [
                "PyGobject https://gitlab.gnome.org/GNOME/pygobject",
                "pycryptodome https://www.pycryptodome.org/",
                "Pillow https://python-pillow.github.io/",
            ],
        )

        about_window.add_acknowledgement_section(
            _("Application Icon"),
            [
                "Paomedia https://www.iconfinder.com/icons/299105/lock_icon",
            ],
        )

        about_window.present(self)

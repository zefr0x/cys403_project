"""RSA encryption page."""

import multiprocessing
from base64 import b64decode, b64encode
from gettext import gettext as _

import gi

from cys403_project.crypto.rsa import MessageTooLongError, RSAEncryptor

gi.require_version("Adw", "1")
gi.require_version("Gtk", "4.0")
from gi.repository import (  # noqa: E402
    Adw,
    GLib,
    Gtk,
)


class KeyGenOptionsDialog(Adw.Dialog):
    """Dialog for selecting key options."""

    def __init__(self) -> None:
        """Initialize the dialog."""
        super().__init__(title=_("Key Generations Options"), hexpand=True)

        layout = Adw.ToolbarView()
        self.set_child(layout)

        # Dialog Header
        header = Adw.HeaderBar(
            show_end_title_buttons=False, show_start_title_buttons=False
        )
        layout.add_top_bar(header)

        cancel_button = Gtk.Button(label=_("Cancel"))
        header.pack_start(cancel_button)
        cancel_button.connect("clicked", lambda _: self.close())

        self.generate_button = Gtk.Button(
            label=_("Generate"), css_classes=("suggested-action",)
        )
        header.pack_end(self.generate_button)

        # Dialog content
        options_group = Adw.PreferencesGroup(
            title=_("RSA Key Options"),
            halign=Gtk.Align.FILL,
            margin_start=24,
            margin_end=24,
            margin_bottom=24,
            margin_top=12,
        )
        layout.set_content(options_group)

        self._modulo_size = Adw.SpinRow.new_with_range(
            min=1, max=18446744073709551616, step=1
        )
        self._modulo_size.set_title(_("Modulo Size"))
        self._modulo_size.set_subtitle(_("Exponents of 2"))
        self._modulo_size.set_value(2048)
        options_group.add(self._modulo_size)

        self._public_exponent = Adw.SpinRow.new_with_range(
            min=1, max=18446744073709551616, step=1
        )
        self._public_exponent.set_title(_("Public Exponent"))
        self._public_exponent.set_subtitle(_("Must be prime number"))
        self._public_exponent.set_value(65537)
        options_group.add(self._public_exponent)

    def get_modulo_size(self) -> int:
        """Get the key size from ui."""
        return int(self._modulo_size.get_value())

    def get_public_exponent(self) -> int:
        """Get the public exponent from ui."""
        return int(self._public_exponent.get_value())


class RsaPage(Adw.Bin):
    """Page as interface to the RSA text encryption."""

    def __init__(self, window: Adw.ApplicationWindow) -> None:
        """Initialize the page."""
        super().__init__()
        self._window = window

        self.split_view = Adw.OverlaySplitView()
        self.set_child(self.split_view)

        # Sidebar
        sidebar_box = Gtk.Box(
            orientation=Gtk.Orientation.VERTICAL,
            spacing=13,
            margin_start=7,
            margin_end=7,
            margin_top=7,
            margin_bottom=7,
        )
        self.split_view.set_sidebar(sidebar_box)
        sidebar_box.set_size_request(250, 0)

        self._key_gen_button = Gtk.Button(label=_("Generate New Key"))
        sidebar_box.append(self._key_gen_button)
        self._key_gen_button.connect("clicked", self._generate_new_key)

        self._modulo = Gtk.TextView(wrap_mode=Gtk.WrapMode.CHAR, vexpand=True)
        self._modulo_scrollable = Gtk.ScrolledWindow(child=self._modulo)
        sidebar_box.append(
            Gtk.Frame(
                child=self._modulo_scrollable,
                label_widget=Gtk.Label(use_markup=True, label=_("<b>Modulo</b>")),
            )
        )

        self._public_exponent = Gtk.TextView(wrap_mode=Gtk.WrapMode.CHAR, vexpand=True)
        self._public_exponent_scrollable = Gtk.ScrolledWindow(
            child=self._public_exponent
        )
        sidebar_box.append(
            Gtk.Frame(
                child=self._public_exponent_scrollable,
                label_widget=Gtk.Label(
                    use_markup=True, label=_("<b>Public Exponent</b>")
                ),
            )
        )

        self._private_exponent = Gtk.TextView(wrap_mode=Gtk.WrapMode.CHAR, vexpand=True)
        self._private_exponent_scrollable = Gtk.ScrolledWindow(
            child=self._private_exponent
        )
        sidebar_box.append(
            Gtk.Frame(
                child=self._private_exponent_scrollable,
                label_widget=Gtk.Label(
                    use_markup=True, label=_("<b>Private Exponent</b>")
                ),
            )
        )

        # Content
        content_box = Gtk.Box(
            orientation=Gtk.Orientation.VERTICAL,
            spacing=13,
            margin_start=7,
            margin_end=7,
            margin_top=7,
            margin_bottom=7,
        )

        self._input_text = Gtk.TextView(wrap_mode=Gtk.WrapMode.CHAR, vexpand=True)
        content_box.append(
            Gtk.Frame(
                child=Gtk.ScrolledWindow(child=self._input_text),
                label_widget=Gtk.Label(use_markup=True, label=_("<b>Input</b>")),
            )
        )

        buttons_box = Gtk.Box(
            orientation=Gtk.Orientation.HORIZONTAL,
            spacing=13,
        )
        content_box.append(buttons_box)

        encrypt_button = Gtk.Button(label=_("Encrypt"))
        buttons_box.append(encrypt_button)
        encrypt_button.connect("clicked", self._encrypt)

        decrypt_button = Gtk.Button(label=_("Decrypt"))
        buttons_box.append(decrypt_button)
        decrypt_button.connect("clicked", self._decrypt)

        self._output_text = Gtk.TextView(wrap_mode=Gtk.WrapMode.CHAR, vexpand=True)
        content_box.append(
            Gtk.Frame(
                child=Gtk.ScrolledWindow(child=self._output_text),
                label_widget=Gtk.Label(use_markup=True, label=_("<b>Output</b>")),
            )
        )

        self.split_view.set_content(content_box)

    def _generate_new_key(self, _button: Gtk.Button) -> None:
        """Create new key and show it in the ui."""
        options_dialog = KeyGenOptionsDialog()

        def on_generate_button_clicked(_button: Gtk.Button) -> None:
            """Key generation handler."""
            options_dialog.close()
            self.set_keygen_loading(True)

            process = KeyGen(
                self,
                key_size=options_dialog.get_modulo_size(),
                key_public_exponent=options_dialog.get_public_exponent(),
            )
            process.start()

            GLib.timeout_add(100, process.check_for_result)

        options_dialog.generate_button.connect("clicked", on_generate_button_clicked)

        options_dialog.present(self._window)

    def set_keygen_loading(self, value: bool) -> None:  # noqa: FBT001
        """Disable or enable key gen button and show spinners in sidebar."""
        self._key_gen_button.set_sensitive(not value)

        if value:
            self._modulo_scrollable.set_child(Adw.Spinner(vexpand=True))  # type: ignore[attr-defined]
            self._public_exponent_scrollable.set_child(Adw.Spinner(vexpand=True))  # type: ignore[attr-defined]
            self._private_exponent_scrollable.set_child(Adw.Spinner(vexpand=True))  # type: ignore[attr-defined]
        else:
            self._modulo_scrollable.set_child(self._modulo)
            self._public_exponent_scrollable.set_child(self._public_exponent)
            self._private_exponent_scrollable.set_child(self._private_exponent)

    def set_key(self, key: tuple[tuple[bytes, bytes], tuple[bytes, bytes]]) -> None:
        """Set the key in the ui."""
        self._public_exponent.get_buffer().set_text(
            b64encode(key[0][0]).decode("ascii")
        )
        self._private_exponent.get_buffer().set_text(
            b64encode(key[1][0]).decode("ascii")
        )
        self._modulo.get_buffer().set_text(b64encode(key[0][1]).decode("ascii"))

    def get_public_exponent(self) -> bytes:
        """Get the public exponent from the ui."""
        buf = self._public_exponent.get_buffer()
        start_iter = buf.get_start_iter()
        end_iter = buf.get_end_iter()

        return b64decode(buf.get_text(start_iter, end_iter, include_hidden_chars=False))

    def get_private_exponent(self) -> bytes:
        """Get the private exponent from the ui."""
        buf = self._private_exponent.get_buffer()
        start_iter = buf.get_start_iter()
        end_iter = buf.get_end_iter()

        return b64decode(buf.get_text(start_iter, end_iter, include_hidden_chars=False))

    def get_modulo(self) -> bytes:
        """Get the modulo from the ui."""
        buf = self._modulo.get_buffer()
        start_iter = buf.get_start_iter()
        end_iter = buf.get_end_iter()

        return b64decode(buf.get_text(start_iter, end_iter, include_hidden_chars=False))

    def _encrypt(self, _button: Gtk.Button) -> None:
        """Encrypt the input using the key."""
        e = self.get_public_exponent()
        n = self.get_modulo()

        if e == b"" or n == b"":
            # TODO: Show error message.
            pass
        else:
            encryptor = RSAEncryptor(public_key=(e, n))

            buf = self._input_text.get_buffer()
            start_iter = buf.get_start_iter()
            end_iter = buf.get_end_iter()

            pt = buf.get_text(start_iter, end_iter, include_hidden_chars=False).encode()

            try:
                ct = encryptor.encrypt(pt)

                self._output_text.get_buffer().set_text(b64encode(ct).decode("ascii"))
            except MessageTooLongError as e:
                # TODO: Handle error.
                pass

    def _decrypt(self, _button: Gtk.Button) -> None:
        """Decrypt the input using the key."""
        d = self.get_private_exponent()
        n = self.get_modulo()

        if d == b"" or n == b"":
            # TODO: Show error message.
            pass
        else:
            encryptor = RSAEncryptor(private_key=(d, n))

            buf = self._input_text.get_buffer()
            start_iter = buf.get_start_iter()
            end_iter = buf.get_end_iter()

            pt = buf.get_text(start_iter, end_iter, include_hidden_chars=False).encode()

            ct = encryptor.decrypt(b64decode(pt))

            self._output_text.get_buffer().set_text(ct.decode("utf-8"))


class KeyGen(multiprocessing.Process):
    """Key generation process."""

    def __init__(self, page: RsaPage, key_size: int, key_public_exponent: int) -> None:
        """Initialize the process."""
        super().__init__(daemon=True)
        self.page = page
        self.key_size = key_size
        self.public_exponent = key_public_exponent

        self.parent_conn, self.child_conn = multiprocessing.Pipe()

    def run(self) -> None:
        """CPU intensive task."""
        key = RSAEncryptor.keygen(self.key_size, self.public_exponent)
        self.child_conn.send(key)
        self.child_conn.close()

    def check_for_result(self) -> bool:
        """Check for results and finalize process."""
        if self.parent_conn.poll():
            self.page.set_key(self.parent_conn.recv())

            self.page.set_keygen_loading(False)

            self.join()
            return False
        return True

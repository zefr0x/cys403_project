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


class RsaPage(Adw.Bin):
    """Page as interface to the RSA text encryption."""

    def __init__(self, window: Adw.ApplicationWindow) -> None:
        """Initialize the page."""
        super().__init__()
        self._window = window

        split_view = Adw.OverlaySplitView()
        self.set_child(split_view)

        # Sidebar
        self.sidebar_box = Gtk.Box(
            orientation=Gtk.Orientation.VERTICAL,
            spacing=13,
            margin_start=7,
            margin_end=7,
            margin_top=7,
            margin_bottom=7,
        )
        split_view.set_sidebar(self.sidebar_box)

        # TODO: Show dialog to configure generated key.
        key_gen_button = Gtk.Button(label=_("Generate New Key"))
        self.sidebar_box.append(key_gen_button)
        key_gen_button.connect("clicked", self._generate_new_key)

        self._modulo = Gtk.TextView(wrap_mode=Gtk.WrapMode.CHAR, vexpand=True)
        self.sidebar_box.append(
            Gtk.Frame(
                child=self._modulo,
                label_widget=Gtk.Label(use_markup=True, label=_("<b>Modulo</b>")),
            )
        )

        self._public_exponent = Gtk.TextView(wrap_mode=Gtk.WrapMode.CHAR, vexpand=True)
        self.sidebar_box.append(
            Gtk.Frame(
                child=self._public_exponent,
                label_widget=Gtk.Label(
                    use_markup=True, label=_("<b>Public Exponent</b>")
                ),
            )
        )

        self._private_exponent = Gtk.TextView(wrap_mode=Gtk.WrapMode.CHAR, vexpand=True)
        self.sidebar_box.append(
            Gtk.Frame(
                child=self._private_exponent,
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
                child=self._input_text,
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
                child=self._output_text,
                label_widget=Gtk.Label(use_markup=True, label=_("<b>Output</b>")),
            )
        )

        split_view.set_content(content_box)

    def _generate_new_key(self, _button: Gtk.Button) -> None:
        """Create new key and show it in the ui."""
        self.sidebar_box.set_sensitive(False)

        class KeyGen(multiprocessing.Process):
            def __init__(self, page: RsaPage) -> None:
                """Initialize the process."""
                super().__init__()
                self.page = page

                self.parent_conn, self.child_conn = multiprocessing.Pipe()

            def run(self) -> None:
                """CPU intensive task."""
                key = RSAEncryptor.keygen()
                self.child_conn.send(key)
                self.child_conn.close()

            def check_for_result(self) -> bool:
                if self.parent_conn.poll():
                    self.page.set_key(self.parent_conn.recv())

                    self.page.sidebar_box.set_sensitive(True)

                    process.join()
                    return False
                return True

        process = KeyGen(self)
        process.start()

        GLib.timeout_add(100, process.check_for_result)

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

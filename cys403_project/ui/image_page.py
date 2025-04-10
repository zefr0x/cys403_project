"""Image encryption page."""

import multiprocessing
from base64 import b64decode, b64encode
from enum import Enum
from gettext import gettext as _
from pathlib import Path
from typing import TYPE_CHECKING

import gi
from PIL import Image

from cys403_project.crypto.imgenc import ImageEncryptor

if TYPE_CHECKING:
    from cys403_project.ui.main_window import Cys403ProjectMainWindow

gi.require_version("Adw", "1")
gi.require_version("Gtk", "4.0")
from gi.repository import (  # noqa: E402
    Adw,
    GdkPixbuf,
    Gio,
    GLib,
    Gtk,
)


class BinMode(Enum):
    """Current mode of output or input bin."""

    CIPHER_IMAGE = 0
    PLAIN_IMAGE = 1


class CipherImage:
    """Represent an encrypted image with its sizes."""

    def __init__(self, width: int, height: int, data: bytes) -> None:
        """Initialize a cipher image."""
        self.width = width
        self.height = height
        self.data = data

    def write_to_file(self, path: Path) -> None:
        """Write cipher image to a file."""
        with Path.open(path, "wb") as f:
            f.write((str(self.width) + "\n" + str(self.height) + "\n").encode("ascii"))
            f.write(self.data)

    def get_size(self) -> tuple[int, int]:
        """Get the image size in Pillow format."""
        return (self.width, self.height)

    @staticmethod
    def read_from_file(path: Path) -> "CipherImage":
        """Read cipher image from a file."""
        with Path.open(path, "rb") as f:
            width = int(f.readline().decode("ascii").strip())
            height = int(f.readline().decode("ascii").strip())
            data = f.read()

        return CipherImage(width, height, data)


class KeyGenOptionsDialog(Adw.Dialog):
    """Dialog for selecting key generation options."""

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
            title=_("Symmetric Key Options"),
            halign=Gtk.Align.FILL,
            margin_start=24,
            margin_end=24,
            margin_bottom=24,
            margin_top=12,
        )
        layout.set_content(options_group)

        self._key_size = Adw.SpinRow.new_with_range(min=1, max=255, step=1)
        self._key_size.set_title(_("Key Size"))
        self._key_size.set_subtitle(_("Number of Bytes"))
        self._key_size.set_value(16)
        options_group.add(self._key_size)

    def get_key_size(self) -> int:
        """Get the key size from ui."""
        return int(self._key_size.get_value())


class ImagePage(Adw.Bin):
    """Page as interface to the image encryption."""

    def __init__(self, window: "Cys403ProjectMainWindow") -> None:
        """Initialize the page."""
        super().__init__()
        self._window = window

        self.input_buffer: bytes
        self._input_buffer_shape: tuple[int, int]
        self.output_buffer: bytes
        self.output_buffer_shape: tuple[int, int]

        self.split_view = Adw.OverlaySplitView()
        self.set_child(self.split_view)

        # Sidebar
        self._sidebar_box = Gtk.Box(
            orientation=Gtk.Orientation.VERTICAL,
            spacing=13,
            margin_start=7,
            margin_end=7,
            margin_top=7,
            margin_bottom=7,
        )
        self._sidebar_box.set_size_request(250, 0)

        self._key_gen_button = Gtk.Button(label=_("Generate New Key"))
        self._sidebar_box.append(self._key_gen_button)
        self._key_gen_button.connect("clicked", self._generate_new_key)

        self._private_key = Gtk.TextView(wrap_mode=Gtk.WrapMode.CHAR, vexpand=True)
        self._sidebar_box.append(
            Gtk.Frame(
                child=Gtk.ScrolledWindow(child=self._private_key),
                label_widget=Gtk.Label(use_markup=True, label=_("<b>Private Key</b>")),
            )
        )

        self.split_view.set_sidebar(self._sidebar_box)

        # Content
        content_box = Gtk.Box(
            orientation=Gtk.Orientation.VERTICAL,
            spacing=13,
            margin_start=7,
            margin_end=7,
            margin_top=7,
            margin_bottom=7,
        )

        input_file_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=13)

        self._input_bin = Adw.Bin(vexpand=True)
        input_file_box.append(self._input_bin)

        self._open_input_button = Gtk.Button(label=_("Open Image File"))
        input_file_box.append(self._open_input_button)
        self._open_input_button.connect("clicked", self._select_input)

        content_box.append(
            Gtk.Frame(
                child=input_file_box,
                label_widget=Gtk.Label(use_markup=True, label=_("<b>Input Image</b>")),
            )
        )

        buttons_box = Gtk.Box(
            orientation=Gtk.Orientation.HORIZONTAL,
            spacing=13,
        )
        content_box.append(buttons_box)

        self._encrypt_button = Gtk.Button(label=_("Encrypt Image"), sensitive=False)
        self._encrypt_button.connect("clicked", self._encrypt)
        buttons_box.append(self._encrypt_button)

        self._decrypt_button = Gtk.Button(label=_("Decrypt Image"), sensitive=False)
        self._decrypt_button.connect("clicked", self._decrypt)
        buttons_box.append(self._decrypt_button)

        output_file_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=13)

        self.output_bin = Adw.Bin(vexpand=True)
        output_file_box.append(self.output_bin)

        self._save_output_button = Gtk.Button(
            label=_("Save Image File"), sensitive=False
        )
        output_file_box.append(self._save_output_button)
        self._save_output_button.connect("clicked", self._select_output)

        content_box.append(
            Gtk.Frame(
                child=output_file_box,
                label_widget=Gtk.Label(use_markup=True, label=_("<b>Output Image</b>")),
            )
        )

        self.split_view.set_content(content_box)

    def _generate_new_key(self, _button: Gtk.Button) -> None:
        """Create new key and show it in the ui."""
        options_dialog = KeyGenOptionsDialog()

        def on_generate_button_clicked(_button: Gtk.Button) -> None:
            """Key generation handler."""
            options_dialog.close()

            self._sidebar_box.set_sensitive(False)

            key = ImageEncryptor.keygen(options_dialog.get_key_size())

            self._private_key.get_buffer().set_text(b64encode(key).decode("ascii"))

            self._sidebar_box.set_sensitive(True)

        options_dialog.generate_button.connect("clicked", on_generate_button_clicked)

        options_dialog.present(self._window)

    def get_private_key(self) -> bytes:
        """Get the private key from the ui."""
        buf = self._private_key.get_buffer()
        start_iter = buf.get_start_iter()
        end_iter = buf.get_end_iter()

        return b64decode(buf.get_text(start_iter, end_iter, include_hidden_chars=False))

    def _select_input(self, _button: Gtk.Button) -> None:
        """Get input path to open image."""
        dialog = Gtk.FileChooserDialog(
            title=_("Select Input Image"),
            action=Gtk.FileChooserAction.OPEN,
            transient_for=self._window,
        )

        dialog.add_button(_("_Cancel"), Gtk.ResponseType.CANCEL)
        dialog.add_button(_("_Open"), Gtk.ResponseType.APPLY)

        filter_image = Gtk.FileFilter()
        filter_image.set_name("Plain Image Files")
        filter_image.add_mime_type("image/bmp")
        filter_image.add_mime_type("image/png")
        filter_image.add_mime_type("image/webp")
        dialog.add_filter(filter_image)

        filter_image = Gtk.FileFilter()
        filter_image.set_name("Cipher Image Files")
        # TODO: Create a custom mime type for cipher images.
        filter_image.add_pattern("*.cipher_image")
        dialog.add_filter(filter_image)

        dialog.connect("response", self._on_file_open_response)

        dialog.show()

    def _on_file_open_response(
        self, dialog: Gtk.FileChooserDialog, response_id: Gtk.ResponseType
    ) -> None:
        """Open file dialog response handler."""
        if response_id == Gtk.ResponseType.APPLY:
            file = dialog.get_file()

            if file:
                self._open_image(file)

        dialog.close()

    def _select_output(self, _button: Gtk.Button) -> None:
        """Get output path to save image."""
        dialog = Gtk.FileChooserDialog(
            title=_("Select Input Image"),
            action=Gtk.FileChooserAction.SAVE,
            transient_for=self._window,
        )

        dialog.add_button(_("_Cancel"), Gtk.ResponseType.CANCEL)
        dialog.add_button(_("_Save"), Gtk.ResponseType.APPLY)

        if hasattr(self, "_output_mode"):
            if self._output_mode == BinMode.CIPHER_IMAGE:
                dialog.set_current_name("output.cipher_image")
            elif self._output_mode == BinMode.PLAIN_IMAGE:
                dialog.set_current_name("output.png")

            dialog.connect("response", self._on_file_save_response)

            dialog.show()
        else:
            self._window.show_error(
                _("Output has not been determined, there is noting to be saved.")
            )

    def _on_file_save_response(
        self, dialog: Gtk.FileChooserDialog, response_id: Gtk.ResponseType
    ) -> None:
        """Save file dialog response handler."""
        if response_id == Gtk.ResponseType.APPLY:
            file = dialog.get_file()

            if file:
                self._save_image(file)

        dialog.close()

    def _open_image(self, file: Gio.File) -> None:
        """Open an image file from path."""
        path = file.get_path()

        if path:
            if path.endswith(".cipher_image"):
                cm = CipherImage.read_from_file(Path(path))

                self._input_mode = BinMode.CIPHER_IMAGE
                self.input_buffer = cm.data
                self._input_buffer_shape = cm.get_size()

                display_buffer = self.input_buffer[
                    len(self.get_private_key()) : cm.width * cm.height * 3
                    + len(self.get_private_key())
                ]

                if len(display_buffer) == cm.width * cm.height * 3:
                    pixbuf = bytes_to_pixbuf(
                        display_buffer,
                        cm.get_size(),
                    )
                    image_widget = Gtk.Image.new_from_pixbuf(pixbuf)
                    self._input_bin.set_child(image_widget)

                    self._encrypt_button.set_sensitive(False)
                    self._decrypt_button.set_sensitive(True)
                else:
                    # When the image was encrypted using smaller key.
                    self._window.show_error(
                        _("Failed to open and display image, key size doesn't match.")
                    )

                    # TODO: Show corrupted image icon.
                    self._input_bin.set_child(
                        Adw.StatusPage(title=_("Corrupted Input"))
                    )
            else:
                pm = Image.open(path).convert("RGB")  # Force RGB format

                self._input_mode = BinMode.PLAIN_IMAGE
                self.input_buffer = pm.tobytes()
                self._input_buffer_shape = pm.size

                pixbuf = bytes_to_pixbuf(self.input_buffer, pm.size)
                image_widget = Gtk.Image.new_from_pixbuf(pixbuf)
                self._input_bin.set_child(image_widget)

                self._encrypt_button.set_sensitive(True)
                self._decrypt_button.set_sensitive(False)

    def _save_image(self, file: Gio.File) -> None:
        """Open an image file from path."""
        path = file.get_path()

        if path:
            if hasattr(self, "output_buffer"):
                if self._output_mode == BinMode.CIPHER_IMAGE:
                    cm = CipherImage(*self.output_buffer_shape, self.output_buffer)

                    if path:
                        cm.write_to_file(Path(path))
                elif self._output_mode == BinMode.PLAIN_IMAGE:
                    pm = Image.frombytes(
                        mode="RGB",
                        size=self.output_buffer_shape,
                        data=self.output_buffer,
                    )
                    pm.save(path)
            else:
                self._window.show_error(
                    _("Output bufer is empty, there is noting to be save.")
                )

    def _encrypt(self, _button: Gtk.Button) -> None:
        """Encrypt the input image using the key."""
        if self.get_private_key():
            if hasattr(self, "input_buffer"):
                self._output_mode = BinMode.CIPHER_IMAGE
                self.output_buffer_shape = self._input_buffer_shape
                self.output_bin.set_child(Adw.Spinner())  # type: ignore[attr-defined]
                self.set_buttons_sensitivity(False)
                self._save_output_button.set_sensitive(False)

                process = Encrypt(self)
                process.start()
                GLib.timeout_add(100, process.check_for_result)
            else:
                self._window.show_error(
                    _("Input buffer is empty, there is noting to be encrypted.")
                )
        else:
            self._window.show_error(_("Private key is empty, can't encrypt."))

    def _decrypt(self, _button: Gtk.Button) -> None:
        """Decrypt the input image using the key."""
        if self.get_private_key():
            if hasattr(self, "input_buffer"):
                self._output_mode = BinMode.PLAIN_IMAGE
                self.output_buffer_shape = self._input_buffer_shape
                self.output_bin.set_child(Adw.Spinner(vexpand=True))  # type: ignore[attr-defined]
                self.set_buttons_sensitivity(False)
                self._save_output_button.set_sensitive(False)

                process = Decrypt(self)
                process.start()
                GLib.timeout_add(100, process.check_for_result)

            else:
                self._window.show_error(
                    _("Input buffer is empty, there is noting to be decrypted.")
                )
        else:
            self._window.show_error(_("Private key is empty, can't decrypt."))

    def set_buttons_sensitivity(self, value: bool) -> None:  # noqa: FBT001
        """Set buttons sinsitivity, and show a spinner in the output bin."""
        self._key_gen_button.set_sensitive(value)
        self._open_input_button.set_sensitive(value)

        if self._input_mode == BinMode.PLAIN_IMAGE:
            self._encrypt_button.set_sensitive(value)
        elif self._input_mode == BinMode.CIPHER_IMAGE:
            self._decrypt_button.set_sensitive(value)

    @property
    def window(self) -> "Cys403ProjectMainWindow":
        """Get the parent window."""
        return self._window

    @property
    def save_output_button(self) -> Gtk.Button:
        """Get the save output button."""
        return self._save_output_button


class Encrypt(multiprocessing.Process):
    """Encrypt process."""

    def __init__(self, page: ImagePage) -> None:
        """Initialize the process."""
        super().__init__(daemon=True)
        self.page = page

        self.parent_conn, self.child_conn = multiprocessing.Pipe()

    def run(self) -> None:
        """CPU intensive task."""
        encryptor = ImageEncryptor(key=self.page.get_private_key())

        self.child_conn.send(encryptor.encrypt(self.page.input_buffer))

    def check_for_result(self) -> bool:
        """Check for results and finalize process."""
        if self.parent_conn.poll():
            self.page.output_buffer = self.parent_conn.recv()

            pixbuf = bytes_to_pixbuf(
                self.page.output_buffer[
                    len(self.page.get_private_key()) : len(self.page.input_buffer)
                    + len(self.page.get_private_key())
                ],
                self.page.output_buffer_shape,
            )
            image_widget = Gtk.Image.new_from_pixbuf(pixbuf)
            self.page.output_bin.set_child(image_widget)
            self.page.set_buttons_sensitivity(True)
            self.page.save_output_button.set_sensitive(True)

            self.join()
            return False
        return True


class Decrypt(multiprocessing.Process):
    """Decrypt process."""

    def __init__(self, page: ImagePage) -> None:
        """Initialize the process."""
        super().__init__(daemon=True)
        self.page = page

        self.parent_conn, self.child_conn = multiprocessing.Pipe()

    def run(self) -> None:
        """CPU intensive task."""
        encryptor = ImageEncryptor(key=self.page.get_private_key())

        self.child_conn.send(encryptor.decrypt(self.page.input_buffer))

    def check_for_result(self) -> bool:
        """Check for results and finalize process."""
        if self.parent_conn.poll():
            self.page.output_buffer = self.parent_conn.recv()

            if (
                len(self.page.output_buffer)
                == self.page.output_buffer_shape[0]
                * self.page.output_buffer_shape[1]
                * 3
            ):
                pixbuf = bytes_to_pixbuf(
                    self.page.output_buffer,
                    self.page.output_buffer_shape,
                )
                image_widget = Gtk.Image.new_from_pixbuf(pixbuf)
                self.page.output_bin.set_child(image_widget)

                self.page.save_output_button.set_sensitive(True)
            else:
                # When the image was encrypted using smaller key.
                self.page.window.show_error(
                    _("Failed to decrypt and display image, key size doesn't match.")
                )

            # TODO: Show corrupted image icon.
            self.page.output_bin.set_child(Adw.StatusPage(title=_("Corrupted Output")))
            self.page.set_buttons_sensitivity(True)

            self.join()
            return False
        return True


def bytes_to_pixbuf(data: bytes, size: tuple[int, int]) -> GdkPixbuf.Pixbuf:
    """Convert a raw image to a GdkPixbuf."""
    width, height = size

    return GdkPixbuf.Pixbuf.new_from_bytes(
        data=GLib.Bytes.new(data),
        colorspace=GdkPixbuf.Colorspace.RGB,
        has_alpha=False,
        bits_per_sample=8,
        width=width,
        height=height,
        rowstride=width * 3,
    )

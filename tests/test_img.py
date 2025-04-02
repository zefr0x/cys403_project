"""Tests for imgenc.py."""

import pytest

from cys403_project.crypto.imgenc import ImageEncryptor, SymmetricKeyError


def test_nokey() -> None:
    """Test encryption without a key."""
    img = ImageEncryptor()
    with pytest.raises(SymmetricKeyError, match="Key must be set before encryption."):
        img.encrypt(b"Test image data")


def test_encrypt_decrypt_perfect_blocks() -> None:
    """Encrypts and decrypts an image that is perfectly divisible by 16 bytes."""
    img = ImageEncryptor(ImageEncryptor.keygen())
    original_image = b"A" * 64
    encrypted_image = img.encrypt(original_image)
    decrypted_image = img.decrypt(encrypted_image)
    assert decrypted_image == original_image


def test_encrypt_decrypt_with_padding() -> None:
    """Encrypts and decrypts an image that is not perfectly divisible by 16 bytes."""
    img = ImageEncryptor(ImageEncryptor.keygen())
    original_image = b"A" * 69
    encrypted_image = img.encrypt(original_image)
    decrypted_image = img.decrypt(encrypted_image)
    assert decrypted_image == original_image

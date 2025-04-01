"""Tests for rsa.py."""

import pytest

from cys403_project.crypto.rsa import (
    MessageTooLongError,
    PadError,
    PrivateKeyError,
    PublicKeyError,
    RSAEncryptor,
)


def test_keygen() -> None:
    """Test RSA key generation."""
    public_key, private_key = RSAEncryptor.keygen()
    assert isinstance(public_key, tuple)
    assert isinstance(private_key, tuple)
    assert len(public_key) == 2
    assert len(private_key) == 2
    assert isinstance(public_key[0], bytes)
    assert isinstance(public_key[1], bytes)
    assert isinstance(private_key[0], bytes)
    assert isinstance(private_key[1], bytes)


def test_encrypt_decrypt() -> None:
    """Test RSA encryption and decryption."""
    public_key, private_key = RSAEncryptor.keygen()
    rsa = RSAEncryptor(public_key=public_key, private_key=private_key)

    message = b"Test message"
    encrypted = rsa.encrypt(message)
    assert isinstance(encrypted, bytes)

    decrypted = rsa.decrypt(encrypted)
    assert decrypted == message


def test_encrypt_without_public_key() -> None:
    """Test encryption without a public key."""
    rsa = RSAEncryptor()
    with pytest.raises(PublicKeyError, match="Public key is not set."):
        rsa.encrypt(b"Test message")


def test_decrypt_without_private_key() -> None:
    """Test decryption without a private key."""
    rsa = RSAEncryptor()
    with pytest.raises(PrivateKeyError, match="Private key is not set."):
        rsa.decrypt(b"Encrypted message")


def test_message_too_long() -> None:
    """Test encryption with a message longer than the modulus."""
    public_key, private_key = RSAEncryptor.keygen(size=16)  # Small key size for testing
    rsa = RSAEncryptor(public_key=public_key)

    message = b"A" * 1000  # Message longer than modulus
    with pytest.raises(MessageTooLongError, match="Message longer than modulus."):
        rsa.encrypt(message)


def test_invalid_padding() -> None:
    """Test decryption with invalid padding."""
    public_key, private_key = RSAEncryptor.keygen()
    rsa = RSAEncryptor(private_key=private_key)

    # Create an invalid encrypted message
    invalid_encrypted_message = b"\x00" * 25
    with pytest.raises(PadError, match="Invalid padding in decrypted message."):
        rsa.decrypt(invalid_encrypted_message)

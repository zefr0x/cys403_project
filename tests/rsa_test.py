"""Tests for rsa.py."""

import pytest
from Crypto.PublicKey import RSA

from cys403_project.crypto.rsa import EncryptedData, RSAEncryptor


def test_key_generation() -> None:
    """Test RSA key generation."""
    encryptor = RSAEncryptor()
    encryptor.keygen()
    assert encryptor.public_key is not None
    assert encryptor.private_key is not None

    # Validate the generated keys
    public_key = RSA.import_key(encryptor.public_key)
    private_key = RSA.import_key(encryptor.private_key)
    assert public_key.has_private() is False
    assert private_key.has_private() is True


def test_encryption_and_decryption():
    """Test encryption and decryption process."""
    encryptor = RSAEncryptor()
    encryptor.keygen()

    data = b"Test data for encryption"
    encrypted_data = encryptor.encrypt(data)

    assert isinstance(encrypted_data, EncryptedData)
    assert encrypted_data.encrypted_key is not None
    assert encrypted_data.nonce is not None
    assert encrypted_data.tag is not None
    assert encrypted_data.ciphertext is not None

    decrypted_data = encryptor.decrypt(encrypted_data)
    assert decrypted_data == data


def test_encryption_without_public_key():
    """Test encryption without setting a public key."""
    encryptor = RSAEncryptor()
    with pytest.raises(ValueError, match="Public key is not set."):
        encryptor.encrypt(b"Test data")


def test_decryption_without_private_key():
    """Test decryption without setting a private key."""
    encryptor = RSAEncryptor()
    encryptor.keygen()
    data = b"Test data for encryption"
    encrypted_data = encryptor.encrypt(data)

    # Create a new encryptor without a private key
    encryptor_no_private = RSAEncryptor(public_key=encryptor.public_key)
    with pytest.raises(ValueError, match="Private key is not set."):
        encryptor_no_private.decrypt(encrypted_data)


def test_invalid_decryption():
    """Test decryption with invalid data."""
    encryptor = RSAEncryptor()
    encryptor.keygen()

    data = b"Test data for encryption"
    encrypted_data = encryptor.encrypt(data)

    # Modify the encrypted data to simulate corruption
    encrypted_data.ciphertext = b"corrupted data"

    with pytest.raises(ValueError):
        encryptor.decrypt(encrypted_data)

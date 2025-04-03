"""Implementation of the RSAEncryptor class."""

import asyncio
from hashlib import sha256
from typing import Optional

from Crypto.Util.number import getPrime


class PrivateKeyError(Exception):
    """Exception for missing private key errors."""


class PublicKeyError(Exception):
    """Exception for missing public key errors."""


class PadError(Exception):
    """Exception for incorrect / missing padding errors."""


class MessageTooLongError(Exception):
    """Exception for message longer than modulus errors."""


class RSAEncryptor:
    """
    A class to handle RSA encryption and decryption.

    This class provides methods to generate RSA keys, encrypt data using the public key,
    and decrypt data using the private key.
    """

    def __init__(
        self,
        public_key: Optional[tuple[bytes, bytes]] = None,
        private_key: Optional[tuple[bytes, bytes]] = None,
    ) -> None:
        """
        Initialize the RSAEncryptor with optional public and private keys.

        Args:
            public_key (tuple): public key for encryption (e, n) (default is None).
            private_key (tuple): private key for decryption (d, n) (default is None).

        """
        self.public_key = public_key
        self.private_key = private_key

    @staticmethod
    async def keygen(
        size: int = 2048, e: int = 65537
    ) -> tuple[tuple[bytes, bytes], tuple[bytes, bytes]]:
        """
        Generate a new RSA key pair.

        This method generates a new public and private key pair for RSA encryption.

        Args:
            size: The size of the key in bits (default is 2048).
            e: The public exponent (default is 65537).

        Returns:
            Tuple: A tuple containing the public and private keys.

        """
        # generate two large prime numbers
        p = await asyncio.to_thread(getPrime, size)
        q = await asyncio.to_thread(getPrime, size)

        n = p * q
        phi = (p - 1) * (q - 1)
        d = pow(e, -1, phi)
        public_key = (
            e.to_bytes((e.bit_length() + 7) // 8, "big"),
            n.to_bytes((n.bit_length() + 7) // 8, "big"),
        )
        private_key = (
            d.to_bytes((d.bit_length() + 7) // 8, "big"),
            n.to_bytes((n.bit_length() + 7) // 8, "big"),
        )
        return public_key, private_key

    def encrypt(self, data: bytes) -> bytes:
        """
        Encrypts the given data with some padding.

        Args:
            data (bytes): The data to encrypt.

        Raises:
            ValueError: If the public key is not set.
            ValueError: If the message is longer than the modulus.

        Returns:
            bytes: encrypted data with padding.

        """
        if not self.public_key:
            msg = "Public key is not set."
            raise PublicKeyError(msg)

        m_int = int.from_bytes(data, byteorder="big")
        e, n = (
            int.from_bytes(self.public_key[0], byteorder="big"),
            int.from_bytes(self.public_key[1], byteorder="big"),
        )
        if m_int >= n:
            # change this so he stops complaining later
            msg = "Message longer than modulus."
            raise MessageTooLongError(msg)

        # padding
        h = sha256()
        h.update(b"")
        hashl = h.digest()
        padding = b"\x00" * (n.bit_length() // 8 - len(hashl) - 2)
        m = padding + b"\x01" + hashl + data

        # encryption
        m_int = int.from_bytes(m, byteorder="big")
        c_int = pow(m_int, e, n)
        return c_int.to_bytes((n.bit_length() + 7) // 8, byteorder="big")

    def decrypt(self, data: bytes) -> bytes:
        """
        Decrypts the given data using RSA algorithm and removes padding.

        Args:
            data (bytes): The encrypted data to decrypt.

        Raises:
            ValueError: If the private key is not set.

        Returns:
            bytes: The decrypted data without padding.

        """
        if not self.private_key:
            msg = "Private key is not set."
            raise PrivateKeyError(msg)

        d = int.from_bytes(self.private_key[0], byteorder="big")
        n = int.from_bytes(self.private_key[1], byteorder="big")
        c_int = int.from_bytes(data, byteorder="big")

        # Decrypt the ciphertext
        m_int = pow(c_int, d, n)
        m = m_int.to_bytes((n.bit_length() + 7) // 8, byteorder="big")

        # Remove padding
        padding_index = m.find(b"\x01")
        if padding_index == -1:
            msg = "Invalid padding in decrypted message."
            raise PadError(msg)

        return m[padding_index + 1 + sha256().digest_size :]

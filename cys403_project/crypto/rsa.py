"""Implementation of the RSAEncryptor class."""

from dataclasses import dataclass
from typing import Optional

from Crypto.Cipher import AES, PKCS1_OAEP
from Crypto.PublicKey import RSA
from Crypto.Random import get_random_bytes


@dataclass
class EncryptedData:
    """
    A class to represent encrypted data.

    Attributes:
        encrypted_key (bytes): The encrypted AES key.
        nonce (bytes): The nonce used for AES encryption.
        tag (bytes): The authentication tag for the AES encryption.
        ciphertext (bytes): The actual encrypted data.

    """

    encrypted_key: bytes
    nonce: bytes
    tag: bytes
    ciphertext: bytes


class RSAEncryptor:
    """
    A class to handle RSA encryption and decryption.

    This class provides methods to generate RSA keys, encrypt data using the public key,
    and decrypt data using the private key.
    """

    def __init__(
        self, public_key: Optional[bytes] = None, private_key: Optional[bytes] = None
    ) -> None:
        """
        Initialize the RSAEncryptor with optional public and private keys.

        Args:
            public_key: The public key for encryption (default is None).
            private_key: The private key for decryption (default is None).

        """
        self.public_key = public_key
        self.private_key = private_key

    def keygen(self, size: int = 2048) -> None:
        """
        Generate a new RSA key pair.

        This method generates a new public and private key pair for RSA encryption.

        Args:
            size: The size of the key in bits (default is 2048).

        Returns:
            None

        """
        key = RSA.generate(size)
        self.public_key = key.publickey().export_key()
        self.private_key = key.export_key()

    def encrypt(self, data: bytes) -> EncryptedData:
        """
        Encrypts the given data.

        Due to RSA being inefficient for large data,
        we use AES for the data and RSA with OAEP for the symmetric key.

        Args:
            data (bytes): The data to encrypt.

        Raises:
            ValueError: If the public key is not set.

        Returns:
            EncryptedData: An object containing the encrypted AES key,
            nonce, tag, and ciphertext.

        """
        if not self.public_key:
            raise ValueError("Public key is not set.")

        # Generate a random AES key
        aes_key = get_random_bytes(32)  # 256-bit AES key
        # Encrypt the AES key using RSA and OAEP
        oaep_rsa = PKCS1_OAEP.new(RSA.import_key(self.public_key))
        encrypted_aes_key = oaep_rsa.encrypt(aes_key)

        # Encrypt the data using AES in EAX mode
        cipher_aes = AES.new(aes_key, AES.MODE_EAX)
        ciphertext, tag = cipher_aes.encrypt_and_digest(data)

        return EncryptedData(
            encrypted_key=encrypted_aes_key,
            nonce=cipher_aes.nonce,
            tag=tag,
            ciphertext=ciphertext,
        )

    def decrypt(self, data: EncryptedData) -> bytes:
        """
        Decrypts the given data using RSA algorithm.

        Args:
            data (EncryptedData): The encrypted data object containing the encrypted
                AES key, nonce, tag, and ciphertext.

        Raises:
            ValueError: If the private key is not set.

        Returns:
            bytes: The decrypted data.

        """
        if not self.private_key:
            raise ValueError("Private key is not set.")

        # Decrypt the AES key using RSA and OAEP
        oaep_rsa = PKCS1_OAEP.new(RSA.import_key(self.private_key))
        aes_key = oaep_rsa.decrypt(data.encrypted_key)
        # Decrypt the data using AES
        cipher_aes = AES.new(aes_key, AES.MODE_EAX, nonce=data.nonce)

        return cipher_aes.decrypt_and_verify(data.ciphertext, data.tag)

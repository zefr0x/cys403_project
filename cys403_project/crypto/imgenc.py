"""Image Encryption class."""

from secrets import token_bytes
from typing import Optional


class SymmetricKeyError(Exception):
    """Exception for missing symmetric key errors."""


class ImageEncryptor:
    """Image encryption and decryption class using a block cipher (CBC) algorithm."""

    def __init__(self, key: Optional[bytes] = None) -> None:
        """
        Initialize the ImageEncryptor with a key.

        Args:
            key (bytes): The key for encryption and decryption.

        """
        # TODO: Make the key size dynamic to accept any key size from the input dialog.
        self.key = key

    @staticmethod
    def keygen(size: int = 16) -> bytes:
        """
        Generate a new (size) byte symmetric key.

        Args:
            size (int): The size of the key to generate. (default: 16 bytes)


        Returns:
            bytes: The generated symmetric key.

        """
        return token_bytes(size)

    # TODO: Implement another cipher block mode.
    def encrypt(self, image: bytes) -> bytes:
        """
        Encrypt the image using a block cipher (CBC) algorithm.

        The way this block cipher works is simple. We split the image into blocks of
        len(key). We then initialize a random initialization vector (IV)
        and XOR it with the block. We then apply our encryption algorithm to the XOR'd
        block. We store the result and then use the result as the IV for the next block.
        The last block is padded with PKCS7 padding.
        We prefix the final resulting encrypted image with the IV.



        Args:
            image (bytes): The image data to encrypt.

        Returns:
            bytes: The encrypted image data.

        """
        if not self.key:
            msg = "Key must be set before encryption."
            raise SymmetricKeyError(msg)
        # get blocksize
        blocksize = len(self.key)
        # initalize IV
        iv = token_bytes(blocksize)
        # split image into blocks of blocksize
        pad_length = blocksize - (len(image) % blocksize)
        image += bytes([pad_length] * pad_length)
        blocks = [image[i : i + blocksize] for i in range(0, len(image), blocksize)]

        # CBC encryption
        encrypted_blocks = []
        iv_original = iv
        for block in blocks:
            # xor the block with IV
            xor_block = bytes(a ^ b for a, b in zip(block, iv))
            # encryption algorithm: invert the bits and xor with the key
            encrypted_block = bytes(
                (~a & 0xFF) ^ b for a, b in zip(xor_block, self.key)
            )
            encrypted_blocks.append(encrypted_block)
            iv = encrypted_block

        return iv_original + b"".join(encrypted_blocks)

    def decrypt(self, encrypted_image: bytes) -> bytes:
        """
        Decrypt the encryption resulting from encrypt() method.

        Args:
            encrypted_image (bytes): The encrypted image data to decrypt.

        Returns:
            bytes: The decrypted image data.

        """
        if not self.key:
            msg = "Key must be set before decryption."
            raise SymmetricKeyError(msg)
        blocksize = len(self.key)
        iv = encrypted_image[:blocksize]

        # split image into blocks of 128 bits
        blocks = [
            encrypted_image[i : i + blocksize]
            for i in range(blocksize, len(encrypted_image), blocksize)
        ]
        decrypted_blocks = []

        # Currently assuming correct input where last block is padded
        for block in blocks:
            xor_result = bytes(a ^ b for a, b in zip(block, self.key))
            inverted = bytes(~a & 0xFF for a in xor_result)
            original_block = bytes(a ^ b for a, b in zip(inverted, iv))
            decrypted_blocks.append(original_block)
            iv = block

        # remove padding
        last_block = decrypted_blocks[-1]
        pad_length = last_block[-1]
        decrypted_blocks[-1] = last_block[:-pad_length]
        return b"".join(decrypted_blocks)

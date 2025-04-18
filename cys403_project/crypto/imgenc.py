"""Image Encryption class."""

from secrets import token_bytes

# Rijndael S-box and inverse S-box
SBOX = (
    0x63,
    0x7C,
    0x77,
    0x7B,
    0xF2,
    0x6B,
    0x6F,
    0xC5,
    0x30,
    0x01,
    0x67,
    0x2B,
    0xFE,
    0xD7,
    0xAB,
    0x76,
    0xCA,
    0x82,
    0xC9,
    0x7D,
    0xFA,
    0x59,
    0x47,
    0xF0,
    0xAD,
    0xD4,
    0xA2,
    0xAF,
    0x9C,
    0xA4,
    0x72,
    0xC0,
    0xB7,
    0xFD,
    0x93,
    0x26,
    0x36,
    0x3F,
    0xF7,
    0xCC,
    0x34,
    0xA5,
    0xE5,
    0xF1,
    0x71,
    0xD8,
    0x31,
    0x15,
    0x04,
    0xC7,
    0x23,
    0xC3,
    0x18,
    0x96,
    0x05,
    0x9A,
    0x07,
    0x12,
    0x80,
    0xE2,
    0xEB,
    0x27,
    0xB2,
    0x75,
    0x09,
    0x83,
    0x2C,
    0x1A,
    0x1B,
    0x6E,
    0x5A,
    0xA0,
    0x52,
    0x3B,
    0xD6,
    0xB3,
    0x29,
    0xE3,
    0x2F,
    0x84,
    0x53,
    0xD1,
    0x00,
    0xED,
    0x20,
    0xFC,
    0xB1,
    0x5B,
    0x6A,
    0xCB,
    0xBE,
    0x39,
    0x4A,
    0x4C,
    0x58,
    0xCF,
    0xD0,
    0xEF,
    0xAA,
    0xFB,
    0x43,
    0x4D,
    0x33,
    0x85,
    0x45,
    0xF9,
    0x02,
    0x7F,
    0x50,
    0x3C,
    0x9F,
    0xA8,
    0x51,
    0xA3,
    0x40,
    0x8F,
    0x92,
    0x9D,
    0x38,
    0xF5,
    0xBC,
    0xB6,
    0xDA,
    0x21,
    0x10,
    0xFF,
    0xF3,
    0xD2,
    0xCD,
    0x0C,
    0x13,
    0xEC,
    0x5F,
    0x97,
    0x44,
    0x17,
    0xC4,
    0xA7,
    0x7E,
    0x3D,
    0x64,
    0x5D,
    0x19,
    0x73,
    0x60,
    0x81,
    0x4F,
    0xDC,
    0x22,
    0x2A,
    0x90,
    0x88,
    0x46,
    0xEE,
    0xB8,
    0x14,
    0xDE,
    0x5E,
    0x0B,
    0xDB,
    0xE0,
    0x32,
    0x3A,
    0x0A,
    0x49,
    0x06,
    0x24,
    0x5C,
    0xC2,
    0xD3,
    0xAC,
    0x62,
    0x91,
    0x95,
    0xE4,
    0x79,
    0xE7,
    0xC8,
    0x37,
    0x6D,
    0x8D,
    0xD5,
    0x4E,
    0xA9,
    0x6C,
    0x56,
    0xF4,
    0xEA,
    0x65,
    0x7A,
    0xAE,
    0x08,
    0xBA,
    0x78,
    0x25,
    0x2E,
    0x1C,
    0xA6,
    0xB4,
    0xC6,
    0xE8,
    0xDD,
    0x74,
    0x1F,
    0x4B,
    0xBD,
    0x8B,
    0x8A,
    0x70,
    0x3E,
    0xB5,
    0x66,
    0x48,
    0x03,
    0xF6,
    0x0E,
    0x61,
    0x35,
    0x57,
    0xB9,
    0x86,
    0xC1,
    0x1D,
    0x9E,
    0xE1,
    0xF8,
    0x98,
    0x11,
    0x69,
    0xD9,
    0x8E,
    0x94,
    0x9B,
    0x1E,
    0x87,
    0xE9,
    0xCE,
    0x55,
    0x28,
    0xDF,
    0x8C,
    0xA1,
    0x89,
    0x0D,
    0xBF,
    0xE6,
    0x42,
    0x68,
    0x41,
    0x99,
    0x2D,
    0x0F,
    0xB0,
    0x54,
    0xBB,
    0x16,
)

INV_SBOX = (
    0x52,
    0x09,
    0x6A,
    0xD5,
    0x30,
    0x36,
    0xA5,
    0x38,
    0xBF,
    0x40,
    0xA3,
    0x9E,
    0x81,
    0xF3,
    0xD7,
    0xFB,
    0x7C,
    0xE3,
    0x39,
    0x82,
    0x9B,
    0x2F,
    0xFF,
    0x87,
    0x34,
    0x8E,
    0x43,
    0x44,
    0xC4,
    0xDE,
    0xE9,
    0xCB,
    0x54,
    0x7B,
    0x94,
    0x32,
    0xA6,
    0xC2,
    0x23,
    0x3D,
    0xEE,
    0x4C,
    0x95,
    0x0B,
    0x42,
    0xFA,
    0xC3,
    0x4E,
    0x08,
    0x2E,
    0xA1,
    0x66,
    0x28,
    0xD9,
    0x24,
    0xB2,
    0x76,
    0x5B,
    0xA2,
    0x49,
    0x6D,
    0x8B,
    0xD1,
    0x25,
    0x72,
    0xF8,
    0xF6,
    0x64,
    0x86,
    0x68,
    0x98,
    0x16,
    0xD4,
    0xA4,
    0x5C,
    0xCC,
    0x5D,
    0x65,
    0xB6,
    0x92,
    0x6C,
    0x70,
    0x48,
    0x50,
    0xFD,
    0xED,
    0xB9,
    0xDA,
    0x5E,
    0x15,
    0x46,
    0x57,
    0xA7,
    0x8D,
    0x9D,
    0x84,
    0x90,
    0xD8,
    0xAB,
    0x00,
    0x8C,
    0xBC,
    0xD3,
    0x0A,
    0xF7,
    0xE4,
    0x58,
    0x05,
    0xB8,
    0xB3,
    0x45,
    0x06,
    0xD0,
    0x2C,
    0x1E,
    0x8F,
    0xCA,
    0x3F,
    0x0F,
    0x02,
    0xC1,
    0xAF,
    0xBD,
    0x03,
    0x01,
    0x13,
    0x8A,
    0x6B,
    0x3A,
    0x91,
    0x11,
    0x41,
    0x4F,
    0x67,
    0xDC,
    0xEA,
    0x97,
    0xF2,
    0xCF,
    0xCE,
    0xF0,
    0xB4,
    0xE6,
    0x73,
    0x96,
    0xAC,
    0x74,
    0x22,
    0xE7,
    0xAD,
    0x35,
    0x85,
    0xE2,
    0xF9,
    0x37,
    0xE8,
    0x1C,
    0x75,
    0xDF,
    0x6E,
    0x47,
    0xF1,
    0x1A,
    0x71,
    0x1D,
    0x29,
    0xC5,
    0x89,
    0x6F,
    0xB7,
    0x62,
    0x0E,
    0xAA,
    0x18,
    0xBE,
    0x1B,
    0xFC,
    0x56,
    0x3E,
    0x4B,
    0xC6,
    0xD2,
    0x79,
    0x20,
    0x9A,
    0xDB,
    0xC0,
    0xFE,
    0x78,
    0xCD,
    0x5A,
    0xF4,
    0x1F,
    0xDD,
    0xA8,
    0x33,
    0x88,
    0x07,
    0xC7,
    0x31,
    0xB1,
    0x12,
    0x10,
    0x59,
    0x27,
    0x80,
    0xEC,
    0x5F,
    0x60,
    0x51,
    0x7F,
    0xA9,
    0x19,
    0xB5,
    0x4A,
    0x0D,
    0x2D,
    0xE5,
    0x7A,
    0x9F,
    0x93,
    0xC9,
    0x9C,
    0xEF,
    0xA0,
    0xE0,
    0x3B,
    0x4D,
    0xAE,
    0x2A,
    0xF5,
    0xB0,
    0xC8,
    0xEB,
    0xBB,
    0x3C,
    0x83,
    0x53,
    0x99,
    0x61,
    0x17,
    0x2B,
    0x04,
    0x7E,
    0xBA,
    0x77,
    0xD6,
    0x26,
    0xE1,
    0x69,
    0x14,
    0x63,
    0x55,
    0x21,
    0x0C,
    0x7D,
)

# 10 round constants might be enough
ROUND_CONST = (0x01, 0x02, 0x04, 0x08, 0x10, 0x20, 0x40, 0x80, 0x1B, 0x36)


class ImageEncryptor:
    """Image encryption and decryption class using the Advanced Encryption Standard."""

    def __init__(self, key: bytes) -> None:
        """
        Initialize the ImageEncryptor with a key.

        Args:
            key (bytes): The key for encryption and decryption.

        """
        self.blocksize = len(key)
        self._rounds = 10  # TODO: make this configurable
        self._key = key

    @property
    def key(self) -> bytes:
        """Get the key."""
        return self._key

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

    def _rotbytes(self, word: bytes) -> bytes:
        """
        Rotate the bytes 1 byte to the left.

        Args:
            word (bytes): The word to rotate.

        Returns:
            bytes: The rotated word.

        """
        return word[1:] + word[:1]

    def _subbytes(self, word: bytes) -> bytes:
        """
        Substitute each byte using the S-box.

        Args:
            word (bytes): The word to substitute.

        Returns:
            bytes: The substituted word.

        """
        return bytes(SBOX[b] for b in word)

    def _inv_subbytes(self, word: bytes) -> bytes:
        """
        Substitute each byte using the inverse S-box.

        Args:
            word (bytes): The word to substitute.

        Returns:
            bytes: The substituted word.

        """
        return bytes(INV_SBOX[b] for b in word)

    def _shift_rows(self, matrix: list[list[int]]) -> list[list[int]]:
        """
        Shift the rows of the matrix.

        The first row is not shifted, the second row is shifted 1 byte to the left,
        the third row is shifted 2 bytes to the left, and the fourth row is shifted
        3 bytes to the left.

        Args:
            matrix (list[list[int]]): The matrix to shift.

        Returns:
            list[list[int]]: The shifted matrix.

        """
        return [
            matrix[0],
            matrix[1][1:] + matrix[1][:1],
            matrix[2][2:] + matrix[2][:2],
            matrix[3][3:] + matrix[3][:3],
        ]

    def _inv_shift_rows(self, matrix: list[list[int]]) -> list[list[int]]:
        """
        Inverse shift the rows of the matrix.

        The first row is not shifted, the second row is shifted 1 byte to the right,
        the third row is shifted 2 bytes to the right, and the fourth row is shifted
        3 bytes to the right.

        Args:
            matrix (list[list[int]]): The matrix to shift.

        Returns:
            list[list[int]]: The shifted matrix.

        """
        return [
            matrix[0],
            matrix[1][-1:] + matrix[1][:-1],
            matrix[2][-2:] + matrix[2][:-2],
            matrix[3][-3:] + matrix[3][:3],
        ]

    # https://en.wikipedia.org/wiki/Rijndael_MixColumns
    def _gf_mul(self, a: int, b: int) -> int:
        """
        Multiply two bytes in GF(2^8).

        Args:
            a (int): The first byte.
            b (int): The second byte.

        Returns:
            int: The result of the multiplication.

        """
        result = 0
        for _ in range(8):
            if b & 1:
                result ^= a
            hi = a & 0x80
            a = (a << 1) & 0xFF
            if hi:
                a ^= 0x1B
            b >>= 1
        return result

    def _mix_columns(self, matrix: list[list[int]]) -> list[list[int]]:
        """
        Mix each column of the matrix.

        The operation can be found at: https://en.wikipedia.org/wiki/Rijndael_MixColumns

        Args:
            matrix (list[list[int]]): The 4x4 matrix to mix.

        Returns:
            list[list[int]]: The mixed 4x4 matrix.

        """
        result = [[0] * 4 for _ in range(4)]
        for c, (a0, a1, a2, a3) in enumerate(zip(*matrix)):
            r0 = self._gf_mul(a0, 2) ^ self._gf_mul(a1, 3) ^ a2 ^ a3
            r1 = a0 ^ self._gf_mul(a1, 2) ^ self._gf_mul(a2, 3) ^ a3
            r2 = a0 ^ a1 ^ self._gf_mul(a2, 2) ^ self._gf_mul(a3, 3)
            r3 = self._gf_mul(a0, 3) ^ a1 ^ a2 ^ self._gf_mul(a3, 2)
            result[0][c], result[1][c], result[2][c], result[3][c] = r0, r1, r2, r3

        return result

    def _inv_mix_columns(self, matrix: list[list[int]]) -> list[list[int]]:
        """
        Inverse mix each column of the state matrix.

        The operation can be found at: https://en.wikipedia.org/wiki/Rijndael_MixColumns

        Args:
            matrix (list[list[int]]): The 4x4 matrix to mix.

        Returns:
            list[list[int]]: The mixed 4x4 matrix.

        """
        result = [[0] * 4 for _ in range(4)]
        for c, (a0, a1, a2, a3) in enumerate(zip(*matrix)):
            r0 = (
                self._gf_mul(a0, 14)
                ^ self._gf_mul(a1, 11)
                ^ self._gf_mul(a2, 13)
                ^ self._gf_mul(a3, 9)
            )
            r1 = (
                self._gf_mul(a0, 9)
                ^ self._gf_mul(a1, 14)
                ^ self._gf_mul(a2, 11)
                ^ self._gf_mul(a3, 13)
            )
            r2 = (
                self._gf_mul(a0, 13)
                ^ self._gf_mul(a1, 9)
                ^ self._gf_mul(a2, 14)
                ^ self._gf_mul(a3, 11)
            )
            r3 = (
                self._gf_mul(a0, 11)
                ^ self._gf_mul(a1, 13)
                ^ self._gf_mul(a2, 9)
                ^ self._gf_mul(a3, 14)
            )
            result[0][c], result[1][c], result[2][c], result[3][c] = r0, r1, r2, r3
        return result

    def _add_round_key(self, matrix: list[list[int]], key: bytes) -> list[list[int]]:
        """
        Add the round key to the matrix.

        Args:
            matrix (list[list[int]]): The matrix to add the key to.
            key (bytes): The key to add.

        Returns:
            list[list[int]]: The matrix with the key added.

        """
        return [
            [a ^ b for a, b in zip(row, key[i * 4 : (i + 1) * 4])]
            for i, row in enumerate(matrix)
        ]

    def _bytes_to_matrix(self, data: bytes) -> list[list[int]]:
        """
        Convert bytes to a 4x4 matrix.

        Args:
            data (bytes): The data to convert.

        Returns:
            list[list[int]]: The converted matrix.

        """
        return [list(data[i : i + 4]) for i in range(0, len(data), 4)]

    def _matrix_to_bytes(self, matrix: list[list[int]]) -> bytes:
        """
        Convert a 4x4 matrix to bytes.

        Args:
            matrix (list[list[int]]): The matrix to convert.

        Returns:
            bytes: The converted bytes.

        """
        return bytes(item for row in matrix for item in row)  # faster than sum()

    # https://en.wikipedia.org/wiki/AES_key_schedule
    def _key_expansion(self) -> list[bytes]:
        """
        Expand the cipher key into round keys for AES-128.

        Returns:
            list[bytes]: A list of (Nr+1) round keys, each 16 bytes.

        """
        nk = self.blocksize // 4  # length of key in multiples of 4

        # split key into words
        key_words = [self._key[i * 4 : (i + 1) * 4] for i in range(nk)]

        # generate the words for the round keys
        for i in range(nk, 4 * (self._rounds + 1)):  # nk -> 4*(Nr+1)
            temp = key_words[i - 1]
            if i % nk == 0:
                # RotWord, SubWord, then XOR with Rcon
                rcon = (ROUND_CONST[i // nk - 1], 0, 0, 0)
                temp = bytes(
                    a ^ b for a, b in zip(self._subbytes(self._rotbytes(temp)), rcon)
                )
            # XOR with the word Nk positions earlier
            new_word = bytes(a ^ b for a, b in zip(key_words[i - nk], temp))
            key_words.append(new_word)

        return [
            b"".join(key_words[4 * r : 4 * (r + 1)]) for r in range(self._rounds + 1)
        ]

    def encrypt(self, image: bytes) -> bytes:
        """
        Encrypt the image using AES-128 in CBC mode with PKCS#7 padding.

        First generates a random Initialization Vector (iv) of blocksize bytes, then
        pads the data to complete the last block, creates a full block of pad if
        correctly sized. Round keys are generated from the main key,
        and data is split into blocks of blocksize.
        Each block is initially turned to a state matrix, then added to 1st round key.
        Then for each round key, the following operations are performed on the
        state matrix: SubBytes, ShiftRows, MixColumns, AddRoundKey.
        The final round doesn't include MixColumns.

        Args:
            image (bytes): The image to encrypt.

        Returns:
            bytes: The encrypted image, with IV prefixed to it.



        """
        iv = token_bytes(self.blocksize)

        # padding
        pad_len = self.blocksize - (len(image) % self.blocksize)
        image += bytes([pad_len]) * pad_len

        # split blocks
        blocks = [
            image[i : i + self.blocksize] for i in range(0, len(image), self.blocksize)
        ]

        # expand key
        round_keys = self._key_expansion()  # list of bytes, length = rounds+1
        encrypted_blocks = []
        prev = iv

        for block in blocks:
            # CBC: xor with previous ciphertext (or IV)
            state_bytes = bytes(a ^ b for a, b in zip(block, prev))
            # initial
            state = self._bytes_to_matrix(state_bytes)
            state = self._add_round_key(state, round_keys[0])

            # rounds 1..Nr-1
            for rk in round_keys[1:-1]:
                state = [list(self._subbytes(bytes(row))) for row in state]
                state = self._shift_rows(state)
                state = self._mix_columns(state)
                state = self._add_round_key(state, rk)

            # final round (no MixColumns)
            state = [list(self._subbytes(bytes(row))) for row in state]
            state = self._shift_rows(state)
            state = self._add_round_key(state, round_keys[-1])

            # to bytes and append
            encrypted_block = self._matrix_to_bytes(state)
            encrypted_blocks.append(encrypted_block)
            prev = encrypted_block

        return iv + b"".join(encrypted_blocks)

    def decrypt(self, encrypted_image: bytes) -> bytes:
        """
        Decrypt the ciphertext resulting of the encrypt method.

        The decryption process applies the encryption steps in reverse.

        Args:
            encrypted_image (bytes): The encrypted image to decrypt.

        Returns:
            bytes: The decrypted image.

        """
        # extract IV and ciphertext blocks
        iv = encrypted_image[: self.blocksize]
        blocks = [
            encrypted_image[i : i + self.blocksize]
            for i in range(self.blocksize, len(encrypted_image), self.blocksize)
        ]

        # expand key into round keys
        round_keys = self._key_expansion()
        plaintext_blocks = []
        prev = iv

        for block in blocks:
            state = self._bytes_to_matrix(block)
            state = self._add_round_key(state, round_keys[-1])
            state = self._inv_shift_rows(state)
            state = [list(self._inv_subbytes(bytes(row))) for row in state]

            for rk in reversed(round_keys[1:-1]):
                state = self._add_round_key(state, rk)
                state = self._inv_mix_columns(state)
                state = self._inv_shift_rows(state)
                state = [list(self._inv_subbytes(bytes(row))) for row in state]

            state = self._add_round_key(state, round_keys[0])

            # CBC
            decrypted = self._matrix_to_bytes(state)
            plain_block = bytes(a ^ b for a, b in zip(decrypted, prev))
            plaintext_blocks.append(plain_block)

            prev = block

        # remove padding
        last = plaintext_blocks[-1]
        pad_len = last[-1]
        plaintext_blocks[-1] = last[:-pad_len]

        return b"".join(plaintext_blocks)

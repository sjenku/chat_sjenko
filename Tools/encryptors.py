import base64
from abc import ABC, abstractmethod
from enum import Enum

from Crypto.Cipher import AES


class Encryptor(ABC):
    @abstractmethod
    def encrypt(self, content: bytes):
        pass

    @abstractmethod
    def decrypt(self, content: bytes):
        pass


class EncryptorAESKeyEnum(str, Enum):
    AES_KEY = "aes_key"
    ENC_KEY = "enc_key"
    HMAC_KEY = "hmac_key"


class EncryptorAES(Encryptor):

    def __init__(self):
        self._key = None
        self._enc_key = None
        self._hmac_key = None
        self._current_enc_key = None

    @property
    def key(self):
        raise AttributeError("You cannot access the key directly.")

    @key.setter
    def key(self, value):
        if not value:
            raise ValueError("Name cannot be empty")
        self._key = value

        # split the key and create one key for encryption and another for hmac
        enc_key, hmac_key = self._split_aes_key()
        self._enc_key = enc_key
        self._hmac_key = hmac_key

    # Encrypt with AES in CTR mode
    def encrypt(self, content: bytes):
        cipher = AES.new(self._current_enc_key, AES.MODE_CTR)
        ciphertext = cipher.encrypt(content)
        cipher.nonce = b'5'
        return base64.b64encode(cipher.nonce + ciphertext).decode()

    # Decrypt with AES in CTR mode
    def decrypt(self, content: bytes):
        raw = base64.b64decode(content)
        nonce, ciphertext = raw[:16], raw[16:]
        cipher = AES.new(self._current_enc_key, AES.MODE_CTR, nonce=nonce)
        return cipher.decrypt(ciphertext)

    def _split_aes_key(self):
        key_enc = self._key[:16]  # First 16 bytes for encryption
        key_hmac = self._key[16:]  # Last 16 bytes for HMAC
        return key_enc, key_hmac


class EncryptorRSA(Encryptor):

    def __init__(self):
        self._private_key = None
        self._public_key = None

    @property
    def private_key(self):
        raise AttributeError("You cannot access the key directly.")

    @property
    def public_key(self):
        raise AttributeError("You cannot access the key directly.")

    @private_key.setter
    def private_key(self, value: str):
        if not value:
            raise ValueError("Name cannot be empty")
        self._private_key = value

    @public_key.setter
    def public_key(self, value: str):
        if not value:
            raise ValueError("Name cannot be empty")
        self._public_key = value

    def encrypt(self, content: str):
        pass

    def decrypt(self, content: str):
        pass

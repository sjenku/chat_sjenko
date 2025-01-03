import base64
from abc import ABC, abstractmethod

from Crypto.Cipher import AES, PKCS1_OAEP
from Crypto.PublicKey import RSA
from Crypto.Random import get_random_bytes


class Encryptor(ABC):

    ENCODING_STD = 'utf-8'

    @abstractmethod
    def encrypt(self, key: bytes, content: str) -> str:
        pass

    @abstractmethod
    def decrypt(self, key: bytes, content: str) -> str:
        pass


class EncryptorAES(Encryptor):

    def __init__(self):
        self._used_nonce = None

    # Encrypt with AES in CTR mode
    def encrypt(self, key: bytes, content: str) -> str:
        nonce = get_random_bytes(8)
        cipher = AES.new(key, AES.MODE_CTR, nonce=nonce)
        self._used_nonce = cipher.nonce  # update the last used nonce.
        ciphertext = cipher.encrypt(content.encode(self.ENCODING_STD))

        return base64.b64encode(cipher.nonce + ciphertext).decode(self.ENCODING_STD)

    # Decrypt with AES in CTR mode
    def decrypt(self, key: bytes, content: str) -> str:
        raw = base64.b64decode(content)
        nonce, ciphertext = raw[:8], raw[8:]
        cipher = AES.new(key, AES.MODE_CTR, nonce=nonce)
        return cipher.decrypt(ciphertext).decode(self.ENCODING_STD)

    def get_used_nonce(self) -> bytes:
        return self._used_nonce


class EncryptorRSA(Encryptor):

    def encrypt(self, key: bytes, content: str) -> str:
        rsa_key = RSA.import_key(key)
        cipher = PKCS1_OAEP.new(rsa_key)
        ciphertext = cipher.encrypt(content.encode(self.ENCODING_STD))
        return base64.b64encode(ciphertext).decode(self.ENCODING_STD)

    def decrypt(self, key: bytes, content: str) -> str:
        rsa_key = RSA.import_key(key)
        cipher = PKCS1_OAEP.new(rsa_key)
        decrypted_bytes = cipher.decrypt(base64.b64decode(content))
        return decrypted_bytes.decode(self.ENCODING_STD)

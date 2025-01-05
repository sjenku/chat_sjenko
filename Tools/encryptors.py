import base64
from abc import ABC, abstractmethod
from typing import Union

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


class EncryptorAESKey:
    def __init__(self,key:Union[bytes,str]):
        if isinstance(key, bytes):
            if len(key) not in (16, 24, 32):
                raise ValueError("AES key must be 16, 24, or 32 bytes long.")
        elif isinstance(key, str):
            decoded_key = base64.b64decode(key)
            if len(decoded_key) not in (16, 24, 32):
                raise ValueError("Base64-decoded AES key must be 16, 24, or 32 bytes long.")
        else:
            raise TypeError("Key must be either bytes or string.")
        self._key = key

    def bytes(self):
        if isinstance(self._key,bytes):
            return self._key
        else:
            return base64.b64decode(self._key)

    def str(self):
        if isinstance(self._key,str):
            return self._key
        else:
            return base64.b64encode(self._key).decode(Encryptor.ENCODING_STD)

    @staticmethod
    def create() -> 'EncryptorAESKey':
        random_bytes = get_random_bytes(32)
        key = base64.b64encode(random_bytes).decode(Encryptor.ENCODING_STD)
        return EncryptorAESKey(key)


class EncryptorAES(Encryptor):

    def __init__(self):
        self._used_nonce = None

    # Encrypt with AES in CTR mode
    def encrypt(self, key: EncryptorAESKey, content: str) -> str:
        nonce = get_random_bytes(8)
        cipher = AES.new(key.bytes(), AES.MODE_CTR, nonce=nonce)
        self._used_nonce = cipher.nonce  # update the last used nonce.
        ciphertext = cipher.encrypt(content.encode(self.ENCODING_STD))

        return base64.b64encode(cipher.nonce + ciphertext).decode(self.ENCODING_STD)

    # Decrypt with AES in CTR mode
    def decrypt(self, key: EncryptorAESKey, content: str) -> str:
        raw = base64.b64decode(content)
        nonce, ciphertext = raw[:8], raw[8:]
        cipher = AES.new(key.bytes(), AES.MODE_CTR, nonce=nonce)
        return cipher.decrypt(ciphertext).decode(self.ENCODING_STD)

    def get_used_nonce(self) -> bytes:
        return self._used_nonce

class EncryptorRSAKey:
    def __init__(self,key:Union[bytes,str]):
        self._key = key

    def bytes(self):
        if isinstance(self._key,bytes):
            return self._key
        else:
            return self._key.encode(Encryptor.ENCODING_STD)

    def str(self):
        if isinstance(self._key,str):
            return self._key
        else:
            return self._key.decode(Encryptor.ENCODING_STD)

    # RSA Key Pair generation
    @staticmethod
    def create_keys() -> ('EncryptorRSAKey', 'EncryptorRSAKey'):
        key = RSA.generate(2048)
        private_key = key.export_key()
        public_key = key.publickey().export_key()
        return EncryptorRSAKey(private_key), EncryptorRSAKey(public_key)


class EncryptorRSA(Encryptor):

    def encrypt(self, key: EncryptorRSAKey, content: str) -> str:
        rsa_key = RSA.import_key(key.bytes())
        cipher = PKCS1_OAEP.new(rsa_key)
        ciphertext = cipher.encrypt(content.encode(self.ENCODING_STD))
        return base64.b64encode(ciphertext).decode(self.ENCODING_STD)

    def decrypt(self, key: EncryptorRSAKey, content: str) -> str:
        rsa_key = RSA.import_key(key.bytes())
        cipher = PKCS1_OAEP.new(rsa_key)
        decrypted_bytes = cipher.decrypt(base64.b64decode(content))
        return decrypted_bytes.decode(self.ENCODING_STD)

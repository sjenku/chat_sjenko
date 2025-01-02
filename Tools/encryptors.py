import base64
from abc import ABC, abstractmethod


from Crypto.Cipher import AES, PKCS1_OAEP
from Crypto.PublicKey import RSA
from Crypto.Random import get_random_bytes



class Encryptor(ABC):
    @abstractmethod
    def encrypt(self, key: bytes, content: bytes):
        pass

    @abstractmethod
    def decrypt(self, key: bytes, content: str):
        pass


class EncryptorAES(Encryptor):

    def __init__(self):
        self._used_nonce = None

    # Encrypt with AES in CTR mode
    def encrypt(self, key: bytes, content: bytes) -> str:
        # create a unique nonce
        nonce = get_random_bytes(8)

        # create a cipher with desired mode
        cipher = AES.new(key, AES.MODE_CTR,nonce=nonce)

        # update the last used nonce
        self._used_nonce = cipher.nonce

        # encrypt
        ciphertext = cipher.encrypt(content)

        return base64.b64encode(cipher.nonce + ciphertext).decode()

    # Decrypt with AES in CTR mode
    def decrypt(self, key: bytes, content: str) -> bytes:
        raw = base64.b64decode(content)
        nonce, ciphertext = raw[:8], raw[8:]
        cipher = AES.new(key, AES.MODE_CTR, nonce=nonce)
        return cipher.decrypt(ciphertext)

    def get_used_nonce(self) -> bytes:
        return self._used_nonce


class EncryptorRSA(Encryptor):

    def encrypt(self,key: bytes, content: bytes):

        rsa_key = RSA.import_key(key)
        cipher_rsa = PKCS1_OAEP.new(rsa_key)
        return base64.b64encode(cipher_rsa.encrypt(content)).decode()

    def decrypt(self,key: bytes, content: str):

        rsa_key = RSA.import_key(key)
        cipher_rsa = PKCS1_OAEP.new(rsa_key)
        return cipher_rsa.decrypt(base64.b64decode(content))


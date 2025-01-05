import base64

from Crypto.Hash import HMAC, SHA256
from Crypto.PublicKey import RSA
from Crypto.Random import get_random_bytes

from Tools.encryptors import EncryptorAESKey


class Tools:
    @staticmethod
    def _split_aes_key(aes_key: bytes) -> (bytes,bytes):
        key_enc = aes_key[:16]  # First 16 bytes for encryption
        key_hmac = aes_key[16:]  # Last 16 bytes for HMAC
        return key_enc, key_hmac

    # Generate HMAC
    @staticmethod
    def generate_hmac(key:EncryptorAESKey, content:bytes) -> str:
        h = HMAC.new(key.bytes(), digestmod=SHA256)
        h.update(content)
        return h.hexdigest()

    @staticmethod
    # Verify HMAC
    def verify_hmac(key:EncryptorAESKey, content:bytes, hmac: str):
        h = HMAC.new(key.bytes(), digestmod=SHA256)
        h.update(content)
        try:
            h.hexverify(hmac)
            return True
        except ValueError:
            return False
import base64

from Crypto.Hash import HMAC, SHA256
from Crypto.PublicKey import RSA
from Crypto.Random import get_random_bytes
from Crypto.Signature import pkcs1_15

from Tools.encryptors import EncryptorAESKey, EncryptorRSAKey


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

    @staticmethod
    def create_signature(rsa_private_key: EncryptorRSAKey,hmac: str) -> str:

        # create a signature, by encrypting HMAC with client's private key
        rsa_private_key = RSA.import_key(rsa_private_key.bytes())
        hash_obj = SHA256.new()
        hash_obj.update(hmac.encode())
        signature = pkcs1_15.new(rsa_private_key).sign(hash_obj)
        return base64.b64encode(signature).decode('utf-8')  # Encode the signature as a Base64 string

    @staticmethod
    def varify_signature(rsa_public_key:EncryptorRSAKey,signature:str,hmac: str):
        """This function raise an ValueError, TypeError if verification fails"""

        rsa_public_key = RSA.import_key(rsa_public_key.bytes())
        decoded_signature = base64.b64decode(signature)

        hash_obj = SHA256.new()
        hash_obj.update(hmac.encode())

        pkcs1_15.new(rsa_public_key).verify(hash_obj, decoded_signature)
from Crypto.Hash import HMAC, SHA256
from Crypto.PublicKey import RSA
from Crypto.Random import get_random_bytes


class Tools:

    # RSA Key Pair generation
    @staticmethod
    def generate_rsa_keys():
        key = RSA.generate(2048)
        private_key = key.export_key()
        public_key = key.publickey().export_key()
        return private_key, public_key

    # AES Key Generation
    @staticmethod
    def generate_aes_key():
        return get_random_bytes(32)

    @staticmethod
    def _split_aes_key(self):
        key_enc = self._key[:16]  # First 16 bytes for encryption
        key_hmac = self._key[16:]  # Last 16 bytes for HMAC
        return key_enc, key_hmac

    # Generate HMAC
    @staticmethod
    def generate_hmac(key, message):
        h = HMAC.new(key, digestmod=SHA256)
        h.update(message)
        return h.hexdigest()

    @staticmethod
    # Verify HMAC
    def verify_hmac(key, message, hmac):
        h = HMAC.new(key, digestmod=SHA256)
        h.update(message)
        try:
            h.hexverify(hmac)
            return True
        except ValueError:
            return False
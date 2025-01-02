import base64

from Crypto.Cipher import AES, PKCS1_OAEP
from Crypto.Hash import HMAC, SHA256
from Crypto.PublicKey import RSA
from Crypto.Random import get_random_bytes


# RSA Key Pair generation
def generate_rsa_keys():
    key = RSA.generate(2048)
    private_key = key.export_key()
    public_key = key.publickey().export_key()
    return private_key, public_key


# AES Key Generation
def generate_aes_key():
    return get_random_bytes(32)


# Encrypt with AES in CTR mode
def aes_encrypt(key, plaintext):
    cipher = AES.new(key, AES.MODE_CTR)
    ciphertext = cipher.encrypt(plaintext)
    cipher.nonce = b'5'
    return base64.b64encode(cipher.nonce + ciphertext).decode()


# Split AES key into two keys: encryption and HMAC
def split_aes_key(aes_key):
    key_enc = aes_key[:16]  # First 16 bytes for encryption
    key_hmac = aes_key[16:]  # Last 16 bytes for HMAC
    return key_enc, key_hmac


# Encrypt AES Key with RSA
def rsa_encrypt(public_key, aes_key):
    rsa_key = RSA.import_key(public_key)
    cipher_rsa = PKCS1_OAEP.new(rsa_key)
    return base64.b64encode(cipher_rsa.encrypt(aes_key)).decode()

# Decrypt AES Key with RSA
def rsa_decrypt(private_key, encrypted_aes_key):
    rsa_key = RSA.import_key(private_key)
    cipher_rsa = PKCS1_OAEP.new(rsa_key)
    return cipher_rsa.decrypt(base64.b64decode(encrypted_aes_key))


# Generate HMAC
def generate_hmac(key, message):
    h = HMAC.new(key, digestmod=SHA256)
    h.update(message)
    return h.hexdigest()


# Verify HMAC
def verify_hmac(key, message, hmac):
    h = HMAC.new(key, digestmod=SHA256)
    h.update(message)
    try:
        h.hexverify(hmac)
        return True
    except ValueError:
        return False


aes_key = generate_aes_key()
aes_encrypt(aes_key,"hello world")
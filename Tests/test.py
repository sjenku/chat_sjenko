from Tools.encryptors import EncryptorAES
from Tools.tools import Tools

encryptor_aes = EncryptorAES()
aes_key = Tools.generate_aes_key()
message = b"hello world this is a megic world and we want to take this output to dance yuhhuuuuuu hello hello hello"
encrypted_message = encryptor_aes.encrypt(aes_key,message)

print(f"encrypted message = {encrypted_message}")

decrypted_message = encryptor_aes.decrypt(aes_key,encrypted_message)

print(f"decrypted message = {decrypted_message}")



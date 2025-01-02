from abc import ABC, abstractmethod


class Encryptor(ABC):
    @abstractmethod
    def encrypt(self, content: str):
        pass

    @abstractmethod
    def decrypt(self, content: str):
        pass


class EncryptorAES(Encryptor):

    def __init__(self):
        self._key = None

    @property
    def key(self):
        raise AttributeError("You cannot access the key directly.")

    @key.setter
    def key(self, value):
        if not value:
            raise ValueError("Name cannot be empty")
        self._key = value

    def encrypt(self, content: str):
        pass

    def decrypt(self, content: str):
        pass


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

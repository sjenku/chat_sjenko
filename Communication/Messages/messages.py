import json
from abc import abstractmethod, ABC
from enum import Enum


# all supported types for messages between server and client and vise versa.
class CommunicationMessageTypesEnum(str,Enum):
    CLIENT_CONTENT_MESSAGE = "client_content_message"
    CLIENT_REGISTRATION_MESSAGE = "client_registration_message"
    SERVER_CONTENT_MESSAGE = "server_content_message"
    KEY_MESSAGE = "key_message"
    OPT_MESSAGE = "opt_message"
    ACK_MESSAGE = "ack_message"


class CommunicationMessage(ABC):
    """This is a Base class for all possible messages classes that support communication."""
    @abstractmethod
    def to_dict(self):
        pass

    def content(self) -> bytes:
        data = self.to_dict()
        serialized_message = json.dumps(data)
        content = serialized_message.encode()
        return content


class ContentMessage(CommunicationMessage):
    """This is a Class that hold the message passed between clients and server."""

    def __init__(self,
                 uid: str,
                 nonce: int,
                 content: str,
                 hmac: str,
                 signature: str):
        self.uid = uid
        self.nonce = nonce
        self.content = content
        self.hmac = hmac
        self.signature = signature

    def to_dict(self):
        pass
        # this message will not be passed


class ClientContentMessage(ContentMessage):
    """Messages sent from Client to Server."""

    def __init__(self,
                 des_uid: str,
                 uid: str,
                 nonce: int,
                 content: str,
                 hmac: str,
                 signature: str):
        super().__init__(uid, nonce, content, hmac, signature)
        self.des_uid = des_uid

    def to_dict(self):
        return {
            "type": CommunicationMessageTypesEnum.CLIENT_CONTENT_MESSAGE,
            "data": self.__dict__.copy()
        }


class ClientRegistrationMessage(CommunicationMessage):
    def __init__(self,
                 uid: str,
                 public_key: str):
        self.uid = uid
        self.public_key = public_key

    def to_dict(self):
        return {
            "type": CommunicationMessageTypesEnum.CLIENT_REGISTRATION_MESSAGE,
            "data": self.__dict__.copy()
        }


class ServerContentMessage(ContentMessage):
    """Message sent from server to Client."""

    def __init__(self, uid: str, nonce: int, content: str, hmac: str, signature: str):
        super().__init__(uid, nonce, content, hmac, signature)

    def to_dict(self):
        return {
            "type": CommunicationMessageTypesEnum.SERVER_CONTENT_MESSAGE,
            "data": self.__dict__.copy()
        }


class KeyMessage(CommunicationMessage):
    """Message that holds a key"""

    def __init__(self, key: str):
        self.key = key

    def to_dict(self):
        return {
            "type": CommunicationMessageTypesEnum.KEY_MESSAGE,
            "data": self.__dict__.copy()
        }


class OptMessage(CommunicationMessage):
    """Message that holds an OPT."""

    def __init__(self, opt: str):
        self.opt = opt

    def to_dict(self):
        return {
            "type": CommunicationMessageTypesEnum.OPT_MESSAGE,
            "data": self.__dict__.copy()
        }


class AckMessage(CommunicationMessage):
    """Message that sent as an acknowledgment to another side that he/her got the message."""

    def __init__(self, ack: str):
        self.ack = ack

    def to_dict(self):
        return {
            "type": CommunicationMessageTypesEnum.ACK_MESSAGE,
            "data": self.__dict__.copy()
        }

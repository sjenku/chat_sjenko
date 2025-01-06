import json
from abc import abstractmethod, ABC
from enum import Enum


# all supported types for messages between server and client and vise versa.
class CommunicationMessageTypesEnum(str,Enum):
    CONTENT_MESSAGE = "content_message"
    CLIENT_REGISTRATION_MESSAGE = "client_registration_message"
    KEY_MESSAGE = "key_message"
    OPT_MESSAGE = "opt_message"
    ACK_MESSAGE = "ack_message"


class CommunicationMessage(ABC):
    """This is a Base class for all possible messages classes that support communication."""
    @abstractmethod
    def to_dict(self):
        pass

    def encode(self) -> bytes:
        data = self.to_dict()
        serialized_message = json.dumps(data)
        content = serialized_message.encode()
        return content

    def __str__(self):
        return self.__dict__.__str__()


class ContentMessage(CommunicationMessage):
    """This is a Class that hold the message content that passed between client to client."""

    def __init__(self,
                 uid: str,
                 des_uid: str,
                 content: str,
                 hmac: str,
                 signature: str):
        self.uid = uid
        self.des_uid = des_uid
        self.content = content
        self.hmac = hmac
        self.signature = signature

    def to_dict(self):
        return {
            "type": CommunicationMessageTypesEnum.CONTENT_MESSAGE,
            "data": self.__dict__.copy()
        }


class ClientRegistrationMessage(CommunicationMessage):
    """This class holds the registration data that sent to the server by the client."""
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



class KeyMessage(CommunicationMessage):
    """Holds a key value"""

    def __init__(self,uid:str ,encrypted_key: str):
        self.uid = uid
        self.encrypted_key = encrypted_key

    def to_dict(self):
        return {
            "type": CommunicationMessageTypesEnum.KEY_MESSAGE,
            "data": self.__dict__.copy()
        }


class OptMessage(CommunicationMessage):
    """Message that holds an OPT."""

    def __init__(self,uid: str, opt: str):
        self.uid = uid
        self.opt = opt

    def to_dict(self):
        return {
            "type": CommunicationMessageTypesEnum.OPT_MESSAGE,
            "data": self.__dict__.copy()
        }


class AckMessage(CommunicationMessage):
    """Message that sent as an acknowledgment to another side that he/her got the message."""

    def __init__(self,uid: str, ack: str):
        self.uid = uid
        self.ack = ack

    def to_dict(self):
        return {
            "type": CommunicationMessageTypesEnum.ACK_MESSAGE,
            "data": self.__dict__.copy()
        }

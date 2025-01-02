class CommunicationMessage:
    """This is a Base class for all possible messages classes that support communication."""
    pass


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


class ClientRegistrationMessage(CommunicationMessage):
    def __init__(self,
                 uid: str,
                 public_key: str):
        self.uid = uid
        self.public_key = public_key


class ServerContentMessage(ContentMessage):
    """Message sent from server to Client."""

    def __init__(self, uid: str, nonce: int, content: str, hmac: str, signature: str):
        super().__init__(uid, nonce, content, hmac, signature)


class KeyMessage(CommunicationMessage):
    """Message that holds a key"""

    def __init__(self, key: str):
        self.key = key


class OptMessage(CommunicationMessage):
    """Message that holds an OPT."""

    def __init__(self, opt: str):
        self.opt = opt


class AckMessage(CommunicationMessage):
    """Message that sent as an acknowledgment to another side that he/her got the message."""

    def __init__(self, ack: str):
        self.ack = ack

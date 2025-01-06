from abc import ABC, abstractmethod


class CommunicationService(ABC):

    @abstractmethod
    def handle_msg_receiving(self, socket, address):
        pass

    @abstractmethod
    def send_by_secure_channel(self,destination,content):
        pass

    @abstractmethod
    def send_msg(self, destination, content):
        pass

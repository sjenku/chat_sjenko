from abc import ABC, abstractmethod


class CommunicationService(ABC):

    @abstractmethod
    def handle_msg_receiving(self, socket, address):
        pass

    @abstractmethod
    def prepare_msg_for_sending(self):
        pass

    @abstractmethod
    def send_msg(self, destination, content):
        pass

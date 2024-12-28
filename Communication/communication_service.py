from abc import ABC, abstractmethod


class CommunicationService(ABC):

    @abstractmethod
    def handle_msg(self):
        pass

    @abstractmethod
    def prepare_msg(self):
        pass

    @abstractmethod
    def send_msg(self,destination, content):
        pass

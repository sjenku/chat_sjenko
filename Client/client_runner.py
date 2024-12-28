from Communication.communication_service import CommunicationService
from Utils.internal_logger import InternalLogger


class ClientRunner(CommunicationService):

    _logger:InternalLogger

    def __init__(self):
        self._logger = InternalLogger()

    def handle_msg(self):
        pass

    def prepare_msg(self):
        pass

    def send_msg(self, destination, content):
        pass

    def start(self):
        self._logger.info("Client runner start")


if __name__ == "__main__":
    client_runner = ClientRunner()
    client_runner.start()


from Communication.communication_service import CommunicationService
from Utils.internal_logger import InternalLogger


class ServerRunner(CommunicationService):

    _logger:InternalLogger

    def __init__(self):
        self._logger = InternalLogger()

    def handle_msg(self):
        self._logger.info("Server handle message")
        pass

    def prepare_msg(self):
        self._logger.info("Server preparing message")
        pass

    def send_msg(self, destination, content):
        self._logger.info(f"Server sending message to {destination}")
        pass

    def start(self):
        self._logger.info("Start server")


if __name__ == "__main__":
    service_runner = ServerRunner()
    service_runner.start()


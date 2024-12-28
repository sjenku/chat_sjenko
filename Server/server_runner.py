import socket
import threading

from Communication.communication_service import CommunicationService
from Utils.internal_logger import InternalLogger


class ServerRunner(CommunicationService):

    _logger:InternalLogger
    _clients:list[socket]

    def __init__(self):
        self._logger = InternalLogger()
        self._clients = []

    def handle_msg_receiving(self,sock,address):
        self._logger.info("Server handle message")
        # Receive encrypted message and HMAC from the server
        data = sock.recv(1024)
        if not data:
            self._logger.warn("Connection closed by the server")
        else:
            print(data)

    def prepare_msg_for_sending(self):
        self._logger.info("Server preparing message")
        pass

    def send_msg(self, destination, content):
        self._logger.info(f"Server sending message to {destination}")
        pass

    def start(self):
        self._logger.info("Start server")
        host = 'localhost'
        port = 12345
        max_connections = 5

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
            server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            server_socket.bind((host, port))
            server_socket.listen()

            self._logger.info("Server is listening for connections...")
            while True:
                client_socket, address = server_socket.accept()
                self._logger.info("New connection with client")
                self._clients.append(client_socket)

                client_handler = threading.Thread(target=self.handle_msg_receiving, args=(client_socket, address))
                client_handler.start()


if __name__ == "__main__":
    service_runner = ServerRunner()
    service_runner.start()


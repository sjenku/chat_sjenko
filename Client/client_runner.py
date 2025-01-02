import socket
from typing import Optional

from Client.client_info import ClientInfo
from Communication.communication_service import CommunicationService
from Utils.internal_logger import InternalLogger


class ClientRunner(CommunicationService):

    def __init__(self, client: ClientInfo = None):
        self._logger: InternalLogger = InternalLogger()
        self.client_info: Optional[ClientInfo] = client
        self._aes_key: Optional[str] = None
        self._rsa_private_key: Optional[str] = None
        self._rsa_public_key: Optional[str] = None

    def handle_msg_receiving(self, n_socket, address):
        self._logger.info("Server handle message")
        pass

    def prepare_msg_for_sending(self):
        pass

    def send_msg(self, sock: socket, content):
        try:
            # Send data
            sock.sendall(content)
            print("Data sent successfully")
        except BrokenPipeError:
            print("Connection broken. Unable to send data.")
        except ConnectionResetError:
            print("Connection reset by peer.")
        except socket.timeout:
            print("Send operation timed out.")
        except OSError as e:
            print(f"OS error occurred: {e}")
        except ValueError as e:
            print(f"Value error: {e}")

    def connect_to_server(self, host: str, port: int, sock: socket):
        try:
            sock.connect((host, port))
        except ConnectionRefusedError:
            self._logger.error("Connection refused. Is the server running?")
        except TimeoutError:
            self._logger.error("Connection timed out. Server may be unreachable.")
        except socket.gaierror as e:
            self._logger.error(f"Address-related error connecting to server: {e}")
        except OSError as e:
            self._logger.error(f"General OS error: {e}")

    def start(self):
        self._logger.info("Client runner start")
        host = 'localhost'
        port = 12345

        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connect_to_server(host=host, port=port, sock=s)
        self.send_msg(sock=s, content=b"Hello World!!!")

        s.close()


if __name__ == "__main__":
    client_info = ClientInfo(uid="05012345678",name="Bob")
    client_runner = ClientRunner()
    client_runner.start()

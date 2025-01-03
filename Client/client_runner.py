import json
import logging
import socket
from enum import Enum

from typing import Optional

from Client.client_info import ClientInfo
from Client.client_outputs import ClientOutputsEnum
from Communication.Messages.messages import ClientRegistrationMessage
from Communication.communication_service import CommunicationService
from Tools.tools import Tools
from Utils.internal_logger import InternalLogger


class ClientRunnerStatusEnum(str,Enum):
    REGISTRATION = "registration"
    WAIT_FOR_OPT = "wait_for_opt"
    WAIT_FOR_SERVER_PUBLIC_KEY = "wait_for_server_public_key"
    COMPLETED_REGISTRATION = "completed_registration"

class ClientRunner(CommunicationService):

    def __init__(self):
        self._logger: InternalLogger = InternalLogger(logging_level=logging.WARN)
        self.client_info: Optional[ClientInfo] = None
        self._aes_key: Optional[str] = None
        self._rsa_private_key: Optional[str] = None
        self._rsa_public_key: Optional[str] = None
        self._server_public_key: Optional[str] = None
        self._status = ClientRunnerStatusEnum.REGISTRATION

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

        # prompt to console
        print(ClientOutputsEnum.WELCOME.value)

        # get answer if user want to start registration
        start_registration = 'N'
        while start_registration != 'Y' and start_registration != 'exit':
            start_registration = input(ClientOutputsEnum.ASK_REGISTRATION.value)
            if start_registration not in ['Y', 'N', 'exit']:
                print("The Value is Invalid.")

        # in case the client decided to exit.
        if start_registration == 'exit' or start_registration == 'N':
            print(ClientOutputsEnum.EXIT.value)
            return

        # create a socket to Server
        host = 'localhost'
        port = 12345
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # connect to the server
        self.connect_to_server(host=host, port=port, sock=s)

        # if we reached here, means user want start registration
        # name = input(ClientOutputsEnum.INSERT_NAME.value)  # todo: check valid input
        # uid = input(ClientOutputsEnum.INSERT_UID.value)  # todo: check valid input
        name = "Jenia"
        uid = "123456789"
        self.client_info = ClientInfo(uid=uid, name=name)

        rsa_private_key, rsa_public_key = Tools.generate_rsa_keys()

        #       - send to server user's public key and uid
        message = ClientRegistrationMessage(uid=uid, public_key=rsa_public_key)

        #       - receive an OPT
        #       - send to the server the OPT
        #       - receive server's public key
        #       - send encrypted AES key ( using server's public key for encryption )
        #       - server's send ACK

        # send message
        self.send_msg(sock=s, content=message.content())

        s.close()


if __name__ == "__main__":
    # 1. get info from the user, name and phone number
    # 2. start registration
    #       - send to server user's public key and uid
    #       - receive an OPT
    #       - send to the server the OPT
    #       - receive server's public key
    #       - send encrypted AES key ( using server's public key for encryption )
    #       - server's send ACK
    # 3.

    client_info = ClientInfo(uid="05012345678", name="Bob")
    client_runner = ClientRunner()
    client_runner.start()

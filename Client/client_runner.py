import json
import logging
import socket
import threading
from enum import Enum

from typing import Optional

from Client.client_info import ClientInfo
from Client.client_outputs import ClientOutputsEnum
from Communication.Messages.messages import ClientRegistrationMessage, OptMessage, KeyMessage, ContentMessage, \
    CommunicationMessageTypesEnum
from Communication.communication_service import CommunicationService
from Tools.encryptors import EncryptorRSA
from Tools.tools import Tools
from Utils.internal_logger import InternalLogger


class ClientRunnerStatusEnum(str, Enum):
    REGISTRATION = "registration"
    WAIT_FOR_OPT = "wait_for_opt"
    WAIT_FOR_SERVER_PUBLIC_KEY = "wait_for_server_public_key"
    COMPLETED_REGISTRATION = "completed_registration"


class ClientRunner(CommunicationService):

    def __init__(self):
        self._logger: InternalLogger = InternalLogger(logging_level=logging.DEBUG)
        self.client_info: Optional[ClientInfo] = None
        self._aes_key: Optional[str] = None
        self._rsa_private_key: Optional[str] = None
        self._rsa_public_key: Optional[str] = None
        self._server_public_key: Optional[str] = None
        self._status = ClientRunnerStatusEnum.REGISTRATION

    def handle_msg_receiving(self, n_socket, address):
        self._logger.info("Client handle message")
        while True:  # Continuous loop to keep receiving messages
            raw_data = n_socket.recv(1024)
            if not raw_data:
                self._logger.warn("Connection closed by the server")
            else:
                message = json.loads(raw_data)
                message_type = message.get("type")
                data = message.get("data")

                if message_type == CommunicationMessageTypesEnum.OPT_MESSAGE:
                    opt_message = OptMessage(**data)
                    self.handle_opt_msg_receiving(opt_message=opt_message, n_socket=n_socket)

                if message_type == CommunicationMessageTypesEnum.KEY_MESSAGE:
                    key_message = KeyMessage(**data)
                    self.handle_key_msg_receiving(key_message=key_message, n_socket=n_socket)

                if message_type == CommunicationMessageTypesEnum.CONTENT_MESSAGE:
                    content_message = ContentMessage(**data)
                    self.handle_content_msg(content_message=content_message)


    def handle_opt_msg_receiving(self, opt_message: OptMessage, n_socket: socket):
        self._logger.info(f"received from server OPT = {opt_message.opt}")
        # check first that we actually waiting for opt, if not write an error
        if self._status != ClientRunnerStatusEnum.WAIT_FOR_OPT:
            self._logger.error("The Client not waiting for OPT!")
            return

        # change the status
        self._status = ClientRunnerStatusEnum.WAIT_FOR_SERVER_PUBLIC_KEY

        # resend opt message to server as approve that this client.
        self.send_msg(n_socket, opt_message.encode())

    def handle_key_msg_receiving(self, key_message: KeyMessage, n_socket: socket):
        self._logger.info("Received key message.")
        # check we waiting for server's public key
        if self._status != ClientRunnerStatusEnum.WAIT_FOR_SERVER_PUBLIC_KEY:
            self._logger.error("Client not waiting for server's public key")
            return

        # save server's public key
        self._server_public_key = key_message.key

        # send to a server the encrypted AES key, for feature communication
        encryptor_rsa = EncryptorRSA()
        encrypted_key = encryptor_rsa.encrypt(key=self._server_public_key.encode(EncryptorRSA.ENCODING_STD),
                                              content=self._aes_key)

        message_to_send = KeyMessage(key=encrypted_key)  # message with the client's encrypted AES key

        self._status = ClientRunnerStatusEnum.COMPLETED_REGISTRATION
        self.send_msg(sock=n_socket, content=message_to_send.encode())


    def handle_content_msg(self, content_message: ContentMessage):
        self._logger.info("Received content message.")
        # check registration completed
        if self._status != ClientRunnerStatusEnum.COMPLETED_REGISTRATION:
            self._logger.error("The registration not completed for this Client.")
            return

        print(f"""
        ====== Received Message ====
        == From    : {content_message.uid}
        == To      : {content_message.des_uid}
        == Content : {content_message.content}
        =========== End ============
        """)

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

    def start_registration(self, sock: socket):

        name = input(ClientOutputsEnum.INSERT_NAME.value)  # todo: check valid input
        uid = input(ClientOutputsEnum.INSERT_UID.value)  # todo: check valid input
        self.client_info = ClientInfo(uid=uid, name=name)

        self._rsa_private_key, self._rsa_public_key = Tools.generate_rsa_keys()

        # set status to wait from OPT from the server
        self._status = ClientRunnerStatusEnum.WAIT_FOR_OPT

        # send to server Client's public key and uid
        message = ClientRegistrationMessage(uid=uid, public_key=self._rsa_public_key)
        self.send_msg(sock=sock, content=message.encode())

    def start(self):

        # generate client's keys
        self._rsa_private_key,self._rsa_public_key = Tools.generate_rsa_keys()
        self._aes_key = Tools.generate_aes_key()
        self._logger.info(f"Aes key = {self._aes_key}")

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

        # start a thread that will handle message receiving
        message_thread = threading.Thread(target=self.handle_msg_receiving, args=(s, (host, port)))
        message_thread.start()

        # if we reached here, means user want start registration
        self.start_registration(sock=s)

        # wait here till the registration not completed
        while self._status != ClientRunnerStatusEnum.COMPLETED_REGISTRATION:
            pass
        print(ClientOutputsEnum.REGISTRATION_COMPLETED.value)

        # print to the Client that now able to send message
        print(ClientOutputsEnum.CAN_SEND_MESSAGE.value)

        # Keep the main thread alive while handling incoming messages
        try:
            while True:
                pass
        except KeyboardInterrupt:
            self._logger.info("Client shutting down")
            s.close()

        s.close()


if __name__ == "__main__":

    client_runner = ClientRunner()
    client_runner.start()

import json
import logging
import random
import socket
import threading
from typing import Optional

from Communication.Messages.messages import ClientRegistrationMessage, OptMessage, KeyMessage, ContentMessage, \
    CommunicationMessageTypesEnum
from Communication.communication_service import CommunicationService
from Tools.encryptors import EncryptorRSA
from Tools.tools import Tools
from Utils.internal_logger import InternalLogger


class ServerRunner(CommunicationService):
    _logger: InternalLogger

    def __init__(self):
        self._logger = InternalLogger(logging_level=logging.DEBUG)
        self._private_key:Optional[str] = None
        self._public_key:Optional[str] = None
        self._clients:list[socket] = []

        self._opt = "" # todo: we will do this just for test

    def handle_msg_receiving(self, sock, address):
        self._logger.info("Server handle message")

        while True:  # Continuous loop to keep receiving messages
            raw_data = sock.recv(1024)
            if not raw_data:
                self._logger.warn("Connection closed by the server")
            else:
                message = json.loads(raw_data)
                message_type = message.get("type")
                data = message.get("data")

                if message_type == CommunicationMessageTypesEnum.CLIENT_REGISTRATION_MESSAGE:
                    client_reg_message = ClientRegistrationMessage(**data)
                    self.handle_client_registration_msg_receiving(client_reg_message=client_reg_message,sock=sock)

                if message_type == CommunicationMessageTypesEnum.OPT_MESSAGE:
                    opt_message = OptMessage(**data)
                    self.handle_opt_msg_receiving(opt_message = opt_message,sock=sock)

                if message_type == CommunicationMessageTypesEnum.KEY_MESSAGE:
                    key_message = KeyMessage(**data)
                    self.handle_key_msg_receiving(key_message=key_message,sock=sock)

                if message_type == CommunicationMessageTypesEnum.CONTENT_MESSAGE:
                    content_message = ContentMessage(**data)
                    self.handle_content_message(content_message=content_message)

    def handle_client_registration_msg_receiving(self,client_reg_message:ClientRegistrationMessage,sock:socket):
        self._logger.info("Received Client Registration msg")
        # send to the client opt
        self._opt = str(random.randint(100000, 999999))
        opt_message = OptMessage(opt=str(self._opt))
        self.send_msg(sock=sock,content=opt_message.encode())

    def handle_opt_msg_receiving(self,opt_message:OptMessage,sock:socket):
        self._logger.info(f"Received OPT message {opt_message.opt}.")
        if opt_message.opt == self._opt:

            # send server public key
            key_message = KeyMessage(key=self._public_key)
            self.send_msg(sock=sock,content=key_message.encode())


    def handle_key_msg_receiving(self,key_message:KeyMessage,sock:socket):
        self._logger.info(f"Received Key Message {key_message.key}")

        encryptor_rsa = EncryptorRSA()
        decrypted_key = encryptor_rsa.decrypt(key=self._private_key.encode(),content=key_message.key)
        pass

    def handle_content_message(self,content_message:ContentMessage):
        self._logger.info("Received Content Message")
        pass

    def prepare_msg_for_sending(self):
        self._logger.info("Server preparing message")
        pass

    def send_msg(self, sock: socket, content):
        self._logger.info(f"Server sending message to {content.decode()}")
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

    def start(self):
        self._logger.info("Start server")

        # create server's private and public keys
        self._private_key,self._public_key = Tools.generate_rsa_keys()


        # set host and port of the server
        host = 'localhost'
        port = 12345
        max_connections = 5

        # create a socket object
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
            server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            server_socket.bind((host, port))
            server_socket.listen()

            self._logger.info("Server is listening for connections...")

            # accept and handle client connections
            while True:
                client_socket, address = server_socket.accept()
                self._logger.info("New connection with client")
                self._clients.append(client_socket)

                client_handler = threading.Thread(target=self.handle_msg_receiving, args=(client_socket, address))
                client_handler.start()



if __name__ == "__main__":
    service_runner = ServerRunner()
    service_runner.start()


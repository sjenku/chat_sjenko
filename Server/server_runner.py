import copy
import json
import logging
import random
import socket
import threading
from datetime import datetime, timedelta
from typing import Optional

from Communication.Messages.messages import ClientRegistrationMessage, OptMessage, KeyMessage, ContentMessage, \
    CommunicationMessageTypesEnum
from Communication.communication_service import CommunicationService
from Server.DB.data_base import DataBase
from Server.DB.rows import RegistrationTableRow, UserKeyTableRow
from Tools.encryptors import EncryptorAES, EncryptorAESKey, EncryptorRSAKey, EncryptorRSA
from Tools.tools import Tools
from Utils.internal_logger import InternalLogger


class ServerRunner(CommunicationService):
    _logger: InternalLogger

    def __init__(self):
        self._logger = InternalLogger(logging_level=logging.DEBUG)
        self._private_key: Optional[EncryptorRSAKey] = None
        self._public_key: Optional[EncryptorRSAKey] = None
        self._clients: list[socket] = []
        self._uid_socket: dict[str, socket] = {}
        self._db = DataBase()

    def handle_msg_receiving(self, sock, address):
        self._logger.info("Server handle message")

        while True:  # Continuous loop to keep receiving messages
            raw_data = sock.recv(1024)
            if not raw_data:
                self._logger.warning("Connection closed by the server")
            else:
                message = json.loads(raw_data)
                message_type = message.get("type")
                data = message.get("data")

                if message_type == CommunicationMessageTypesEnum.CLIENT_REGISTRATION_MESSAGE:
                    client_reg_message = ClientRegistrationMessage(**data)
                    self.handle_client_registration_msg_receiving(client_reg_message=client_reg_message, sock=sock)

                if message_type == CommunicationMessageTypesEnum.OPT_MESSAGE:
                    opt_message = OptMessage(**data)
                    self.handle_opt_msg_receiving(opt_message=opt_message, sock=sock)

                if message_type == CommunicationMessageTypesEnum.KEY_MESSAGE:
                    key_message = KeyMessage(**data)
                    self.handle_key_msg_receiving(key_message=key_message)

                if message_type == CommunicationMessageTypesEnum.CONTENT_MESSAGE:
                    content_message = ContentMessage(**data)
                    self.handle_content_message(content_message=content_message)

    def handle_client_registration_msg_receiving(self, client_reg_message: ClientRegistrationMessage, sock: socket):
        self._logger.info("Received Client Registration msg")
        # bind the socket to the uid
        self._uid_socket[client_reg_message.uid] = sock

        # add client to the registration_table
        success = self._db.registration_table.add_row(RegistrationTableRow(uid=client_reg_message.uid))
        if not success:
            raise ValueError("This account already exists in data base")

        # add client public key to the user_key_table
        success = self._db.user_key_table.add_row(UserKeyTableRow(uid=client_reg_message.uid,
                                                                  public_key=client_reg_message.public_key))
        if not success:
            raise ValueError("This user already exists in the data base")

        # update the registration_table with info that client provided the public key
        registration_row = self._db.registration_table.find_by_uid(client_reg_message.uid)
        registration_row.recieved_pub_key = True
        self._db.registration_table.update_row(registration_row)

        # send to the client opt
        opt = str(random.randint(100000, 999999))
        opt_message = OptMessage(uid=client_reg_message.uid, opt=str(opt))
        self.send_msg(sock=sock, content=opt_message.encode())

        # update the time of the opt that sent
        registration_row.opt_time = datetime.now()
        registration_row.sent_opt = True
        self._db.registration_table.update_row(registration_row)

    def handle_opt_msg_receiving(self, opt_message: OptMessage, sock: socket):
        self._logger.info(f"Received OPT message {opt_message.opt}.")
        registration_row = self._db.registration_table.find_by_uid(opt_message.uid)
        if not registration_row:
            self._logger.error("Client not registered and sent OPT code!")

        if datetime.now() - registration_row.opt_time >= timedelta(seconds=10):
            self._logger.error("Time Limit reached for OPT,resending new opt to the client")

            # send to the client opt
            opt = str(random.randint(100000, 999999))
            new_opt_message = OptMessage(uid=opt_message.uid, opt=str(opt))
            self.send_msg(sock=sock, content=new_opt_message.encode())

            # update the time of opt message sending
            registration_row.opt_time = datetime.now()
            self._db.registration_table.update_row(registration_row)
            return

        # update registration table that server received opt from client
        registration_row.recieved_opt = True
        self._db.registration_table.update_row(registration_row)

        # send server public key
        key_message = KeyMessage(uid=opt_message.uid, encrypted_key=self._public_key.str())
        self.send_msg(sock=sock, content=key_message.encode())

    def handle_key_msg_receiving(self, key_message: KeyMessage):
        self._logger.info(f"Received Key Message {key_message.encrypted_key}")

        registration_row = self._db.registration_table.find_by_uid(key_message.uid)
        if not registration_row:
            self._logger.error("Client not registered and sent OPT code!")

        # update registration table
        registration_row.recieved_aes = True
        registration_row.passed_registration = True
        self._logger.info(f"Registration Row: {registration_row}")
        self._db.registration_table.update_row(registration_row)

        user_key_row = self._db.user_key_table.find_by_uid(key_message.uid)
        if not user_key_row:
            self._logger.error("The user doesn't have a row in user key database.")

        # update user key row table
        user_key_row.encrypted_aes_key = key_message.encrypted_key
        self._db.user_key_table.update_row(user_key_row)

    def handle_content_message(self, content_message: ContentMessage):
        self._logger.info(f"Server received message {content_message}")
        # check if the user passed the registration
        registration_row_client_from = self._db.registration_table.find_by_uid(content_message.uid)
        registration_row_client_to = self._db.registration_table.find_by_uid(content_message.des_uid)

        if not registration_row_client_from or not registration_row_client_from.passed_registration:
            self._logger.error(f"Client with uid = {content_message.uid} not registered.")
            return
        if not registration_row_client_to or not registration_row_client_to.passed_registration:
            self._logger.error(f"Client that message need to be delivered to with uid = "
                               f"{content_message.des_uid} not registered.")
            return

        encryptor_aes = EncryptorAES()
        encryptor_rsa = EncryptorRSA()

        # decrypt the aes keys of the client's from and to
        client_from_encrypted_aes_key = self._db.user_key_table.find_by_uid(content_message.uid).encrypted_aes_key
        client_from_decrypted_aes_key = encryptor_rsa.decrypt(key=self._private_key,
                                                              content=client_from_encrypted_aes_key)
        client_from_aes_key = EncryptorAESKey(key=client_from_decrypted_aes_key)

        client_to_encrypted_aes_key = self._db.user_key_table.find_by_uid(content_message.des_uid).encrypted_aes_key
        client_to_decrypted_aes_key = encryptor_rsa.decrypt(key=self._private_key,
                                                            content=client_to_encrypted_aes_key)
        client_to_aes_key = EncryptorAESKey(key=client_to_decrypted_aes_key)

        # compare hmac
        if not Tools.verify_hmac(key=client_from_aes_key,
                             content=content_message.content.encode(),
                             hmac=content_message.hmac):
            self._logger.warning("The HMAC not identical")
            return

        # first decrypt the content with client's aes key that sent the message
        decrypted_content = encryptor_aes.decrypt(key=client_from_aes_key, content=content_message.content)

        # encrypt the content with aes_key of the client that the message will be delivered to
        encrypted_content = encryptor_aes.encrypt(key=client_to_aes_key,content=decrypted_content)

        # set a new hmac on encrypted_content
        hmac = Tools.generate_hmac(key=client_to_aes_key,content=encrypted_content.encode())

        # create a new message
        new_content_message = copy.deepcopy(content_message)
        new_content_message.content = encrypted_content
        new_content_message.hmac = hmac

        # if both registered send message
        self.send_msg(sock=self._uid_socket[content_message.des_uid], content=new_content_message.encode())

    def prepare_msg_for_sending(self):
        self._logger.info("Server preparing message")
        pass

    def send_msg(self, sock: socket, content:bytes):
        self._logger.info(f"Server sending message to {content.decode()}")
        try:
            # Send data
            sock.sendall(content)
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
        self._private_key, self._public_key = EncryptorRSAKey.create_keys()

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

import base64
import json
import logging
import socket
import threading
from enum import Enum

from typing import Optional

from Crypto.Hash import SHA256
from Crypto.PublicKey import RSA
from Crypto.PublicKey.RSA import RsaKey
from Crypto.Signature import pkcs1_15

from Client.client_info import ClientInfo
from Client.client_outputs import ClientOutputsEnum
from Communication.Messages.messages import ClientRegistrationMessage, OptMessage, KeyMessage, ContentMessage, \
    CommunicationMessageTypesEnum
from Communication.communication_service import CommunicationService
from Tools.encryptors import EncryptorRSA, EncryptorAES, EncryptorAESKey, EncryptorRSAKey
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
        self._aes_key: Optional[EncryptorAESKey] = None
        self._rsa_private_key: Optional[EncryptorRSAKey] = None
        self._rsa_public_key: Optional[EncryptorRSAKey] = None
        self._server_public_key: Optional[EncryptorRSAKey] = None
        self._uid:str = ""
        self._status:ClientRunnerStatusEnum = ClientRunnerStatusEnum.REGISTRATION

        # we use this attributes, in case we receive message, and message on console removed by incoming message
        self._waiting_uid_des_input:bool = False
        self._waiting_content_input:bool = False

    def handle_msg_receiving(self, n_socket, address):
        self._logger.info("Client handle message")
        while True:  # Continuous loop to keep receiving messages
            raw_data = n_socket.recv(1024)
            if not raw_data:
                self._logger.warning("Connection closed by the server")
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
        if (self._status != ClientRunnerStatusEnum.WAIT_FOR_OPT and
                self._status != ClientRunnerStatusEnum.WAIT_FOR_SERVER_PUBLIC_KEY):
            self._logger.error("The Client not waiting for OPT!")
            return

        # prompt to the Client that received opt and need to resend it to the server
        client_opt = input(ClientOutputsEnum.RECEIVED_OPT.value.format(opt_message.opt))
        respond_opt_message = OptMessage(uid=opt_message.uid,opt=client_opt)

        # change the status
        self._status = ClientRunnerStatusEnum.WAIT_FOR_SERVER_PUBLIC_KEY

        # resend opt message to server as approve that this client.
        self.send_msg(n_socket, respond_opt_message.encode())

    def handle_key_msg_receiving(self, key_message: KeyMessage, n_socket: socket):
        self._logger.info("Received key message.")
        # check we waiting for server's public key
        if self._status != ClientRunnerStatusEnum.WAIT_FOR_SERVER_PUBLIC_KEY:
            self._logger.error("Client not waiting for server's public key")
            return

        # save server's public key
        self._server_public_key = EncryptorRSAKey(key_message.encrypted_key)

        # send to a server the encrypted AES key, for feature communication
        encryptor_rsa = EncryptorRSA()
        encrypted_key = encryptor_rsa.encrypt(key=self._server_public_key,
                                              content=self._aes_key.str())

        # message with the client's encrypted AES key
        message_to_send = KeyMessage(uid=key_message.uid,encrypted_key=encrypted_key)

        self._status = ClientRunnerStatusEnum.COMPLETED_REGISTRATION
        self.send_msg(sock=n_socket, content=message_to_send.encode())

    def handle_content_msg(self, content_message: ContentMessage):
        self._logger.info("Received content message.")
        # check registration completed
        if self._status != ClientRunnerStatusEnum.COMPLETED_REGISTRATION:
            self._logger.error("The registration not completed for this Client.")
            return

        # compare hmac
        if not Tools.verify_hmac(key=self._aes_key,
                                 content=content_message.content.encode(),
                                 hmac=content_message.hmac):
            self._logger.warning("The HMAC not identical")
            return

        # check signature
        # todo:

        # decrypt the message with client's aes key
        encryptor_aes = EncryptorAES()
        dycrypted_content = encryptor_aes.decrypt(key=self._aes_key,content=content_message.content)

        print(f"""
        ====== Received Message ====
        == From    : {content_message.uid}
        == To      : {content_message.des_uid}
        == Content : {dycrypted_content}
        =========== End ============
        """)

        if self._waiting_uid_des_input:
            print(ClientOutputsEnum.CAN_SEND_MESSAGE_WRITE_TO.value)
        if self._waiting_content_input:
            print(ClientOutputsEnum.CAN_SEND_MESSAGE_WRITE_CONTENT.value)

    def prepare_msg_for_sending(self):
       pass

    def send_msg(self, sock: socket, content):
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
        self._uid = uid
        self.client_info = ClientInfo(uid=uid, name=name)

        self._rsa_private_key, self._rsa_public_key = EncryptorRSAKey.create_keys()

        # set status to wait from OPT from the server
        self._status = ClientRunnerStatusEnum.WAIT_FOR_OPT

        # send to server Client's public key and uid
        message = ClientRegistrationMessage(uid=uid, public_key=self._rsa_public_key.str())
        self.send_msg(sock=sock, content=message.encode())

    def start(self):

        # generate client's keys
        self._rsa_private_key, self._rsa_public_key = EncryptorRSAKey.create_keys()
        self._aes_key = EncryptorAESKey.create()
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

        # print to the Client that now able to send message
        print(ClientOutputsEnum.REGISTRATION_COMPLETED.value)
        while True:
            self._waiting_uid_des_input = True
            des_uid = input(ClientOutputsEnum.CAN_SEND_MESSAGE_WRITE_TO.value)
            self._waiting_uid_des_input = False
            if des_uid == 'exit':
                break
            self._waiting_content_input = True
            content = input(ClientOutputsEnum.CAN_SEND_MESSAGE_WRITE_CONTENT.value)
            self._waiting_content_input = False
            if content == 'exit':
                break

            # encrypt the content of the message
            encryptor_aes = EncryptorAES()
            encrypted_content = encryptor_aes.encrypt(key=self._aes_key,content=content)

            # create hmac
            hmac = Tools.generate_hmac(key=self._aes_key,content=encrypted_content.encode())

            # create signature
            signature = Tools.create_signature(rsa_private_key=self._rsa_private_key,hmac=hmac)

            message = ContentMessage(uid=self._uid,
                                     des_uid=des_uid,
                                     content=encrypted_content,
                                     hmac=hmac,
                                     signature=signature)
            self.send_msg(sock=s,content=message.encode())


        s.close()


if __name__ == "__main__":
    client_runner = ClientRunner()
    client_runner.start()

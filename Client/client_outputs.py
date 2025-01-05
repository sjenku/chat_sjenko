from enum import Enum


class ClientOutputsEnum(str, Enum):
    WELCOME = "Hello Dear User, Welcome to SjenkuChatApp"
    ASK_REGISTRATION = "Do you want to start registration Y/N ( write 'exit' if you would like to exit ):"
    EXIT = "Thank you, see you next time."
    INSERT_NAME = "Please insert your name:"
    INSERT_UID = "Please insert your phone number:"
    REGISTRATION_COMPLETED = "Hey! Good news, the registration completed ( press 'exit' if you would to exit ):"
    CAN_SEND_MESSAGE_WRITE_TO = "To send a message write to and press 'Enter':"
    CAN_SEND_MESSAGE_WRITE_CONTENT = "write content of the message and press 'Enter':"
    RECEIVED_OPT = "You received opt: {}, please resend it to server:"

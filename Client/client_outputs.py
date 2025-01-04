from enum import Enum


class ClientOutputsEnum(str, Enum):
    WELCOME = "Hello Dear User, Welcome to SjenkuChatApp"
    ASK_REGISTRATION = "Do you want to start registration Y/N ( write 'exit' if you would like to exit ):"
    EXIT = "Thank you, see you next time."
    INSERT_NAME = "Please insert your name:"
    INSERT_UID = "Please insert your phone number:"
    REGISTRATION_COMPLETED = "Hey! Good news, the registration completed"
    CAN_SEND_MESSAGE = "To send a message write the message and press Enter"
    RECEIVED_OPT = "You received opt: {}, please resend it to server:"


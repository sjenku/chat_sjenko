from Server.DB.pending_message_table_row import PendingMessageTableRow
from Server.DB.registration_table_tow import RegistrationTableRow
from Server.DB.user_key_table_row import UserKeyTableRow


class DataBase:

    def __init__(self):
        self.user_key_table: list[UserKeyTableRow] = list()
        self.registration_table: list[RegistrationTableRow] = list()
        self.pending_message_table: list[PendingMessageTableRow] = list()

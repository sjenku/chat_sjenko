from Server.DB.tables import UserKeyTable, RegistrationTable, PendingMessageTable


class DataBase:

    def __init__(self):
        self.user_key_table: UserKeyTable = UserKeyTable()
        self.registration_table: RegistrationTable = RegistrationTable()
        self.pending_message_table: PendingMessageTable = PendingMessageTable()

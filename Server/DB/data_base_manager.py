from Server.DB.data_base import DataBase
from Server.DB.pending_message_table_row import PendingMessageTableRow
from Server.DB.registration_table_tow import RegistrationTableRow
from Server.DB.table_row import TableRow
from Server.DB.user_key_table_row import UserKeyTableRow


class DataBaseManager:

    def __init__(self,db:DataBase):
        if not db:
            raise ValueError("must pass not None db")
        self.db = db

    def insert_row(self,row:TableRow):

        if not row:
            raise ValueError("row table missing.")

        if isinstance(row,UserKeyTableRow):
            self.db.user_key_table.append(row)
            return

        if isinstance(row,RegistrationTableRow):
            self.db.registration_table.append(row)
            return

        if isinstance(row,PendingMessageTableRow):
            self.db.pending_message_table.append(row)
            return



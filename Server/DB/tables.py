import copy
from typing import Generic, TypeVar, Optional

from Server.DB.rows import UserKeyTableRow, RegistrationTableRow, PendingMessageTableRow

T = TypeVar('T', bound='TableRow')

class Table(Generic[T]):
    def __init__(self):
        self.rows: list[T] = []

    def find_by_uid(self, uid: str) -> Optional[T]:
        """Find a row by its uid."""
        for row in self.rows:
            if row._uid == uid:
                return copy.deepcopy(row)

        return None

    def is_row_exist(self,row:T) -> bool:
        """find row by passed row object."""
        for row_in_table in self.rows:
            if row_in_table == row:
                return True

        return False

    def add_row(self,row:T) -> bool:
        row_exist = self.is_row_exist(row)
        if not row_exist:
            self.rows.append(copy.deepcopy(row))
            return True

        return False

    def remove_row(self,row:T):
        row_exist = self.is_row_exist(row)
        if row_exist:
            self.rows.remove(row)
            return True

        return False

    def update_row(self,row:T):
        row_in_data_base = self.find_by_uid(uid=row._uid)
        if row_in_data_base:
            self.remove_row(row_in_data_base)
            self.add_row(row)


    def remove_row_by_uid(self,uid: str) -> bool:
        row = self.find_by_uid(uid=uid)
        if row:
            self.remove_row(row)
            return True

        return False


class UserKeyTable(Table[UserKeyTableRow]):
    pass


class RegistrationTable(Table[RegistrationTableRow]):
    pass


class PendingMessageTable(Table[PendingMessageTableRow]):
    pass

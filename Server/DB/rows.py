from datetime import time, datetime


class TableRow:
    def __init__(self,uid: str):
        self._uid = uid

    def __eq__(self, other):
        if isinstance(other, TableRow):
            return self._uid == other._uid
        return False

    def __str__(self):
        return self.__dict__.__str__()


class UserKeyTableRow(TableRow):
    def __init__(self, uid: str, encrypted_aes_key: str = "", public_key: str = ""):
        super().__init__(uid)
        self.encrypted_aes_key = encrypted_aes_key
        self.public_key = public_key


class RegistrationTableRow(TableRow):
    def __init__(self, uid: str,
                 sent_opt: bool = False,
                 recieved_opt: bool = False,
                 opt_time: datetime = None,
                 recieved_aes: bool = False,
                 recieved_pub_key: bool = False,
                 passed_registration: bool = False):
        super().__init__(uid)
        self.sent_opt = sent_opt
        self.recieved_opt = recieved_opt
        self.opt_time = opt_time
        self.recieved_aes = recieved_aes
        self.recieved_pub_key = recieved_pub_key
        self.passed_registration = passed_registration


class PendingMessageTableRow(TableRow):
    def __init__(self, uid: str, des_uid: str, message: dict[str, str], timestamp: time, remain_tries):
        super().__init__(uid)
        self.des_uid = des_uid
        self.message = message
        self.timestamp = timestamp
        self.remain_tries = remain_tries
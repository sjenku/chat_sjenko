from datetime import time


class PendingMessageTableRow:
    def __init__(self,
                 uid: str,
                 des_uid: str,
                 message: dict[str, str],
                 timestamp: time,
                 remain_tries):
        self.uid = uid
        self.des_uid = des_uid
        self.message = message
        self.timestamp = timestamp
        self.remain_tries = remain_tries

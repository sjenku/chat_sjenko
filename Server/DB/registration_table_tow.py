from datetime import time


class RegistrationTableRow:
    def __init__(self,
                 uid: str,
                 sent_opt: bool,
                 rec_opt: bool,
                 opt_time: time,
                 rec_aes: bool,
                 rec_pub_key: bool,
                 passed_registration: bool):
        self.uid = uid
        self.sent_opt = sent_opt
        self.rec_opt = rec_opt
        self.opt_time = opt_time
        self.rec_aes = rec_aes
        self.rec_pub_key = rec_pub_key
        self.passed_registration = passed_registration

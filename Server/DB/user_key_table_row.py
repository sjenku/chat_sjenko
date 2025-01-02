class UserKeyTableRow:
    def __init__(self, uid: str, aes_key: str, public_key: str):
        self.uid = uid
        self.aes_key = aes_key
        self.public_key = public_key

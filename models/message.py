from utils import datetime_from_str, str_from_datetime
from .model import Model


class Message(Model):
    def __init__(self, message_id: int = None, room_id: int = None, user_id: int = None, text: str = None,
                 added: str = None):
        self.message_id = message_id
        self.room_id = room_id
        self.user_id = user_id
        self.text = text
        self.added = datetime_from_str(added)

    def view(self) -> dict:
        added = str_from_datetime(self.added)
        return {'id': self.message_id, 'userId': self.user_id, 'text': self.text, 'added': added}

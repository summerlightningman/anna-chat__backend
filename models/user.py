from utils import datetime_from_str
from .model import Model


class User(Model):
    def __init__(self, user_id: int = None, name: str = None, login: str = None, password: str = None,
                 added: str = None):
        self.user_id = user_id
        self.name = name
        self.login = login
        self.password = password
        self.added = datetime_from_str(added)

    def __str__(self):
        return 'User(id={}, name={})'.format(self.user_id, self.name)

    def view(self) -> dict:
        return {'id': self.user_id, 'name': self.name}

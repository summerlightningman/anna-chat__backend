from utils import datetime_from_str
from typing import Dict
from aiohttp.web import WebSocketResponse
from .model import Model


class Room(Model):
    def __init__(self, room_id: int = None, name: str = None, creator: int = None, added: str = None):
        self.room_id = room_id
        self.name = name
        self.creator = creator
        self.added = datetime_from_str(added)

        self.__user_list: Dict[int, WebSocketResponse] = {}

    def __str__(self):
        return 'Room(id={}, name={})'.format(self.room_id, self.name)

    def add_user(self, user_id: int, ws: WebSocketResponse) -> str:
        if user_id in self.__user_list:
            return 'User already in room'
        self.__user_list[user_id] = ws
        return 'Success'

    def remove_user(self, user_id) -> str:
        if user_id in self.__user_list:
            return 'User not exists'
        self.__user_list.pop(user_id)
        return 'Success'

    def view(self) -> dict:
        return {'id': self.room_id, 'name': self.name}

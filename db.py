import sqlite3
from typing import Iterable, Tuple

from config import DB_NAME
from models.message import Message
from models.room import Room
from models.user import User


class Db:
    def __init__(self):
        self.connection = sqlite3.Connection(DB_NAME)
        self.cursor = self.connection.cursor()

        self.message_keys = ['id', 'userId', 'text', 'added']

    def login_user(self, login: str, password: str) -> [User, None]:
        sql = 'SELECT user_id, name FROM user WHERE login = ? AND password = ?'
        self.cursor.execute(sql, (login, password))
        if args := self.cursor.fetchone():
            return User(*args)
        else:
            return

    def get_user_data(self, user_id: int) -> [User, None]:
        sql = 'SELECT name FROM user WHERE user_id = ?'
        self.cursor.execute(sql, (user_id,))
        if args := self.cursor.fetchone():
            return User(*args)
        else:
            return

    def get_user_list(self) -> Tuple[User]:
        sql = 'SELECT user_id, name FROM user'
        self.cursor.execute(sql)
        return tuple(User(*args) for args in self.cursor.fetchall())

    def get_room_list(self, user_id: int) -> tuple:
        sql = 'SELECT room_id, name FROM room WHERE room_id IN (SELECT room_id FROM room_user WHERE user_id = ? ) ' \
              'ORDER BY added'
        self.cursor.execute(sql, (user_id,))
        return tuple(Room(*args).view() for args in self.cursor.fetchall())

    def get_message_list(self, room_id: int) -> tuple:
        sql = 'SELECT message_id, room_id, user_id, text, added FROM message WHERE room_id = ? ORDER BY added'
        self.cursor.execute(sql, (room_id,))
        return tuple(Message(*args).view() for args in self.cursor.fetchall())

    def get_names_from_id(self, id_list: Iterable) -> tuple:
        sql = 'SELECT user_id, name FROM user WHERE user_id IN ({})'.format(",".join(map(str, id_list)))
        self.cursor.execute(sql)
        return tuple(User(*args).view() for args in self.cursor.fetchall())

    def get_users_by_room_id(self, room_id: int) -> tuple:
        sql = 'SELECT u.user_id, name FROM user u INNER JOIN room_user ru on u.user_id = ru.user_id WHERE room_id = ?'
        self.cursor.execute(sql, (room_id,))
        return tuple(User(*args).view() for args in self.cursor.fetchall())

    def save_message(self, room_id: int, user_id: int, text: str, added: str) -> dict:
        args = (room_id, user_id, text, added)
        insert_sql = 'INSERT INTO message (room_id, user_id, text, added) VALUES (?, ?, ?, ?)'
        self.cursor.execute(insert_sql, args)
        self.connection.commit()
        select_sql = 'SELECT message_id, user_id, text, added FROM message ' \
                     'WHERE room_id = ? AND user_id = ? AND text = ? AND added = ?'
        self.cursor.execute(select_sql, args)
        return dict(zip(self.message_keys, self.cursor.fetchone()))

import logging
from collections import defaultdict

import jwt
import aiohttp
from aiohttp import web

from db import Db
from models.user import User
from secret_code import SECRET

logging.basicConfig(level=logging.DEBUG)

DB = Db()
CORS_HEADERS = {
    'Access-Control-Allow-Origin': 'http://localhost:3000',
    'Access-Control-Allow-Credentials': 'true'
}


def json_response(data: dict, headers=None, **kwargs) -> web.json_response:
    if headers is None:
        headers = {}
    return web.json_response(data, headers={**headers, **CORS_HEADERS}, status=data['code'], **kwargs)


def get_user_id(token: str):
    logging.info(f'get_user_id | token: {token}')
    return jwt.decode(token, SECRET, 'HS256')['id']


async def authorize(request: web.Request) -> web.json_response:
    data = await request.post()

    login: str = data.get('login')
    password: str = data.get('password')
    logging.info(f'authorize | login: {login}; password: {password}')
    if login and password:
        user: User = DB.login_user(login, password)
        if not user:
            resp = json_response({'code': 401, 'text': 'Login and/or password are not correct'})
        else:
            token = jwt.encode({'id': user.user_id, 'name': user.name}, SECRET, algorithm='HS256')
            resp = json_response({'code': 200, 'text': 'success', 'token': token})
            resp.set_cookie('token', token)
    else:
        resp = json_response({'code': 400, 'text': 'Login and/or password did not sent'})
    return resp


async def get_user_data_by_token(request: web.Request) -> web.json_response:
    logging.info(f"get user data by token | token: {request.cookies.get('token')}")
    if not (token := request.cookies.get('token')):
        return json_response({'code': 400, 'text': 'Token not found'})

    user_data = jwt.decode(token, SECRET, algorithms='HS256')
    return json_response({'code': 200, 'text': 'success', **user_data})


async def get_user_list(request: web.Request) -> web.json_response:
    logging.info(f"get user list | token: {request.cookies.get('token')}")
    if 'token' not in request.cookies:
        return json_response({'code': 400, 'text': 'Token not found'})

    user_list: tuple = DB.get_user_list()
    return json_response({'code': 200, 'text': 'Success', 'userList': user_list})


async def get_room_list(request: web.Request) -> web.json_response:
    if not (token := request.cookies.get('token')):
        return json_response({'code': 400, 'text': 'Token not found'})

    user_id = get_user_id(token)
    room_list = DB.get_room_list(user_id)
    return json_response({'code': 200, 'text': 'Success', 'roomList': room_list})


async def logout(request: web.Request) -> web.json_response:
    if 'token' in request.cookies:
        resp = json_response({'code': 200, 'text': 'Success'})
        resp.set_cookie('token', '', max_age=-1)
        return resp
    return json_response({'code': 400, 'text': 'Token not found'})


async def start_chat(request: web.Request) -> web.WebSocketResponse:
    room_id = request.match_info.get('id')
    ws = web.WebSocketResponse()
    if not (token := request.cookies.get('token')):
        await ws.close()
        return ws

    user_id = get_user_id(token)

    if not ws.can_prepare(request):
        await ws.close(code=aiohttp.WSCloseCode.PROTOCOL_ERROR)

    await ws.prepare(request)

    async for message in ws:
        if not isinstance(message, aiohttp.WSMessage):
            break
        if message.type == web.WSMsgType.text:
            msg = message.json()
            command = msg['type']
            logging.info(f"start chat | user_id: {user_id}; room_id: {room_id}; msg: {msg['type']}")
            if command == 'leave_room':
                if user_id in request.app['websockets'][room_id]:
                    request.app['websockets'][room_id].pop(user_id)
                    if room_id in request.app['websockets'] and not request.app['websockets'][room_id]:
                        return request.app['websockets'].pop(room_id)
            if command == 'join_room':
                if user_id in request.app['websockets'][room_id]:
                    await ws.close(code=aiohttp.WSCloseCode.TRY_AGAIN_LATER, message=b'Username already in use')

                if not ws.closed:
                    message_list = DB.get_message_list(room_id)
                    room_user_list = DB.get_users_by_room_id(room_id)
                    await ws.send_json({'type': 'start', 'messageList': message_list, 'userList': room_user_list})

                request.app['websockets'][room_id][user_id] = ws
            if command == 'send_message':
                text = msg['text']
                added = msg['added']
                new_message = DB.save_message(room_id, user_id, text, added)
                for user_ws in request.app['websockets'][room_id].values():
                    if not ws.closed:
                        await user_ws.send_json({'type': 'new_text_message', 'message': new_message})
    return ws


if __name__ == '__main__':
    app = web.Application()
    app['websockets'] = defaultdict(dict)
    app.add_routes([
        web.post('/login', authorize),
        web.get('/profile', get_user_data_by_token),
        web.get('/user_list', get_user_list),
        web.get('/room_list', get_room_list),
        web.get('/logout', logout),
        web.get('/chat/{id}', start_chat),
    ])

    web.run_app(app)

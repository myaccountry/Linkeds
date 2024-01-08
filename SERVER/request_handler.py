import logging
import os
import pickle
import time

from DATABASE.database import Database


class RequestHandler:

    def __init__(self, transport, main_work):

        self.methods = {}
        for key, value in RequestHandler.__dict__.items():
            if key[:2] != '__' and key[-2:] != '__':
                self.methods[f"<{key.upper().replace('_', '-')}>"] = key

        self.main_work = main_work
        self.CONNECTIONS = {}
        self._transport = transport
        self.addr = transport.get_extra_info("peername")
        self.database = Database()
        self.database.connect()

    @staticmethod
    def form_request(method, data):
        return {'method': method, 'data': data}

    def send_request(self, data) -> None:
        self._transport.write(pickle.dumps(data) + b"<END>")

    def send_request_to(self, data, addr) -> None:
        logging.debug('SEND REQUEST TO CONNECTIONS: ', self.CONNECTIONS)
        logging.debug('SEND REQUEST TO ADDR: ', self.CONNECTIONS.get(addr))
        logging.debug('SEND REQUEST TO TRANSPORT: ', self.CONNECTIONS.get(addr).get('transport'))
        transport = self.CONNECTIONS.get(addr).get('transport')
        transport.write(pickle.dumps(data) + b"<END>")

    def call_method(self, data):
        needed_data = data.get('data')
        return getattr(self, self.methods.get(data.get('method')))(needed_data)

    def registration(self, data) -> dict:
        user_data = data.get('user_data')
        user_login = user_data.get('login')
        if self.database.login_exist(user_login):
            return self.form_request('<REGISTRATION-DENIED>', {'reason': 'Такой логин уже существует!'})
        user_data = self.database.configure_data(user_data, 'User')
        user_data['ip'] = self.addr[0]
        registered_data = self.database.registrate_user(user_data)
        user_social = self.database.select(
            table_name='social', id=registered_data.get('id'))[0]
        return self.form_request('<REGISTRATION-SUCCESS>',
                                 {'user_data': registered_data, 'user_social': user_social})

    def login(self, data) -> dict:
        user_data = data.get('user_data')
        user_login = user_data.get('login')
        if not self.database.login_exist(user_login):
            return self.form_request('<LOGIN-DENIED>', {'reason': 'Такого логина не существует!'})
        user_password = user_data.get('password')
        actual_password = self.database.select(
            table_name='user', id=user_login, subject='password', criterion='login')[0].get('password')
        if user_password != actual_password:
            return self.form_request('<LOGIN-DENIED>', {'reason': 'Неправильный пароль!'})
        user_data = self.database.select(
            table_name='user', id=user_login, criterion='login')[0]
        user_social = self.database.select(
            table_name='social', id=user_data.get('id'))[0]
        return self.form_request('<LOGIN-SUCCESS>', {'user_data': user_data, 'user_social': user_social})

    def online(self, data) -> dict:
        user_data = data.get('user_data')
        self.database.update(id=user_data.get('id'), subject='online', subject_value='True')
        if self.database.is_user_online(user_data.get('id')):
            return self.form_request(
                '<ONLINE-DENIED>',
                {'reason': 'Ваш аккаунт уже используется с другого устройства!'})
        connection = {'ip': f"{self.addr[0]}:{self.addr[1]}", 'id': user_data.get('id'), 'user_data': 'None'}
        self.database.insert(table_name='connection', subject_values=connection)
        self.database.update(table_name='connection', criterion='ip', id=f'{self.addr[0]}:{self.addr[1]}',
                             subject='user_data', subject_value=pickle.dumps(user_data))
        return self.form_request('<COMPLETE>', {'None': 'None'})

    def offline(self, data) -> dict:
        user_data = data.get('user_data')
        self.database.update(id=user_data.get('id'), subject='online', subject_value='False')
        self.database.delete(table_name='connection', criterion='ip', id=f'{self.addr[0]}:{self.addr[1]}')
        return self.form_request('<COMPLETE>', {'None': 'None'})

    def change_user_data(self, data) -> dict:
        user_data = data.get('user_data')
        for key, value in user_data.items():
            self.database.update(id=user_data.get('id'), subject=key, subject_value=value)
        return self.form_request('<COMPLETE>', {'None': 'None'})

    def get_image(self, data) -> dict:
        path = data.get('path')
        bytes_array = self.database.load_image(path)
        return self.form_request('<GET-IMAGE-SUCCESS>', {'image': bytes_array})

    def save_image(self, data) -> dict:
        image_type = data.get('image_type')
        image_bytes = data.get('image_bytes')
        user_social = data.get('user_social')
        self.database.save_image(user_social, image_type, image_bytes)
        return self.form_request('<COMPLETE>', {'None': 'None'})

    def set_user_social(self, data):
        id = data.get('user_data').get('id')
        user_social = self.database.select(table_name='social', id=id)[0]
        return self.form_request('<SET-USER-SOCIAL>', {'user_social': user_social})

    def update_pfp(self, data):
        path = data.get('user_social').get('pfp')
        if path == 'None':
            return self.form_request('<COMPLETE>', {'None': 'None'})
        image_bytes = self.database.load_image(path)
        return self.form_request('<UPDATE-PFP>', {'image_bytes': image_bytes})

    def update_friends(self, data) -> dict:
        return self.form_request('<COMPLETE>', {'None': 'None'})

    def update_request_friends(self, data) -> dict:
        user_data = data.get('user_data')
        self.database.connect()
        user_social = self.database.select(table_name='social', id=user_data.get('id'))[0]

        friends_requests = user_social.get('request_friends')
        if friends_requests == b'None':
            return self.form_request('<UPDATE-REQUEST-FRIENDS>', {'friends_requests': 'None'})

        data_to_send = []
        for friend_request in pickle.loads(friends_requests):
            friend_data = friend_request.get('friend_data')
            request_status = friend_request.get('request_status')
            friend_pfp_path = self.database.select(
                table_name='social', id=friend_data.get('id'))[0].get('pfp')
            friend_pfp = self.database.load_image(friend_pfp_path)
            data_to_send.append(
                {'friend_data': friend_data, 'friend_pfp': friend_pfp, 'request_status': request_status}
            )

        return self.form_request('<UPDATE-REQUEST-FRIENDS>', {'friends_requests': data_to_send})

    def add_request_friend(self, data) -> dict:
        self.database.connect()
        user_data = data.get('user_data')
        user_social = data.get('user_social')
        friend_id = data.get('friend_id')
        user_id = user_data.get('id')

        if int(user_id) == int(friend_id):
            return self.form_request(
                '<ADD-REQUEST-FRIEND-DENIED>',
                {'reason': 'Вы не можете добавить в друзья самого себя!'}
            )

        friend_data = self.database.select(table_name='user', id=friend_id)[0]
        friend_social = self.database.select(table_name='social', id=friend_id)[0]

        if user_social.get('request_friends') == b'None':
            static = pickle.dumps([{'friend_data': friend_data, 'request_status': 'sender', 'friend_id': friend_id}])
        else:
            request_friends = pickle.loads(user_social.get('request_friends'))
            print('User requests', request_friends)
            for request in request_friends:
                if int(friend_id) == int(request.get('friend_id')):
                    if request.get('request_status') == 'sender':
                        return self.form_request(
                            '<ADD-REQUEST-FRIEND-DENIED>',
                            {'reason': 'Вы уже отправили заявку этому пользователю'}
                        )
                    return self.form_request(
                        '<ADD-REQUEST-FRIEND-DENIED>',
                        {'reason': 'Этот пользователь уже отправил вам заявку, ответьте на неё!'}
                    )
            request_friends.append({'friend_data': friend_data, 'request_status': 'sender', 'friend_id': friend_id})
            static = pickle.dumps(request_friends)
        self.database.update_binary(table_name='social', id=user_id,
                                    subject='request_friends', subject_value=static)

        if friend_social.get('request_friends') == b'None':
            static = pickle.dumps([{'friend_data': user_data, 'request_status': 'receiver', 'friend_id': user_id}])
        else:
            request_friends = pickle.loads(friend_social.get('request_friends'))
            request_friends.append({'friend_data': user_data, 'request_status': 'receiver', 'friend_id': user_id})
            static = pickle.dumps(request_friends)
        self.database.update_binary(table_name='social', id=friend_id,
                                    subject='request_friends', subject_value=static)

        user_social = self.database.select(table_name='social', id=user_id)[0]
        friend_social = self.database.select(table_name='social', id=friend_id)[0]

        friend_data = self.database.select(table_name='user', id=friend_id)[0]
        if friend_data.get('online') == 'True':
            friend_addr = self.database.select(
                table_name='connection', criterion='id', id=friend_id)[0].get('ip').split(':')
            friend_addr = tuple([friend_addr[0], int(friend_addr[1])])
            self.send_request_to(self.form_request(
                '<SET-USER-SOCIAL>', {'user_social': friend_social}), friend_addr)

        return self.form_request(
            '<SET-USER-SOCIAL>',
            {'user_social': user_social})

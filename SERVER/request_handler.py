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
        logging.debug(f'SEND REQUEST TO CONNECTIONS: {str(self.CONNECTIONS)}')
        logging.debug(f'SEND REQUEST TO ADDR: {str(self.CONNECTIONS.get(addr))}')
        logging.debug(f'SEND REQUEST TO TRANSPORT: {str(self.CONNECTIONS.get(addr).get("transport"))}')
        transport = self.CONNECTIONS.get(addr).get('transport')
        transport.write(pickle.dumps(data) + b"<END>")

    def send_request_if_online(self, request, user_id) -> bool:
        self.database.connect()
        user_data = self.database.select(table_name='user', id=user_id)[0]
        if user_data.get('online') == 'True':
            user_addr = self.database.select(
                table_name='connection', criterion='id', id=user_id)[0].get('ip').split(':')
            user_addr = tuple([user_addr[0], int(user_addr[1])])

            self.send_request_to(request, user_addr)
            return True
        return False

    def update_data_for_all_friends_online(self, user_data) -> None:
        self.database.connect()
        sended = []

        user_social = self.database.select(table_name='social', id=user_data.get('id'))[0]
        if user_social.get('friends') != b'None':
            for friend in pickle.loads(user_social.get('friends')):
                friend_id = friend.get('friend_id')
                if friend_id in sended:
                    continue
                friend_social = self.database.select(table_name='social', id=friend_id)[0]
                if self.send_request_if_online(self.form_request(
                    '<SET-USER-SOCIAL>',
                    {'user_social': friend_social}
                ), friend_id):
                    sended.append(friend_id)

        if user_social.get('request_friends') != b'None':
            for friend in pickle.loads(user_social.get('request_friends')):
                friend_id = friend.get('friend_id')
                if friend_id in sended:
                    continue
                friend_social = self.database.select(table_name='social', id=friend_id)[0]
                if self.send_request_if_online(self.form_request(
                        '<SET-USER-SOCIAL>',
                        {'user_social': friend_social}
                ), friend_id):
                    sended.append(friend_id)

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
        pfp_image = self.database.load_image('\\pfp_storage\\standard.png')
        self.database.save_image(user_social, 'pfp', pfp_image)
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
        self.database.connect()
        id = data.get('user_data').get('id')
        password = data.get('user_data').get('password')
        user_data = self.database.select(table_name='user', id=id)[0]
        if user_data is None:
            return self.form_request('<COMPLETE>', {'None': 'None'})
        if str(password) != str(user_data['password']):
            return self.form_request(
                '<ONLINE-DENIED>',
                {'reason': 'Пароль на вашем аккаунте был сменён.\nАвто-вход невозможен!'})
        if user_data.get('deleted_status') == 'True':
            return self.form_request(
                '<ONLINE-DENIED>',
                {'reason': 'Ваш аккаунт удалён!'})
        self.database.update(id=user_data.get('id'), subject='online', subject_value='True')
        if self.database.is_user_online(user_data.get('id')):
            return self.form_request(
                '<ONLINE-DENIED>',
                {'reason': 'Ваш аккаунт уже используется с другого устройства!'})
        connection = {'ip': f"{self.addr[0]}:{self.addr[1]}", 'id': user_data.get('id'), 'user_data': 'None'}
        self.database.insert(table_name='connection', subject_values=connection)
        self.database.update(table_name='connection', criterion='ip', id=f'{self.addr[0]}:{self.addr[1]}',
                             subject='user_data', subject_value=pickle.dumps(user_data))
        user_data = self.database.select(table_name='user', id=user_data.get('id'))[0]
        self.update_data_for_all_friends_online(user_data)
        return self.form_request('<SET-USER-DATA>', {'user_data': user_data})

    def offline(self, data) -> dict:
        user_data = data.get('user_data')
        self.database.update(id=user_data.get('id'), subject='online', subject_value='False')
        self.database.delete(table_name='connection', criterion='ip', id=f'{self.addr[0]}:{self.addr[1]}')
        user_data = self.database.select(table_name='user', id=user_data.get('id'))[0]
        self.update_data_for_all_friends_online(user_data)
        return self.form_request('<COMPLETE>', {'None': 'None'})

    def change_user_data(self, data) -> dict:
        user_data = data.get('user_data')
        for key, value in user_data.items():
            self.database.update(id=user_data.get('id'), subject=key, subject_value=value)
        user_data = self.database.select(table_name='user', id=user_data.get('id'))[0]
        self.update_data_for_all_friends_online(user_data)
        return self.form_request('<COMPLETE>', {'None': 'None'})

    def change_login(self, data) -> dict:
        self.database.connect()
        user_data = data.get('user_data')
        login = user_data.get('login')
        if self.database.login_exist(login):
            return self.form_request('<REQUEST-DENIED>', {'reason': 'Такой логин уже существует!'})
        self.change_user_data({'user_data': user_data})
        return self.form_request('<SET-USER-DATA>', {'user_data': user_data})

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

    def set_user_data(self, data):
        id = data.get('id')
        user_data = self.database.select(table_name='user', id=id)[0]
        return self.form_request('<SET-USER-DATA>', {'user_data': user_data})

    def set_user_social(self, data):
        id = data.get('user_data').get('id')
        user_social = self.database.select(table_name='social', id=id)[0]
        return self.form_request('<SET-USER-SOCIAL>', {'user_social': user_social})

    def update_pfp(self, data):
        self.database.connect()
        path = data.get('user_social').get('pfp')
        if path == 'None':
            return self.form_request('<COMPLETE>', {'None': 'None'})
        image_bytes = self.database.load_image(path)
        user_data = self.database.select(table_name='user', id=data.get('user_social').get('id'))[0]
        return self.form_request('<UPDATE-PFP>', {'image_bytes': image_bytes})

    def update_friends(self, data) -> dict:
        self.database.connect()

        user_data = data.get('user_data')
        user_social = self.database.select(table_name='social', id=user_data.get('id'))[0]
        friends = user_social.get('friends')

        if friends == b'None':
            return self.form_request('<UPDATE-FRIENDS>', {'friends': 'None'})

        friends = pickle.loads(friends)
        data_to_send = []
        for friend in friends:
            friend_id = friend.get('friend_id')
            friend_data = self.database.select(table_name='user', id=friend_id)[0]
            friend_social = self.database.select(table_name='social', id=friend_id)[0]
            friend_pfp = self.database.load_image(friend_social.get('pfp'))
            data_to_send.append(
                {'friend_data': friend_data, 'friend_pfp': friend_pfp, 'friend_social': friend_social}
            )

        return self.form_request('<UPDATE-FRIENDS>', {'friends': data_to_send})

    def update_request_friends(self, data) -> dict:
        self.database.connect()

        user_data = data.get('user_data')
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

    def update_black_list(self, data) -> dict:
        self.database.connect()
        user_data = data.get('user_data')
        user_social = self.database.select(table_name='social', id=user_data.get('id'))[0]

        black_list = user_social.get('black_list_friends')
        if black_list == b"None" or black_list == 'None' or black_list is None:
            return self.form_request('<UPDATE-BLACK-LIST>', {'black_list': 'None'})

        data_to_send = []
        for friend_bl in pickle.loads(black_list):
            friend_data = self.database.select(table_name='user', id=friend_bl.get('friend_id'))[0]
            friend_pfp_path = self.database.select(
                table_name='social', id=friend_data.get('id'))[0].get('pfp')
            friend_pfp = self.database.load_image(friend_pfp_path)
            data_to_send.append(
                {'friend_data': friend_data, 'friend_pfp': friend_pfp})

        return self.form_request('<UPDATE-BLACK-LIST>', {'black_list': data_to_send})

    def add_request_friend(self, data) -> dict:
        self.database.connect()
        user_data = data.get('user_data')
        user_social = data.get('user_social')
        friend_id = data.get('friend_id')
        user_id = user_data.get('id')

        if str(user_id) == str(friend_id):
            return self.form_request(
                '<ADD-REQUEST-FRIEND-DENIED>',
                {'reason': 'Вы не можете добавить в друзья самого себя!'}
            )

        if not self.database.id_exist(str(friend_id)):
            if not self.database.login_exist(str(friend_id)):
                return self.form_request(
                    '<ADD-REQUEST-FRIEND-DENIED>',
                    {'reason': 'Такого пользователя не существует'}
                )
            friend_id = self.database.select(
                table_name='user', criterion='login', id=friend_id)[0].get('id')

        friend_data = self.database.select(table_name='user', id=friend_id)[0]
        friend_social = self.database.select(table_name='social', id=friend_id)[0]

        if friend_data.get('deleted_status') == 'True':
            return self.form_request(
                '<ADD-REQUEST-FRIEND-DENIED>',
                {'reason': 'Аккаунт этого пользователя заблокирован/удалён'}
            )
        # Adding to user_social[request_friends] new request
        if user_social.get('request_friends') == b'None':
            static = pickle.dumps([{'friend_data': friend_data, 'request_status': 'sender', 'friend_id': friend_id}])
        else:
            request_friends = pickle.loads(user_social.get('request_friends'))
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

        # Adding to friend_social[request_friends] new request
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

        self.send_request_if_online(self.form_request(
            '<SET-USER-SOCIAL>',
            {'user_social': friend_social}
        ), friend_id)

        user_data = self.database.select(table_name='user', id=user_data.get('id'))[0]

        return self.form_request(
            '<SET-USER-SOCIAL>',
            {'user_social': user_social}
        )

    def add_friend(self, data) -> dict:
        self.database.connect()
        user_data = data.get('user_data')
        user_social = data.get('user_social')
        user_id = user_data.get('id')
        friend_id = data.get('friend_id')

        friend_data = self.database.select(table_name='user', id=friend_id)[0]
        friend_social = self.database.select(table_name='social', id=friend_id)[0]

        if user_social.get('friends') == b'None':
            static = pickle.dumps([{'friend_data': friend_data, 'friend_id': friend_id}])
        else:
            friends = pickle.loads(user_social.get('friends'))
            friends.append({'friend_data': friend_data, 'friend_id': friend_id})
            static = pickle.dumps(friends)
        self.database.update_binary(
            table_name='social', id=user_id, subject='friends', subject_value=static)

        request_friends = pickle.loads(user_social.get('request_friends'))
        for request in request_friends:
            if int(request.get('friend_id')) == int(friend_id):
                del request_friends[request_friends.index(request)]
                if not request_friends:
                    request_friends = b'None'
                    break
                request_friends = pickle.dumps(request_friends)
                break
        self.database.update_binary(
            table_name='social', id=user_id, subject='request_friends', subject_value=request_friends)

        if friend_social.get('friends') == b'None':
            static = pickle.dumps([{'friend_data': user_data, 'friend_id': user_id}])
        else:
            friends = pickle.loads(friend_social.get('friends'))
            friends.append({'friend_data': user_data, 'friend_id': user_id})
            static = pickle.dumps(friends)
        self.database.update_binary(
            table_name='social', id=friend_id, subject='friends', subject_value=static)

        request_friends = pickle.loads(friend_social.get('request_friends'))
        for request in request_friends:
            if int(request.get('friend_id')) == int(user_id):
                del request_friends[request_friends.index(request)]
                if not request_friends:
                    request_friends = b'None'
                    break
                request_friends = pickle.dumps(request_friends)
                break
        self.database.update_binary(
            table_name='social', id=friend_id, subject='request_friends', subject_value=request_friends)

        user_social = self.database.select(table_name='social', id=user_id)[0]
        friend_social = self.database.select(table_name='social', id=friend_id)[0]

        self.send_request_if_online(self.form_request(
            '<SET-USER-SOCIAL>',
            {'user_social': friend_social}
        ), friend_id)

        user_data = self.database.select(table_name='user', id=user_data.get('id'))[0]

        return self.form_request(
            '<SET-USER-SOCIAL>',
            {'user_social': user_social}
        )

    def cancel_request_friend(self, data) -> dict:
        user_social = data.get('user_social')
        friend_id = data.get('friend_id')
        user_id = user_social.get('id')

        friend_social = self.database.select(table_name='social', id=friend_id)[0]

        request_friends = pickle.loads(user_social.get('request_friends'))
        for request in request_friends:
            if int(request.get('friend_id')) == int(friend_id):
                del request_friends[request_friends.index(request)]
                if not request_friends:
                    request_friends = b'None'
                    break
                request_friends = pickle.dumps(request_friends)
                break
        self.database.update_binary(
            table_name='social', id=user_id, subject='request_friends', subject_value=request_friends)

        request_friends = pickle.loads(friend_social.get('request_friends'))
        for request in request_friends:
            if int(request.get('friend_id')) == int(user_id):
                del request_friends[request_friends.index(request)]
                if not request_friends:
                    request_friends = b'None'
                    break
                request_friends = pickle.dumps(request_friends)
                break
        self.database.update_binary(
            table_name='social', id=friend_id, subject='request_friends', subject_value=request_friends)

        user_social = self.database.select(table_name='social', id=user_id)[0]
        friend_social = self.database.select(table_name='social', id=friend_id)[0]

        self.send_request_if_online(self.form_request(
            '<SET-USER-SOCIAL>',
            {'user_social': friend_social}
        ), friend_id)

        return self.form_request(
            '<SET-USER-SOCIAL>',
            {'user_social': user_social}
        )

    def add_friend_to_black_list(self, data) -> dict:
        self.database.connect()
        user_social = data.get('user_social')
        user_id = user_social.get('id')
        friend_id = data.get('friend_id')
        friend_social = self.database.select(table_name='social', id=friend_id)[0]

        if user_social.get('black_list_friends') in (b"None", 'None', None):
            static = pickle.dumps([{'friend_id': friend_id}])
        else:
            black_list_friends = pickle.loads(user_social.get('black_list_friends'))
            black_list_friends.append({'friend_id': friend_id})
            static = pickle.dumps(black_list_friends)
        self.database.update_binary(
            table_name='social', id=user_id, subject='black_list_friends', subject_value=static)

        user_social = self.database.select(table_name='social', id=user_id)[0]
        request = self.delete_friend({'user_social': user_social, 'friend_id': friend_id})
        return request

    def delete_friend(self, data) -> dict:
        self.database.connect()
        user_social = data.get('user_social')
        friend_id = data.get('friend_id')
        user_id = user_social.get('id')

        friend_social = self.database.select(table_name='social', id=friend_id)[0]

        friends = pickle.loads(user_social.get('friends'))
        for friend in friends:
            if int(friend.get('friend_id')) == int(friend_id):
                del friends[friends.index(friend)]
                if not friends:
                    friends = b'None'
                    break
                friends = pickle.dumps(friends)
                break
        self.database.update_binary(
            table_name='social', id=user_id, subject='friends', subject_value=friends)

        friends = pickle.loads(friend_social.get('friends'))
        for friend in friends:
            if int(friend.get('friend_id')) == int(user_id):
                del friends[friends.index(friend)]
                if not friends:
                    friends = b'None'
                    break
                friends = pickle.dumps(friends)
                break
        self.database.update_binary(
            table_name='social', id=friend_id, subject='friends', subject_value=friends)

        user_social = self.database.select(table_name='social', id=user_id)[0]
        friend_social = self.database.select(table_name='social', id=friend_id)[0]

        self.send_request_if_online(self.form_request(
            '<SET-USER-SOCIAL>',
            {'user_social': friend_social}
        ), friend_id)

        return self.form_request(
            '<SET-USER-SOCIAL>',
            {'user_social': user_social}
        )

    def remove_from_black_list(self, data) -> dict:
        self.database.connect()
        user_social = data.get('user_social')
        friend_id = data.get('friend_id')
        user_id = user_social.get('id')

        black_list = pickle.loads(user_social.get('black_list_friends'))
        for friend in black_list:
            if int(friend.get('friend_id')) == int(friend_id):
                del black_list[black_list.index(friend)]
                if not black_list:
                    black_list = b'None'
                    break
                black_list = pickle.dumps(black_list)
                break
        self.database.update_binary(
            table_name='social', id=user_id, subject='black_list_friends', subject_value=black_list)

        user_social = self.database.select(table_name='social', id=user_id)[0]
        return self.form_request(
            '<SET-USER-SOCIAL>',
            {'user_social': user_social}
        )

    def show_friend_profile(self, data) -> dict:
        self.database.connect()
        friend_id = data.get('friend_id')

        friend_data = self.database.select(table_name='user', id=friend_id)[0]
        friend_pfp_path = self.database.select(
            table_name='social', id=friend_data.get('id'))[0].get('pfp')
        friend_pfp = self.database.load_image(friend_pfp_path)

        return self.form_request('<SHOW-FRIEND-PROFILE>',
                                 {'friend_data': friend_data, 'friend_pfp': friend_pfp})

    def delete_account(self, data) -> dict:
        self.database.connect()
        user_data = data.get('user_data')
        user_id = user_data.get('id')
        user_data['name'] = 'DELETED'
        user_data['password'] = '.'
        user_data['status'] = 'No longer bio'
        user_data['deleted_status'] = 'True'

        user_social = self.database.select(table_name='social', id=user_id)[0]
        pfp_image = self.database.load_image('\\pfp_storage\\deleted.png')
        self.database.save_image(user_social, 'pfp', pfp_image)
        self.change_user_data({'user_data': user_data})

        return self.form_request('<COMPLETE>', {'None': 'None'})

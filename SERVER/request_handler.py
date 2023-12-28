import pickle
from DATABASE.database import Database


class RequestHandler:

    def __init__(self, transport):

        self.methods = {}
        for key, value in RequestHandler.__dict__.items():
            if key[:2] != '__' and key[-2:] != '__':
                self.methods[f"<{key.upper().replace('_', '-')}>"] = key

        self._transport = transport
        self.addr = transport.get_extra_info("peername")
        self.database = Database()
        self.database.connect()

    @staticmethod
    def form_request(method, data):
        return {'method': method, 'data': data}

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
        return self.form_request('<REGISTRATION-SUCCESS>', {'user_data': registered_data})

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
        return self.form_request('<LOGIN-SUCCESS>', {'user_data': user_data})

    def online(self, data) -> dict:
        ...

    def offline(self, data) -> dict:
        ...

    def change_user_data(self, data) -> dict:
        user_data = data.get('user_data')
        for key, value in user_data.items():
            self.database.update(id=user_data.get('id'), subject=key, subject_value=value)
        return self.form_request('<COMPLETE>', {'None': 'None'})

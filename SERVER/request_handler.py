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

    def registration(self, data):
        user_data = data.get('user_data')
        registered_data = self.database.registrate_user(user_data)
        return self.form_request('<REGISTRATION-SUCCESS>', {'registered_data': registered_data})

import pickle
from PyQt6.QtCore import QObject, pyqtSignal


class RequestHandler:

    def __init__(self, transport, main_work):

        self.methods = {}
        for key, value in RequestHandler.__dict__.items():
            if key[:2] != '__' and key[-2:] != '__':
                self.methods[f"<{key.upper().replace('_', '-')}>"] = key

        self._transport = transport
        self._main_work = main_work

    @staticmethod
    def form_request(method: str, data: dict) -> dict:
        """
        Format of request -> {
            method: str
            data: dict
        }
        <- standard request: dict
        """
        return {'method': method, 'data': data}

    def call_method(self, data) -> None:
        method = self.methods.get(data.get('method'))
        getattr(self, method)(data)
        signal = self._main_work.client_window.form_signal(
            method=getattr(self._main_work.client_window, method), data=data.get('data'))
        signal.emit()

    def close_connection(self) -> None:
        self._transport.close()

    def send_request(self, data) -> None:
        self._transport.write(pickle.dumps(data) + b"<END>")

    def registration_success(self, data=None) -> None:
        ...

    def registration_denied(self, data=None) -> None:
        ...

    def login_success(self, data=None) -> None:
        ...

    def login_denied(self, data=None) -> None:
        ...

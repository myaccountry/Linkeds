import sys
import pickle
from asyncio import Protocol, BaseProtocol, BaseTransport
from threading import Thread
from PyQt6 import QtWidgets, QtCore, QtGui, QtMultimediaWidgets, QtMultimedia
from LinkedsMain.CLIENT.request_handler import RequestHandler


class ClientProtocol(Protocol):

    def __init__(self, on_con_lost, main_work):
        self._main_work = main_work
        self.on_con_lost = on_con_lost
        self._transport = None
        self.conn_status = False
        self.current_data = b''
        self.usable_data = None
        self.handler = None

    def connection_made(self, transport: BaseTransport) -> None:
        """
        Saving transport and setting connection status
        """
        self._transport = transport
        self.handler = RequestHandler(self._transport, self._main_work)
        self.conn_status = True

    def connection_lost(self, exc: Exception | None) -> None:
        print('Connection lost')

    def data_received(self, data: bytes) -> None:
        self.current_data += data

        if b'<END>' in self.current_data:
            self.usable_data = self.current_data.replace(b'<END>', b'')
            self.current_data = b''
            self.usable_data = pickle.loads(self.usable_data)
            self.handler.call_method(self.usable_data)

    def send_request(self, data):
        self._transport.write(pickle.dumps(data) + b"<END>")

    def close_connection(self):
        self._transport.close()

    @staticmethod
    def exit_app():
        self._main_work.loop.close()

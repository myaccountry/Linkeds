import pickle
import sys
import pathlib
import asyncio

path = '\\'.join(str(pathlib.Path().resolve()).split('\\')[:-1])
sys.path.insert(0, f'{path}')

from asyncio import Protocol, BaseProtocol
from threading import Thread
from PyQt6 import QtWidgets, QtCore, QtGui, QtMultimediaWidgets, QtMultimedia
from GUI.linkeds_gui import WelcomeWindow, AppWindow
from CLIENT.linkeds_client import ClientProtocol
from CLIENT.client_config import *


class MainWork:
    """
    Class to work between of main Threads
    """
    def __init__(self):
        self.user_data = {
            'id': 'Ожидаем данные',
            'ip': 'Ожидаем данные',
            'online': 'Ожидаем данные',
            'login': 'Ожидаем данные',
            'password': 'Ожидаем данные',
            'gender': 'Ожидаем данные',
            'email': 'Ожидаем данные',
            'name': 'Ожидаем данные',
            'status': 'Ожидаем данные'
        }
        self.client_window = None
        self.protocol = None
        self.app = None
        self.transport = None
        self.loop = None

    def init_welcome_gui(self):
        """
        Initialize GUI, running in another thread
        """
        path = str(pathlib.Path().resolve()) + "\\CACHE"
        with open(path + '\\auto_login.txt', 'r') as file:
            auto_login = file.read().split('\n')

        if auto_login[0] == "False":
            self.app = QtWidgets.QApplication(sys.argv)
            self.client_window = WelcomeWindow(self)
            self.client_window.show()
            sys.exit(self.app.exec())
        else:
            self.user_data['id'] = auto_login[1]
            self.user_data['password'] = auto_login[2]
            self.init_app_gui()

    def init_app_gui(self):
        self.app = QtWidgets.QApplication(sys.argv)
        self.client_window = AppWindow(self, self.user_data)
        self.client_window.show()
        sys.exit(self.app.exec())

    async def init_connection(self):
        """
        Creating loop to connect to the server using asyncio Protocol
        """
        self.loop = asyncio.get_running_loop()
        on_con_lost = self.loop.create_future()

        try:
            self.transport, self.protocol = await self.loop.create_connection(
                lambda: ClientProtocol(on_con_lost, self), SERVER_IP, SERVER_PORT)

            try:
                await on_con_lost
            finally:
                self.transport.close()

        except Exception as error:
            print(error)

    def run_client(self):
        asyncio.run(self.init_connection())


if __name__ == '__main__':
    try:
        main = MainWork()
        welcome_window = Thread(target=main.init_welcome_gui, daemon=True)
        welcome_window.start()
        main.run_client()
    except KeyboardInterrupt:
        main.client_window.init_offline()
        main.client_window.auto_login(True)
        print('App closed')

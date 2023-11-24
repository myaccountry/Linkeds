import sys
from asyncio import Protocol, BaseProtocol
from threading import Thread
from PyQt6 import QtWidgets, QtCore, QtGui, QtMultimediaWidgets, QtMultimedia
from GUI.linkeds_gui import WelcomeWindow
from CLIENT.linkeds_client import ClientProtocol


class MainWork:
    """
    Class to work between of main Threads
    """
    def __init__(self):
        self.welcome_window = None
        self.app = None

    def init_gui(self):
        """
        Initialize GUI, running in another thread
        """
        self.app = QtWidgets.QApplication(sys.argv)
        self.welcome_window = WelcomeWindow(self)
        self.welcome_window.show()
        sys.exit(self.app.exec())

    def init_connection(self):
        ...


if __name__ == '__main__':
    main = MainWork()
    main.init_connection()
    welcome_window = Thread(target=main.init_gui)
    welcome_window.start()

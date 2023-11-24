import sys
from asyncio import Protocol, BaseProtocol
from threading import Thread
from PyQt6 import QtWidgets, QtCore, QtGui, QtMultimediaWidgets, QtMultimedia


class ClientProtocol(Protocol):

    def __init__(self):
        ...

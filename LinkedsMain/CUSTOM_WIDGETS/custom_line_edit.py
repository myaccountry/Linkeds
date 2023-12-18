from PyQt6 import QtWidgets, QtCore, QtGui
import os


class StandardLineEdit(QtWidgets.QLineEdit):

    def __init__(self, text='Введите текст...', *args, **kwargs):
        super(StandardLineEdit, self).__init__(*args, **kwargs)
        self.setObjectName('StandardLineEdit')
        self.setPlaceholderText(text)

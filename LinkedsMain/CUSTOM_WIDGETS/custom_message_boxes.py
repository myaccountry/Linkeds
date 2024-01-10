import time
from PyQt6 import QtWidgets, QtCore, QtGui
import os
import sys


class StandardMessageBox(QtWidgets.QWidget):
    """
    Custom QMessageWindow with standard style
    """
    def __init__(self, icon=None, *args, **kwargs):
        super(StandardMessageBox, self).__init__(*args, **kwargs)

        self.setStyleSheet("""
QWidget {
    background: #262D37;
    font-family: "Calibri";
    font-size: 15px;
    color: #fff;
}
QPushButton {
    color: #ffffff;
    border: 1px solid #ffffff;
    border-radius: 6px;
    font-size: 15px;
    padding: 5px 5px 5px 5px;
    background: #262D37;
}
QPushButton:hover {
    background: #1a232e;
    border: 2px solid #ffffff;
}
QPushButton:pressed {
    background: #13181f;
    border: 2px solid #ffffff;
}
        """)
        self.messageBox = QtWidgets.QMessageBox()
        if icon is not None:
            self.setWindowIcon(QtGui.QIcon(icon))
        self.layout = QtWidgets.QVBoxLayout()
        self.layout.addWidget(self.messageBox)

    def information(self, title='Not Stated', text='Not Stated'):
        self.messageBox.information(self, title, text)

    def warning(self, title='Not Stated', text='Not Stated'):
        self.messageBox.warning(self, title, text)


class YNMessageBox(StandardMessageBox):
    """
    Custom QMessageWindow with standard style
    """
    def __init__(self, icon=None):
        super().__init__()

        self.style_sheet = """
QWidget {
    background: #262D37;
    font-family: "Calibri";
    font-size: 15px;
    color: #fff;
}
QPushButton {
    color: #ffffff;
    border: 1px solid #ffffff;
    border-radius: 6px;
    font-size: 15px;
    padding: 10px 10px 10px 10px;
    margin-left: 20px;
    background: #262D37;
}
QPushButton:hover {
    background: #1a232e;
    border: 2px solid #ffffff;
}
QPushButton:pressed {
    background: #13181f;
    border: 2px solid #ffffff;
}
        """
        self.setStyleSheet(self.style_sheet)
        self.icon = icon
        self.messageBox = QtWidgets.QMessageBox()
        if icon is not None:
            self.setWindowIcon(QtGui.QIcon(icon))
            self.messageBox.setWindowIcon(QtGui.QIcon(self.icon))
        self.messageBox.setIcon(QtWidgets.QMessageBox.Icon.Question)

        self.flag = None
        self.messageBox.setStandardButtons(
            QtWidgets.QMessageBox.StandardButton.Yes | QtWidgets.QMessageBox.StandardButton.No)
        self.yes_btn = self.messageBox.button(QtWidgets.QMessageBox.StandardButton.Yes)
        self.yes_btn.clicked.connect(self.yes_flag)
        self.yes_btn.setText('Да')
        self.no_btn = self.messageBox.button(QtWidgets.QMessageBox.StandardButton.No)
        self.no_btn.clicked.connect(self.no_flag)
        self.no_btn.setText('Нет')

        self.layout = QtWidgets.QVBoxLayout()
        self.layout.addWidget(self.messageBox)

    def yes_flag(self):
        self.flag = 'Yes'

    def no_flag(self):
        self.flag = 'No'

    def question(self, title, text):
        self.messageBox.setStyleSheet(self.style_sheet)
        self.messageBox.setWindowTitle(title)
        self.messageBox.setText(text)
        self.exec()

    def exec(self):
        self.messageBox.exec()

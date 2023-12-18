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




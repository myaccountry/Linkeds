from PyQt6 import QtWidgets, QtCore, QtGui
from LinkedsMain.CUSTOM_WIDGETS.custom_line_edit import StandardLineEdit
from LinkedsMain.CUSTOM_WIDGETS.custom_widgets import ComplimentWidget
import os


class StandardLabel(QtWidgets.QLabel):

    def __init__(self, text='', *args, **kwargs):
        super(StandardLabel, self).__init__(*args, **kwargs)
        self.setObjectName('StandardLabel')
        self.setText(text)


class MenuLabel(StandardLabel):

    def __init__(self, *args, **kwargs):
        super(MenuLabel, self).__init__(*args, **kwargs)


class PixmapLabel(StandardLabel):

    def __init__(self, image_bytes=None, *args, **kwargs):
        super(PixmapLabel, self).__init__(*args, **kwargs)
        if image_bytes is not None:
            with open('static.png', 'wb') as image:
                image.write(image_bytes)
            self.setPixmap(QtGui.QPixmap('static.png').scaled(64, 64, QtCore.Qt.AspectRatioMode.KeepAspectRatio))
            os.remove('static.png')
        self.setText('')


class HeadingLabel(StandardLabel):

    def __init__(self, *args, **kwargs):
        super(HeadingLabel, self).__init__(*args, **kwargs)
        self.setObjectName('HeadingLabel')
        self.setFont(QtGui.QFont('Trebuchet MS'))


class InputLabel(ComplimentWidget):

    def __init__(self, text: str = '', *args, **kwargs):
        super(InputLabel, self).__init__(*args, **kwargs)
        layout = QtWidgets.QVBoxLayout()
        self.setLayout(layout)
        self.label = StandardLabel(text)
        self.input = StandardLineEdit()
        layout.addWidget(self.label)
        layout.addWidget(self.input)
        self.setSizePolicy(
            QtWidgets.QSizePolicy.Policy.MinimumExpanding,
            QtWidgets.QSizePolicy.Policy.MinimumExpanding
        )

    def sizeHint(self):
        return QtCore.QSize(300, 70)

    def setPlaceholderText(self, text='') -> None:
        self.input.setPlaceholderText(text)

    def setText(self, text: str = '') -> None:
        self.label.setText(text)

    def setInputText(self, text: str = '') -> None:
        self.input.setText(text)

    def text(self) -> str:
        return self.input.text()

    def setEchoMode(self, a0):
        self.input.setEchoMode(a0)

    def setMinimumWidth(self, minw: int) -> None:
        self.label.setMinimumWidth(minw)
        self.input.setMinimumWidth(minw)

    def setMinimumHeight(self, minh: int) -> None:
        self.label.setMinimumHeight(minh)
        self.input.setMinimumHeight(minh)

    def setMinimumSize(self, minw: int, minh: int) -> None:
        self.label.setMinimumSize(minw, minh)
        self.input.setMinimumSize(minw, minh)


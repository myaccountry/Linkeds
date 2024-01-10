from PyQt6 import QtWidgets, QtCore, QtGui
from LinkedsMain.CUSTOM_WIDGETS.custom_line_edit import StandardLineEdit
from LinkedsMain.CUSTOM_WIDGETS.custom_widgets import ComplimentWidget
from LinkedsMain.CUSTOM_WIDGETS.custom_buttons import StandardButton
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


class ClickableLabel(StandardLabel):
    def __init__(self, *args, **kwargs):
        super(ClickableLabel, self).__init__(*args, **kwargs)


class ChangeableDataLabel(QtWidgets.QWidget):

    def __init__(self, status, text='', inputText='', inputPlaceholderText='', event=None):
        super().__init__()
        self.setObjectName('StandardWidget')
        self.layout = QtWidgets.QHBoxLayout()
        self.setLayout(self.layout)

        if status == 'LABEL':
            self.label = StandardLabel(text)
            self.label.mousePressEvent = self.showInput
        elif status == 'BUTTON':
            self.label = StandardButton(text)
            self.label.mousePressEvent = self.showInput

        self.input = StandardLineEdit(inputText)
        self.input.setText(inputPlaceholderText)
        self.confirm_button = StandardButton('OK')
        self.confirm_button.clicked.connect(self.hideInput)
        self.event_object = event

        self.inputText = ''

        self.layout.addWidget(self.label)
        self.layout.addWidget(self.input)
        self.layout.addWidget(self.confirm_button)
        self.input.hide()
        self.confirm_button.hide()

    def showInput(self, *args, **kwargs):
        self.label.hide()
        self.input.show()
        self.confirm_button.show()

    def hideInput(self):
        self.label.show()
        self.inputText = self.input.text()
        self.input.hide()
        self.confirm_button.hide()
        self.event_object()

    def setPlaceHolderText(self, text='') -> None:
        self.input.setPlaceholderText(text)

    def setLabelText(self, text='') -> None:
        self.label.setText(text)

    def setInputText(self, text='') -> None:
        self.input.setText(text)

    def connectConfirmButton(self, a0) -> None:
        self.event_object = a0

    def text(self) -> str:
        return self.inputText

from PyQt6 import QtWidgets, QtCore, QtGui


class StandardWidget(QtWidgets.QWidget):

    def __init__(self):
        # super(StandardWidget, self).__init__(*args, **kwargs)
        super().__init__()
        self.setObjectName('StandardWidget')

    def setBackgroundColor(self, color: str) -> None:
        self.setStyleSheet(color)


class MainWindowWidget(QtWidgets.QWidget):

    def __init__(self, *args, **kwargs):
        super(MainWindowWidget, self).__init__(*args, **kwargs)
        self.setObjectName('MainWindowWidget')


class ComplimentWidget(StandardWidget):

    def __init__(self, *args, **kwargs):
        super(ComplimentWidget, self).__init__(*args, **kwargs)
        self.setObjectName('ComplimentWidget')


class MenuWidget(StandardWidget):

    def __init__(self, *args, **kwargs):
        super(MenuWidget, self).__init__(*args, **kwargs)
        self.setObjectName('MenuWidget')
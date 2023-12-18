from PyQt6 import QtWidgets, QtCore, QtGui


class StandardWidget(QtWidgets.QWidget):

    def __init__(self, *args, **kwargs):
        super(StandardWidget, self).__init__(*args, **kwargs)
        self.setObjectName('StandardWidget')


class MainWindowWidget(StandardWidget):

    def __init__(self, *args, **kwargs):
        super(MainWindowWidget, self).__init__(*args, **kwargs)
        self.setObjectName('MainWindowWidget')


class ComplimentWidget(StandardWidget):

    def __init__(self, *args, **kwargs):
        super(ComplimentWidget, self).__init__(*args, **kwargs)
        self.setObjectName('ComplimentWidget')


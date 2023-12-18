from PyQt6 import QtWidgets, QtCore, QtGui
import os


class StandardButton(QtWidgets.QPushButton):
    """
    Custom PushButton with standard style
    """
    def __init__(self, text=None, *args, **kwargs):
        super(StandardButton, self).__init__(*args, **kwargs)

        self.setObjectName('StandardButton')

        if text is not None:
            self.setText(text)


class MenuButton(StandardButton):
    """
    Menu button which inherits Standard Button and change it
    """
    def __init__(self, *args, **kwargs):
        super(MenuButton, self).__init__(*args, **kwargs)


class BorderlessButton(StandardButton):
    """
    Borderless button which inherits Standard Button and change it
    """
    def __init__(self, *args, **kwargs):
        super(BorderlessButton, self).__init__(*args, **kwargs)
        self.setObjectName('BorderlessButton')


class DangerButton(StandardButton):
    """
    Borderless button which inherits Standard Button and change it
    """
    def __init__(self, *args, **kwargs):
        super(DangerButton, self).__init__(*args, **kwargs)
        self.setObjectName('ExitButton')

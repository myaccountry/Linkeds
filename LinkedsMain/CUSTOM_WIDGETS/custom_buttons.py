from PyQt6 import QtWidgets, QtCore, QtGui
import os
import functools


class StandardButton(QtWidgets.QPushButton):
    """
    Custom PushButton with standard style
    """
    def __init__(self, text=None, *args, **kwargs):
        super().__init__()

        self.setObjectName('StandardButton')

        if text is not None:
            self.setText(text)


class MenuButton(StandardButton):
    """
    Menu button which inherits Standard Button and change it
    """
    def __init__(self, *args, **kwargs):
        super(MenuButton, self).__init__(*args, **kwargs)
        self.setObjectName('MenuButton')
        self.x = 150
        self.y = 65
        self.setIconSize(QtCore.QSize(25, 25))
        self.setMinimumSize(self.x, self.y)
        self.resize(self.x, self.y)

        self.anim_size_up = QtCore.QPropertyAnimation(self, b"size")
        self.anim_size_up.setEndValue(QtCore.QSize(self.x + 25, self.y))
        self.anim_size_up.setDuration(100)
        self.anim_size_up.finished.connect(functools.partial(self.animEnd, 'up'))

        self.anim_size_down = QtCore.QPropertyAnimation(self, b"size")
        self.anim_size_down.setEasingCurve(QtCore.QEasingCurve.Type.OutBounce)
        self.anim_size_down.setEndValue(QtCore.QSize(self.x, self.y))
        self.anim_size_down.setDuration(500)
        self.anim_size_down.finished.connect(functools.partial(self.animEnd, 'down'))

        self.setSizePolicy(
            QtWidgets.QSizePolicy.Policy.MinimumExpanding,
            QtWidgets.QSizePolicy.Policy.MinimumExpanding
        )
        self.adjustSize()
        self.anim_size_down.start()

    def focusInEvent(self, a0) -> None:
        super().focusInEvent(a0)
        self.anim_size_up.start()

    def focusOutEvent(self, a0) -> None:
        super().focusOutEvent(a0)
        self.anim_size_down.start()

    def animEnd(self, status):
        if status == 'down':
            self.resize(self.x, self.y)
        if status == 'up':
            self.resize(self.x + 25, self.y)


class MenuExitButton(StandardButton):
    """
    Menu exit button which inherits Standard Button and change it
    """
    def __init__(self, *args, **kwargs):
        super(MenuExitButton, self).__init__(*args, **kwargs)
        self.setObjectName('MenuButton')
        self.setIconSize(QtCore.QSize(25, 25))
        self.setMinimumSize(50, 50)


class BorderlessButton(StandardButton):
    """
    Borderless button which inherits Standard Button and change it
    """
    def __init__(self):
        super().__init__()
        self.setObjectName('BorderlessButton')


class DangerButton(StandardButton):
    """
    Borderless button which inherits Standard Button and change it
    """
    def __init__(self, *args, **kwargs):
        super(DangerButton, self).__init__(*args, **kwargs)
        self.setObjectName('ExitButton')

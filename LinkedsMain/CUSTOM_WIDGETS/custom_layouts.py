from PyQt6 import QtWidgets, QtCore, QtGui
from LinkedsMain.CUSTOM_WIDGETS.custom_widgets import StandardWidget
import typing


class StandardVLayout(QtWidgets.QVBoxLayout):

    def __init__(self, *args, **kwargs):
        super(StandardVLayout, self).__init__(*args, **kwargs)
        self.setObjectName('StandardVLayout')


class StandardHLayout(QtWidgets.QHBoxLayout):

    def __init__(self, *args, **kwargs):
        super(StandardHLayout, self).__init__(*args, **kwargs)
        self.setObjectName('StandardHLayout')


class LayoutWidget(QtWidgets.QWidget):

    def __init__(self, orientation: bool = True, *args, **kwargs):
        """
        Orientation is What layout will be used as the basis
        True - StandardVLayout
        False - StandardHLayout
        """
        super(LayoutWidget, self).__init__(*args, **kwargs)
        if orientation:
            self.layout = StandardVLayout()
        else:
            self.layout = StandardHLayout()
        self.setLayout(self.layout)

    def addWidget(self, a0, stretch=0, alignment=None) -> None:
        if alignment is None:
            self.layout.addWidget(a0, stretch)
        else:
            self.layout.addWidget(a0, stretch, alignment)

    def addSpacing(self, size: int = 10) -> None:
        self.layout.addSpacing(size)

    def addStretch(self, stretch: int = 1) -> None:
        self.layout.addStretch(stretch)

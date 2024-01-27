from PyQt6 import QtWidgets, QtCore, QtGui
from LinkedsMain.CUSTOM_WIDGETS.custom_widgets import StandardWidget
import typing


class StandardVLayout(QtWidgets.QVBoxLayout):

    def __init__(self, *args, **kwargs):
        super(StandardVLayout, self).__init__(*args, **kwargs)
        self.setObjectName('StandardVLayout')
        self.setContentsMargins(0, 0, 0, 0)


class StandardHLayout(QtWidgets.QHBoxLayout):

    def __init__(self, *args, **kwargs):
        super(StandardHLayout, self).__init__(*args, **kwargs)
        self.setObjectName('StandardHLayout')
        self.setContentsMargins(0, 0, 0, 0)


class LayoutWidget(QtWidgets.QFrame):

    def __init__(self, orientation: bool = True, *args, **kwargs):
        """
        Orientation is What layout will be used as the basis
        True - StandardVLayout
        False - StandardHLayout
        """
        super(LayoutWidget, self).__init__(*args, **kwargs)
        self.setContentsMargins(0, 0, 0, 0)
        if orientation:
            self.layout = StandardVLayout()
        else:
            self.layout = StandardHLayout()
        self.setLayout(self.layout)

    def addShadow(self, rgb=(255, 255, 255)):
        shadow = QtWidgets.QGraphicsDropShadowEffect()
        shadow.setBlurRadius(10)
        shadow.setColor(QtGui.QColor(rgb[0], rgb[1], rgb[2]))
        shadow.setXOffset(0)
        shadow.setYOffset(0)

        self.setGraphicsEffect(shadow)

    def addWidget(self, a0, stretch=0, alignment=None) -> None:
        if alignment is None:
            self.layout.addWidget(a0, stretch)
        else:
            self.layout.addWidget(a0, stretch, alignment)

    def addSpacing(self, size: int = 10) -> None:
        self.layout.addSpacing(size)

    def addStretch(self, stretch: int = 1) -> None:
        self.layout.addStretch(stretch)

import pathlib
import pickle
import sys
import pathlib
import hashlib
import functools
import time
from asyncio import Protocol, BaseProtocol
from threading import Thread

from PyQt6 import QtWidgets, QtCore, QtGui
from PyQt6.QtCore import pyqtSlot
from PyQt6 import QtWidgets, QtCore, QtGui, QtMultimediaWidgets, QtMultimedia
from LinkedsMain.CLIENT.CFIE import User
from LinkedsMain.CUSTOM_WIDGETS.custom_buttons import StandardButton, BorderlessButton, DangerButton, MenuButton, \
    MenuExitButton
from LinkedsMain.CUSTOM_WIDGETS.custom_widgets import StandardWidget, MainWindowWidget
from LinkedsMain.CUSTOM_WIDGETS.custom_labels import StandardLabel, PixmapLabel, HeadingLabel, InputLabel, \
    ClickableLabel, ChangeableDataLabel
from LinkedsMain.CUSTOM_WIDGETS.custom_message_boxes import StandardMessageBox, YNMessageBox
from LinkedsMain.CUSTOM_WIDGETS.custom_line_edit import StandardLineEdit
from LinkedsMain.CUSTOM_WIDGETS.custom_layouts import StandardHLayout, StandardVLayout, LayoutWidget
from LinkedsMain.CUSTOM_WIDGETS.custom_frames import FriendsFrame, MessengerFrame

style_path = str(pathlib.Path().resolve()) + "\\CUSTOM_WIDGETS\\STYLES"
with open(f'{style_path}\\dark_theme.сss', 'r') as style:
    DARK_THEME_STYLE = style.read()
with open(f'{style_path}\\light_theme.сss', 'r') as style:
    LIGHT_THEME_STYLE = style.read()


class SignalHandler(QtCore.QObject):
    signal = QtCore.pyqtSignal()


class RegLogWindow(StandardWidget):

    def __init__(self, main_work):
        """
        Init block with GUI
        """
        super().__init__()
        self.main_work = main_work

        self.theme = 'DARK'
        self.form = 'REG'
        self.main_work.app.setStyleSheet(DARK_THEME_STYLE)

        self.init_images()

        self.setWindowTitle("Linkeds - Регистрация")
        self.setWindowIcon(QtGui.QIcon(self.logo_image))

        self.init_ui()

    def init_images(self):
        path = str(pathlib.Path().resolve()) + "\\IMAGES"
        self.logo_image = QtGui.QPixmap(f"{path}\\icon_photo.png")
        self.chat_dark = QtGui.QIcon(f"{path}\\chat_dark.png")
        self.chat_light = QtGui.QIcon(f"{path}\\chat_light.png")
        self.theme_dark = QtGui.QIcon(f"{path}\\theme_dark.png")
        self.theme_light = QtGui.QIcon(f"{path}\\theme_light.png")
        self.friends_dark = QtGui.QIcon(f"{path}\\add_user_dark.png")
        self.friends_light = QtGui.QIcon(f"{path}\\add_user_light.png")
        self.profile_light = QtGui.QIcon(f"{path}\\home_light.png")
        self.profile_dark = QtGui.QIcon(f"{path}\\home_dark.png")
        self.settings_light = QtGui.QIcon(f"{path}\\settings_light.png")
        self.settings_dark = QtGui.QIcon(f"{path}\\settings_dark.png")
        self.exit_light = QtGui.QIcon(f"{path}\\exit_light.png")
        self.exit_dark = QtGui.QIcon(f"{path}\\exit_dark.png")
        self.hideMenu_light = QtGui.QIcon(f"{path}\\hide_menu_light.png")
        self.hideMenu_dark = QtGui.QIcon(f"{path}\\hide_menu_dark.png")
        self.showMenu_light = QtGui.QIcon(f"{path}\\show_menu_light.png")
        self.showMenu_dark = QtGui.QIcon(f"{path}\\show_menu_dark.png")

        try:
            static = open("images/pfp_image.png", 'rb')
            static.close()
            self.userPfp_image = QtGui.QPixmap("images/pfp_image.png").scaled(180, 180)
            self.userPfp_image = self.round_image(self.userPfp_image)
        except FileNotFoundError:
            self.userPfp_image = QtGui.QPixmap("images/pfp_image_standard.png").scaled(180, 180)
            self.userPfp_image = self.round_image(self.userPfp_image)

    def init_ui(self):

        self.layout = QtWidgets.QVBoxLayout()
        self.setLayout(self.layout)

        self.title_widget = StandardWidget()
        self.title_layout = QtWidgets.QHBoxLayout()
        self.title_widget.setLayout(self.title_layout)
        self.title_label = HeadingLabel('\nLinkeds')
        self.title_icon = StandardLabel()
        self.title_icon.setPixmap(self.logo_image.scaled(64, 64))
        self.changeTheme_button = BorderlessButton()
        self.changeTheme_button.setIcon(QtGui.QIcon(self.theme_dark))
        self.changeTheme_button.setIconSize(QtCore.QSize(40, 40))
        self.changeTheme_button.clicked.connect(lambda: self.change_theme_button(self.theme))

        self.title_layout.addWidget(self.title_icon)
        self.title_layout.addWidget(self.title_label)
        self.title_layout.addStretch(1)
        self.title_layout.addWidget(self.changeTheme_button)

        self.userData_widget = StandardWidget()
        self.userData_layout = QtWidgets.QVBoxLayout()
        self.userData_widget.setLayout(self.userData_layout)
        self.login_label = InputLabel("Логин")
        self.login_label.setPlaceholderText("Введите логин...")
        self.password_label = InputLabel("Пароль")
        self.password_label.setPlaceholderText("Введите пароль...")
        self.password_label.setEchoMode(QtWidgets.QLineEdit.EchoMode.Password)
        self.email_label = InputLabel("Эл.Почта")
        self.email_label.setPlaceholderText("Введите эл.почту...")

        self.userData_layout.addWidget(self.login_label)
        self.userData_layout.addWidget(self.password_label)
        self.userData_layout.addWidget(self.email_label)

        self.logReg_button = StandardButton('Зарегистрироваться')
        self.logReg_button.clicked.connect(self.registration)
        self.logReg_button.setMinimumHeight(30)

        self.logRegForm_layout = QtWidgets.QHBoxLayout()
        self.logRegForm_widget = StandardWidget()
        self.logRegForm_widget.setLayout(self.logRegForm_layout)
        self.logRegForm_label = StandardLabel('Есть Аккаунт?')
        self.logRegForm_label.setMinimumHeight(30)
        self.logRegForm_button = StandardButton('Войти')
        self.logRegForm_button.clicked.connect(lambda: self.changeForm(self.form))
        self.logRegForm_button.setMinimumHeight(30)
        self.logRegForm_layout.addWidget(self.logRegForm_label)
        self.logRegForm_layout.addWidget(self.logRegForm_button)

        self.exit_button = DangerButton('Выйти')
        self.exit_button.clicked.connect(self.closeEvent)
        self.exit_button.setMinimumHeight(30)

        self.layout.addWidget(self.title_widget)
        self.layout.addWidget(self.userData_widget)
        self.layout.addWidget(self.logReg_button)
        self.layout.addStretch(1)
        self.layout.addWidget(self.logRegForm_widget)
        self.layout.addWidget(self.exit_button)

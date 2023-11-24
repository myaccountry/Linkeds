import sys
import pathlib
from asyncio import Protocol, BaseProtocol
from threading import Thread
from PyQt6 import QtWidgets, QtCore, QtGui, QtMultimediaWidgets, QtMultimedia
from LinkedsMain.CUSTOM_WIDGETS.custom_buttons import StandardButton, BorderlessButton
from LinkedsMain.CUSTOM_WIDGETS.custom_widgets import StandardWidget, MainWindowWidget
from LinkedsMain.CUSTOM_WIDGETS.custom_labels import StandardLabel, PixmapLabel, HeadingLabel, InputLabel

style_path = str(pathlib.Path().resolve()) + "\\CUSTOM_WIDGETS\\STYLES"
with open(f'{style_path}\\dark_theme.css', 'r') as style:
    DARK_THEME_STYLE = style.read()
with open(f'{style_path}\\light_theme.css', 'r') as style:
    LIGHT_THEME_STYLE = style.read()


class WelcomeWindow(StandardWidget):
    """
    Window to registrate new users or login in system
    """
    def __init__(self, main_work):
        """
        Init block with GUI
        """
        super().__init__()
        self.main_work = main_work
        self.theme = 'DARK'
        self.main_work.app.setStyleSheet(DARK_THEME_STYLE)

        self.setWindowTitle("Регистрация")
        self.setMinimumSize(400, 550)

        self.init_images()
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
        self.main_widget = MainWindowWidget()
        self.layout.addWidget(self.main_widget)

        self.main_layout = QtWidgets.QGridLayout()

        self.title_label = HeadingLabel('\nLinkeds')
        self.title_icon = StandardLabel()
        self.title_icon.setPixmap(self.logo_image.scaled(64, 64))

        self.changeTheme_button = BorderlessButton()
        self.changeTheme_button.setIcon(QtGui.QIcon(self.theme_dark))
        self.changeTheme_button.setIconSize(QtCore.QSize(40, 40))
        self.changeTheme_button.clicked.connect(lambda: self.change_theme_button(self.theme))

        self.userData_widget = MainWindowWidget()
        self.userData_layout = QtWidgets.QGridLayout()
        self.userData_widget.setLayout(self.userData_layout)
        self.login_label = InputLabel("Логин")
        self.login_label.setMinimumHeight(30)
        self.password_label = InputLabel("Пароль")
        self.password_label.setMinimumHeight(30)
        self.email_label = InputLabel("Эл.Почта")
        self.email_label.setMinimumHeight(30)
        self.userData_layout.addWidget(self.login_label, 0, 0)
        self.userData_layout.addWidget(self.password_label, 1, 0)
        self.userData_layout.addWidget(self.email_label, 2, 0)

        self.registration_button = StandardButton('Зарегистрироваться')
        self.registration_button.setMinimumHeight(30)

        self.main_layout.addWidget(self.title_icon, 0, 0)
        self.main_layout.addWidget(self.title_label, 0, 1)
        self.main_layout.setColumnStretch(2, 1)
        self.main_layout.addWidget(self.changeTheme_button, 0, 3)
        self.main_layout.addWidget(self.userData_widget, 3, 0, 2, 0)
        self.main_layout.setRowStretch(7, 1)
        self.main_layout.addWidget(self.registration_button, 8, 0, 2, 0)

        self.main_widget.setLayout(self.main_layout)


    def change_theme_button(self, theme):
        if theme == 'DARK':
            self.main_work.app.setStyleSheet(LIGHT_THEME_STYLE)
            self.changeTheme_button.setIcon(QtGui.QIcon((self.theme_light)))
            self.theme = 'LIGHT'
        if theme == 'LIGHT':
            self.main_work.app.setStyleSheet(DARK_THEME_STYLE)
            self.changeTheme_button.setIcon(QtGui.QIcon((self.theme_dark)))
            self.theme = 'DARK'

    @staticmethod
    def round_image(image):
        rounded = QtGui.QPixmap(image.size())
        rounded.fill(QtGui.QColor("transparent"))
        painter = QtGui.QPainter(rounded)
        painter.setBrush(QtGui.QBrush(image))
        painter.drawRoundedRect(image.rect(), 100, 100)
        return rounded


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


class MainWindowGui(MainWindowWidget):

    def __init__(self, main_work, user_data):
        super().__init__()
        self.user_data = user_data
        self.main_work = main_work
        self.user_social = None

        self.current_window = 'PROFILE'
        self.current_friend_window = 'FRIENDS-LIST'
        self.current_chat_flag = False
        self.current_chat = 'None'
        self.theme = 'DARK'
        self.setStyleSheet(DARK_THEME_STYLE)
        self.setObjectName('MainWindowWidget')

        self.shadow = QtWidgets.QGraphicsDropShadowEffect()
        self.shadow.setBlurRadius(10)
        self.shadow.setColor(QtGui.QColor(255, 255, 255))
        self.shadow.setXOffset(0)
        self.shadow.setYOffset(0)

        self.init_images()

        self.setWindowTitle('Linkeds - Главный Экран')
        self.setWindowIcon(QtGui.QIcon(self.logo_image))
        self.setMinimumSize(600, 450)
        self.resize(1200, 700)

        self.init_gui()
        self.init_online()
        self.user_data['online'] = 'True'
        self.auto_login(True)

    def init_images(self) -> None:
        path = str(pathlib.Path().resolve()) + "\\IMAGES"
        self.logo_image = QtGui.QPixmap(f"{path}\\icon_photo.png").scaled(120, 120, QtCore.Qt.AspectRatioMode.KeepAspectRatio)
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
        self.sendMessage_image = QtGui.QIcon(f"{path}\\send_message.png")

        try:
            static = open("images/pfp_image.png", 'rb')
            static.close()
            self.userPfp_image = QtGui.QPixmap("images/pfp_image.png").scaled(225, 225)
            self.userPfp_image = self.round_image(self.userPfp_image)
        except FileNotFoundError:
            self.userPfp_image = QtGui.QPixmap("images/pfp_image_standard.png").scaled(225, 225)
            self.userPfp_image = self.round_image(self.userPfp_image)

    def init_gui(self) -> None:
        self.clearFocus()
        self.widget = StandardWidget()
        self.setCentralWidget(self.widget)
        self.layout = StandardHLayout()
        self.widget.setLayout(self.layout)

        # -- MENU --- RISE --
        self.menu_widget = LayoutWidget(orientation=True)
        self.menu_widget.setFixedWidth(175)
        self.menu_widget.setObjectName('MenuWidget')

        self.logo_label = StandardLabel()
        self.logo_label.setPixmap(self.logo_image)
        self.logo_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignHCenter)

        self.menuButtons_widget = LayoutWidget(orientation=True)

        self.profile_button = MenuButton('Профиль')
        self.profile_button.setIcon(self.profile_light)
        self.profile_button.clicked.connect(lambda: self.changeWindowFrame('PROFILE'))

        self.messenger_button = MenuButton('Мессенджер')
        self.messenger_button.setIcon(self.chat_light)
        self.messenger_button.clicked.connect(lambda: self.changeWindowFrame('MESSENGER'))

        self.friends_button = MenuButton('Друзья')
        self.friends_button.setIcon(self.friends_light)
        self.friends_button.clicked.connect(lambda: self.changeWindowFrame('FRIENDS'))

        self.settings_button = MenuButton('Настройки')
        self.settings_button.setIcon(self.settings_light)
        self.settings_button.clicked.connect(lambda: self.changeWindowFrame('SETTINGS'))

        self.exit_button = MenuExitButton('Выйти')
        self.exit_button.setIcon(self.exit_light)
        self.exit_button.clicked.connect(self.closeEvent)

        self.menuButtons_widget.addSpacing(25)
        self.menuButtons_widget.addWidget(self.profile_button)
        self.menuButtons_widget.addSpacing(25)
        self.menuButtons_widget.addStretch(2)
        self.menuButtons_widget.addWidget(self.messenger_button)
        self.menuButtons_widget.addSpacing(25)
        self.menuButtons_widget.addStretch(2)
        self.menuButtons_widget.addWidget(self.friends_button)
        self.menuButtons_widget.addSpacing(25)
        self.menuButtons_widget.addStretch(2)
        self.menuButtons_widget.addWidget(self.settings_button)
        self.menuButtons_widget.addSpacing(25)

        self.menu_widget.addWidget(self.logo_label)
        self.menu_widget.addWidget(self.menuButtons_widget)
        self.menu_widget.addStretch(1)
        self.menu_widget.addWidget(self.exit_button)
        self.menu_widget.addSpacing(25)
        # -- MENU --- END --

        # -- WINDOW --- RISE --
        self.windowFrame_widget = LayoutWidget()

        # -- PROFILE --- RISE --
        self.profile_widget = LayoutWidget()
        self.profile_widget.setObjectName('WindowFrameWidget')

        self.profilePfp_label = StandardLabel()
        self.profilePfp_label.setFixedWidth(350)
        self.profilePfp_label.setPixmap(self.userPfp_image)
        self.profilePfp_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignHCenter)
        self.profilePfp_label.mousePressEvent = self.changePfp

        self.profileInfo_widget = LayoutWidget(orientation=False)
        self.profileInfoId_label = StandardLabel(f'ID: {self.user_data.get("id")}')
        self.profileInfoLogin_label = StandardLabel(f'Login: {self.user_data.get("login")}')
        self.profileInfoId_label.setObjectName('BorderLabel')
        self.profileInfoLogin_label.setObjectName('BorderLabel')
        self.profileInfo_widget.addWidget(self.profileInfoId_label)
        self.profileInfo_widget.addWidget(self.profileInfoLogin_label)

        self.profileMainInfo_widget = LayoutWidget(False)
        self.profileMainInfo_widget.addShadow()
        self.profileMainInfo_widget.setObjectName('FrameWidget')

        self.profileMainInfoData_widget = LayoutWidget(orientation=True)
        self.profileMainInfoData_widget.addShadow()
        self.profileMainInfoData_widget.setObjectName('FrameWidget')

        self.profileMainInfoName_widget = LayoutWidget(orientation=False)
        self.name_input = StandardLineEdit('Введите новое имя...')
        self.confirmName_button = StandardButton('OK')
        self.profileName = StandardLabel(f'{self.user_data.get("name")}')
        self.profileName.setObjectName('BorderLabel')
        self.profileName.mousePressEvent = self.changeNameForm
        self.profileMainInfoName_widget.addWidget(self.name_input)
        self.profileMainInfoName_widget.addWidget(self.confirmName_button)
        self.profileMainInfoName_widget.addWidget(self.profileName)
        self.name_input.hide()
        self.confirmName_button.hide()

        self.profileMainInfoStatus_widget = LayoutWidget(orientation=False)
        self.status_input = StandardLineEdit('Введите новый статус...')
        self.confirmStatus_button = StandardButton('OK')
        self.profileStatus = StandardLabel(f'{self.user_data.get("status")}')
        self.profileStatus.setObjectName('BorderLabel')
        self.profileStatus.mousePressEvent = self.changeStatusForm
        self.profileMainInfoStatus_widget.addWidget(self.status_input)
        self.profileMainInfoStatus_widget.addWidget(self.confirmStatus_button)
        self.profileMainInfoStatus_widget.addWidget(self.profileStatus)
        self.status_input.hide()
        self.confirmStatus_button.hide()

        self.profileMainInfoData_widget.addWidget(self.profileMainInfoName_widget)
        self.profileMainInfoData_widget.addWidget(self.profileMainInfoStatus_widget)
        self.profileMainInfoData_widget.addStretch(1)

        self.profileMainInfo_widget.addWidget(self.profilePfp_label)
        self.profileMainInfo_widget.addWidget(self.profileMainInfoData_widget)

        self.profile_widget.addWidget(self.profileInfo_widget)
        self.profile_widget.addSpacing(50)
        self.profile_widget.addWidget(self.profileMainInfo_widget)
        self.profile_widget.addStretch(1)
        # -- PROFILE --- END --

        # -- MESSENGER --- RISE --
        self.messenger_widget = LayoutWidget()
        self.messenger_widget.setObjectName('WindowFrameWidget')

        self.messengerContent_widget = LayoutWidget()

        self.messengerChat_frame = LayoutWidget()
        self.chatButtons_frame = MessengerFrame(self)

        self.messengerContent_widget.addWidget(self.chatButtons_frame)
        self.messengerContent_widget.addWidget(self.messengerChat_frame)

        self.messenger_widget.addWidget(self.messengerContent_widget)
        # -- MESSENGER --- END --

        # -- FRIENDS --- RISE --
        self.friends_widget = LayoutWidget()
        self.friends_widget.setObjectName('WindowFrameWidget')

        self.addFriend_input = InputLabel('Добавить друга')
        self.addFriend_input.setPlaceholderText('Введите ID или Логин друга, которого хотите добавить...')
        self.confirmAddFriend_button = StandardButton('Отправить запрос дружбы')
        self.confirmAddFriend_button.clicked.connect(self.add_friend)

        self.friendsFramesButtons_widget = LayoutWidget(orientation=False)
        self.showFriendsFrame_button = StandardButton('Друзья')
        self.showFriendsFrame_button.clicked.connect(lambda: self.changeWindowFrame('FRIENDS-LIST'))
        self.showFriendsRequestsFrame_button = StandardButton('Заявки в друзья')
        self.showFriendsRequestsFrame_button.clicked.connect(lambda: self.changeWindowFrame('FRIENDS-REQUESTS-LIST'))
        self.showBlackListFriendsFrame_button = StandardButton('Чёрный список')
        self.showBlackListFriendsFrame_button.clicked.connect(lambda: self.changeWindowFrame('FRIENDS-BLACK-LIST'))
        self.friendsFramesButtons_widget.addWidget(self.showFriendsFrame_button)
        self.friendsFramesButtons_widget.addWidget(self.showFriendsRequestsFrame_button)
        self.friendsFramesButtons_widget.addWidget(self.showBlackListFriendsFrame_button)

        self.friendsFrame_widget = FriendsFrame(self)
        self.friendProfile_widget = LayoutWidget()

        self.friendsRequestsFrame_widget = FriendsFrame(self)
        self.friendsBlackListFrame_widget = FriendsFrame(self)

        self.friends_widget.addWidget(self.addFriend_input)
        self.friends_widget.addWidget(self.confirmAddFriend_button)
        self.friends_widget.addWidget(self.friendsFramesButtons_widget, 0, QtCore.Qt.AlignmentFlag.AlignHCenter)
        self.friends_widget.addWidget(self.friendsFrame_widget, 1)
        self.friends_widget.addWidget(self.friendsRequestsFrame_widget, 1)
        self.friends_widget.addWidget(self.friendsBlackListFrame_widget, 1)
        # -- FRIENDS --- END --

        # -- SETTINGS --- RISE --
        self.settings_widget = LayoutWidget()
        self.settings_widget.setObjectName('WindowFrameWidget')

        self.changeLogin_button = ChangeableDataLabel('BUTTON',
                                                      'Сменить логин', 'Введите новый логин...',
                                                      self.user_data.get('login'), self.changeLogin)
        self.changePasswordForm_button = ChangeableDataLabel('BUTTON',
                                                             'Сменить пароль', 'Введите новый пароль...', '',
                                                             self.changePassword)
        self.changePasswordForm_button.input.setEchoMode(QtWidgets.QLineEdit.EchoMode.Password)
        self.changeIdForm_button = ChangeableDataLabel('BUTTON',
                                                       'Запрос на смену ID', 'Введите новый ID...',
                                                       str(self.user_data.get('id')), self.changeID)

        self.logout_button = DangerButton('Разлогиниться')
        self.logout_button.setIcon(self.exit_light)
        self.logout_button.clicked.connect(self.logout)

        self.deleteAccount_button = DangerButton('Удалить аккаунт')
        self.deleteAccount_button.clicked.connect(self.delete_account)

        self.callError_button = DangerButton('Вызвать ошибку')
        self.callError_button.setIcon(QtGui.QIcon(self.userPfp_image.scaled(25, 25)))
        self.callError_button.clicked.connect(lambda: self.windowFrame_widget.addRofls())

        self.settings_widget.addWidget(self.changeLogin_button)
        self.settings_widget.addWidget(self.changePasswordForm_button)
        self.settings_widget.addWidget(self.changeIdForm_button)
        self.settings_widget.addWidget(self.deleteAccount_button)
        self.settings_widget.addWidget(self.callError_button)
        self.settings_widget.addStretch(1)
        self.settings_widget.addWidget(self.logout_button)
        # -- SETTINGS --- END --

        self.windowFrame_widget.addWidget(self.profile_widget)
        self.windowFrame_widget.addWidget(self.messenger_widget)
        self.windowFrame_widget.addWidget(self.friends_widget)
        self.windowFrame_widget.addWidget(self.settings_widget)

        self.changeWindowFrame(self.current_window)
        self.changeWindowFrame(self.current_friend_window)
        # -- WINDOW --- END --

        self.context_menu = QtWidgets.QMenu(self)
        self.context_menu.setObjectName('StandardMenu')
        # MAKE STYLE SHEET
        action1 = self.context_menu.addAction("Сменить тему")
        action2 = self.context_menu.addAction("Закрыть приложение")

        action1.triggered.connect(lambda: self.action1_triggered(self.theme))
        action2.triggered.connect(self.action2_triggered)

        self.layout.addWidget(self.menu_widget)
        self.layout.addWidget(self.windowFrame_widget)
        self.widget.show()

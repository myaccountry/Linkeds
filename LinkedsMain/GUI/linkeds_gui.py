import pickle
import sys
import pathlib
import hashlib
import functools
from asyncio import Protocol, BaseProtocol
from threading import Thread
from LinkedsMain.CLIENT.CFIE import User
from PyQt6 import QtWidgets, QtCore, QtGui, QtMultimediaWidgets, QtMultimedia
from PyQt6.QtCore import pyqtSlot
from LinkedsMain.CUSTOM_WIDGETS.custom_buttons import StandardButton, BorderlessButton, DangerButton, MenuButton, \
    MenuExitButton
from LinkedsMain.CUSTOM_WIDGETS.custom_widgets import StandardWidget, MainWindowWidget
from LinkedsMain.CUSTOM_WIDGETS.custom_labels import StandardLabel, PixmapLabel, HeadingLabel, InputLabel, \
    ClickableLabel
from LinkedsMain.CUSTOM_WIDGETS.custom_message_boxes import StandardMessageBox
from LinkedsMain.CUSTOM_WIDGETS.custom_line_edit import StandardLineEdit
from LinkedsMain.CUSTOM_WIDGETS.custom_layouts import StandardHLayout, StandardVLayout, LayoutWidget

if __name__ == '__main__':
    print('Do not run from NotMain application')
    exit()

style_path = str(pathlib.Path().resolve()) + "\\CUSTOM_WIDGETS\\STYLES"
with open(f'{style_path}\\dark_theme.сss', 'r') as style:
    DARK_THEME_STYLE = style.read()
with open(f'{style_path}\\light_theme.сss', 'r') as style:
    LIGHT_THEME_STYLE = style.read()


class SignalHandler(QtCore.QObject):
    signal = QtCore.pyqtSignal()


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

    def changeForm(self, form):
        if form == 'REG':
            self.email_label.hide()
            self.setWindowTitle('Linkeds - Вход в Аккаунт')
            self.logReg_button.setText('Войти в Аккаунт')
            self.logReg_button.disconnect()
            self.logReg_button.clicked.connect(self.login)
            self.logRegForm_label.setText('Нет Аккаунта?')
            self.logRegForm_button.setText('Зарегистрироваться')
            self.form = 'LOG'

        if form == 'LOG':
            self.email_label.show()
            self.setWindowTitle('Linkeds - Регистрация')
            self.logReg_button.setText('Зарегистрироваться')
            self.logReg_button.disconnect()
            self.logReg_button.clicked.connect(self.registration)
            self.logRegForm_label.setText('Есть Аккаунт?')
            self.logRegForm_button.setText('Войти')
            self.form = 'REG'

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

    @staticmethod
    def hash_data(data) -> str:
        """
        -> data: str
        <- hexdigest hash data: str
        """
        return hashlib.sha512(data.encode('utf-8')).hexdigest()

    @staticmethod
    def form_request(method: str = '<CHECK-CONNECTION>', data: dict = {'<NO-DATA>': '<NO-DATA>'}) -> dict:
        """
        Format of request -> {
            method: str
            data: dict
        }
        <- standard request: dict
        """
        return {'method': method, 'data': data}

    def registration(self):
        login = self.login_label.text()
        password = self.password_label.text()
        email = self.email_label.text()

        msgBox = StandardMessageBox(self.logo_image)
        try:
            user = User(login, password, email)
        except ValueError as error:
            msgBox.information('Предупреждение', str(error))
            self.login_label.setInputText()
            self.password_label.setInputText()
            self.email_label.setInputText()
            return

        hash_password = self.hash_data(password)
        user_data = {'login': login, 'email': email, 'password': hash_password}
        request = self.form_request('<REGISTRATION>', {'user_data': user_data})

        self.main_work.protocol.send_request(request)

    def login(self):
        login = self.login_label.text()
        password = self.password_label.text()

        msgBox = StandardMessageBox(self.logo_image)
        try:
            user = User(login, password)
        except ValueError as error:
            msgBox.information('Предупреждение', str(error))
            self.login_label.setInputText()
            self.password_label.setInputText()
            return

        hash_password = self.hash_data(password)
        user_data = {'login': login, 'password': hash_password}
        request = self.form_request('<LOGIN>', {'user_data': user_data})

        self.main_work.protocol.send_request(request)

    @pyqtSlot()
    def registration_success(self, data):
        msgBox = StandardMessageBox(self.logo_image)
        msgBox.information('Информация', 'Вы успешно зарегистрировали свой аккаунт')
        self.login_success(data)

    @pyqtSlot()
    def registration_denied(self, data):
        msgBox = StandardMessageBox(self.logo_image)
        msgBox.information('Информация', data.get('reason'))

    @pyqtSlot()
    def login_success(self, data):
        msgBox = StandardMessageBox(self.logo_image)
        msgBox.information('Информация', 'Вы успешно вошли в свой аккаунт!')

        user_data = data.get('user_data')
        self.destroy()
        self.main_work.client_window = AppWindow(self.main_work, user_data)
        self.main_work.client_window.show()

    @pyqtSlot()
    def login_denied(self, data):
        msgBox = StandardMessageBox(self.logo_image)
        msgBox.information('Информация', data.get('reason'))

    @pyqtSlot()
    def online_denied(self, data):
        msgBox = StandardMessageBox(self.logo_image)
        msgBox.information('Информация', data.get('reason'))
        self.hide()
        raise KeyboardInterrupt('GUI closed')

    def form_signal(self, method, data=None):
        self.signal_handler = SignalHandler()
        self.signal_handler.signal.connect(functools.partial(method, data))
        return self.signal_handler.signal

    def closeEvent(self, a0) -> None:
        self.hide()
        raise KeyboardInterrupt('GUI closed')


class AppWindow(QtWidgets.QMainWindow):

    def __init__(self, main_work, user_data):
        super().__init__()
        self.user_data = user_data
        self.main_work = main_work

        self.theme = 'DARK'
        self.setStyleSheet(DARK_THEME_STYLE)
        self.setObjectName('MainWindowWidget')

        self.init_images()

        self.setWindowTitle('Linkeds - Главный Экран')
        self.setWindowIcon(QtGui.QIcon(self.logo_image))
        self.setMinimumSize(600, 450)
        self.resize(1200, 700)

        self.menu_buttons_config = {'profile': ...}

        self.init_gui()
        self.init_online()
        self.auto_login(True)

    def init_online(self):
        request = self.form_request('<ONLINE>', {'user_data': self.user_data})
        self.main_work.protocol.send_request(request)

    def init_offline(self):
        request = self.form_request('<OFFLINE>', {'user_data': self.user_data})
        self.main_work.protocol.send_request(request)

    def init_images(self) -> None:
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

    def init_gui(self) -> None:
        print(self.user_data)
        self.widget = StandardWidget()
        self.setCentralWidget(self.widget)
        self.layout = StandardHLayout()
        self.widget.setLayout(self.layout)

        # -- MENU --- RISE --
        self.menu_widget = LayoutWidget(orientation=True)
        self.menu_widget.setFixedWidth(185)
        self.menu_widget.setObjectName('StandardWidget')

        self.logo_label = StandardLabel()
        self.logo_label.setPixmap(self.logo_image.scaled(125, 125))
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

        self.exit_button = MenuExitButton('Разлогиниться')
        self.exit_button.setIcon(self.exit_light)
        self.exit_button.clicked.connect(self.logout)

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
        # -- MENU --- END --

        # -- WINDOW --- RISE --
        self.windowFrame_widget = LayoutWidget()

        # -- PROFILE --- RISE --
        self.profile_widget = LayoutWidget()
        self.profile_widget.setStyleSheet('MainWindowWidget')

        self.profilePfp_label = StandardLabel()
        self.profilePfp_label.setMaximumWidth(250)
        self.profilePfp_label.setPixmap(self.userPfp_image)
        self.profilePfp_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignHCenter)
        self.profilePfp_label.mousePressEvent = self.changePfp

        self.profileInfo_widget = LayoutWidget(orientation=False)
        self.profileInfoId_label = StandardLabel(f'ID: {self.user_data.get("id")}')
        self.profileInfoLogin_label = StandardLabel(f'Login: {self.user_data.get("login")}')
        self.profileInfoId_label.setObjectName('BorderLabel')
        self.profileInfoLogin_label.setObjectName('BorderLabel')
        self.profileInfo_widget.setObjectName('FrameWidget')
        self.profileInfo_widget.addWidget(self.profileInfoId_label)
        self.profileInfo_widget.addWidget(self.profileInfoLogin_label)

        self.profileMainInfo_widget = LayoutWidget(orientation=True)

        self.profileMainInfoName_widget = LayoutWidget(orientation=False)
        self.name_input = StandardLineEdit('Введите новое имя...')
        self.confirmName_button = StandardButton('OK')
        self.profileName = StandardLabel(f'Имя: {self.user_data.get("name")}')
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
        self.profileStatus = StandardLabel(f'Статус: {self.user_data.get("status")}')
        self.profileStatus.setObjectName('BorderLabel')
        self.profileStatus.mousePressEvent = self.changeStatusForm
        self.profileMainInfoStatus_widget.addWidget(self.status_input)
        self.profileMainInfoStatus_widget.addWidget(self.confirmStatus_button)
        self.profileMainInfoStatus_widget.addWidget(self.profileStatus)
        self.status_input.hide()
        self.confirmStatus_button.hide()

        self.profileMainInfo_widget.addWidget(self.profileMainInfoName_widget)
        self.profileMainInfo_widget.addWidget(self.profileMainInfoStatus_widget)

        self.profile_widget.addWidget(self.profileInfo_widget)
        self.profile_widget.addWidget(self.profilePfp_label, stretch=0, alignment=QtCore.Qt.AlignmentFlag.AlignHCenter)
        self.profile_widget.addWidget(self.profileMainInfo_widget)
        self.profile_widget.addStretch(1)
        # -- PROFILE --- END --

        # -- MESSENGER --- RISE --
        self.messenger_widget = LayoutWidget()
        # -- MESSENGER --- END --

        # -- FRIENDS --- RISE --
        self.friends_widget = LayoutWidget()
        # -- FRIENDS --- END --

        # -- SETTINGS --- RISE --
        self.settings_widget = LayoutWidget()
        # -- SETTINGS --- END --

        self.windowFrame_widget.addWidget(self.profile_widget)
        self.windowFrame_widget.addWidget(self.messenger_widget)
        self.windowFrame_widget.addWidget(self.friends_widget)
        self.windowFrame_widget.addWidget(self.settings_widget)
        self.changeWindowFrame('PROFILE')
        # -- WINDOW --- END --

        self.context_menu = QtWidgets.QMenu(self)
        self.context_menu.setObjectName('StandardMenu')
        # MAKE STYLE SHEET
        action1 = self.context_menu.addAction("Сменить тему")
        action2 = self.context_menu.addAction("Закрыть приложение")

        action1.triggered.connect(lambda: self.action1_triggered(self.theme))
        action2.triggered.connect(self.action2_triggered)

        self.layout.addWidget(self.menu_widget)
        self.layout.addWidget(self.profile_widget)
        self.widget.show()

    def changeWindowFrame(self, frame):
        if frame == 'PROFILE':
            for widget in (self.profile_widget, self.messenger_widget, self.friends_widget, self.settings_widget):
                widget.hide()
            self.profile_widget.show()
        if frame == 'MESSENGER':
            for widget in (self.profile_widget, self.messenger_widget, self.friends_widget, self.settings_widget):
                widget.hide()
            self.messenger_widget.show()
        if frame == 'FRIENDS':
            for widget in (self.profile_widget, self.messenger_widget, self.friends_widget, self.settings_widget):
                widget.hide()
            self.friends_widget.show()
        if frame == 'SETTINGS':
            for widget in (self.profile_widget, self.messenger_widget, self.friends_widget, self.settings_widget):
                widget.hide()
            self.settings_widget.show()

    def changeNameForm(self, *args, **kwargs):
        self.name_input.show()
        self.confirmName_button.show()
        self.profileName.hide()
        self.confirmName_button.disconnect()
        self.confirmName_button.clicked.connect(self.changeName)

    def changeName(self):
        msgBox = StandardMessageBox(self.logo_image)
        try:
            login = self.user_data.get('login')
            user = User(login=login, name=self.name_input.text())
        except ValueError as error:
            msgBox.information('Предупреждение', str(error))
            self.profileName.show()
            self.name_input.hide()
            self.confirmName_button.hide()
            return

        self.user_data['name'] = self.name_input.text()
        self.send_request(self.form_request('<CHANGE-USER-DATA>', {'user_data': self.user_data}))
        self.profileName.setText(f'Имя: {self.user_data.get("name")}')
        self.profileName.show()
        self.name_input.hide()
        self.confirmName_button.hide()

    def changeStatusForm(self, *args, **kwargs):
        self.status_input.show()
        self.confirmStatus_button.show()
        self.profileStatus.hide()
        self.confirmStatus_button.disconnect()
        self.confirmStatus_button.clicked.connect(self.changeStatus)

    def changeStatus(self):
        msgBox = StandardMessageBox(self.logo_image)
        try:
            login = self.user_data.get('login')
            user = User(login=login, status=self.status_input.text())
        except ValueError as error:
            msgBox.information('Предупреждение', str(error))
            self.profileStatus.show()
            self.status_input.hide()
            self.confirmStatus_button.hide()
            return

        self.user_data['status'] = self.status_input.text()
        self.send_request(self.form_request('<CHANGE-USER-DATA>', {'user_data': self.user_data}))
        self.profileStatus.setText(f'Статус: {self.user_data.get("status")}')
        self.profileStatus.show()
        self.status_input.hide()
        self.confirmStatus_button.hide()

    def changePfp(self, *args, **kwargs):
        file_name, file_type = QtWidgets.QFileDialog.getOpenFileName(
            self, "Выбрать файл", ".",
            "JPEG Files(*.jpeg);;PNG Files(*.png);;")
        if file_name == '':
            return

        image_bytes = b""
        with open(file_name, 'rb') as image:
            image_bytes += image.read()

        with open("images/pfp_image.png", 'wb') as image:
            image.write(image_bytes)

        self.userPfp_image = QtGui.QPixmap(file_name).scaled(180, 180)
        self.userPfp_image = self.round_image(self.userPfp_image)
        self.profilePfp_label.setPixmap(self.userPfp_image)

    def contextMenuEvent(self, event) -> None:
        self.context_menu.exec(event.globalPos())

    def action1_triggered(self, theme):
        if theme == 'DARK':
            self.setStyleSheet(LIGHT_THEME_STYLE)
            self.profile_button.setIcon(self.profile_dark)
            self.messenger_button.setIcon(self.chat_dark)
            self.friends_button.setIcon(self.friends_dark)
            self.settings_button.setIcon(self.settings_dark)
            self.exit_button.setIcon(self.exit_dark)
            self.theme = 'LIGHT'

        if theme == 'LIGHT':
            self.setStyleSheet(DARK_THEME_STYLE)
            self.profile_button.setIcon(self.profile_light)
            self.messenger_button.setIcon(self.chat_light)
            self.friends_button.setIcon(self.friends_light)
            self.settings_button.setIcon(self.settings_light)
            self.exit_button.setIcon(self.exit_light)
            self.theme = 'DARK'

    def action2_triggered(self):
        self.close()

    def auto_login(self, activate):
        if activate:
            path = str(pathlib.Path().resolve()) + "\\CACHE"
            with open(path + '\\auto_login.txt', 'wb') as file:
                file.write(b"True\n" + pickle.dumps(self.user_data))
        if not activate:
            path = str(pathlib.Path().resolve()) + "\\CACHE"
            with open(path + '\\auto_login.txt', 'wb') as file:
                file.write(b"False\n")

    @staticmethod
    def round_image(image) -> QtGui.QPixmap:
        rounded = QtGui.QPixmap(image.size())
        rounded.fill(QtGui.QColor("transparent"))
        painter = QtGui.QPainter(rounded)
        painter.setBrush(QtGui.QBrush(image))
        painter.drawRoundedRect(image.rect(), 100, 100)
        return rounded

    @staticmethod
    def hash_data(data) -> str:
        """
        -> data: str
        <- hexdigest hash data: str
        """
        return hashlib.sha512(data.encode('utf-8')).hexdigest()

    @staticmethod
    def form_request(method: str = '<CHECK-CONNECTION>', data: dict = {'<NO-DATA>': '<NO-DATA>'}) -> dict:
        """
        Format of request -> {
            method: str
            data: dict
        }
        <- standard request: dict
        """
        return {'method': method, 'data': data}

    @pyqtSlot()
    def online_denied(self, data):
        msgBox = StandardMessageBox(self.logo_image)
        msgBox.information('Информация', data.get('reason'))
        self.auto_login(False)
        self.hide()
        raise KeyboardInterrupt('GUI closed')

    def form_signal(self, method, data=None):
        self.signal_handler = SignalHandler()
        self.signal_handler.signal.connect(functools.partial(method, data))
        return self.signal_handler.signal

    def send_request(self, request):
        self.main_work.protocol.send_request(request)

    def logout(self):
        self.init_offline()
        self.auto_login(False)
        self.hide()
        raise KeyboardInterrupt('GUI closed')

    def closeEvent(self, a0) -> None:
        self.init_offline()
        self.auto_login(True)
        self.hide()
        raise KeyboardInterrupt('GUI closed')

from LinkedsMain.GUI.reg_log_window_gui import RegLogWindow
from LinkedsMain.GUI.main_window_gui import *

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


class StaticMethods:

    @staticmethod
    def round_image(image) -> QtGui.QPixmap:
        rounded = QtGui.QPixmap(image.size())
        rounded.fill(QtGui.QColor("transparent"))
        painter = QtGui.QPainter(rounded)
        painter.setBrush(QtGui.QBrush(image))
        painter.drawRoundedRect(image.rect(), 150, 150)
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


class WelcomeWindow(RegLogWindow, StaticMethods):
    """
    Window to registrate new users or login in system
    """
    def __init__(self, main_work):
        super().__init__(main_work)

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
        self.main_work.client_window.send_request(
            self.main_work.client_window.form_request(
                '<SET-USER-SOCIAL>', {'user_data': self.main_work.client_window.user_data}))
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


class AppWindow(MainWindowGui, StaticMethods):

    def __init__(self, main_work, user_data):
        super().__init__(main_work, user_data)

    def update_gui(self):
        self.init_images()
        self.init_gui()
        self.changeWindowFrame(self.current_window)
        self.changeWindowFrame(self.current_friend_window)

        self.send_request(self.form_request(
            '<UPDATE-PFP>', {'user_social': self.user_social}
        ))

    def init_online(self):
        request = self.form_request('<ONLINE>', {'user_data': self.user_data})
        self.main_work.protocol.send_request(request)

    def init_offline(self):
        request = self.form_request('<OFFLINE>', {'user_data': self.user_data})
        self.main_work.protocol.send_request(request)

    def add_friend(self):
        friend_id = self.addFriend_input.text()

        self.send_request(self.form_request(
            '<ADD-REQUEST-FRIEND>',
            {
                'user_data': self.user_data,
                'user_social': self.user_social,
                'friend_id': friend_id
            }
        ))

    def delete_account(self):
        questionBox = YNMessageBox(self.logo_image)
        questionBox.question('Предпреждение', 'Вы уверены, что хотите удалить свой аккаунт?')

        if questionBox.flag == 'Yes':
            questionBox = YNMessageBox(self.logo_image)
            questionBox.question('Предпреждение', 'Вы точно уверены, что хотите удалить свой аккаунт?')
            if questionBox.flag == 'Yes':
                self.__delete_account()
            if questionBox.flag == 'No':
                return
        if questionBox.flag == 'No':
            return

    def changeWindowFrame(self, frame):
        menu_frames = {
            'PROFILE': self.profile_widget,
            'MESSENGER': self.messenger_widget,
            'FRIENDS': self.friends_widget,
            'SETTINGS': self.settings_widget,
            'FRIEND-PROFILE': self.friendProfile_widget
        }

        menu_frames_translate = {
            'PROFILE': 'Профиль',
            'MESSENGER': 'Мессенджер',
            'FRIENDS': 'Друзья',
            'SETTINGS': 'Настройки',
            'FRIEND-PROFILE': 'Профиль друга'
        }

        friends_list_frames = {
            'FRIENDS-LIST': self.friendsFrame_widget,
            'FRIENDS-REQUESTS-LIST': self.friendsRequestsFrame_widget,
            'FRIENDS-BLACK-LIST': self.friendsBlackListFrame_widget
        }

        if frame in menu_frames.keys():
            for widget in menu_frames.values():
                widget.hide()
            self.setWindowTitle(f'Linkeds - {menu_frames_translate.get(frame)}')
            self.current_window = frame
            menu_frames.get(frame).show()

        if frame in friends_list_frames.keys():
            for widget in friends_list_frames.values():
                widget.hide()
            self.current_friend_window = frame
            friends_list_frames.get(frame).show()

    def changeLogin(self):
        msgBox = StandardMessageBox(self.logo_image)
        try:
            user = User(login=self.changeLogin_button.text())
        except ValueError as error:
            msgBox.information('Предупреждение', str(error))
            return

        check_data = self.user_data
        check_data['login'] = self.changeLogin_button.text()
        self.send_request(self.form_request('<CHANGE-LOGIN>', {'user_data': check_data}))

    def changePassword(self):
        msgBox = StandardMessageBox(self.logo_image)
        try:
            user = User(login=self.user_data.get('login'), password=self.changePasswordForm_button.text())
        except ValueError as error:
            msgBox.information('Предупреждение', str(error))
            return

        self.user_data['password'] = self.hash_data(self.changePasswordForm_button.text())
        self.send_request(self.form_request('<CHANGE-USER-DATA>', {'user_data': self.user_data}))
        self.update_gui()

    def changeID(self):
        infoBox = StandardMessageBox(self.logo_image)
        infoBox.information('Информация', 'В смене ID отказано,\nвы должны иметь особый статус')

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
        self.update_gui()

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
        self.update_gui()

    def changePfp(self, *args, **kwargs):
        file_name, file_type = QtWidgets.QFileDialog.getOpenFileName(
            self, "Выбрать файл", ".",
            "JPEG Files(*.jpeg);;PNG Files(*.png);;")
        if file_name == '':
            return

        image_bytes = b""
        with open(file_name, 'rb') as image:
            image_bytes += image.read()

        # with open("images/pfp_image.png", 'wb') as image:
        #     image.write(image_bytes)
        #
        # self.userPfp_image = QtGui.QPixmap(file_name).scaled(180, 180)
        # self.userPfp_image = self.round_image(self.userPfp_image)
        # self.profilePfp_label.setPixmap(self.userPfp_image)

        self.send_request(self.form_request(
            '<SAVE-IMAGE>',
            {
                'user_social': self.user_social,
                'image_type': 'pfp',
                'image_bytes': image_bytes
            }
        ))
        time.sleep(0.5)
        self.send_request(self.form_request(
            '<UPDATE-PFP>',
            {
                'user_social': self.user_social
            }
        ))

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
            with open(path + '\\auto_login.txt', 'w') as file:
                file.write("True\n" + str(self.user_data.get('id')) + '\n' + str(self.user_data.get('password')))
        if not activate:
            path = str(pathlib.Path().resolve()) + "\\CACHE"
            with open(path + '\\auto_login.txt', 'w') as file:
                file.write("False\n")

    @pyqtSlot()
    def online_denied(self, data):
        msgBox = StandardMessageBox(self.logo_image)
        msgBox.information('Информация', data.get('reason'))
        self.auto_login(False)
        self.hide()
        raise KeyboardInterrupt('GUI closed')

    @pyqtSlot()
    def set_user_data(self, data):
        self.user_data = data.get('user_data')
        print('UserData: ', self.user_data)
        self.send_request(self.form_request(
            '<SET-USER-SOCIAL>', {'user_data': self.user_data}
        ))

    @pyqtSlot()
    def set_user_social(self, data):
        self.user_social = data.get('user_social')
        print('UserSocial: ', self.user_social)
        self.update_gui()

    @pyqtSlot()
    def update_pfp(self, data):
        image_bytes = data.get('image_bytes')
        with open("images/pfp_image.png", 'wb') as image:
            image.write(image_bytes)

        self.userPfp_image = QtGui.QPixmap("images/pfp_image.png").scaled(225, 225)
        self.userPfp_image = self.round_image(self.userPfp_image)
        self.profilePfp_label.setPixmap(self.userPfp_image)

        self.send_request(self.form_request(
            '<UPDATE-FRIENDS>',
            {
                'user_data': self.user_data
            }
        ))

    @pyqtSlot()
    def update_friends(self, data):
        friends_data = data.get('friends')
        if friends_data == 'None':
            self.friendsFrame_widget.clearLayout()
            self.friendsFrame_widget.youHaveNoFriends()

            self.send_request(self.form_request(
                '<UPDATE-REQUEST-FRIENDS>',
                {
                    'user_data': self.user_data
                }
            ))
            return

        self.friendsFrame_widget.clearLayout()
        for friend in friends_data:
            with open('static.png', 'wb') as image:
                image.write(friend.get('friend_pfp'))
            friend_pfp = QtGui.QPixmap('static.png')
            self.friendsFrame_widget.createFriendWidget(
                friend.get('friend_data'), friend_pfp)

        self.send_request(self.form_request(
            '<UPDATE-REQUEST-FRIENDS>',
            {
                'user_data': self.user_data
            }
        ))

    @pyqtSlot()
    def update_request_friends(self, data):
        friends_data = data.get('friends_requests')
        if friends_data == 'None':
            self.friendsRequestsFrame_widget.clearLayout()
            self.friendsRequestsFrame_widget.youHaveNoRequestFriends()

            self.send_request(self.form_request(
                '<UPDATE-BLACK-LIST>',
                {
                    'user_data': self.user_data
                }
            ))
            return

        self.friendsRequestsFrame_widget.clearLayout()
        for friend in friends_data:
            with open('static.png', 'wb') as image:
                image.write(friend.get('friend_pfp'))
            friend_pfp = QtGui.QPixmap('static.png')
            self.friendsRequestsFrame_widget.createRequestFriendWidget(
                friend.get('friend_data'), friend_pfp, friend.get('request_status'))

        self.send_request(self.form_request(
            '<UPDATE-BLACK-LIST>',
            {
                'user_data': self.user_data
            }
        ))

    @pyqtSlot()
    def update_black_list(self, data):
        black_list = data.get('black_list')
        if black_list == 'None':
            self.friendsBlackListFrame_widget.clearLayout()
            self.friendsBlackListFrame_widget.youHaveNoBlackListFriends()

            self.send_request(self.form_request(
                '<UPDATE-CHATS>',
                {
                    'user_data': self.user_data
                }
            ))
            return

        self.friendsBlackListFrame_widget.clearLayout()
        for friend_bl in black_list:
            with open('static.png', 'wb') as image:
                image.write(friend_bl.get('friend_pfp'))
            friend_pfp = QtGui.QPixmap('static.png')
            self.friendsBlackListFrame_widget.createBlackListWidget(
                friend_bl.get('friend_data'), friend_pfp)

        self.send_request(self.form_request(
            '<UPDATE-CHATS>',
            {
                'user_data': self.user_data
            }
        ))

    @pyqtSlot()
    def update_chats(self, data):
        chats = data.get('chats')
        if chats == 'None':
            self.chatButtons_frame.clearLayout()
            self.chatButtons_frame.youHaveNoChats()
            return

        self.chatButtons_frame.clearLayout()
        for chat in chats:
            chat_config = chat.get('chat_config')
            chatBtn_config = chat.get('chatBtn_config')
            with open('static.png', 'wb') as image:
                image.write(chat_config.get('friend_pfp'))
            friend_pfp = self.round_image(QtGui.QPixmap('static.png').scaled(75, 75))
            chat_config['friend_pfp'] = friend_pfp
            chatBtn_config['friend_pfp'] = friend_pfp
            self.chatButtons_frame.createChat(chatBtn_config, chat_config)
        self.chatButtons_frame.vbox.addStretch(1)

        if self.current_chat_flag:
            self.chatButtons_frame.showChat(self.current_chat)
        self.cnt = 0

    @pyqtSlot()
    def add_message(self, data):
        if not self.current_chat_flag:
            self.update_gui()
            return
        msg_config = data.get('msg_config')
        msg_config['chat_id'] = str(msg_config.get('chat_id'))
        with open('static.png', 'wb') as image:
            image.write(msg_config.get('friend_pfp'))
        friend_pfp = self.round_image(QtGui.QPixmap('static.png').scaled(75, 75))
        msg_config['friend_pfp'] = friend_pfp
        chat_widget = self.chatButtons_frame.chatFrame_widgets.get(msg_config.get('chat_id'))
        chat_widget.messages = data.get('messages')
        chat_widget.createMessage(msg_config=msg_config.get('message'))
        chat_widget.set_to_bottom()

    def keyPressEvent(self, a0) -> None:
        if self.current_chat_flag:
            if a0.key() == 16777220:
                msg_input = self.chatButtons_frame.chatInput_widgets.get(self.current_chat)
                self.chatButtons_frame.send_message(self.current_chat, msg_input)

    @pyqtSlot()
    def show_friend_profile(self, data):
        self.update_gui()
        friend_data = data.get('friend_data')
        with open('static.png', 'wb') as image:
            image.write(data.get('friend_pfp'))
        friend_pfp = self.round_image(QtGui.QPixmap('static.png')).scaled(200, 200)

        self.friendProfile_widget = LayoutWidget(orientation=True)
        self.friendProfile_widget.setObjectName('StandardWidget')
        back_btn = StandardButton('Вернуться назад')
        back_btn.clicked.connect(self.close_friend_profile)
        friend_profile = self.friendsFrame_widget.createFriendProfileWidget(friend_data, friend_pfp)
        self.friendProfile_widget.addWidget(back_btn)
        self.friendProfile_widget.addWidget(friend_profile)

        self.windowFrame_widget.layout.replaceWidget(self.friends_widget, self.friendProfile_widget)

    def close_friend_profile(self):
        self.update_gui()

    @pyqtSlot()
    def add_request_friend_denied(self, data):
        reason = data.get('reason')
        infoBox = StandardMessageBox(icon=self.logo_image)
        infoBox.information('Информация', reason)

    @pyqtSlot()
    def request_denied(self, data):
        reason = data.get('reason')
        infoBox = StandardMessageBox(icon=self.logo_image)
        infoBox.information('Информация', reason)

    def form_signal(self, method, data=None):
        self.signal_handler = SignalHandler()
        self.signal_handler.signal.connect(functools.partial(method, data))
        return self.signal_handler.signal

    def send_request(self, request):
        self.main_work.protocol.send_request(request)

    @pyqtSlot()
    def unpredictable_error(self, data):
        reason = data.get('reason')
        infoBox = StandardMessageBox(icon=self.logo_image)
        infoBox.warning('Ошибка', reason)
        self.hide()
        raise KeyboardInterrupt('GUI closed')

    def __delete_account(self):
        self.send_request(self.form_request(
            '<DELETE-ACCOUNT>',
            {'user_data': self.user_data}
        ))
        time.sleep(5)
        self.logout()

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

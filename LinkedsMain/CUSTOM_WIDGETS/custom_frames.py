import typing

from PyQt6 import QtWidgets, QtCore, QtGui
from LinkedsMain.CUSTOM_WIDGETS.custom_widgets import StandardWidget
from LinkedsMain.CUSTOM_WIDGETS.custom_buttons import StandardButton, MenuExitButton
from LinkedsMain.CUSTOM_WIDGETS.custom_labels import StandardLabel
from LinkedsMain.CUSTOM_WIDGETS.custom_layouts import LayoutWidget


class StandardFrame(QtWidgets.QWidget):

    def __init__(self):
        # super(StandardWidget, self).__init__(*args, **kwargs)
        super().__init__()
        self.setObjectName('StandardWidget')


class FriendsFrame(QtWidgets.QScrollArea):

    def __init__(self, main_window):
        super().__init__()
        self.setObjectName('StandardArea')
        self.main_window = main_window
        self.user_data = main_window.user_data
        self.user_social = main_window.user_social

        self.widget = StandardWidget()
        self.vbox = QtWidgets.QVBoxLayout()

        self.friends_widgets = {}

        self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setWidgetResizable(True)
        self.setWidget(self.widget)

        self.widget.setLayout(self.vbox)

    def createFriendProfileWidget(self, friend_data, friend_pfp):
        profile_widget = LayoutWidget(orientation=True)

        profilePfp_label = StandardLabel()
        profilePfp_label.setMaximumWidth(350)
        profilePfp_label.setPixmap(friend_pfp)
        profilePfp_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignHCenter)

        profileInfo_widget = LayoutWidget(orientation=False)
        profileInfo_widget.setMaximumHeight(75)
        profileInfoId_label = StandardLabel(f'ID: {friend_data.get("id")}')
        profileInfoLogin_label = StandardLabel(f'Login: {friend_data.get("login")}')
        profileInfoId_label.setObjectName('BorderLabel')
        profileInfoLogin_label.setObjectName('BorderLabel')
        profileInfo_widget.setObjectName('FrameWidget')
        profileInfo_widget.addWidget(profileInfoId_label)
        profileInfo_widget.addWidget(profileInfoLogin_label)

        profileMainInfo_widget = LayoutWidget(orientation=True)
        profileMainInfo_widget.setObjectName('FrameWidget')

        profileMainInfoName_widget = LayoutWidget(orientation=False)
        profileName = StandardLabel(f'Имя: {friend_data.get("name")}')
        profileName.setObjectName('BorderLabel')
        profileMainInfoName_widget.addWidget(profileName)

        profileMainInfoStatus_widget = LayoutWidget(orientation=False)
        profileStatus = StandardLabel(f'Статус: {friend_data.get("status")}')
        profileStatus.setObjectName('BorderLabel')
        profileMainInfoStatus_widget.addWidget(profileStatus)

        profileMainInfo_widget.addWidget(profileMainInfoName_widget)
        profileMainInfo_widget.addWidget(profileMainInfoStatus_widget)

        profile_widget.addWidget(profileInfo_widget)
        profile_widget.addWidget(profilePfp_label, stretch=0, alignment=QtCore.Qt.AlignmentFlag.AlignHCenter)
        profile_widget.addSpacing(50)
        profile_widget.addWidget(profileMainInfo_widget)
        profile_widget.addStretch(1)

        return profile_widget

    def createFriendWidget(self, friend_data, friend_pfp):
        widget = LayoutWidget(orientation=False)
        widget.setObjectName('FrameWidget')
        widget.setMaximumHeight(150)

        pfp_label = StandardLabel()
        pfp_label.setPixmap(friend_pfp.scaled(75, 75))

        friendData_widget = LayoutWidget(orientation=True)
        friend_name = StandardLabel(friend_data.get('name'))
        if friend_data.get('online') == 'True':
            friend_online = StandardLabel('В сети')
        else:
            friend_online = StandardLabel('Не в сети')
        friendData_widget.addWidget(friend_name)
        friendData_widget.addWidget(friend_online)

        friendActionButtons_widget = LayoutWidget(orientation=True)
        showProfile_button = StandardButton('Показать профиль')
        showProfile_button.clicked.connect(lambda: self.show_friend_profile(self.friends_widgets.get(widget)))
        showProfile_button.setStyleSheet('font-size: 12px')
        addToBlackList_button = StandardButton('Добавить в ЧС')
        addToBlackList_button.clicked.connect(lambda: self.add_to_black_list(self.friends_widgets.get(widget)))
        addToBlackList_button.setStyleSheet('font-size: 12px')
        deleteFriend_button = StandardButton('Удалить из друзей')
        deleteFriend_button.clicked.connect(lambda: self.delete_friend(self.friends_widgets.get(widget)))
        deleteFriend_button.setStyleSheet('font-size: 12px')
        friendActionButtons_widget.addWidget(showProfile_button)
        friendActionButtons_widget.addWidget(addToBlackList_button)
        friendActionButtons_widget.addWidget(deleteFriend_button)

        widget.addWidget(pfp_label)
        widget.addSpacing(10)
        widget.addWidget(friendData_widget)
        widget.addStretch(1)
        widget.addWidget(friendActionButtons_widget)
        widget.addSpacing(10)

        self.friends_widgets[widget] = friend_data.get('id')
        self.vbox.addWidget(widget)
        self.vbox.addSpacing(15)
        self.vbox.addStretch(1)

        self.widget.setLayout(self.vbox)
        self.setWidget(self.widget)

    def createRequestFriendWidget(self, friend_data, friend_pfp, request_status):
        widget = LayoutWidget(orientation=False)
        widget.setObjectName('FrameWidget')
        widget.setMaximumHeight(150)

        pfp_label = StandardLabel()
        pfp_label.setPixmap(friend_pfp.scaled(75, 75))

        friendData_widget = LayoutWidget(orientation=True)
        friend_name = StandardLabel(friend_data.get('name'))
        friendData_widget.addWidget(friend_name)

        friendActionButtons_widget = LayoutWidget(orientation=True)
        if request_status == 'receiver':
            addRequest_button = StandardButton('Добавить в друзья')
            addRequest_button.setStyleSheet('font-size: 12px')
            addRequest_button.clicked.connect(lambda: self.accept_request_friend(self.friends_widgets.get(widget)))
            deleteRequest_button = StandardButton('Отклонить')
            deleteRequest_button.setStyleSheet('font-size: 12px')
            deleteRequest_button.clicked.connect(lambda: self.cancel_request_friend(self.friends_widgets.get(widget)))
            friendActionButtons_widget.addWidget(addRequest_button)
            friendActionButtons_widget.addWidget(deleteRequest_button)

        if request_status == 'sender':
            sender_label = StandardLabel('Ожидаем принятия заявки...')
            cancelRequest_label = StandardButton('Отменить заявку')
            cancelRequest_label.setStyleSheet('font-size: 12px')
            cancelRequest_label.clicked.connect(lambda: self.cancel_request_friend(self.friends_widgets.get(widget)))
            friendActionButtons_widget.addWidget(sender_label)
            friendActionButtons_widget.addWidget(cancelRequest_label)

        widget.addWidget(pfp_label)
        widget.addSpacing(10)
        widget.addWidget(friendData_widget)
        widget.addStretch(1)
        widget.addWidget(friendActionButtons_widget)
        widget.addSpacing(10)

        self.friends_widgets[widget] = friend_data.get('id')
        self.vbox.addWidget(widget)
        self.vbox.addSpacing(15)
        self.vbox.addStretch(1)

        self.widget.setLayout(self.vbox)
        self.setWidget(self.widget)

    def createBlackListWidget(self, friend_data, friend_pfp):
        widget = LayoutWidget(orientation=False)
        widget.setObjectName('FrameWidget')
        widget.setMaximumHeight(150)

        pfp_label = StandardLabel()
        pfp_label.setPixmap(friend_pfp.scaled(75, 75))

        friendData_widget = LayoutWidget(orientation=True)
        friend_name = StandardLabel(friend_data.get('name'))
        friendData_widget.addWidget(friend_name)

        friendActionButtons_widget = LayoutWidget(orientation=True)
        delFromBL_button = StandardButton('Убрать из Чёрного Списка')
        delFromBL_button.setStyleSheet('font-size: 12px')
        delFromBL_button.clicked.connect(lambda: self.remove_from_black_list(self.friends_widgets.get(widget)))
        friendActionButtons_widget.addWidget(delFromBL_button)

        widget.addWidget(pfp_label)
        widget.addSpacing(10)
        widget.addWidget(friendData_widget)
        widget.addStretch(1)
        widget.addWidget(friendActionButtons_widget)
        widget.addSpacing(10)

        self.friends_widgets[widget] = friend_data.get('id')
        self.vbox.addWidget(widget)
        self.vbox.addSpacing(15)
        self.vbox.addStretch(1)

        self.widget.setLayout(self.vbox)
        self.setWidget(self.widget)

    def youHaveNoFriends(self):
        label = StandardLabel('У вас нет друзей.\nДобавьте кого нибудь!')
        label.setStyleSheet('font-size: 24px')

        self.friends_widgets[label] = 'None'
        self.vbox.addWidget(label)
        self.widget.setLayout(self.vbox)
        self.setWidget(self.widget)

    def youHaveNoRequestFriends(self):
        label = StandardLabel('У вас нет заявок в друзья.')
        label.setStyleSheet('font-size: 24px')

        self.friends_widgets[label] = 'None'
        self.vbox.addWidget(label)
        self.widget.setLayout(self.vbox)
        self.setWidget(self.widget)

    def youHaveNoBlackListFriends(self):
        label = StandardLabel('У вас нет пользователей, занесённых в Чёрный список')
        label.setStyleSheet('font-size: 24px')

        self.friends_widgets[label] = 'None'
        self.vbox.addWidget(label)
        self.widget.setLayout(self.vbox)
        self.setWidget(self.widget)

    def clearLayout(self):
        for i in reversed(range(self.vbox.count())):
            try:
                self.vbox.itemAt(i).widget().deleteLater()
            except AttributeError:
                pass
        self.friends_widgets = {}

    def accept_request_friend(self, friend_id):
        self.main_window.send_request(self.main_window.form_request(
            '<ADD-FRIEND>',
            {
                'user_data': self.main_window.user_data,
                'user_social': self.main_window.user_social,
                'friend_id': friend_id
            }
        ))

    def cancel_request_friend(self, friend_id):
        self.main_window.send_request(self.main_window.form_request(
            '<CANCEL-REQUEST-FRIEND>',
            {
                'user_social': self.main_window.user_social,
                'friend_id': friend_id
            }
        ))

    def show_friend_profile(self, friend_id):
        self.main_window.send_request(self.main_window.form_request(
            '<SHOW-FRIEND-PROFILE>',
            {
                'friend_id': friend_id
            }
        ))

    def add_to_black_list(self, friend_id):
        self.main_window.send_request(self.main_window.form_request(
            '<ADD-FRIEND-TO-BLACK-LIST>',
            {
                'user_social': self.main_window.user_social,
                'friend_id': friend_id
            }
        ))

    def delete_friend(self, friend_id):
        self.main_window.send_request(self.main_window.form_request(
            '<DELETE-FRIEND>',
            {
                'user_social': self.main_window.user_social,
                'friend_id': friend_id
            }
        ))

    def remove_from_black_list(self, friend_id):
        self.main_window.send_request(self.main_window.form_request(
            '<REMOVE-FROM-BLACK-LIST>',
            {
                'user_social': self.main_window.user_social,
                'friend_id': friend_id
            }
        ))


class MessengerFrame(QtWidgets.QScrollArea):

    def __init__(self, main_window):
        super().__init__()
        self.setObjectName('StandardArea')
        self.main_window = main_window
        self.user_data = main_window.user_data
        self.user_social = main_window.user_social

        self.widget = StandardWidget()
        self.vbox = QtWidgets.QVBoxLayout()

        self.friends_widgets = {}

        self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setWidgetResizable(True)
        self.setWidget(self.widget)

        self.widget.setLayout(self.vbox)

    def createChat(self, chatBtn_config: dict, chat_config: dict) -> None:
        friend_pfp = chatBtn_config.get('friend_pfp')
        friend_data = chatBtn_config.get('friend_data')
        last_message = chatBtn_config.get('last_message')
        last_message_time = chatBtn_config.get('last_message_time')

        chat_widget = self.chatWidget(chat_config)

        chatBtn_widget = LayoutWidget(False)
        chatBtn_widget.mousePressEvent = ...

    def showChat(self, id):
        ...

    def chatWidget(self, chat_config: dict):
        """
        Return chat widget
        """
        chat_widget = ChatFrame(self.main_window)
        return chat_widget


class ChatFrame:

    def __init__(self, main_window):
        super().__init__()
        self.setObjectName('StandardArea')
        self.main_window = main_window
        self.user_data = main_window.user_data
        self.user_social = main_window.user_social

        self.widget = StandardWidget()
        self.vbox = QtWidgets.QVBoxLayout()

        self.friends_widgets = {}

        self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setWidgetResizable(True)
        self.setWidget(self.widget)

        self.widget.setLayout(self.vbox)

    def createMessage(self, chat, msg_config: dict) -> None:
        ...

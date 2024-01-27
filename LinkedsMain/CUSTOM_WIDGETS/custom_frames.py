import time
import typing
import functools

from PyQt6 import QtWidgets, QtCore, QtGui
from LinkedsMain.CUSTOM_WIDGETS.custom_widgets import StandardWidget
from LinkedsMain.CUSTOM_WIDGETS.custom_buttons import StandardButton, MenuExitButton, BorderlessButton
from LinkedsMain.CUSTOM_WIDGETS.custom_labels import StandardLabel
from LinkedsMain.CUSTOM_WIDGETS.custom_layouts import LayoutWidget
from LinkedsMain.CUSTOM_WIDGETS.custom_line_edit import StandardLineEdit


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
        widget.addShadow()
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
        widget.addShadow()
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
        widget.addShadow()
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

        self.chat_widgets = {}
        self.chatFrame_widgets = {}
        self.chatInput_widgets = {}

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
        message_status = chatBtn_config.get('status')
        chat_config['chat_id'] = str(chat_config.get('chat_id'))

        chat_widget = self.chatWidget(chat_config)
        self.main_window.messengerChat_frame.addWidget(chat_widget)
        chat_widget.hide()
        self.chat_widgets[chat_config.get('chat_id')] = chat_widget

        chatBtn_widget = LayoutWidget(False)
        chatBtn_widget.addShadow()
        chatBtn_widget.setObjectName('FrameWidget')
        chatBtn_widget.mousePressEvent = functools.partial(self.showChat, chat_config.get('chat_id'))

        pfp_label = StandardLabel()
        pfp_label.setPixmap(friend_pfp)

        chatBtnInfo_widget = LayoutWidget(True)
        friendName_label = StandardLabel(friend_data.get('name'))
        friendName_label.setStyleSheet('font-size: 18px; background: transparent')
        message_widget = LayoutWidget(False)
        messagePfp_label = StandardLabel()
        messagePfp_label.setPixmap(self.main_window.userPfp_image.scaled(25, 25))
        messageText_label = StandardLabel(last_message)
        messageText_label.setObjectName('MessageWidget')
        messageTime_label = StandardLabel(last_message_time)
        if message_status == 'sender':
            message_widget.addWidget(messagePfp_label)
        message_widget.addWidget(messageText_label)
        message_widget.addWidget(messageTime_label)
        chatBtnInfo_widget.addWidget(friendName_label, 0, QtCore.Qt.AlignmentFlag.AlignLeft)
        chatBtnInfo_widget.addWidget(message_widget, 0, QtCore.Qt.AlignmentFlag.AlignLeft)

        chatBtn_widget.addSpacing(30)
        chatBtn_widget.addWidget(pfp_label)
        chatBtn_widget.addWidget(chatBtnInfo_widget)
        chatBtn_widget.addStretch(1)

        self.vbox.addWidget(chatBtn_widget)

    def showChat(self, *args, **kwargs):
        chat_id = str(args[0])
        self.main_window.chatButtons_frame.hide()
        for widget in self.chat_widgets.values():
            widget.hide()
        self.main_window.current_chat_flag = True
        self.main_window.current_chat = str(chat_id)

        print(self.chat_widgets)
        self.chat_widgets.get(chat_id).show()
        self.chatFrame_widgets.get(chat_id).set_to_bottom()

    def hideChat(self):
        self.main_window.current_chat_flag = False
        self.main_window.current_chat = ''
        self.main_window.update_gui()

    def chatWidget(self, chat_config: dict):
        """
        Return chat widget
        """
        friend_data = chat_config.get('friend_data')
        friend_data['id'] = str(friend_data.get('id'))
        friend_pfp = chat_config.get('friend_pfp')
        messages = chat_config.get('messages')

        chat_widget = LayoutWidget(True)

        back_btn = BorderlessButton()
        back_btn.setText('Вернуться назад')
        back_btn.setIcon(self.main_window.hideMenu_light)
        back_btn.setIconSize(QtCore.QSize(35, 35))
        back_btn.clicked.connect(self.hideChat)

        sendMessage_widget = LayoutWidget(False)
        sendMessage_input = StandardLineEdit('Написать сообщение...')
        sendMessage_button = BorderlessButton()
        sendMessage_button.clicked.connect(lambda: self.send_message(friend_data.get('id'), sendMessage_input))
        sendMessage_button.setIcon(self.main_window.sendMessage_image)
        sendMessage_button.setIconSize(QtCore.QSize(35, 35))
        sendMessage_button.resize(50, 50)
        sendMessage_widget.addWidget(sendMessage_input, 1)
        sendMessage_widget.addWidget(sendMessage_button)

        chatMessages_frame = ChatFrame(self.main_window, friend_data, friend_pfp, messages)
        self.chatFrame_widgets[friend_data.get('id')] = chatMessages_frame
        self.chatInput_widgets[friend_data.get('id')] = sendMessage_input
        for message in messages:
            chatMessages_frame.createMessage(msg_config=message)
        chatMessages_frame.vbox.addStretch(1)

        chat_widget.addWidget(back_btn, 0, QtCore.Qt.AlignmentFlag.AlignLeft)
        chat_widget.addWidget(chatMessages_frame, 1)
        chat_widget.addWidget(sendMessage_widget, 0)

        return chat_widget

    def send_message(self, friend_id, msg_input):
        self.main_window.send_request(self.main_window.form_request(
            '<SEND-MESSAGE>',
            {
                'user_data': self.main_window.user_data,
                'friend_id': friend_id,
                'message': {'text': msg_input.text(), 'time': time.strftime("%H:%M")}
            }
        ))
        msg_input.setText('')

    def youHaveNoChats(self):
        label = StandardLabel('У вас нет друзей, с которыми у вас может быть переписка.\nДобавьте кого нибудь!')
        label.setStyleSheet('font-size: 24px')

        self.chat_widgets[label] = 'None'
        self.vbox.addWidget(label)
        self.widget.setLayout(self.vbox)
        self.setWidget(self.widget)

    def clearLayout(self):
        for i in reversed(range(self.vbox.count())):
            try:
                self.vbox.itemAt(i).widget().deleteLater()
            except AttributeError:
                pass
        self.chat_widgets = {}


class ChatFrame(QtWidgets.QScrollArea):

    def __init__(self, main_window, friend_data, friend_pfp, messages):
        super().__init__()
        self.setObjectName('StandardArea')
        self.main_window = main_window
        self.messages = messages
        self.user_data = main_window.user_data
        self.user_social = main_window.user_social
        self.user_pfp = main_window.userPfp_image.scaled(100, 100)
        self.friend_data = friend_data
        self.friend_pfp = friend_pfp

        self.widget = StandardWidget()
        self.vbox = QtWidgets.QVBoxLayout()

        self.messages_widgets = {}

        self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setWidgetResizable(True)
        self.setWidget(self.widget)

        self.widget.setLayout(self.vbox)

    def createMessage(self, chat=None, msg_config: dict = None) -> None:
        if msg_config is None:
            msg_config = {}

        print(self.messages)
        msg_config['id'] = str(msg_config.get('id'))
        msg_config['image'] = str(msg_config.get('image'))
        msg_config['status'] = str(msg_config.get('status'))
        msg_config['from_'] = str(msg_config.get('from_'))

        try:
            last_message = self.messages[self.messages.index(msg_config) - 1]
            if self.messages.index(msg_config) - 1 == -1:
                last_message = {}
        except IndexError:
            last_message = {}
        last_message_from = last_message.get('from_')
        last_message_to = last_message.get('to_')

        if str(msg_config.get('from_')) == str(self.main_window.user_data.get('id')):
            msg_config['status'] = 'sender'
        else:
            msg_config['status'] = 'receiver'
        message_status = str(msg_config.get('status'))
        message_text = str(msg_config.get('text'))
        message_time = str(msg_config.get('time'))
        message_id = str(msg_config.get('chat_id'))
        if message_status not in ('receiver', 'sender'):
            message_status = 'sender'

        message_widget = LayoutWidget(False)

        if message_status == 'receiver':
            senderPfp_label = StandardLabel()
            senderPfp_label.setMinimumWidth(100)

            sender_widget = LayoutWidget(True)
            sender_widget.setObjectName('FrameWidget')
            sender_widget.setStyleSheet('border: transparent')

            senderName_label = StandardLabel(self.friend_data.get('name'))

            messageInfo_widget = LayoutWidget(False)
            messageText_label = StandardLabel(self.cut_message_text(message_text))
            messageText_label.setObjectName('MessageWidget')
            messageTime_label = StandardLabel(message_time)
            messageInfo_widget.addWidget(messageText_label, 1)
            messageInfo_widget.addWidget(messageTime_label, 0, QtCore.Qt.AlignmentFlag.AlignBottom)

            if str(last_message_from) != str(self.friend_data.get('id')):
                sender_widget.addWidget(senderName_label, 0, QtCore.Qt.AlignmentFlag.AlignRight)
            sender_widget.addWidget(messageInfo_widget)

            message_widget.addWidget(sender_widget)
            if str(last_message_from) != str(self.friend_data.get('id')):
                senderPfp_label.setPixmap(self.friend_pfp)
            message_widget.addWidget(senderPfp_label)
            message_widget.addStretch(1)

        if message_status == 'sender':
            senderPfp_label = StandardLabel()
            senderPfp_label.setMinimumWidth(100)

            sender_widget = LayoutWidget(True)
            sender_widget.setObjectName('FrameWidget')
            sender_widget.setStyleSheet('border: transparent')

            senderName_label = StandardLabel(self.user_data.get('name'))

            messageInfo_widget = LayoutWidget(False)
            messageText_label = StandardLabel(self.cut_message_text(message_text))
            messageText_label.setObjectName('MessageWidget')
            messageTime_label = StandardLabel(message_time)
            messageInfo_widget.addWidget(messageText_label, 1)
            messageInfo_widget.addWidget(messageTime_label, 0, QtCore.Qt.AlignmentFlag.AlignBottom)

            if str(last_message_from) != str(self.user_data.get('id')):
                sender_widget.addWidget(senderName_label, 0, QtCore.Qt.AlignmentFlag.AlignLeft)
            sender_widget.addWidget(messageInfo_widget)

            if str(last_message_from) != str(self.user_data.get('id')):
                senderPfp_label.setPixmap(self.user_pfp.scaled(75, 75))
            message_widget.addWidget(senderPfp_label)
            message_widget.addWidget(sender_widget)
            message_widget.addStretch(1)

        if message_status == 'sender':
            self.vbox.addWidget(message_widget, 0, QtCore.Qt.AlignmentFlag.AlignLeft)
        if message_status == 'receiver':
            self.vbox.addWidget(message_widget, 0, QtCore.Qt.AlignmentFlag.AlignRight)

        self.messages_widgets[message_widget] = msg_config
        self.set_to_bottom()

    def cut_message_text(self, message: str) -> str:
        cnt = 0
        cut_message = ''
        for i in range(len(message)):
            if cnt > 60 and message[i] == ' ':
                cut_message += '\n'
                cnt = 0
                continue
            cut_message += message[i]
            cnt += 1
        return cut_message

    def set_to_bottom(self):
        x = self.verticalScrollBar().maximum()
        self.verticalScrollBar().setValue(x)

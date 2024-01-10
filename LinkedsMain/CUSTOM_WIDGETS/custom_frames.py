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
        showProfile_button.setStyleSheet('font-size: 12px')
        addToBlackList_button = StandardButton('Добавить в ЧС')
        addToBlackList_button.setStyleSheet('font-size: 12px')
        deleteFriend_button = StandardButton('Удалить из друзей')
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

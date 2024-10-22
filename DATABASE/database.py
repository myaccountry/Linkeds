import pymysql
import pathlib
from operator import itemgetter
from CONFIG.database_config import *
from DATABASE.user_config import User, Social, Connection, Message


class Database:
    """
    Class Database with standard requests to mysql using python
    Such as - SELECT; INSERT; DELETE; UPDATE; CREATE
    """
    DATA_CONFIGURES = {
        'User': User,
        'Social': Social,
        'Connection': Connection,
        'Message': Message
    }

    elements = User()
    social_elements = Social()
    connection_elements = Connection()
    message_elements = Message()
    DB_TABLE_ELEMENTS = {
        'user': [el for el in elements.__dict__.keys()],
        'social': [el for el in social_elements.__dict__.keys()],
        'connection': [el for el in connection_elements.__dict__.keys()],
        'message': [el for el in message_elements.__dict__.keys()]
    }

    def __init__(self):
        try:
            self._connection = pymysql.connect(
                host=DB_HOST,
                port=DB_PORT,
                user=DB_USER,
                password=DB_PASSWORD,
                database=DB_NAME,
                charset=DB_CHARSET,
                cursorclass=pymysql.cursors.DictCursor
            )
            self.is_alive = True
            self._connection.close()
            self._connection = None
        except Exception as error:
            self.is_alive = False
            raise ConnectionError(str(error))

    def __del__(self):
        try:
            self._connection.close()
        except Exception as error:
            self.error_report = error
            return

    def connect(self) -> str:
        """
        Connecting to DB, raise Error if database is not alive
        If connect successful - returns DB config
        """
        try:
            self._connection = pymysql.connect(
                host=DB_HOST,
                port=DB_PORT,
                user=DB_USER,
                password=DB_PASSWORD,
                database=DB_NAME,
                charset=DB_CHARSET,
                cursorclass=pymysql.cursors.DictCursor
            )
            self.is_alive = True

            return f'Connected to {DB_NAME} | HOST: {DB_HOST} | PORT: {DB_PORT} |'

        except Exception as error_data:
            raise ConnectionError(str(error_data))

    def connection_proc(self, process) -> None:
        """
        Executing function results into mysql
        """
        try:
            with self._connection.cursor() as self.cursor:
                conn_process = process
                self.cursor.execute(conn_process)
        except Exception as error_data:
            raise ValueError('(RequestError): ' + str(error_data))

    def select(self, table_name: str = 'None', id: str = 'None', subject: str = '*', criterion: str = 'id'):
        """
        Returns selected data from selected Table
        """
        if table_name == 'None':
            raise ValueError(f'Table not specified in module "{self}.select"')

        if id == 'None':
            self.connection_proc(f"SELECT {subject} FROM `{table_name}`")
            return self.cursor.fetchall()

        self.connection_proc(f"SELECT {subject} FROM `{table_name}` WHERE {criterion} = '{id}'")
        return self.cursor.fetchall()

    def update(self, table_name: str = 'user', id: str = 'None', subject: str = None,
               subject_value=None, criterion: str = 'id') -> str:
        """
        Rewrite old data to new
        """
        if table_name == 'None':
            raise ValueError(f'Table not specified in module "{self}.update"')

        if subject_value is None or subject is None:
            raise ValueError(f'Update func doesnt get any type of data to update in module "{self}.update"')

        if subject == 'user_data' and table_name == 'connection':
            with self._connection.cursor() as self.cursor:
                conn_process = f"UPDATE `{table_name}` SET {subject} = %s WHERE `{criterion}` = '{id}'"
                arguments = (subject_value, )
                self.cursor.execute(conn_process, arguments)
            self._connection.commit()
            return f'Updated data in `{table_name}`["{subject}" = "bytes"] for {criterion}[{id}]'

        if id == 'None':
            self.connection_proc(f"UPDATE `{table_name}` SET {subject} = '{subject_value}'")
            self._connection.commit()
            return f'Updated data in `{table_name}`["{subject}" = "{subject_value}"] for all IDs'

        self.connection_proc(f"UPDATE `{table_name}` SET `{subject}` = '{subject_value}' WHERE `{criterion}` = '{id}'")
        self._connection.commit()
        return f'Updated data in `{table_name}`["{subject}" = "{subject_value}"] for {criterion}[{id}]'

    def update_binary(self, table_name: str = 'user', id: str = 'None', subject: str = None,
                      subject_value: bytes = None, criterion: str = 'id') -> str:
        if table_name is None:
            raise ValueError(f'Table not specified in module "{self}.update"')

        if subject_value is None or subject is None:
            raise ValueError(f'Update func doesnt get any type of data to update in module "{self}.update"')

        with self._connection.cursor() as self.cursor:
            conn_process = f"UPDATE `{table_name}` SET {subject} = %s WHERE `{criterion}` = '{id}'"
            arguments = (subject_value,)
            self.cursor.execute(conn_process, arguments)
        self._connection.commit()
        return f'Updated data in `{table_name}`["{subject}" = "bytes"] for {criterion}[{id}]'

    def create(self, status: str = 'table', name: str = 'example', table_args: set[str] = None) -> str:
        """
        Create table or Database
        """
        if table_args is None:
            table_args = ('Row1 INT', 'Row2 VARCHAR(59)')  # standard values to create

        if status == 'database':
            self.connection_proc(f"CREATE {status.upper()} `{name}`")
            self._connection.commit()
            return f'Created {status.upper()} with name[{name}]'

        elif status == 'table':
            self.connection_proc(f"CREATE {status.upper()} `{name}` ({', '.join(table_args)})")
            self._connection.commit()
            return (f'Created {status.upper()} with name[{name}]\n'
                    f'Args: [{", ".join(table_args)}]')

        else:
            raise ValueError('Incorrect type of status, must be ("table", "database")')

    def insert(self, table_name: str = 'user', subject_values=None) -> str:
        """
        Insert row of data in table
        """

        table_elements = self.DB_TABLE_ELEMENTS.get(table_name)
        try:
            if table_name == 'user':
                del subject_values['id']
                table_elements.remove('id')
        except ValueError:
            pass

        if subject_values is None:
            raise ValueError("Subject values must be dict, not NoneType object")

        if len(subject_values) != len(table_elements):
            raise ValueError("Not enough values to make INSERT func")

        request = map(lambda x: f"'{str(x)}'", subject_values.values())
        request_to = f"INSERT INTO `{table_name}` ({', '.join(table_elements)}) VALUES ({', '.join(list(request))});"
        self.connection_proc(request_to)
        self._connection.commit()
        return f"Inserted data in table {table_name}"

    def delete(self, table_name: str = None, id: str = None, criterion: str = 'id') -> str:
        """
        Delete Data from specified table
        """
        if table_name is None or id is None:
            raise ValueError(f"Not enough data for module {self}.delete")

        self.connection_proc(f"DELETE FROM `{table_name}` WHERE {criterion} = '{id}'")
        self._connection.commit()
        return f"Deleted data from table:`{table_name}` where {criterion}:'{id}'"

    def registrate_user(self, user_data):
        user_data = self.configure_data(user_data, 'User')
        self.insert(table_name='user', subject_values=user_data)

        user_id = self.select(
            table_name='user', id=user_data.get('login'), subject='id', criterion='login')[0].get('id')

        user_social_data = self.configure_data({'id': user_id}, 'Social')
        self.insert(table_name='social', subject_values=user_social_data)

        return self.select(table_name='user', id=user_id)[0]

    def configure_data(self, data: dict | None = None, config: str | None = None) -> dict:
        """
        Adding missing elements of data using class.__dict__
        """
        data_config = self.DATA_CONFIGURES.get(config)()
        data_config.set_exist_items(data)
        return data_config.__dict__

    def login_exist(self, login: str) -> bool:
        logins = self.select(table_name='user', subject='login')
        for el in logins:
            if el.get('login') == login:
                return True
        return False

    def id_exist(self, id: str) -> bool:
        ids = self.select(table_name='user', subject='id')
        for el in ids:
            if str(el.get('id')) == str(id):
                return True
        return False

    def is_user_online(self, id: str) -> bool:
        ids = self.select(table_name='connection', subject='id')
        for el in ids:
            if el.get('id') == id:
                return True
        return False

    def save_image(self, user_social, image_type, image_bytes, post=None, chat=None) -> None:
        current_path = '\\'.join(str(pathlib.Path().resolve()).split('\\')[:-1]) + '\\DATABASE'
        path = current_path + f"\\{image_type}_storage\\{user_social.get('id')}.png"
        with open(path, 'wb') as image:
            image.write(image_bytes)
        if post is None and chat is None:
            self.update(table_name='social', id=user_social.get('id'), subject='pfp',
                        subject_value=f"\\\\{image_type}_storage\\\\{user_social.get('id')}.png")

    @staticmethod
    def load_image(image_path) -> bytes:
        current_path = '\\'.join(str(pathlib.Path().resolve()).split('\\')[:-1]) + '\\DATABASE'
        path = current_path + image_path
        with open(path, 'rb') as image:
            image_bytes = image.read()
        return image_bytes

    def load_messages(self, user_id, friend_id) -> list:
        user_id = str(user_id)
        friend_id = str(friend_id)
        from_ = []
        from__ = self.select(table_name='message', criterion='from_', id=user_id)
        for el in from__:
            if str(el.get('to_')) == friend_id:
                from_.append(el)
        to_ = []
        to__ = self.select(table_name='message', criterion='to_', id=user_id)
        for el in to__:
            if str(el.get('from_')) == friend_id:
                to_.append(el)
        messages = [el for el in from_] + [el for el in to_]
        messages_s = []
        for el in messages:
            el['id'] = int(el.get('id'))
            messages_s.append(el)
        messages = messages_s
        if messages is None:
            messages = []
        messages.sort(key=itemgetter('id'))
        messages_s = []
        for el in messages:
            el['id'] = str(el.get('id'))
            messages_s.append(el)
        messages = messages_s
        return messages

import re


class User:

    def __init__(self, login, password, email):
        self.methods = {}
        for key, value in User.__dict__.items():
            if key[:2] != '__' and key[-2:] != '__':
                self.methods[f"<{key.upper().replace('_', '-')}>"] = key

        self.login = login
        self.password = password
        self.email = email

    def __str__(self) -> str:
        return f"Login:{self.login}|Password:{self.password}|Email:{self.email}"

    def __getattr__(self, item) -> str:
        return f"Attribute '{item}' does not exist."

    def __setattr__(self, key, value) -> None:
        if key == 'methods':
            self.__dict__[key] = value
            return
        if not self.call_method(f"<{key.upper()}>")(value):
            raise ValueError
        self.__dict__[key] = value

    def call_method(self, method: str = None):
        """
        Return object of class method

        <- str[<EMAIL>]
        if exist
            -> class method["method"]
        else
            raise error
        """
        method_call = self.methods.get(method)
        if method_call is None:
            return False
        return getattr(self, method_call)

    @classmethod
    def email(cls, data: str = None) -> bool:
        if type(data) is not str:
            return False
        if not cls.check_data(data):
            return False
        pattern = r"([A-Za-z0-9]+[.-_])*[A-Za-z0-9]+@[A-Za-z0-9-]+(\.[A-Z|a-z]{2,})"
        match = re.fullmatch(pattern, data)
        if match is not None:
            return True
        else:
            return False

    @classmethod
    def login(cls, data: str = None) -> bool:
        return cls.check_data(data) and cls.alphabet(data)

    @classmethod
    def password(cls, data: str = None) -> bool:
        return cls.check_data(data) and cls.alphabet(data)

    @classmethod
    def check_data(cls, data: str = None) -> bool:
        if data.isspace():
            return False
        if data == '':
            return False
        return True

    @classmethod
    def alphabet(cls, data: str = None) -> bool:
        """
        If the string consists of [A-Z][a-z][0-9] return True
        else return False

        data: str
        return -> bool
        """
        if type(data) is not str:
            return False
        pattern = r"[a-zA-Z0-9]+"
        match = re.fullmatch(pattern, data)
        if match is None:
            return False
        return True


if __name__ == '__main__':
    user = User('Ivankov', 'iva123456', 'ivachan2011@gmail.com')
    print(user)
    print('ok')


class User:

    def __init__(self):
        self.id = None
        self.ip = None
        self.online = 'False'
        self.login = None
        self.password = None
        self.email = None
        self.gender = None
        self.name = None
        self.status = None

    def set_items(self, items):
        if len(self.__dict__.items()) != len(items.items()):
            raise ValueError('Items length doesnt match to self.__dict__')
        self.__dict__ = items


class Social:

    def __init__(self):
        self.id = None
        self.posts = None
        self.friends = None
        self.messages = None
        self.request_friends = None
        self.black_list_friends = None

    def set_items(self, items):
        if len(self.__dict__.items()) != len(items.items()):
            raise ValueError('Items length doesnt match to self.__dict__')
        self.__dict__ = items


if __name__ == '__main__':
    ...
    # user = Social()
    # test = {'id': 24, 'login': 'testFunction', 'password': 'password123'}
    # example = user.__dict__
    # print(example)
    # for key, value in test.items():
    #     if key not in example.keys():
    #         continue
    #     example[key] = value
    # print(example)
    # user = User()
    # print(user.__dict__)
    # user.set_items({'login': 'Ivankov', 'password': 'iva123456', 'gender': 'Male', 'email': 'ivachan@gmail.com'})
    # print(user.__dict__)

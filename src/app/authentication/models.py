
class User:
    """ stores token info """
    def __init__(self, email: str, user_id, permissions):
        self.email = email
        self.user_id = user_id
        self.permissions = permissions
        self.username = self.email
        self.is_authenticated = True

    def json(self):
        return vars(self)

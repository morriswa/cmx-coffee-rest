
from django.conf import settings


class User:
    """ stores token info """
    def __init__(self, email: str, user_id, jwt_perms, vendor_id):
        self.email = email
        self.user_id = user_id
        self.vendor_id = vendor_id
        self.username = self.email
        self.is_authenticated = True
        self.__build_perms(jwt_perms)

    def __build_perms(self, jwt_perms):
        self.permissions = jwt_perms + settings.USER_PERMISSIONS
        if self.vendor_id is not None:
            self.permissions += settings.VENDOR_PERMISSIONS

    def json(self):
        return vars(self)

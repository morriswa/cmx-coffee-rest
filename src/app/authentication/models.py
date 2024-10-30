
import uuid

from django.conf import settings


class User:
    """ represents a user and stores important authentication info """
    def __init__(self, **kwargs):
        self.user_id: uuid = kwargs.get('user_id')
        self.email: str = kwargs.get('email')
        self.username: str = self.email

        self.vendor_id: int = kwargs.get('vendor_id')
        self.__jwt_permissions: list[str] = kwargs.get('jwt_permissions') or []

    def json(self):
        return vars(self)

    @property
    def permissions(self) -> list[str]:
        # add token permissions
        perms = self.__jwt_permissions

        # if user_id is present, grant user permissions
        if self.user_id is not None:
            perms += settings.USER_PERMISSIONS

        # if vendor_id is present, grant vendor permissions
        if self.vendor_id is not None:
            perms += settings.VENDOR_PERMISSIONS

        return perms

    @property
    def is_authenticated(self) -> bool:
        # users without an id, email, or username will not be considered authenticated
        return (self.user_id is not None
                and self.email is not None
                and self.username is not None)

from typing import override

from django.conf import settings
from rest_framework.permissions import BasePermission

from app.authentication import jwt_has_permissions, JwtUser


class HasAdminPermission(BasePermission):
    """ django permission class to check if a user has admin access """

    @override
    def has_permission(self, request, view) -> bool:
        user: JwtUser = request.user
        # retrieve decoded token from user obj
        decoded = user.token
        # checks if admin scope is on the verified token
        return jwt_has_permissions(decoded, [settings.ADMIN_PERMISSION])

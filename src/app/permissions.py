from typing import override

from django.conf import settings
from rest_framework.permissions import BasePermission

from app.authentication import jwt_has_scope, JwtUser


class HasAdminPermission(BasePermission):

    @override
    def has_permission(self, request, view):
        user: JwtUser = request.user
        print(user.token)
        decoded = user.token
        return jwt_has_scope(decoded, [settings.ADMIN_SCOPE])

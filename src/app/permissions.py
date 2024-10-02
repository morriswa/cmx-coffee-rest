from typing import override

from rest_framework.permissions import BasePermission

from app.authentication import jwt_has_scope, JwtUser


ADMIN_SCOPE = 'cmx_coffee:admin'



class HasAdminPermission(BasePermission):

    @override
    def has_permission(self, request, view):
        user: JwtUser = request.user
        print(user.token)
        decoded = user.token
        return jwt_has_scope(decoded, [ADMIN_SCOPE])

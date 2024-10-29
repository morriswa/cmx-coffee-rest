import logging
from typing import override

from django.conf import settings
from rest_framework.permissions import BasePermission, IsAuthenticated
from rest_framework import exceptions

from app.authentication import User


def has_permissions(user_permissions, required_permissions):

    has_all_permissions = True

    for permission in required_permissions:
        # make sure all required permissions are present in token's provided permission array
        if permission not in user_permissions:
            has_all_permissions = False

    return has_all_permissions


def WithPermissions(permissions):
    class HasPermission(BasePermission):
        @override
        def has_permission(self, request, view) -> bool:
            allowed = isinstance(request.user, User) and has_permissions(request.user.permissions, permissions)
            if not allowed:
                logging.warn(f'SECURITY WARNING: user {request.user.user_id} with email {request.user.email} attempted to access an endpoint '
                             f'that requires permissions: {permissions}... access denied')
            return allowed

    return HasPermission

import logging
import jwt

from functools import wraps

from django.conf import settings
from rest_framework.response import Response
from rest_framework.decorators import permission_classes, authentication_classes, api_view

from app.exceptions import APIException
from app.authentication import User
from app.permissions import has_permissions


def requires_permissions(
        required_permissions: list[str],
        or_else_error = 'You don\'t have access to this resource'
):
    """Determines if the required scope is present in the Access Token
        Args:
            required_scope (str): The scope required to access the resource
        Source: https://auth0.com/docs/quickstart/backend/django/01-authorization
    """
    def require_permissions(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            request = args[0]
            if isinstance(request.user, User) and has_permissions(request.user.permissions, required_permissions):
                return f(*args, **kwargs)
            else:
                return Response(status=403, data={'msg': or_else_error})

        return decorated

    return require_permissions


def __customized_view(methods, permission_clazzes, authentication_clazzes):
    """ view for unsecured requests
     includes error handling from morriswa package"""
    def wrapper(func):
        return api_view(methods)(
            # override w_view to use no permission or authentication guards
            permission_classes(permission_clazzes)(
                authentication_classes(authentication_clazzes)(
                    func
                )
            )
        )

    return wrapper


def any_view(methods):
    """ view for unsecured requests
     includes error handling from morriswa package"""
    return __customized_view(methods, [], [])


def user_view(methods):
    """ view for secured requests
        includes error handling from morriswa package"""
    return __customized_view(
        methods,
        settings.DJANGO_USER_PERMISSION_CLASSES,
        settings.DJANGO_USER_AUTHENTICATION_CLASSES
    )


def admin_view(methods):
    """ view for secured requests
        includes error handling from morriswa package"""
    return __customized_view(
        methods,
        settings.DJANGO_ADMIN_PERMISSION_CLASSES,
        settings.DJANGO_USER_AUTHENTICATION_CLASSES
    )

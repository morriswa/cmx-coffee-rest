import logging
import jwt

from functools import wraps

from rest_framework.response import Response
from rest_framework.decorators import permission_classes, authentication_classes, api_view
from rest_framework.permissions import IsAuthenticated

from app.exceptions import APIException
from app.authentication import JwtUser, jwt_has_permissions
from app.permissions import HasAdminPermission


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
            user: JwtUser = request.user
            decoded = user.token
            if jwt_has_permissions(decoded, required_scopes):
                return f(*args, **kwargs)
            else:
                return Response(status=403, data={'msg': or_else_error})

        return decorated

    return require_permissions

def any_view(methods):
    """ view for unsecured requests
     includes error handling from morriswa package"""
    def wrapper(func):
        return api_view(methods)(
            # override w_view to use no permission or authentication guards
            permission_classes([])(
                authentication_classes([])(
                    func
                )
            )
        )

    return wrapper

def secure_view(methods):
    """ view for secured requests
        includes error handling from morriswa package"""
    def wrapper(func):
        return api_view(methods)(func)

    return wrapper

def admin_view(methods):
    """ view for secured requests
        includes error handling from morriswa package"""

    def wrapper(func):
        return api_view(methods)(
            permission_classes([HasAdminPermission])(
                func
            )
        )

    return wrapper

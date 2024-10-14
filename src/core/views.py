import json
import logging

from django.conf import settings
from rest_framework.request import Request
from rest_framework.response import Response

from app.decorators import any_view, secure_view, admin_view, user_view
from app.views import AdminView
from app.authentication import JwtUser

import core.daos as dao


@any_view(['GET'])
def health(request: Request) -> Response:
    """ health endpoint to test any_view """
    #returns a simple JSON response with message hello world
    return Response({
        "msg": "hello world!"
    }, status=200)

@secure_view(['GET'])
def secure_health(request: Request) -> Response:
    """ health endpoint to test any_view """
    #returns a simple JSON response with message hello world

    user: JwtUser = request.user

    return Response({
        "msg": "hello jwt world!",
        "decoded_jwt": user.token
    }, status=200)

@admin_view(['GET'])
def admin_secure_health(request: Request) -> Response:
    """ health endpoint to test any_view """
    #returns a simple JSON response with message hello world
    return Response({
        "msg": "hello admin world!",
        "decoded_jwt": request.user.token
    }, status=200)

@secure_view(['GET'])
def login(request: Request) -> Response:
    """ health endpoint to test any_view """
    #returns a simple JSON response with message hello world

    user: JwtUser = request.user

    dao.register(user.username)

    perms = user.token.get('permissions') or []

    perms.append(settings.VENDOR_PERMISSION)

    return Response({
        "permissions": perms
    }, status=200)

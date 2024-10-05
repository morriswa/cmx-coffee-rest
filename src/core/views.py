import json
import logging

from rest_framework.request import Request
from rest_framework.response import Response

from app.decorators import any_view, secure_view, admin_view
from app.views import AdminView
from app.authentication import JwtUser


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

    logging.info(user.token)

    perms = user.token.get('permissions') or []

    logging.info(perms)

    return Response({
        "permissions": perms
    }, status=200)

import json
import logging

from rest_framework.request import Request
from rest_framework.response import Response

# from app.auth0authorization import jwt_decode_token
from app.decorators import any_view, secure_view, admin_view
from app.views import AdminView


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

    return Response({
        "msg": "hello jwt world!",
        "jwt": request.user.token
    }, status=200)

@admin_view(['GET'])
def admin_secure_health(request: Request) -> Response:
    """ health endpoint to test any_view """
    #returns a simple JSON response with message hello world
    return Response({
        "msg": "hello admin world!",
        "jwt": request.user.token
    }, status=200)

class AdminSecureHealthView(AdminView):
    @staticmethod
    def get(request: Request) -> Response:
        """ health endpoint to test any_view """
        #returns a simple JSON response with message hello world
        return Response({
            "msg": "hello admin world 2!",
            "jwt": request.user.token
        }, status=200)

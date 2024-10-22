import json
import logging

from django.conf import settings
from rest_framework.request import Request
from rest_framework.response import Response

from app.decorators import any_view, admin_view, user_view
from app.views import AdminView
from app.authentication import User



@any_view(['GET'])
def health(request: Request) -> Response:
    """ health endpoint to test any_view """
    #returns a simple JSON response with message hello world
    return Response({
        "msg": "hello world!"
    }, status=200)

@user_view(['GET'])
def permissions(request: Request) -> Response:
    return Response(request.user.permissions, status=200)

from typing import override

from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from app.authentication import UserAuthenticationWithJwt
from app.permissions import HasAdminPermission


class AnyView(APIView):
    """ inherit this class to create a view for unsecured requests
     includes error handling from morriswa package"""
    authentication_classes = []
    permission_classes = []

class SecureView(APIView):
    pass

class UserView(APIView):
    permission_classes = []
    authentication_classes = [UserAuthenticationWithJwt]

class AdminView(APIView):
    permission_classes = [HasAdminPermission]

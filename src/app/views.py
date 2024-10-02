from typing import override

from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from app.decorators import requires_scope
from app.permissions import HasAdminPermission


class AnyView(APIView):
    """ inherit this class to create a view for unsecured requests
     includes error handling from morriswa package"""
    authentication_classes = []
    permission_classes = []

class SecureView(APIView):
    pass

class AdminView(APIView):
    permission_classes = [HasAdminPermission]

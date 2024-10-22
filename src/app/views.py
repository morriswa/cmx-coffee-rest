from typing import override

from django.conf import settings
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView


class AnyView(APIView):
    """ inherit this class to create a view for unsecured requests
     includes error handling from morriswa package"""
    authentication_classes = []
    permission_classes = []

class UserView(APIView):
    permission_classes = settings.DJANGO_USER_PERMISSION_CLASSES
    authentication_classes = settings.DJANGO_USER_AUTHENTICATION_CLASSES

class AdminView(APIView):
    permission_classes = settings.DJANGO_ADMIN_PERMISSION_CLASSES
    authentication_classes = settings.DJANGO_USER_AUTHENTICATION_CLASSES

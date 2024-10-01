from typing import override

from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from app.decorators import app_exception_handler, requires_scope


class _ErrorHandlingView(APIView):
    """ class to provide a Django View
    and handle exceptions provided by this package """
    @override
    @app_exception_handler
    def handle_exception(self, *args, **kwargs):
        return super(_ErrorHandlingView, self).handle_exception(*args, **kwargs)

class AnyView(_ErrorHandlingView):
    """ inherit this class to create a view for unsecured requests
     includes error handling from morriswa package"""
    authentication_classes = []
    permission_classes = []

class SecureView(_ErrorHandlingView):
    pass

class AdminView(_ErrorHandlingView):
    @override
    @requires_scope(['cmx_coffee:admin'])
    def dispatch(self, request, *args, **kwargs):
        return super(AdminView, self).dispatch(request, *args, **kwargs)

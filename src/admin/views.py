"""
    Admin-related django views (http request actions) go here
"""

from rest_framework.request import Request
from rest_framework.response import Response

from app.decorators import admin_view

import admin.daos as admin_dao

@admin_view(['GET'])
def get_pending_vendor_applications(request: Request) -> Response:
    apps = admin_dao.get_pending_vendor_applications()
    return Response(status=200, data=[app.json() for app in apps])

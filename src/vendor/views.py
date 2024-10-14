"""
    Vendor-related django views (http request actions) go here
"""

from rest_framework.request import Request
from rest_framework.response import Response

from app.decorators import user_view

from vendor.models import VendorApplicationRequest
import vendor.daos as dao

@user_view(['POST'])
def apply_for_vendor(request: Request) -> Response:
    user_id = request.user.user_id
    application = VendorApplicationRequest(**request.data)
    dao.apply_for_vendor(user_id, application)
    return Response(status=200, data=application.json())

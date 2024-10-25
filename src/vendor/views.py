"""
    Vendor-related django views (http request actions) go here
"""
import logging

from rest_framework.request import Request
from rest_framework.response import Response

from app.views import VendorView
from app.decorators import user_view, vendor_view

from vendor.models import VendorApplicationRequest, CreateProductRequest
import vendor.daos as dao


@user_view(['POST'])
def apply_for_vendor(request: Request) -> Response:
    user_id = request.user.user_id
    application = VendorApplicationRequest(**request.data)
    dao.apply_for_vendor(user_id, application)
    return Response(status=200, data=application.json())


class VendorProductView(VendorView):
    @staticmethod
    def get(request: Request) -> Response:
        vendor_id: int = dao.get_vendor_id_associated_with_user(request.user.user_id)
        products = dao.get_products(vendor_id)
        return Response(status=200, data=[product.json() for product in products])

    @staticmethod
    def post(request: Request) -> Response:
        user_id = request.user.user_id
        vendor_id = dao.get_vendor_id_associated_with_user(user_id)
        product_listing = CreateProductRequest(**request.data)
        dao.list_product(vendor_id, user_id, product_listing)
        return Response(status=204)

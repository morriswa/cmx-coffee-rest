"""
    Vendor-related django views (http request actions) go here
"""
import logging
import uuid

from rest_framework.request import Request
from rest_framework.response import Response

from app.views import VendorView
from app.decorators import user_view, vendor_view
from app import s3client

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


class VendorProductDetailsView(VendorView):
    @staticmethod
    def get(request: Request, product_id: int) -> Response:
        vendor_id: int = dao.get_vendor_id_associated_with_user(request.user.user_id)
        product_details = dao.get_product_details(vendor_id, product_id)
        return Response(status=200, data=product_details.json())


class VendorProductImageView(VendorView):
    @staticmethod
    def get(request: Request, product_id: int) -> Response:
        vendor_id: int = dao.get_vendor_id_associated_with_user(request.user.user_id)
        keylist = s3client.list(f'cmx/coffee/public/product/{product_id}')
        images = [s3client.get(key) for key in keylist]
        return Response(status=200, data=images)

    @staticmethod
    def post(request: Request, product_id: int) -> Response:
        vendor_id: int = dao.get_vendor_id_associated_with_user(request.user.user_id)
        image_id = uuid.uuid4()
        key = f'cmx/coffee/public/product/{product_id}/{image_id}'
        s3client.upload(
            request.FILES.get('image_upload'),
            key
        )
        return Response(status=200, data=key)


@vendor_view(['DELETE'])
def delete_product_image(request: Request, product_id: int, image_id: str) -> Response:
    vendor_id: int = dao.get_vendor_id_associated_with_user(request.user.user_id)
    s3client.delete(f'cmx/coffee/public/product/{product_id}/{image_id}')
    return Response(status=204)

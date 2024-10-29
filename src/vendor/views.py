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
from app.exceptions import BadRequestException

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
        vendor_id: int = request.user.vendor_id
        products = dao.get_products(vendor_id)
        return Response(status=200, data=[product.json() for product in products])

    @staticmethod
    def post(request: Request) -> Response:
        user_id = request.user.user_id
        vendor_id: int = request.user.vendor_id
        product_listing = CreateProductRequest(**request.data)
        dao.list_product(vendor_id, user_id, product_listing)
        return Response(status=204)


class VendorProductDetailsView(VendorView):
    @staticmethod
    def get(request: Request, product_id: int) -> Response:
        vendor_id: int = request.user.vendor_id
        # assert logged in vendor has permission to modify product
        dao.assert_vendor_owns_product(vendor_id, product_id)

        product_details = dao.get_product_details(vendor_id, product_id)
        return Response(status=200, data=product_details.json())


@vendor_view(['POST'])
def upload_product_image(request: Request, product_id: int) -> Response:
    vendor_id: int = request.user.vendor_id
    # assert logged in vendor has permission to modify product
    dao.assert_vendor_owns_product(vendor_id, product_id)

    # count images that belong to product
    product_prefix = f'cmx/coffee/public/product/{product_id}'
    image_count = len(s3client.list(product_prefix))
    if image_count >= 10:  # and throw error if the max has been reached
        raise BadRequestException('cannot have more than 10 images for a product, not uploading...')

    # generate uuid for image
    image_id = uuid.uuid4()
    s3client.upload(  # and upload
        request.FILES.get('image_upload'),
        f'{product_prefix}/{image_id}'
    )

    # return generated id
    return Response(status=200, data=image_id)


@vendor_view(['DELETE'])
def delete_product_image(request: Request, product_id: int, image_id: str) -> Response:
    vendor_id: int = request.user.vendor_id
    # assert logged in vendor has permission to modify product
    dao.assert_vendor_owns_product(vendor_id, product_id)

    s3client.delete(f'cmx/coffee/public/product/{product_id}/{image_id}')
    return Response(status=204)

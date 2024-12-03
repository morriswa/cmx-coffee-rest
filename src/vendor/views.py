"""
    Vendor-related django views (http request actions) go here
"""
import logging
import uuid

from rest_framework.request import Request
from rest_framework.response import Response

from app.views import VendorView
from app.decorators import user_view, vendor_view
from app.exceptions import BadRequestException

from vendor.models import VendorApplicationRequest, CreateProductRequest, UpdateProductRequest
import vendor.daos as dao
from vendor import content as vc


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
        vendor_id: int = request.user.vendor_id #line 46
        # assert logged in vendor has permission to modify product
        dao.assert_vendor_owns_product(vendor_id, product_id)

        product_details = dao.get_product_details(vendor_id, product_id)
        return Response(status=200, data=product_details.json()) #line 51

    @staticmethod
    def patch(request: Request, product_id: int) -> Response:
        # make sure vendor owns product
        vendor_id: int = request.user.vendor_id #line 56
        dao.assert_vendor_owns_product(vendor_id, product_id)
        # build datamodel from request.data.get('coffee_bean_characteristics')
        update_product_request = UpdateProductRequest(**request.data)
        # pass datamodel to dao,
        # update existing table data and create if there is none
        dao.updated_existing_product(product_id, update_product_request)
        # return 204 no content resposne
        return Response(status=204) #line 64

    @staticmethod
    def delete(request: Request, product_id: int) -> Response:
        # make sure vendor owns product
        vendor_id: int = request.user.vendor_id #line 69
        dao.assert_vendor_owns_product(vendor_id, product_id)
        # delete product
        dao.unlist_product(product_id)
        # return 204 no content resposne
        return Response(status=204)#line 74


class VendorProductImagesView(VendorView):

    @staticmethod
    def get(request: Request, product_id: int) -> Response:
        dao.assert_vendor_owns_product(request.user.vendor_id, product_id)#line 81
        key_image_pairs = vc.get_product_images_with_keys(product_id)
        return Response(status=200, data=key_image_pairs)#line 83

    @staticmethod
    def post(request: Request, product_id: int) -> Response:
        vendor_id: int = request.user.vendor_id # line 87
        # assert logged in vendor has permission to modify product
        dao.assert_vendor_owns_product(vendor_id, product_id)

        image_id = vc.upload_product_image(product_id, request.FILES.get('image_upload'))
        # return generated id
        return Response(status=200, data=image_id)# line 93


@vendor_view(['DELETE'])
def delete_product_image(request: Request, product_id: int, image_id: str) -> Response:
    vendor_id: int = request.user.vendor_id #line 98
    # assert logged in vendor has permission to modify product
    dao.assert_vendor_owns_product(vendor_id, product_id)
    vc.delete_product_image(product_id, image_id)
    return Response(status=204) # line 102

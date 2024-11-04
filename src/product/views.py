
from rest_framework.request import Request
from rest_framework.response import Response

from app import s3client
from app.decorators import user_view

import product.daos as dao


@user_view(['GET'])
def get_product_images(request: Request, product_id: int) -> Response:
    keylist = s3client.list(f'cmx/coffee/public/product/{product_id}')
    images = [s3client.get(key) for key in keylist]
    return Response(status=200, data=images)

@user_view(['GET'])
def get_products_for_sale(request: Request) -> Response:
    products = dao.get_products_for_sale(request.data)
    return Response(status=200, data=[product.json() for product in products])

@user_view(['GET'])
def get_product_details(request: Request, product_id: int) -> Response:
    product = dao.get_product_details(product_id)
    return Response(status=200, data=product.json())

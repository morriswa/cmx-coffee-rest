
from rest_framework.request import Request
from rest_framework.response import Response

from app import s3client
from app.decorators import any_view

from product.models import BaseProduct
import product.daos as dao


@any_view(['GET'])
def get_product_images(request: Request, product_id: int) -> Response:
    keylist = s3client.list(f'cmx/coffee/public/product/{product_id}')
    images = [s3client.get(key) for key in keylist]
    return Response(status=200, data=images)

@any_view(['GET'])
def get_products_for_sale(request: Request) -> Response:
    products: list[BaseProduct] = dao.get_products_for_sale(request.data, 30)
    products_with_images = []
    for product in products:
        keys = s3client.list(f'cmx/coffee/public/product/{product.product_id}')
        first_image = None
        if len(keys) > 0:
            key = keys[0]
            first_image = s3client.get(key)
            product.first_image = first_image
        products_with_images.append(product)

    return Response(status=200, data=[product.json() for product in products_with_images])

@any_view(['GET'])
def get_product_details(request: Request, product_id: int) -> Response:
    product = dao.get_product_details(product_id)
    return Response(status=200, data=product.json())

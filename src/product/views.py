
from rest_framework.request import Request
from rest_framework.response import Response

from app.decorators import any_view

from product.models import BaseProduct
import product.daos as dao
from product import content


@any_view(['GET'])
def get_product_images(request: Request, product_id: int) -> Response:
    images = content.get_product_images(product_id)
    return Response(status=200, data=images)

@any_view(['GET'])
def get_products_for_sale(request: Request) -> Response:
    products: list[BaseProduct] = dao.get_products_for_sale(request.data, 30)
    products_with_images = []
    for product in products:
        product.first_image = content.get_random_product_image(product.product_id)
        products_with_images.append(product)

    return Response(status=200, data=[product.json() for product in products_with_images])

@any_view(['GET'])
def get_product_details(request: Request, product_id: int) -> Response:
    product = dao.get_product_details(product_id)
    return Response(status=200, data=product.json())

@any_view(['GET'])
def get_featured_products(request: Request) -> Response:
    products = dao.get_featured_products()
    return Response(status=200, data=products.json())


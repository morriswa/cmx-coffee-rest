"""
    Product Review http functions go here
"""
from rest_framework.request import Request
from rest_framework.response import Response

from app import s3client
from app.decorators import any_view

import product.daos as dao

@any_view(['DELETE'])
def delete_product_reviews(request: Request, review_id: int) -> Response:
    dao.delete_product_reviews(review_id)
    return Response(status=204)
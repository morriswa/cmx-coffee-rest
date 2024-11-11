"""
    Product Review http functions go here
"""
from rest_framework.request import Request
from rest_framework.response import Response

from app import s3client
from app.decorators import user_view, any_view

import product.daos as dao
from product.models import CreateProductReview, ProductReview


@any_view(['GET'])
def get_product_reviews(request: Request, product_id: int) -> Response:
    # Retrieve reviews for the specified product
    reviews = dao.get_reviews_for_product(product_id)

    # Serialize reviews into a JSON-friendly format
    review_data = [review.__dict__ for review in reviews]

    return Response(status=200, data=review_data)

@user_view(['POST'])
def add_product_review(request: Request) -> Response:
    # Validate and parse input data
    review_data = CreateProductReview(**request.data)

    # Call DAO function to save review in the database
    dao.save_product_review(review_data)

    return Response(status=204)  # No Content, indicating success

@user_view(['DELETE'])
def delete_product_reviews(request: Request, review_id: int) -> Response:
    dao.delete_product_reviews(review_id)
    return Response(status=204)

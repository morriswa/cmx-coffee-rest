"""
    Product Review http functions go here
"""
from rest_framework.request import Request
from rest_framework.response import Response

from app.decorators import user_view, any_view

from . import daos
from .models import CreateProductReview, ProductReview


@user_view(['POST'])
def add_product_review(request: Request) -> Response:
    # Validate and parse input data
    review_data = CreateProductReview(**request.data)

    # Call DAO function to save review in the database
    daos.save_product_review(review_data)

    return Response(status=204)  # No Content, indicating success


@any_view(['GET'])
def get_product_reviews(request: Request, product_id: int) -> Response:
    # Retrieve reviews for the specified product
    reviews = daos.get_reviews_for_product(product_id)

    # Serialize reviews into a JSON-friendly format
    review_data = [review.__dict__ for review in reviews]

    return Response(status=200, data=review_data)

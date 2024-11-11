"""
    Product Review http functions go here
"""
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.decorators import api_view
from . import daos
from .models import CreateProductReview, ProductReview


@api_view(['POST'])
def add_product_review(request: Request) -> Response:
    try:
        # Validate and parse input data
        review_data = CreateProductReview(**request.data)
        
        # Call DAO function to save review in the database
        daos.save_product_review(review_data)
        
        return Response(status=204)  # No Content, indicating success
    except ValidationException as e:
        return Response(status=400, data={'errors': str(e)})
    except Exception as e:
        return Response(status=500, data={'error': 'Internal server error'})


@api_view(['GET'])
def get_product_reviews(request: Request, product_id: int) -> Response:
    try:
        # Retrieve reviews for the specified product
        reviews = daos.get_reviews_for_product(product_id)
        
        # Serialize reviews into a JSON-friendly format
        review_data = [review.__dict__ for review in reviews]
        
        return Response(status=200, data=review_data)
    except Exception as e:
        return Response(status=500, data={'error': 'Internal server error'})

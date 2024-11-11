"""
    Product Review database functions go here
"""
from .models import ProductReview
from app import connections
import logging


def save_product_review(review_data: ProductReview):
    query = """
        INSERT INTO product_reviews (user_id, product_id, review_text, review_score)
        VALUES (%(user_id)s, %(product_id)s, %(review_text)s, %(review_score)s)
    """
    params = {
        'user_id': review_data.user_id,
        'product_id': review_data.product_id,
        'review_text': review_data.review_text,
        'review_score': review_data.review_score
    }
    with connections.cursor() as cur:
        try:
            cur.execute(query, params)
        except Exception as e:
            logging.error("Error saving review: %s", e)
            raise e


def get_reviews_for_product(product_id: int):
    query = """
        SELECT review_id, user_id, product_id, review_text, review_score
        FROM product_reviews
        WHERE product_id = %(product_id)s
    """
    params = {'product_id': product_id}
    reviews = []
    with connections.cursor() as cur:
        try:
            cur.execute(query, params)
            rows = cur.fetchall()
            for row in rows:
                reviews.append(ProductReview(
                    review_id=row['review_id'],
                    user_id=row['user_id'],
                    product_id=row['product_id'],
                    review_text=row['review_text'],
                    review_score=row['review_score']
                ))
        except Exception as e:
            logging.error("Error retrieving reviews: %s", e)
            raise e
    return reviews

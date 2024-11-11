"""
    Product Review database functions go here
"""

import logging
import decimal

from psycopg2 import errors

from app import connections

from .models import BaseProduct

def delete_user_product_reviews(review_id: int):
    with connections.cursor() as cur:
        cur.execute("""
        DELETE FROM product_review 
        WHERE review_id = %(review_id)s
        """), {'review_id': review_id}
import logging

from app import connections

from .models import ProductReview


def save_product_review(review_data: ProductReview):
    query = """
        INSERT INTO product_reviews
            (user_id, product_id, review_text, review_score)
        VALUES
            (%(user_id)s, %(product_id)s, %(review_text)s, %(review_score)s)
    """
    params = {
        'user_id': review_data.user_id,
        'product_id': review_data.product_id,
        'review_text': review_data.review_text,
        'review_score': review_data.review_score
    }
    with connections.cursor() as cur:
        cur.execute(query, params)



def get_reviews_for_product(product_id: int):
    query = """
        SELECT review_id, user_id, product_id, review_text, review_score
        FROM product_reviews
        WHERE product_id = %(product_id)s
    """
    params = {'product_id': product_id}
    reviews = []
    with connections.cursor() as cur:
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

    return reviews

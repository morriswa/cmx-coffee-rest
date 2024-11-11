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
"""
    Product Review database functions go here
"""

from app import connections

from product_review.models import ProductReview, ProductStats


def get_product_review_stats(product_id: int):
    with connections.cursor() as cur:
        cur.execute("""
            SELECT
                COUNT(review_id) review_count,
                AVG(review_score) average_review_score
            FROM product_reviews
            WHERE product_id = %(product_id)s
        """,{
            'product_id': product_id
        })
        result = cur.fetchone()
        return ProductStats(**result)


def delete_product_review(user_id, product_id: int, review_id: int):
    with connections.cursor() as cur:
        cur.execute("""
            DELETE FROM product_reviews
            WHERE   review_id = %(review_id)s
            AND     product_id = %(product_id)s
            AND     user_id = %(user_id)s
        """, {
            'review_id': review_id,
            'product_id': product_id,
            'user_id': user_id
        })


def save_product_review(user_id, product_id, review_data: ProductReview):
    query = """
        INSERT INTO product_reviews
            (user_id, product_id, review_text, review_score)
        VALUES
            (%(user_id)s, %(product_id)s, %(review_text)s, %(review_score)s)
    """
    params = {
        'user_id': user_id,
        'product_id': product_id,
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
            reviews.append(ProductReview(**row))

    return reviews

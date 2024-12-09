
import logging
import decimal

from psycopg2 import errors

from app import connections
from app.exceptions import BadRequestException

from .models import BaseProduct


def get_products_for_sale(filters = {}, limit = 10):

    # initial query and params
    query = """
        select
            product.product_id,
            product.product_name,
            product.description,
            product.initial_price price,
            pdetails.cb_taste_strength as taste_strength,
            pdetails.cb_decaf as decaf,
            pdetails.cb_flavored as flavored,
            pdetails.cb_single_origin as single_origin,
            v.vendor_id,
            v.business_name
        from vendor_product product
            left join product_characteristics pdetails
                on product.product_id = pdetails.product_id
            left join vendor v
                on product.vendor_id = v.vendor_id
        where product.status = 'A'
    """
    params = {'limit': limit}

    # build where clause based on requested filters
    if filters.get('decaf') is not None:
        if filters['decaf'] == 'y':
            query += " and cb_decaf = 'y' "
        else:
            query += " and cb_decaf = 'n' "

    if filters.get('flavored') is not None:
        if filters['flavored'] == 'y':
            query += " and cb_flavored = 'y' "
        else:
            query += " and cb_flavored = 'n' "

    if filters.get('single_origin') is not None:
        if filters['single_origin'] == 'y':
            query += " and cb_single_origin = 'y' "
        else:
            query += " and cb_single_origin = 'n' "

    if filters.get('taste_strength') is not None:
        query += " and cb_taste_strength in %(taste_strengths)s "
        params['taste_strengths'] = tuple(filters['taste_strength'])

    query += " limit %(limit)s"

    with connections.cursor() as cur:
        try:
            cur.execute(query, params)
        except errors.SyntaxError as se:
            logging.error(
                "SECURITY WARNING: "
                "invalid query attempted to execute on database "
                "in function get_products_for_sale"
            )
            raise se

        res = cur.fetchall()
        products = []
        for data in res:
            products.append(BaseProduct(**data))
        return products

def get_product_details(product_id: int):
    with connections.cursor() as cur:
        cur.execute("""
            select
                product.product_id,
                product.product_name,
                product.description,
                product.initial_price price,
                pdetails.cb_decaf as decaf,
                pdetails.cb_flavored as flavored,
                pdetails.cb_single_origin as single_origin
            from vendor_product product
                left join product_characteristics pdetails
                    on product.product_id = pdetails.product_id
                left join vendor v
                    on product.vendor_id = v.vendor_id
            where product.product_id = %(product_id)s
        """, {
            'product_id': product_id
        })

        data = cur.fetchone()
        if data is None:
            raise BadRequestException(f'could not find product {product_id}')

        return BaseProduct(**data)
    

def get_featured_products(product: int):
    with connections.cursor() as cur: 
        cur.execute("""
           select
                product.product_id,
                product.product_name,
                product.description,
                product.initial_price price,
                pdetails.cb_decaf as decaf,
                pdetails.cb_flavored as flavored,
                pdetails.cb_single_origin as single_origin
            from vendor_product product
                left join product_characteristics pdetails
                    on product.product_id = pdetails.product_id
                left join vendor v
                    on product.vendor_id = v.vendor_id
                left join product_review review
                    on product.product_id = review.product_id
                where product.status = 'A'
                    
            GROUP BY(product.product_id, 
                    pdetails.cb_decaf, 
                    pdetails.cb_flavored, 
                    pdetails.cb_single_origin)
            HAVING AVG(review.review_score) > 3.5
                    ORDER BY RANDOM() LIMIT 2  
        """)
        res = cur.fetchall()
        products = []
        for data in res:
            products.append(BaseProduct(**data))
        return products
    
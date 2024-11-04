
import logging
import decimal

from psycopg2 import errors

from app import connections

from .models import BaseProduct


def get_products_for_sale(filters = {}, limit = 10):

    # initial query and params
    query = """
        select
            product.product_id,
            product.product_name,
            product.description,
            product.initial_price,
            pdetails.cb_decaf as decaf,
            pdetails.cb_flavored as flavored,
            pdetails.cb_single_origin as single_origin
        from vendor_product product
        left join product_characteristics pdetails
        on product.product_id = pdetails.product_id
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
            initial_price: decimal.Decimal = data['initial_price']
            price = initial_price * decimal.Decimal(1.2)
            price = price.quantize(decimal.Decimal('1.00'), rounding=decimal.ROUND_UP)
            products.append(BaseProduct(**data, price=price,))
        return products

def get_product_details(product_id: int):
    with connections.cursor() as cur:
        cur.execute("""
            select
                product.product_id,
                product.product_name,
                product.description,
                product.initial_price,
                pdetails.cb_decaf as decaf,
                pdetails.cb_flavored as flavored,
                pdetails.cb_single_origin as single_origin
            from vendor_product product
            left join product_characteristics pdetails
            on product.product_id = pdetails.product_id
            where product.product_id = %(product_id)s
        """, {
            'product_id': product_id
        })

        data = cur.fetchone()
        initial_price: decimal.Decimal = data['initial_price']
        price = initial_price * decimal.Decimal(1.2)
        price = price.quantize(decimal.Decimal('1.00'), rounding=decimal.ROUND_UP)

        return BaseProduct(**data, price=price)

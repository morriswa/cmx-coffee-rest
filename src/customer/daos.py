import logging
import uuid

from app import connections
from app.connections import cursor
from app.exceptions import BadRequestException

from .models import CartItem, CustomerPreferences


def get_shopping_cart(user_id: uuid) -> list[CartItem]:
    with connections.cursor() as cur:  # open a database cursor
        # retrieve and return latest shopping cart entries
        cur.execute("""
            select * from shopping_cart
            where user_id = %(user_id)s
        """, {
            'user_id': user_id
        })
        rows = cur.fetchall()
        return [CartItem(row['product_id'], row['quantity']) for row in rows]

def update_shopping_cart(user_id: uuid, items: list[CartItem]) -> list[CartItem]:
    with connections.cursor() as cur:   # open a database cursor
        for item in items:   # for every item in the cart...
            # check if the item is already present in the user's cart
            cur.execute("""
                select id
                from shopping_cart
                where       user_id = %(user_id)s
                       and  product_id = %(product_id)s
            """,{
                'user_id': user_id,
                'product_id': item.product_id
            })
            res = cur.fetchone()

            if res is None:  # if product is not in cart add it
                cur.execute("""
                    insert into shopping_cart
                        (user_id, product_id, quantity)
                    values
                        (%(user_id)s, %(product_id)s, %(quantity)s)
                """, {
                    'user_id': user_id,
                    'product_id': item.product_id,
                    'quantity': item.quantity
                })
            else:  # if product is in cart, modify with new quantity
                cur.execute("""
                    update shopping_cart
                    set
                        quantity = %(quantity)s
                    where user_id = %(user_id)s
                      and product_id = %(product_id)s
                """, {
                    'user_id': user_id,
                    'product_id': item.product_id,
                    'quantity': item.quantity
                })

def reset_shopping_cart(user_id: uuid):
    with connections.cursor() as cur:
        cur.execute("delete from shopping_cart where user_id = %(user_id)s", {'user_id': user_id})


def get_customer_preferences(user_id: uuid) -> CustomerPreferences:
    with connections.cursor() as cur:
        cur.execute("""
            SELECT
                p_cb_strength_mild,
                p_cb_strength_med,
                p_cb_strength_bold,
                p_cb_strength_blonde,
                p_cb_caf,
                p_cb_decaf,
                p_cb_flavored,
                p_cb_origin_single,
                p_cb_origin_blend,
                p_cb_keywords
            FROM customer_preferences
            WHERE user_id = %(user_id)s
        """, {'user_id': user_id})

        row = cur.fetchone()
        if row is not None:
            return CustomerPreferences(
                strength_mild=row['p_cb_strength_mild'],
                strength_med=row['p_cb_strength_med'],
                strength_bold=row['p_cb_strength_bold'],
                blonde=row['p_cb_strength_blonde'],
                caffinated=row['p_cb_caf'],
                decaf=row['p_cb_decaf'],
                flavored=row['p_cb_flavored'],
                single_origin=row['p_cb_origin_single'],
                origin_blend=row['p_cb_origin_blend'],
            )
        else:
            raise BadRequestException(f'could not locate customer preferences for user {user_id}')


def update_customer_preferences(user_id: uuid, request: CustomerPreferences):
    with cursor() as cur:
        cur.execute(
            'SELECT * FROM customer_preferences WHERE user_id = %(user_id)s',
            {'user_id': user_id}
        )
        res = cur.fetchone()

        if res is None:
            cur.execute("""
                INSERT INTO customer_preferences
                    (user_id,
                     p_cb_strength_mild, p_cb_strength_med,
                     p_cb_strength_bold, p_cb_strength_blonde,
                     p_cb_caf, p_cb_decaf, p_cb_flavored,
                     p_cb_origin_single, p_cb_origin_blend)
                VALUES
                    (%(user_id)s,
                    %(p_cb_strength_mild)s, %(p_cb_strength_med)s,
                    %(p_cb_strength_bold)s, %(p_cb_strength_blonde)s,
                    %(p_cb_caf)s, %(p_cb_decaf)s, %(p_cb_flavored)s,
                    %(p_cb_origin_single)s, %(p_cb_origin_blend)s)
            """, {
                'user_id': user_id,
                'p_cb_strength_mild': request.strength_mild,
                'p_cb_strength_med': request.strength_med,
                'p_cb_strength_bold': request.strength_bold,
                'p_cb_strength_blonde': request.blonde,
                'p_cb_caf': request.caffinated,
                'p_cb_decaf': request.decaf,
                'p_cb_flavored': request.flavored,
                'p_cb_origin_single': request.single_origin,
                'p_cb_origin_blend': request.origin_blend,
            })
        else:
            cur.execute("""
                UPDATE customer_preferences
                SET
                    p_cb_strength_mild = COALESCE(%(p_cb_strength_mild)s, p_cb_strength_mild),
                    p_cb_strength_med = COALESCE(%(p_cb_strength_med)s, p_cb_strength_med),
                    p_cb_strength_bold = COALESCE(%(p_cb_strength_bold)s, p_cb_strength_bold),
                    p_cb_strength_blonde = COALESCE(%(p_cb_strength_blonde)s, p_cb_strength_blonde),
                    p_cb_caf = COALESCE(%(p_cb_caf)s, p_cb_caf),
                    p_cb_decaf = COALESCE(%(p_cb_decaf)s, p_cb_decaf),
                    p_cb_flavored = COALESCE(%(p_cb_flavored)s, p_cb_flavored),
                    p_cb_origin_single = COALESCE(%(p_cb_origin_single)s, p_cb_origin_single),
                    p_cb_origin_blend = COALESCE(%(p_cb_origin_blend)s, p_cb_origin_blend),
                    p_cb_keywords = COALESCE(%(p_cb_keywords)s, p_cb_keywords)
                WHERE user_id = %(user_id)s
            """, {
                'user_id': user_id,
                'p_cb_strength_mild': request.get('strength_mild'),
                'p_cb_strength_med': request.get('strength_medium'),
                'p_cb_strength_bold': request.get('strength_bold'),
                'p_cb_strength_blonde': request.get('strength_blonde'),
                'p_cb_caf': request.get('caffeinated'),
                'p_cb_decaf': request.get('decaffeinated'),
                'p_cb_flavored': request.get('flavored'),
                'p_cb_origin_single': request.get('origin_single'),
                'p_cb_origin_blend': request.get('origin_blend'),
                'p_cb_keywords': request.get('keywords')
            })

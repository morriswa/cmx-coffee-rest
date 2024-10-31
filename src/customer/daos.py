import logging
import uuid

from app import connections

from .models import CartItem


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

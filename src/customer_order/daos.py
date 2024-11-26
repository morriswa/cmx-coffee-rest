
import uuid
from rest_framework import exceptions

from app import connections
from app.exceptions import APIException, BadRequestException

from customer_order.models import CreateOrderItem, OrderItem, Order


def create_order(user_id) -> uuid.UUID:
    with connections.cursor() as cur:
        cur.execute("""
            select
                cart.product_id,
                cart.quantity,
                pr.initial_price each_price
            from shopping_cart cart
                left join vendor_product pr
                    on cart.product_id = pr.product_id
            where   cart.user_id = %(user_id)s
            and     cart.quantity > 1
        """, {
            'user_id': user_id,
        })
        items = [CreateOrderItem(**data) for data in cur.fetchall()]

        if len(items) < 1:
            raise BadRequestException('cannot checkout with an empty cart')

        subtotal = 0
        for item in items:
            subtotal += ( item.quantity * item.each_price )

        # TODO add calculate tax rate
        cur.execute("""
            insert into mock_order
                (user_id, subtotal, tax_rate, tax, total)
            values
                (%(user_id)s, %(subtotal)s, %(tax_rate)s, %(tax)s, %(total)s)
            returning order_id;
        """,{
            'user_id': user_id,
            'subtotal': subtotal,
            'tax_rate': 0,
            'tax': 0,
            'total': subtotal,
        })
        res = cur.fetchone()
        if res is None:
            raise APIException('failed to retrieve newly created order ID')
        order_id = res['order_id']
        item: CreateOrderItem
        for item in items:
            cur.execute("""
                insert into mock_order_item
                    (order_id, product_id, quantity, each_price)
                values
                    (%(order_id)s, %(product_id)s, %(quantity)s, %(each_price)s)
            """, {
                'order_id': order_id,
                'product_id': item.product_id,
                'quantity': item.quantity,
                'each_price': item.each_price
            })

        cur.execute("""
            delete from shopping_cart
            where user_id = %(user_id)s
        """, {'user_id': user_id})

        return order_id;


def review_order(user_id, order_id) -> Order:
    with connections.cursor() as cur:
        cur.execute("""
            select
                odr.order_id,
                odr.payment_id,
                odr.payment_status,
                odr.status,
                odr.subtotal,
                odr.tax_rate,
                odr.tax,
                odr.total
            from mock_order odr
            where   odr.user_id = %(user_id)s
            and     odr.order_id = %(order_id)s
            and     odr.status = 'incompl'
        """, {
            'user_id': user_id,
            'order_id': order_id,
        })
        res = cur.fetchone()
        if res is None:
            raise APIException('failed to retrieve order')
        order = Order(**res)

        cur.execute("""
            select
                items.product_id,
                pd.product_name,

                items.quantity,
                items.each_price,

                pd.vendor_id,
                v.business_name vendor_name
            from mock_order_item items
                left join vendor_product pd
                    on items.product_id = pd.product_id
                left join vendor v
                    on pd.vendor_id = v.vendor_id
            where items.order_id = %(order_id)s
        """, {
            'order_id':order_id,
        })
        # add items to order
        order.items = [OrderItem(**data) for data in cur.fetchall()]
        return order

def delete_order_draft(user_id, order_id):
    with connections.cursor() as cur:
        cur.execute("""
            select status
            from mock_order
            where user_id = %(user_id)s
            and order_id = %(order_id)s
        """, {
            'user_id': user_id,
            'order_id': order_id
        })
        res = cur.fetchone()
        if res is None:
            raise BadRequestException('no such order')
        order_status = res['status']
        if order_status != 'incompl':
            raise exceptions.PermissionDenied('cannot delete submitted orders')
        else:
            cur.execute("""
                delete from mock_order_item
                where order_id = %(order_id)s
            """, {'order_id': order_id})
            cur.execute("""
                delete from mock_order
                where user_id = %(user_id)s
                and order_id = %(order_id)s
            """, {
                'user_id': user_id,
                'order_id': order_id
            })

def submit_order(user_id, order_id, payment_id):
    with connections.cursor() as cur:
        # TODO add payment validation
        cur.execute("""
            update mock_order
            set
                payment_id = %(payment_id)s,
                payment_status = 'paid',
                status = 'shipped'
            where user_id = %(user_id)s and order_id = %(order_id)s
        """, {
            'payment_id': payment_id,
            'user_id': user_id,
            'order_id': order_id
        })

def get_customer_orders(user_id) -> list[Order]:
    with connections.cursor() as cur:
        cur.execute("""
            select
                odr.order_id,
                odr.payment_id,
                odr.payment_status,
                odr.status,
                odr.subtotal,
                odr.tax_rate,
                odr.tax,
                odr.total
            from mock_order odr
            where   odr.user_id = %(user_id)s
            and     odr.status in ('shipped', 'process')
        """, {'user_id': user_id,})
        res = cur.fetchall()
        orders = [Order(**data) for data in res]
        orders_with_items = []
        for order in orders:
            cur.execute("""
                select
                    items.product_id,
                    pd.product_name,

                    items.quantity,
                    items.each_price,

                    pd.vendor_id,
                    v.business_name
                from mock_order_item items
                    left join mock_order odr
                        on items.order_id = odr.order_id
                    left join vendor_product pd
                        on items.product_id = pd.product_id
                    left join vendor v
                        on pd.vendor_id = v.vendor_id
                where   odr.user_id = %(user_id)s
                and     odr.order_id = %(order_id)s
               """, {
                'user_id': user_id,
                'order_id': order.order_id
            })
            items = [OrderItem(**data) for data in cur.fetchall()]
            order.items = items
            orders_with_items.append(order)
        return orders_with_items

import decimal
import random
import uuid

from django.test import TestCase
from rest_framework import exceptions

from app import connections
from app.exceptions import BadRequestException

import customer_order.daos as daos


__all__ = [
    'CreateOrderDAOTests',
    'DeleteOrderDAOTests',
]


class CreateOrderDAOTests(TestCase):

    def __setup_test_successfully_create_order(self):
        with connections.cursor() as cur:
            user_id = uuid.uuid4()
            vendor_user_id = uuid.uuid4()

            product_one_price = round(random.uniform(0.0, 29.99), 2)
            product_two_price = round(random.uniform(0.0, 29.99), 2)
            product_three_price = round(random.uniform(0.0, 29.99), 2)

            product_one_quantity = random.randint(1, 10)
            product_two_quantity = random.randint(1, 10)
            product_three_quantity = random.randint(1, 10)

            cur.execute("""
                insert into auth_integration (user_id, email)
                values (%(vendor_user_id)s, 'vendor@morriswa.org');

                insert into vendor
                    (vendor_id, user_id, business_name, business_email, phone,
                    address_one, city, zip, territory, approved_by)
                values
                    (1, %(vendor_user_id)s, 'Business Name', 'vendor@morriswa.org', '1231231234',
                    'address line 1', 'city', '55555', 'USA_MO', %(vendor_user_id)s);

                insert into vendor_product
                    (product_id, vendor_id, listed_by, product_name, initial_price)
                values
                    (1, 1, %(vendor_user_id)s, 'Product 1 Name', %(p1p)s),
                    (2, 1, %(vendor_user_id)s, 'Product 2 Name', %(p2p)s),
                    (3, 1, %(vendor_user_id)s, 'Product 3 Name', %(p3p)s);

                insert into auth_integration (user_id, email)
                values (%(user_id)s, 'test@morriswa.org');

                insert into shopping_cart (user_id, product_id, quantity)
                values
                    (%(user_id)s, 1, %(p1q)s),
                    (%(user_id)s, 2, %(p2q)s),
                    (%(user_id)s, 3, %(p3q)s);
            """, {
                'user_id': user_id,
                'vendor_user_id': vendor_user_id,
                'p1p': product_one_price,
                'p2p': product_two_price,
                'p3p': product_three_price,
                'p1q': product_one_quantity,
                'p2q': product_two_quantity,
                'p3q': product_three_quantity,
            })

            return user_id, (product_one_price, product_two_price, product_three_price,
                             product_one_quantity, product_two_quantity, product_three_quantity)

    def test_successfully_create_order(self):

        user_id, cart = self.__setup_test_successfully_create_order()

        order_id = daos.create_order(user_id)

        self.assertIsNotNone(order_id)

        subtotal = (cart[0] * cart[3]) + (cart[1] * cart[4]) + (cart[2] * cart[5])
        subtotal = decimal.Decimal(subtotal)
        subtotal = subtotal.quantize(decimal.Decimal('0.01'), rounding=decimal.ROUND_HALF_UP)

        with connections.cursor() as cur:
            cur.execute(
                """select * from mock_order where order_id = %(order_id)s""",
                {'order_id': order_id}
            )
            row = cur.fetchone()
            self.assertIsNotNone(row, 'should be in database')
            self.assertEqual(row['user_id'], user_id)
            self.assertEqual(row['status'], 'incompl', 'is a draft')
            self.assertIsNone(row['payment_id'], 'order drafts do not yet have payment id')
            self.assertEqual(row['payment_status'], 'none', 'order drafts do not yet have payment')
            self.assertEqual(row['subtotal'], subtotal, 'should correctly tabulate test data')
            self.assertEqual(row['subtotal'] + row['tax'], row['total'], 'should correctly tabulate test data')

    def __setup_test_create_empty_order(self):
        with connections.cursor() as cur:
            user_id = uuid.uuid4()
            vendor_user_id = uuid.uuid4()

            product_one_price = round(random.uniform(0.0, 29.99), 2)
            product_two_price = round(random.uniform(0.0, 29.99), 2)
            product_three_price = round(random.uniform(0.0, 29.99), 2)

            cur.execute("""
                insert into auth_integration (user_id, email)
                values (%(vendor_user_id)s, 'vendor@morriswa.org');

                insert into vendor
                    (vendor_id, user_id, business_name, business_email, phone,
                    address_one, city, zip, territory, approved_by)
                values
                    (1, %(vendor_user_id)s, 'Business Name', 'vendor@morriswa.org', '1231231234',
                    'address line 1', 'city', '55555', 'USA_MO', %(vendor_user_id)s);

                insert into vendor_product
                    (product_id, vendor_id, listed_by, product_name, initial_price)
                values
                    (1, 1, %(vendor_user_id)s, 'Product 1 Name', %(p1p)s),
                    (2, 1, %(vendor_user_id)s, 'Product 2 Name', %(p2p)s),
                    (3, 1, %(vendor_user_id)s, 'Product 3 Name', %(p3p)s);

                insert into auth_integration (user_id, email)
                values (%(user_id)s, 'test@morriswa.org');

                insert into shopping_cart (user_id, product_id, quantity)
                values
                    (%(user_id)s, 1, 0),
                    (%(user_id)s, 2, 0),
                    (%(user_id)s, 3, 0);
            """, {
                'user_id': user_id,
                'vendor_user_id': vendor_user_id,
                'p1p': product_one_price,
                'p2p': product_two_price,
                'p3p': product_three_price
            })

            return user_id

    def test_create_empty_order(self):

        user_id = self.__setup_test_create_empty_order()

        try:
            order_id = daos.create_order(user_id)
            self.fail('should never execute this line if no order was created')
        except BadRequestException as bre:
            self.assertEqual(bre.error, 'cannot checkout with an empty cart')

        with connections.cursor() as cur:
            cur.execute(
                """select * from mock_order where user_id = %(user_id)s""",
                {'user_id': user_id}
            )
            row = cur.fetchone()
            self.assertIsNone(row, 'should NOT be in database')


class DeleteOrderDAOTests(TestCase):

    def __setup_test_delete_order_success(self):
        with connections.cursor() as cur:
            user_id = uuid.uuid4()
            vendor_user_id = uuid.uuid4()
            order_id = uuid.uuid4()

            cur.execute("""
                insert into auth_integration (user_id, email)
                values (%(vendor_user_id)s, 'vendor@morriswa.org');

                insert into vendor
                    (vendor_id, user_id, business_name, business_email, phone,
                    address_one, city, zip, territory, approved_by)
                values
                    (1, %(vendor_user_id)s, 'Business Name', 'vendor@morriswa.org', '1231231234',
                    'address line 1', 'city', '55555', 'USA_MO', %(vendor_user_id)s);

                insert into vendor_product
                    (product_id, vendor_id, listed_by, product_name, initial_price)
                values
                    (1, 1, %(vendor_user_id)s, 'Product 1 Name', 11),
                    (2, 1, %(vendor_user_id)s, 'Product 2 Name', 12),
                    (3, 1, %(vendor_user_id)s, 'Product 3 Name', 13);

                insert into auth_integration (user_id, email)
                values (%(user_id)s, 'test@morriswa.org');

                insert into mock_order
                    (order_id, user_id, subtotal, tax_rate, tax, total)
                values
                    (%(order_id)s, %(user_id)s, 10, 0, 0, 10);
            """, {
                'user_id': user_id,
                'vendor_user_id': vendor_user_id,
                'order_id': order_id
            })

            return user_id, order_id


    def test_delete_order_success(self):
        user_id, order_id = self.__setup_test_delete_order_success()

        daos.delete_order_draft(user_id, order_id)

        with connections.cursor() as cur:
            cur.execute("select * from mock_order where order_id = %(order_id)s", {'order_id': order_id})
            self.assertIsNone(cur.fetchone(), 'order should have been deleted from database')

            cur.execute("select * from mock_order_item where order_id = %(order_id)s", {'order_id': order_id})
            self.assertEqual(len(cur.fetchall()), 0, 'order items should have been deleted from database')

    def __setup_test_delete_complete_order(self):
        with connections.cursor() as cur:
            user_id = uuid.uuid4()
            vendor_user_id = uuid.uuid4()
            order_id = uuid.uuid4()

            cur.execute("""
                insert into auth_integration (user_id, email)
                values (%(vendor_user_id)s, 'vendor@morriswa.org');

                insert into vendor
                    (vendor_id, user_id, business_name, business_email, phone,
                    address_one, city, zip, territory, approved_by)
                values
                    (1, %(vendor_user_id)s, 'Business Name', 'vendor@morriswa.org', '1231231234',
                    'address line 1', 'city', '55555', 'USA_MO', %(vendor_user_id)s);

                insert into vendor_product
                    (product_id, vendor_id, listed_by, product_name, initial_price)
                values
                    (1, 1, %(vendor_user_id)s, 'Product 1 Name', 11),
                    (2, 1, %(vendor_user_id)s, 'Product 2 Name', 12),
                    (3, 1, %(vendor_user_id)s, 'Product 3 Name', 13);

                insert into auth_integration (user_id, email)
                values (%(user_id)s, 'test@morriswa.org');

                insert into mock_order
                    (order_id, user_id, status, subtotal, tax_rate, tax, total)
                values
                    (%(order_id)s, %(user_id)s, 'process', 10, 0, 0, 10);
            """, {
                'user_id': user_id,
                'vendor_user_id': vendor_user_id,
                'order_id': order_id
            })

            return user_id, order_id


    def test_delete_complete_order(self):
        user_id, order_id = self.__setup_test_delete_complete_order()

        try:
            daos.delete_order_draft(user_id, order_id)
            self.fail('should never execute this line')
        except exceptions.PermissionDenied as pde:
            self.assertEqual(pde.detail, 'cannot delete submitted orders')

    def __setup_test_delete_nonexistent_order(self):
        with connections.cursor() as cur:
            user_id = uuid.uuid4()
            vendor_user_id = uuid.uuid4()

            cur.execute("""
                insert into auth_integration (user_id, email)
                values (%(vendor_user_id)s, 'vendor@morriswa.org');

                insert into vendor
                    (vendor_id, user_id, business_name, business_email, phone,
                    address_one, city, zip, territory, approved_by)
                values
                    (1, %(vendor_user_id)s, 'Business Name', 'vendor@morriswa.org', '1231231234',
                    'address line 1', 'city', '55555', 'USA_MO', %(vendor_user_id)s);

                insert into vendor_product
                    (product_id, vendor_id, listed_by, product_name, initial_price)
                values
                    (1, 1, %(vendor_user_id)s, 'Product 1 Name', 11),
                    (2, 1, %(vendor_user_id)s, 'Product 2 Name', 12),
                    (3, 1, %(vendor_user_id)s, 'Product 3 Name', 13);

                insert into auth_integration (user_id, email)
                values (%(user_id)s, 'test@morriswa.org');
            """, {
                'user_id': user_id,
                'vendor_user_id': vendor_user_id,
            })

            return user_id


    def test_delete_nonexistent_order(self):
        user_id = self.__setup_test_delete_nonexistent_order()

        try:
            daos.delete_order_draft(user_id, uuid.uuid4())
            self.fail('should never execute this line')
        except BadRequestException as bre:
            self.assertEqual(bre.error, 'no such order')

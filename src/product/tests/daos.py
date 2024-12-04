
import decimal
import uuid

from django.test import TestCase

from app import connections

import product.daos as daos


__all__ = [
    'GetProductsForSaleDAOTests',
    'GetProductDetailsDAOTests'
]


class GetProductsForSaleDAOTests(TestCase):
    def __setup_test_get_products_for_sale(self):
        with connections.cursor() as cur:
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
                    (product_id, vendor_id, listed_by, product_name, description ,initial_price)
                values
                    (1, 1, %(vendor_user_id)s, 'Product 1 Name','description',10.00),
                    (2, 1, %(vendor_user_id)s, 'Product 2 Name','description',20.00),
                    (3, 1, %(vendor_user_id)s, 'Product 3 Name','description',30.00);
            """,{'vendor_user_id': vendor_user_id})

    def test_successfully_get_products_for_sale(self):
        #setup
        self.__setup_test_get_products_for_sale()

        #execute
        products = daos.get_products_for_sale()

        #assert
        self.assertEqual(products[0].product_id, 1)
        self.assertEqual(products[0].product_name, 'Product 1 Name')
        self.assertEqual(products[0].description, 'description')
        self.assertEqual(products[0].price, decimal.Decimal('10.00'))
        self.assertTrue(
            isinstance(products, list),
            'correctly returns a list of products'
        )
        self.assertEqual(
            len(products),
            3,
            'correct number of products returned'
        )


class GetProductDetailsDAOTests(TestCase):

    def __setup_get_products_details(self):
        vendor_user_id = uuid.uuid4()
        with connections.cursor() as cur:
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
                    (product_id, vendor_id, listed_by, product_name, description ,initial_price)
                values
                    (1, 1, %(vendor_user_id)s, 'Product 1 Name','description',10.00),
                    (2, 1, %(vendor_user_id)s, 'Product 2 Name','description',20.00),
                    (3, 1, %(vendor_user_id)s, 'Product 3 Name','description',30.00);
            """,{'vendor_user_id': vendor_user_id})

    def test_successfully_get_products_details(self):
        #setup
        self.__setup_get_products_details()

        #execute
        product = daos.get_product_details(1)

        #assert
        self.assertEqual(product.product_id, 1)
        self.assertEqual(product.product_name, 'Product 1 Name')
        self.assertEqual(product.description, 'description')
        self.assertEqual(product.price, decimal.Decimal('10.00'))

# src/vendor/tests/daos.py

import uuid

from unittest.mock import patch, MagicMock

from django.test import TestCase
from rest_framework import exceptions

from app import connections
from app.exceptions import BadRequestException, APIException

import vendor.daos as vendor_dao
from vendor.models import (
    VendorApplicationRequest,
    CreateProductRequest,
    UpdateProductRequest,
    CoffeeBeanCharacteristics,
    VendorProductResponse,
)


class ApplyForVendorDAOTests(TestCase):
    def test_apply_for_vendor_success(self):
        user_id = uuid.uuid4()
        application_data = VendorApplicationRequest(
            business_name='Test Business',
            business_email='test@business.com',
            phone='1234567890',
            address_line_one='123 Main St',
            city='Testville',
            zip='12345',
            territory='USA_KS'
        )

        # Insert user into auth_integration
        with connections.cursor() as cur:
            cur.execute("""
                INSERT INTO auth_integration (user_id, email)
                VALUES (%(user_id)s, %(email)s)
            """, {
                'user_id': user_id,
                'email': 'user@test.com'
            })

        # Execute
        vendor_dao.apply_for_vendor(user_id, application_data)

        # Assert
        with connections.cursor() as cur:
            cur.execute("""
                SELECT * FROM vendor_applicant WHERE user_id = %(user_id)s
            """, {'user_id': user_id})
            res = cur.fetchone()
            self.assertIsNotNone(res, 'Application should be created')
            self.assertEqual(res['business_name'], 'Test Business', 'Business name should match')

    def test_apply_for_vendor_already_applied(self):
        user_id = uuid.uuid4()
        application_data = VendorApplicationRequest(
            business_name='Test Business',
            business_email='test@business.com',
            phone='1234567890',
            address_line_one='123 Main St',
            city='Testville',
            zip='12345',
            territory='USA_KS'
        )

        # Insert user and application into database
        with connections.cursor() as cur:
            cur.execute("""
                INSERT INTO auth_integration (user_id, email)
                VALUES (%(user_id)s, %(email)s);

                INSERT INTO vendor_applicant
                (user_id, business_name, business_email, phone, address_one, city, zip, territory_id)
                VALUES
                (%(user_id)s, %(business_name)s, %(business_email)s, %(phone)s,
                %(address_one)s, %(city)s, %(zip)s, %(territory_id)s)
            """, {
                'user_id': user_id,
                'email': 'user@test.com',
                'business_name': 'Test Business',
                'business_email': 'test@business.com',
                'phone': '1234567890',
                'address_one': '123 Main St',
                'city': 'Testville',
                'zip': '12345',
                'territory_id': 'USA_KS'
            })

        # Execute and expect exception
        with self.assertRaises(BadRequestException) as context:
            vendor_dao.apply_for_vendor(user_id, application_data)

        self.assertEqual(str(context.exception), 'you have already applied with this account!')


class GetVendorIdAssociatedWithUserDAOTests(TestCase):
    def setUp(self):
        self.user_id_with_vendor = uuid.uuid4()
        self.user_id_without_vendor = uuid.uuid4()

        # Insert users into auth_integration
        with connections.cursor() as cur:
            cur.execute("""
                INSERT INTO auth_integration (user_id, email)
                VALUES (%(user_id_with_vendor)s, 'vendoruser@test.com'),
                       (%(user_id_without_vendor)s, 'nouser@test.com');
            """, {
                'user_id_with_vendor': self.user_id_with_vendor,
                'user_id_without_vendor': self.user_id_without_vendor
            })

            # Insert vendor for user_id_with_vendor
            cur.execute("""
                INSERT INTO vendor
                (user_id, business_name, business_email, phone, address_one, city, zip, territory)
                VALUES
                (%(user_id)s, 'Vendor Name', 'vendor@test.com', '1234567890',
                '123 Vendor St', 'Vendor City', '54321', 'USA_KS');
            """, {
                'user_id': self.user_id_with_vendor
            })

    def test_get_vendor_id_associated_with_user_success(self):
        vendor_id = vendor_dao.get_vendor_id_associated_with_user(self.user_id_with_vendor)
        self.assertIsNotNone(vendor_id, 'Vendor ID should be returned')

    def test_get_vendor_id_associated_with_user_not_found(self):
        with self.assertRaises(BadRequestException) as context:
            vendor_dao.get_vendor_id_associated_with_user(self.user_id_without_vendor)
        self.assertIn('could not find vendor associated with user_id', str(context.exception))


class ListProductDAOTests(TestCase):
    def setUp(self):
        self.user_id = uuid.uuid4()
        self.vendor_id = None

        # Create user and vendor
        with connections.cursor() as cur:
            cur.execute("""
                INSERT INTO auth_integration (user_id, email)
                VALUES (%(user_id)s, %(email)s);

                INSERT INTO vendor
                (user_id, business_name, business_email, phone, address_one, city, zip, territory)
                VALUES
                (%(user_id)s, 'Vendor Name', 'vendor@test.com', '1234567890',
                '123 Vendor St', 'Vendor City', '54321', 'USA_KS')
                RETURNING vendor_id;
            """, {
                'user_id': self.user_id,
                'email': 'vendor@test.com'
            })
            res = cur.fetchone()
            self.vendor_id = res['vendor_id']

    def test_list_product_success(self):
        product_data = CreateProductRequest(
            product_name='Test Product',
            description='Test Description',
            initial_price=9.99,
            coffee_bean_characteristics={
                'taste_strength': '5',
                'decaf': 'n',
                'flavored': 'n',
                'single_origin': 'y',
                'regions': 'Region1',
                'keywords': 'keyword1,keyword2'
            }
        )

        # Execute
        vendor_dao.list_product(self.vendor_id, self.user_id, product_data)

        # Assert
        with connections.cursor() as cur:
            cur.execute("""
                SELECT * FROM vendor_product WHERE vendor_id = %(vendor_id)s
            """, {'vendor_id': self.vendor_id})
            res = cur.fetchone()
            self.assertIsNotNone(res, 'Product should be listed')
            self.assertEqual(res['product_name'], 'Test Product', 'Product name should match')

            # Check product characteristics
            product_id = res['product_id']
            cur.execute("""
                SELECT * FROM product_characteristics WHERE product_id = %(product_id)s
            """, {'product_id': product_id})
            char_res = cur.fetchone()
            self.assertIsNotNone(char_res, 'Product characteristics should be saved')
            self.assertEqual(char_res['cb_taste_strength'], '5', 'Taste strength should match')

    @patch('vendor.daos.cursor')
    def test_list_product_failure(self, mock_cursor):
        # Mock the cursor to return None on fetchone
        mock_cur_instance = MagicMock()
        mock_cursor.return_value.__enter__.return_value = mock_cur_instance
        mock_cur_instance.fetchone.return_value = None

        product_data = CreateProductRequest(
            product_name='Test Product',
            description='Test Description',
            initial_price=9.99,
            coffee_bean_characteristics={
                'taste_strength': '5',
                'decaf': 'n',
                'flavored': 'n',
                'single_origin': 'y',
                'regions': 'Region1',
                'keywords': 'keyword1,keyword2'
            }
        )

        with self.assertRaises(APIException) as context:
            vendor_dao.list_product(self.vendor_id, self.user_id, product_data)

        self.assertEqual(str(context.exception), 'failed to retrieve newly created product ID')


class GetProductDetailsDAOTests(TestCase):
    def setUp(self):
        self.user_id = uuid.uuid4()
        self.vendor_id = None
        self.product_id = None

        # Create user, vendor, and product
        with connections.cursor() as cur:
            cur.execute("""
                INSERT INTO auth_integration (user_id, email)
                VALUES (%(user_id)s, 'vendor@test.com');

                INSERT INTO vendor
                (user_id, business_name, business_email, phone,
                address_one, city, zip, territory)
                VALUES
                (%(user_id)s, 'Vendor Name', 'vendor@test.com', '1234567890',
                '123 Vendor St', 'Vendor City', '54321', 'USA_KS')
                RETURNING vendor_id;
            """, {'user_id': self.user_id})
            res = cur.fetchone()
            self.vendor_id = res['vendor_id']

            cur.execute("""
                INSERT INTO vendor_product
                (vendor_id, listed_by, product_name, description, initial_price)
                VALUES
                (%(vendor_id)s, %(user_id)s, 'Test Product', 'Test Description', 9.99)
                RETURNING product_id;
            """, {
                'vendor_id': self.vendor_id,
                'user_id': self.user_id
            })
            res = cur.fetchone()
            self.product_id = res['product_id']

    def test_get_product_details_success(self):
        product = vendor_dao.get_product_details(self.vendor_id, self.product_id)
        self.assertIsInstance(product, VendorProductResponse)
        self.assertEqual(product.product_name, 'Test Product')

    def test_get_product_details_not_found(self):
        non_existent_product_id = 9999
        with self.assertRaises(BadRequestException) as context:
            vendor_dao.get_product_details(self.vendor_id, non_existent_product_id)
        expected_msg = f'could not find product #{non_existent_product_id} with vendor {self.vendor_id}'
        self.assertEqual(str(context.exception), expected_msg)


class AssertVendorOwnsProductDAOTests(TestCase):
    def setUp(self):
        self.vendor_id = 1
        self.other_vendor_id = 2
        self.product_id = None

        # Generate UUIDs for user_ids
        self.user_id_vendor1 = uuid.uuid4()
        self.user_id_vendor2 = uuid.uuid4()

        # Create users, vendors, and product
        with connections.cursor() as cur:
            # Insert users into auth_integration
            cur.execute("""
                INSERT INTO auth_integration (user_id, email)
                VALUES (%(user_id_vendor1)s, 'vendor1@test.com'),
                       (%(user_id_vendor2)s, 'vendor2@test.com');
            """, {
                'user_id_vendor1': self.user_id_vendor1,
                'user_id_vendor2': self.user_id_vendor2
            })

            # Insert vendors
            cur.execute("""
                INSERT INTO vendor (vendor_id, user_id, business_name, business_email,
                phone, address_one, city, zip, territory)
                VALUES
                (%(vendor_id)s, %(user_id_vendor1)s, 'Vendor 1', 'vendor1@test.com', '1234567890',
                'Address', 'City', '12345', 'USA_KS'),
                (%(other_vendor_id)s, %(user_id_vendor2)s, 'Vendor 2', 'vendor2@test.com', '1234567890',
                'Address', 'City', '12345', 'USA_KS');
            """, {
                'vendor_id': self.vendor_id,
                'other_vendor_id': self.other_vendor_id,
                'user_id_vendor1': self.user_id_vendor1,
                'user_id_vendor2': self.user_id_vendor2
            })

            # Insert product associated with vendor_id
            cur.execute("""
                INSERT INTO vendor_product
                (vendor_id, listed_by, product_name, description, initial_price)
                VALUES
                (%(vendor_id)s, %(listed_by)s, 'Test Product', 'Test Description', 9.99)
                RETURNING product_id;
            """, {
                'vendor_id': self.vendor_id,
                'listed_by': self.user_id_vendor1  # Assume the product is listed by vendor1
            })
            res = cur.fetchone()
            self.product_id = res['product_id']


    def test_assert_vendor_owns_product_success(self):
        vendor_dao.assert_vendor_owns_product(self.vendor_id, self.product_id)
        # Should not raise an exception

    def test_assert_vendor_owns_product_permission_denied(self):
        with self.assertRaises(exceptions.PermissionDenied):
            vendor_dao.assert_vendor_owns_product(self.other_vendor_id, self.product_id)


class UpdateExistingProductDAOTests(TestCase):
    def setUp(self):
        self.vendor_id = None
        self.user_id = uuid.uuid4()
        self.product_id = None

        # Create user, vendor, and product
        with connections.cursor() as cur:
            cur.execute("""
                INSERT INTO auth_integration (user_id, email)
                VALUES (%(user_id)s, 'vendor@test.com');

                INSERT INTO vendor
                (user_id, business_name, business_email, phone,
                address_one, city, zip, territory)
                VALUES
                (%(user_id)s, 'Vendor Name', 'vendor@test.com', '1234567890',
                '123 Vendor St', 'Vendor City', '54321', 'USA_KS')
                RETURNING vendor_id;
            """, {'user_id': self.user_id})
            res = cur.fetchone()
            self.vendor_id = res['vendor_id']

            cur.execute("""
                INSERT INTO vendor_product
                (vendor_id, listed_by, product_name, description, initial_price)
                VALUES
                (%(vendor_id)s, %(user_id)s, 'Original Product', 'Original Description', 9.99)
                RETURNING product_id;
            """, {
                'vendor_id': self.vendor_id,
                'user_id': self.user_id
            })
            res = cur.fetchone()
            self.product_id = res['product_id']

    def test_update_existing_product_insert_characteristics(self):
        # Ensure characteristics do not exist
        with connections.cursor() as cur:
            cur.execute("""
                SELECT * FROM product_characteristics WHERE product_id = %(product_id)s
            """, {'product_id': self.product_id})
            self.assertIsNone(cur.fetchone())

        update_data = UpdateProductRequest(
            product_name='Updated Product',
            description='Updated Description',
            initial_price=19.99,
            coffee_bean_characteristics={
                'taste_strength': '7',
                'decaf': 'y',
                'flavored': 'n',
                'single_origin': 'n',
                'regions': 'Region2',
                'keywords': 'updated,keywords'
            }
        )


        vendor_dao.updated_existing_product(self.product_id, update_data)

        # Verify characteristics inserted
        with connections.cursor() as cur:
            cur.execute("""
                SELECT * FROM product_characteristics WHERE product_id = %(product_id)s
            """, {'product_id': self.product_id})
            char_res = cur.fetchone()
            self.assertIsNotNone(char_res)
            self.assertEqual(char_res['cb_taste_strength'], '7')

    def test_update_existing_product_update_characteristics(self):
        # Insert initial characteristics
        with connections.cursor() as cur:
            cur.execute("""
                INSERT INTO product_characteristics
                (product_id, cb_taste_strength, cb_decaf, cb_flavored, cb_single_origin,
                cb_regions, cb_keywords)
                VALUES
                (%(product_id)s, '5', 'n', 'n', 'y', 'Region1', 'keyword1');
            """, {'product_id': self.product_id})

        update_data = UpdateProductRequest(
            product_name='Updated Product',
            description='Updated Description',
            initial_price=19.99,
            coffee_bean_characteristics={
                'taste_strength': '8',
                'decaf': 'y',
                'flavored': 'y',
                'single_origin': 'n',
                'regions': 'Region3',
                'keywords': 'new,keywords'
            }
        )




        vendor_dao.updated_existing_product(self.product_id, update_data)

        # Verify characteristics updated
        with connections.cursor() as cur:
            cur.execute("""
                SELECT * FROM product_characteristics WHERE product_id = %(product_id)s
            """, {'product_id': self.product_id})
            char_res = cur.fetchone()
            self.assertEqual(char_res['cb_taste_strength'], '8')
            self.assertEqual(char_res['cb_decaf'], 'y')
            self.assertEqual(char_res['cb_flavored'], 'y')
            self.assertEqual(char_res['cb_single_origin'], 'n')
            self.assertEqual(char_res['cb_regions'], 'Region3')
            self.assertEqual(char_res['cb_keywords'], 'new,keywords')


class UnlistProductDAOTests(TestCase):
    def setUp(self):
        self.vendor_id = None
        self.user_id = uuid.uuid4()
        self.product_id = None

        # Create user, vendor, and product
        with connections.cursor() as cur:
            cur.execute("""
                INSERT INTO auth_integration (user_id, email)
                VALUES (%(user_id)s, 'vendor@test.com');

                INSERT INTO vendor
                (user_id, business_name, business_email, phone,
                address_one, city, zip, territory)
                VALUES
                (%(user_id)s, 'Vendor Name', 'vendor@test.com', '1234567890',
                '123 Vendor St', 'Vendor City', '54321', 'USA_KS')
                RETURNING vendor_id;
            """, {'user_id': self.user_id})
            res = cur.fetchone()
            self.vendor_id = res['vendor_id']

            cur.execute("""
                INSERT INTO vendor_product
                (vendor_id, listed_by, product_name, description, initial_price, status)
                VALUES
                (%(vendor_id)s, %(user_id)s, 'Product to Unlist', 'Description', 9.99, 'A')
                RETURNING product_id;
            """, {
                'vendor_id': self.vendor_id,
                'user_id': self.user_id
            })
            res = cur.fetchone()
            self.product_id = res['product_id']

    def test_unlist_product(self):
        # Verify initial status is 'A'
        with connections.cursor() as cur:
            cur.execute("""
                SELECT status FROM vendor_product WHERE product_id = %(product_id)s
            """, {'product_id': self.product_id})
            res = cur.fetchone()
            self.assertEqual(res['status'], 'A')

        # Unlist the product
        vendor_dao.unlist_product(self.product_id)

        # Verify status is now 'U'
        with connections.cursor() as cur:
            cur.execute("""
                SELECT status FROM vendor_product WHERE product_id = %(product_id)s
            """, {'product_id': self.product_id})
            res = cur.fetchone()
            self.assertEqual(res['status'], 'U')

class GetProductsDAOTests(TestCase):
    def setUp(self):
        self.vendor_id = None
        self.user_id = uuid.uuid4()
        self.product_ids = []

        # Create user and vendor
        with connections.cursor() as cur:
            # Insert user into auth_integration
            cur.execute("""
                INSERT INTO auth_integration (user_id, email)
                VALUES (%(user_id)s, %(email)s);
            """, {
                'user_id': self.user_id,
                'email': 'vendor@test.com'
            })

            # Insert vendor
            cur.execute("""
                INSERT INTO vendor
                (user_id, business_name, business_email, phone,
                address_one, city, zip, territory)
                VALUES
                (%(user_id)s, 'Test Vendor', 'vendor@test.com', '1234567890',
                '123 Vendor St', 'Vendor City', '12345', 'USA_KS')
                RETURNING vendor_id;
            """, {'user_id': self.user_id})
            res = cur.fetchone()
            self.vendor_id = res['vendor_id']

            # Insert products for the vendor
            cur.execute("""
                INSERT INTO vendor_product
                (vendor_id, listed_by, product_name, description, initial_price, status)
                VALUES
                (%(vendor_id)s, %(user_id)s, 'Product 1', 'Description 1', 10.0, 'A'),
                (%(vendor_id)s, %(user_id)s, 'Product 2', 'Description 2', 20.0, 'A'),
                (%(vendor_id)s, %(user_id)s, 'Product 3', 'Description 3', 30.0, 'U')  -- Unlisted product
                RETURNING product_id;
            """, {
                'vendor_id': self.vendor_id,
                'user_id': self.user_id
            })
            # Get the product_ids
            res = cur.fetchall()
            self.product_ids = [row['product_id'] for row in res]

            # For one product, add coffee_bean_characteristics
            product_id_with_chars = self.product_ids[0]
            cur.execute("""
                INSERT INTO product_characteristics
                (product_id, cb_taste_strength, cb_decaf, cb_flavored, cb_single_origin,
                cb_regions, cb_keywords)
                VALUES
                (%(product_id)s, '5', 'n', 'y', 'n', 'Region1', 'keyword1,keyword2');
            """, {'product_id': product_id_with_chars})

    def test_get_products_success(self):
        # Call the function
        products = vendor_dao.get_products(self.vendor_id)

        # Should return 2 products (status 'A')
        self.assertEqual(len(products), 2, 'Should return 2 active products')

        # Check the products
        product_names = [product.product_name for product in products]
        self.assertIn('Product 1', product_names)
        self.assertIn('Product 2', product_names)

        # Check coffee_bean_characteristics for Product 1
        for product in products:
            if product.product_name == 'Product 1':
                self.assertIsNotNone(product.coffee_bean_characteristics)
                self.assertEqual(product.coffee_bean_characteristics.taste_strength, '5')
                self.assertEqual(product.coffee_bean_characteristics.decaf, 'n')
                self.assertEqual(product.coffee_bean_characteristics.flavored, 'y')
                self.assertEqual(product.coffee_bean_characteristics.single_origin, 'n')
            else:
                # Product 2 should have no characteristics
                self.assertIsNone(product.coffee_bean_characteristics.taste_strength)
                self.assertIsNone(product.coffee_bean_characteristics.decaf)
                self.assertIsNone(product.coffee_bean_characteristics.flavored)
                self.assertIsNone(product.coffee_bean_characteristics.single_origin)

    def test_get_products_no_active_products(self):
        # Unlist all products
        with connections.cursor() as cur:
            cur.execute("""
                UPDATE vendor_product SET status = 'U' WHERE vendor_id = %(vendor_id)s
            """, {'vendor_id': self.vendor_id})

        # Call the function
        products = vendor_dao.get_products(self.vendor_id)

        # Should return 0 products since all are unlisted
        self.assertEqual(len(products), 0, 'Should return no products when all are unlisted')

    def test_get_products_no_products(self):
        # Create a vendor with no products
        user_id = uuid.uuid4()
        with connections.cursor() as cur:
            # Insert user
            cur.execute("""
                INSERT INTO auth_integration (user_id, email)
                VALUES (%(user_id)s, %(email)s);
            """, {
                'user_id': user_id,
                'email': 'novendor@test.com'
            })
            # Insert vendor
            cur.execute("""
                INSERT INTO vendor
                (user_id, business_name, business_email, phone,
                address_one, city, zip, territory)
                VALUES
                (%(user_id)s, 'No Product Vendor', 'novendor@test.com', '1234567890',
                '123 Vendor St', 'Vendor City', '12345', 'USA_KS')
                RETURNING vendor_id;
            """, {'user_id': user_id})
            res = cur.fetchone()
            vendor_id_no_products = res['vendor_id']

        # Call the function
        products = vendor_dao.get_products(vendor_id_no_products)

        # Should return an empty list
        self.assertEqual(len(products), 0, 'Should return no products for vendor with no products')

    def test_get_products_with_missing_characteristics(self):
        # Remove characteristics for all products
        with connections.cursor() as cur:
            cur.execute("""
                DELETE FROM product_characteristics WHERE product_id IN %(product_ids)s
            """, {'product_ids': tuple(self.product_ids)})

        # Call the function
        products = vendor_dao.get_products(self.vendor_id)


        # All products should have coffee_bean_characteristics as None
        for product in products:

            for prop in vars(product.coffee_bean_characteristics):
                self.assertIsNone(getattr(product.coffee_bean_characteristics, prop))

    @patch('vendor.daos.cursor')
    def test_get_products_database_error(self, mock_cursor):
        # Simulate a database error
        mock_cursor.side_effect = Exception('Database error')

        with self.assertRaises(Exception) as context:
            vendor_dao.get_products(self.vendor_id)
        self.assertIn('Database error', str(context.exception))

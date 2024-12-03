import uuid
from rest_framework.test import APITestCase
from unittest.mock import patch


from app.authentication import User
from app.exceptions import BadRequestException
from app import connections


import vendor.views as vendor_views
from vendor.models import VendorApplicationRequest, VendorProductResponse, CreateProductRequest, CoffeeBeanCharacteristics
from decimal import Decimal

class ApplyForVendorEndpointTests(APITestCase):
    def setUp(self):
        self.user_id = uuid.uuid4()
        self.client.force_authenticate(
            user=User(
                user_id=self.user_id,
                email='user@test.com',
                username='user@test.com',
                vendor_id=None,
                jwt_permissions=['cmx_coffee:appuser']
            )
        )


        # Insert user into auth_integration
        with connections.cursor() as cur:
            cur.execute("""
                INSERT INTO auth_integration (user_id, email)
                VALUES (%(user_id)s, %(email)s)
            """, {
                'user_id': self.user_id,
                'email': 'user@test.com'
            })


    def test_apply_for_vendor_success(self):
        application_data = {
            'business_name': 'Test Business',
            'business_email': 'test@business.com',
            'phone': '1234567890',
            'address_line_one': '123 Main St',
            'city': 'Testville',
            'zip': '12345',
            'territory': 'USA_KS'
        }


        response = self.client.post('/s/forms/vendor-application', data=application_data, format='json')
        self.assertEqual(response.status_code, 200, 'Application should be submitted successfully')
        self.assertEqual(response.data['business_name'], 'Test Business', 'Business name should match')


    def test_apply_for_vendor_already_applied(self):
        # Insert an existing application
        with connections.cursor() as cur:
            cur.execute("""
                INSERT INTO vendor_applicant
                (user_id, business_name, business_email, phone, address_one, city, zip, territory_id)
                VALUES
                (%(user_id)s, %(business_name)s, %(business_email)s, %(phone)s, %(address_one)s, %(city)s, %(zip)s, %(territory_id)s)
            """, {
                'user_id': self.user_id,
                'business_name': 'Existing Business',
                'business_email': 'existing@business.com',
                'phone': '1234567890',
                'address_one': '123 Main St',
                'city': 'Testville',
                'zip': '12345',
                'territory_id': 'USA_KS'
            })


        application_data = {
            'business_name': 'Test Business',
            'business_email': 'test@business.com',
            'phone': '1234567890',
            'address_line_one': '123 Main St',
            'city': 'Testville',
            'zip': '12345',
            'territory': 'USA_KS'
        }


        response = self.client.post('/s/forms/vendor-application', data=application_data, format='json')
        self.assertEqual(response.status_code, 400, 'Should return Bad Request for duplicate application')
        self.assertEqual(response.data['msg'], 'you have already applied with this account!')


class VendorProductViewTests(APITestCase):
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
                (%(user_id)s, 'Vendor Name', 'vendor@test.com', '1234567890', '123 Vendor St', 'Vendor City', '54321', 'USA_KS')
                RETURNING vendor_id;
            """, {
                'user_id': self.user_id,
                'email': 'vendor@test.com'
            })
            res = cur.fetchone()
            self.vendor_id = res['vendor_id']


        self.client.force_authenticate(
            user=User(
                user_id=self.user_id,
                email='vendor@test.com',
                username='vendor@test.com',
                vendor_id=self.vendor_id,
                jwt_permissions=['cmx_coffee:vendor']
            )
        )


    def test_get_vendor_products_empty(self):
        response = self.client.get('/s/vendor/products')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, [], 'Vendor should have no products initially')


    def test_post_vendor_product_success(self):
        product_data = {
            'product_name': 'Test Product',
            'description': 'Test Description',
            'initial_price': 9.99,
            'coffee_bean_characteristics': {
                'taste_strength': '5',
                'decaf': 'n',
                'flavored': 'n',
                'single_origin': 'y',
                'regions': 'Region1',
                'keywords': 'keyword1,keyword2'
            }
        }


        response = self.client.post('/s/vendor/products', data=product_data, format='json')
        self.assertEqual(response.status_code, 204, 'Product should be created successfully')


        # Verify product was created
        response = self.client.get('/s/vendor/products')
        self.assertEqual(len(response.data), 1, 'Vendor should have one product')


    # Additional tests for update, delete, and get details can be added here

class VendorProductDetailsViewTests(APITestCase):
    def setUp(self):
        self.user_id = uuid.uuid4()
        self.vendor_id = None
        self.product_id = None

        # Create user, vendor, and product
        with connections.cursor() as cur:
            # Insert user and vendor
            cur.execute("""
                INSERT INTO auth_integration (user_id, email)
                VALUES (%(user_id)s, %(email)s);

                INSERT INTO vendor
                (user_id, business_name, business_email, phone,
                address_one, city, zip, territory)
                VALUES
                (%(user_id)s, 'Vendor Name', 'vendor@test.com', '1234567890',
                '123 Vendor St', 'Vendor City', '54321', 'USA_KS')
                RETURNING vendor_id;
            """, {'user_id': self.user_id, 'email': 'vendor@test.com'})
            res = cur.fetchone()
            self.vendor_id = res['vendor_id']

            # Insert product
            cur.execute("""
                INSERT INTO vendor_product
                (vendor_id, listed_by, product_name, description, initial_price)
                VALUES
                (%(vendor_id)s, %(user_id)s, 'Test Product', 'Test Description', 9.99)
                RETURNING product_id;
            """, {'vendor_id': self.vendor_id, 'user_id': self.user_id})
            res = cur.fetchone()
            self.product_id = res['product_id']

        self.client.force_authenticate(
            user=User(
                user_id=self.user_id,
                email='vendor@test.com',
                username='vendor@test.com',
                vendor_id=self.vendor_id,
                jwt_permissions=['cmx_coffee:vendor']
            )
        )

    def test_get_product_details_success(self):
        response = self.client.get(f'/s/vendor/product/{self.product_id}')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['product_name'], 'Test Product')
        self.assertEqual(response.data['description'], 'Test Description')
        self.assertEqual(response.data['initial_price'], Decimal('9.99'))

    def test_get_product_details_permission_denied(self):
        # Create another vendor and product
        other_user_id = uuid.uuid4()
        with connections.cursor() as cur:
            cur.execute("""
                INSERT INTO auth_integration (user_id, email)
                VALUES (%(user_id)s, 'othervendor@test.com');

                INSERT INTO vendor
                (user_id, business_name, business_email, phone,
                address_one, city, zip, territory)
                VALUES
                (%(user_id)s, 'Other Vendor', 'othervendor@test.com', '1234567890',
                '123 Other St', 'Other City', '54321', 'USA_KS')
                RETURNING vendor_id;
            """, {'user_id': other_user_id})
            res = cur.fetchone()
            other_vendor_id = res['vendor_id']

            # Insert product for other vendor
            cur.execute("""
                INSERT INTO vendor_product
                (vendor_id, listed_by, product_name, description, initial_price)
                VALUES
                (%(vendor_id)s, %(user_id)s, 'Other Product', 'Other Description', 19.99)
                RETURNING product_id;
            """, {'vendor_id': other_vendor_id, 'user_id': other_user_id})
            res = cur.fetchone()
            other_product_id = res['product_id']

        # Attempt to get other vendor's product
        response = self.client.get(f'/s/vendor/product/{other_product_id}')
        self.assertEqual(response.status_code, 403, 'Should not be able to access another vendor\'s product')

    def test_patch_product_details_success(self):
        update_data = {
            'product_name': 'Updated Product',
            'description': 'Updated Description',
            'initial_price': 15.0,
            'coffee_bean_characteristics': {
                'taste_strength': '7',
                'decaf': 'n',
                'flavored': 'y',
                'single_origin': 'n',
                'regions': 'Region2',
                'keywords': 'updated,keywords'
            }
        }

        response = self.client.patch(f'/s/vendor/product/{self.product_id}', data=update_data, format='json')
        self.assertEqual(response.status_code, 204)

        # Verify that the product was updated
        response = self.client.get(f'/s/vendor/product/{self.product_id}')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['product_name'], 'Updated Product')
        self.assertEqual(response.data['description'], 'Updated Description')
        self.assertEqual(response.data['initial_price'], 15.0)

    def test_delete_product_success(self):
        response = self.client.delete(f'/s/vendor/product/{self.product_id}')
        self.assertEqual(response.status_code, 204)

        # Verify that the product is unlisted
        with connections.cursor() as cur:
            cur.execute("""
                SELECT status FROM vendor_product WHERE product_id = %(product_id)s
            """, {'product_id': self.product_id})
            res = cur.fetchone()
            self.assertEqual(res['status'], 'U', 'Product should be unlisted')

    def test_patch_product_permission_denied(self):
        # Create another vendor and product
        other_user_id = uuid.uuid4()
        with connections.cursor() as cur:
            cur.execute("""
                INSERT INTO auth_integration (user_id, email)
                VALUES (%(user_id)s, 'othervendor@test.com');

                INSERT INTO vendor
                (user_id, business_name, business_email, phone,
                address_one, city, zip, territory)
                VALUES
                (%(user_id)s, 'Other Vendor', 'othervendor@test.com', '1234567890',
                '123 Other St', 'Other City', '54321', 'USA_KS')
                RETURNING vendor_id;
            """, {'user_id': other_user_id})
            res = cur.fetchone()
            other_vendor_id = res['vendor_id']

            # Insert product for other vendor
            cur.execute("""
                INSERT INTO vendor_product
                (vendor_id, listed_by, product_name, description, initial_price)
                VALUES
                (%(vendor_id)s, %(user_id)s, 'Other Product', 'Other Description', 19.99)
                RETURNING product_id;
            """, {'vendor_id': other_vendor_id, 'user_id': other_user_id})
            res = cur.fetchone()
            other_product_id = res['product_id']

        update_data = {'product_name': 'Hacked Product'}
        response = self.client.patch(f'/s/vendor/product/{other_product_id}', data=update_data, format='json')
        self.assertEqual(response.status_code, 403, 'Should not be able to update another vendor\'s product')

    def test_delete_product_permission_denied(self):
        # Create another vendor and product
        other_user_id = uuid.uuid4()
        with connections.cursor() as cur:
            cur.execute("""
                INSERT INTO auth_integration (user_id, email)
                VALUES (%(user_id)s, 'othervendor@test.com');

                INSERT INTO vendor
                (user_id, business_name, business_email, phone,
                address_one, city, zip, territory)
                VALUES
                (%(user_id)s, 'Other Vendor', 'othervendor@test.com', '1234567890',
                '123 Other St', 'Other City', '54321', 'USA_KS')
                RETURNING vendor_id;
            """, {'user_id': other_user_id})
            res = cur.fetchone()
            other_vendor_id = res['vendor_id']

            # Insert product for other vendor
            cur.execute("""
                INSERT INTO vendor_product
                (vendor_id, listed_by, product_name, description, initial_price)
                VALUES
                (%(vendor_id)s, %(user_id)s, 'Other Product', 'Other Description', 19.99)
                RETURNING product_id;
            """, {'vendor_id': other_vendor_id, 'user_id': other_user_id})
            res = cur.fetchone()
            other_product_id = res['product_id']

        response = self.client.delete(f'/s/vendor/product/{other_product_id}')
        self.assertEqual(response.status_code, 403, 'Should not be able to delete another vendor\'s product')


class VendorProductImagesViewTests(APITestCase):
    def setUp(self):
        self.user_id = uuid.uuid4()
        self.vendor_id = None
        self.product_id = None

        # Create user, vendor, and product
        with connections.cursor() as cur:
            # Insert user and vendor
            cur.execute("""
                INSERT INTO auth_integration (user_id, email)
                VALUES (%(user_id)s, %(email)s);

                INSERT INTO vendor
                (user_id, business_name, business_email, phone,
                address_one, city, zip, territory)
                VALUES
                (%(user_id)s, 'Vendor Name', 'vendor@test.com', '1234567890',
                '123 Vendor St', 'Vendor City', '54321', 'USA_KS')
                RETURNING vendor_id;
            """, {'user_id': self.user_id, 'email': 'vendor@test.com'})
            res = cur.fetchone()
            self.vendor_id = res['vendor_id']

            # Insert product
            cur.execute("""
                INSERT INTO vendor_product
                (vendor_id, listed_by, product_name, description, initial_price)
                VALUES
                (%(vendor_id)s, %(user_id)s, 'Test Product', 'Test Description', 9.99)
                RETURNING product_id;
            """, {'vendor_id': self.vendor_id, 'user_id': self.user_id})
            res = cur.fetchone()
            self.product_id = res['product_id']

        self.client.force_authenticate(
            user=User(
                user_id=self.user_id,
                email='vendor@test.com',
                username='vendor@test.com',
                vendor_id=self.vendor_id,
                jwt_permissions=['cmx_coffee:vendor']
            )
        )

    @patch('vendor.content.s3client')
    def test_get_product_images_success(self, mock_s3client):
        # Mock the s3client methods
        mock_s3client.list.return_value = ['image1', 'image2']
        mock_s3client.get.side_effect = lambda key: f'https://s3.amazonaws.com/{key}'

        response = self.client.get(f'/s/vendor/product/{self.product_id}/images')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 2)
        expected_url = f'https://s3.amazonaws.com/coffee/public/product/{self.product_id}/image1'
        self.assertEqual(response.data[0]['url'], expected_url)

    @patch('vendor.content.s3client')
    def test_post_product_image_success(self, mock_s3client):
        # Mock the s3client methods
        mock_s3client.list.return_value = []
        mock_s3client.upload.return_value = None

        # Create a fake image file
        from django.core.files.uploadedfile import SimpleUploadedFile
        image_file = SimpleUploadedFile('test_image.jpg', b'file_content', content_type='image/jpeg')

        response = self.client.post(f'/s/vendor/product/{self.product_id}/images', {'image_upload': image_file})
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.data)  # Should return image_id

    @patch('vendor.content.s3client')
    def test_post_product_image_max_limit_reached(self, mock_s3client):
        # Mock the s3client methods
        mock_s3client.list.return_value = ['image' + str(i) for i in range(10)]  # Simulate 10 images already uploaded

        # Create a fake image file
        from django.core.files.uploadedfile import SimpleUploadedFile
        image_file = SimpleUploadedFile('test_image.jpg', b'file_content', content_type='image/jpeg')

        response = self.client.post(f'/s/vendor/product/{self.product_id}/images', {'image_upload': image_file})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data['msg'], 'cannot have more than 10 images for a product, not uploading...')

    @patch('vendor.content.s3client')
    def test_delete_product_image_success(self, mock_s3client):
        image_id = 'image1'
        response = self.client.delete(f'/s/vendor/product/{self.product_id}/image/{image_id}')
        self.assertEqual(response.status_code, 204)
        mock_s3client.delete.assert_called_with(f'coffee/public/product/{self.product_id}/{image_id}')

    @patch('vendor.content.s3client')
    def test_get_product_images_permission_denied(self, mock_s3client):
        # Create another vendor and product
        other_user_id = uuid.uuid4()
        with connections.cursor() as cur:
            cur.execute("""
                INSERT INTO auth_integration (user_id, email)
                VALUES (%(user_id)s, 'othervendor@test.com');

                INSERT INTO vendor
                (user_id, business_name, business_email, phone,
                address_one, city, zip, territory)
                VALUES
                (%(user_id)s, 'Other Vendor', 'othervendor@test.com', '1234567890',
                '123 Other St', 'Other City', '54321', 'USA_KS')
                RETURNING vendor_id;
            """, {'user_id': other_user_id})
            res = cur.fetchone()
            other_vendor_id = res['vendor_id']

            # Insert product for other vendor
            cur.execute("""
                INSERT INTO vendor_product
                (vendor_id, listed_by, product_name, description, initial_price)
                VALUES
                (%(vendor_id)s, %(user_id)s, 'Other Product', 'Other Description', 19.99)
                RETURNING product_id;
            """, {'vendor_id': other_vendor_id, 'user_id': other_user_id})
            res = cur.fetchone()
            other_product_id = res['product_id']

        response = self.client.get(f'/s/vendor/product/{other_product_id}/images')
        self.assertEqual(response.status_code, 403, 'Should not be able to get images of another vendor\'s product')

    @patch('vendor.content.s3client')
    def test_delete_product_image_permission_denied(self, mock_s3client):
        # Create another vendor and product
        other_user_id = uuid.uuid4()
        with connections.cursor() as cur:
            cur.execute("""
                INSERT INTO auth_integration (user_id, email)
                VALUES (%(user_id)s, 'othervendor@test.com');

                INSERT INTO vendor
                (user_id, business_name, business_email, phone,
                address_one, city, zip, territory)
                VALUES
                (%(user_id)s, 'Other Vendor', 'othervendor@test.com', '1234567890',
                '123 Other St', 'Other City', '54321', 'USA_KS')
                RETURNING vendor_id;
            """, {'user_id': other_user_id})
            res = cur.fetchone()
            other_vendor_id = res['vendor_id']

            # Insert product for other vendor
            cur.execute("""
                INSERT INTO vendor_product
                (vendor_id, listed_by, product_name, description, initial_price)
                VALUES
                (%(vendor_id)s, %(user_id)s, 'Other Product', 'Other Description', 19.99)
                RETURNING product_id;
            """, {'vendor_id': other_vendor_id, 'user_id': other_user_id})
            res = cur.fetchone()
            other_product_id = res['product_id']

        image_id = 'image1'
        response = self.client.delete(f'/s/vendor/product/{other_product_id}/image/{image_id}')
        self.assertEqual(response.status_code, 403, 'Should not be able to delete images of another vendor\'s product')





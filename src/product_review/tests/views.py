from rest_framework.test import APITestCase
from rest_framework import status
import uuid
from app.authentication import User
from django.contrib.auth import get_user_model
from app import connections


class DeleteProductReviewTests(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user_id = uuid.uuid4()
        cls.user = User(
            user_id=cls.user_id,
            email='testuser2@example.com',
            jwt_permissions=['cmx_coffee:appuser']
        )
        cls.product_id = 4
        cls.vendor_id = 2
        cls.order_id = uuid.uuid4() 
        cls.payment_id = uuid.uuid4()
        cls.order_item_id = 28
        cls.review_id = 4  # The review ID we'll be deleting

        with connections.cursor() as cursor:
            # Insert user into auth_integration
            cursor.execute("""
                INSERT INTO auth_integration (user_id, email)
                VALUES (%s, %s)
            """, [cls.user_id, 'testuser2@example.com'])
            
            # Insert customer territory
            cursor.execute("""
                INSERT INTO customer_approved_territory (
                    territory_id, state_code, country_code, display_name, tax_rate
                )
                VALUES (%s, %s, %s, %s, %s)
            """, ['USA_KS2', 'KS', 'USA', 'Kansas', 9])

            # Insert vendor territory
            cursor.execute("""
                INSERT INTO vendor_approved_territory (
                    territory_id, state_code, country_code, display_name
                )
                VALUES (%s, %s, %s, %s)
            """, ['USA_KS2', 'K2', 'USA', 'Kansas'])

            # Insert vendor
            cursor.execute("""
                INSERT INTO vendor (
                    vendor_id, user_id, business_name, business_email, phone,
                    address_one, city, zip, territory
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, [
                cls.vendor_id, cls.user_id, 'Vendor Name 2', 'vendor2@example.com',
                '0987654321', 'Vendor Address 2', 'Vendor City 2', '67890', 'USA_KS2'
            ])

            # Insert product
            cursor.execute("""
                INSERT INTO vendor_product (
                    product_id, vendor_id, listed_by, product_name,
                    description, initial_price, status
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, [
                cls.product_id, cls.vendor_id, cls.user_id, 'Product to Delete Review',
                'Description', 25.00, 'A'
            ])

            # Insert payment
            cursor.execute("""
                INSERT INTO mock_payment (
                    payment_id, user_id, payment_method, nickname, billing_address_territory
                )
                VALUES (%s,%s,%s,%s,%s)
            """, [
                cls.payment_id, cls.user_id, 'crcard', 'rahul', 'USA_KS2' 
            ])

            # Insert order
            cursor.execute("""
                INSERT INTO mock_order (
                    order_id, user_id, payment_id, payment_status, status,
                    subtotal, tax_rate, tax, total
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, [
                cls.order_id, cls.user_id, cls.payment_id, 'paid', 'shipped', 
                25.00, 9, 2.25, 27.25
            ])

            # Insert order item
            cursor.execute("""
                INSERT INTO mock_order_item (
                    order_item_id, order_id, product_id, quantity, each_price
                )
                VALUES (%s, %s, %s, %s, %s)
            """, [
                cls.order_item_id, cls.order_id, cls.product_id, 1, 25.00
            ])

            # Insert the review we'll be deleting
            cursor.execute("""
                INSERT INTO product_reviews (
                    review_id, user_id, product_id, review_text, review_score
                )
                VALUES (%s, %s, %s, %s, %s)
            """, [cls.review_id, cls.user_id, cls.product_id, 'Review to delete', 4])
    

    def setUp(self):
        self.user = User(
            user_id=self.user_id,
            email='testuser2@example.com',
            jwt_permissions=['cmx_coffee:appuser']
        )
        self.client.force_authenticate(user=self.user)

    def test_delete_product_review_success(self):
        print(f"Testing with user_id: {self.user_id}")
        print(f"User permissions: {self.user.permissions}")
        print(f"User is_authenticated: {self.user.is_authenticated}")

        # First verify the review exists
        with connections.cursor() as cursor:
            cursor.execute("""
                SELECT review_text, review_score 
                FROM product_reviews 
                WHERE review_id = %s AND user_id = %s AND product_id = %s
            """, [self.review_id, self.user_id, self.product_id])
            review_before = cursor.fetchone()
            
        print(f"\nReview before deletion: {review_before}")
        self.assertIsNotNone(review_before, "Review should exist before deletion")
        
        # Make DELETE request to remove review with the exact URL pattern from urls.py
        url = f'/s/product/{self.product_id}/review/{self.review_id}'
        print(f"\nTrying DELETE request to URL: {url}")
        response = self.client.delete(url)
        
        print(f"API Response:")
        print(f"Response status: {response.status_code}")
        print(f"Response content: {response.content.decode()}")
        if hasattr(response, 'data'):
            print(f"Response data: {response.data}")
        
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        
        # Verify review was deleted
        with connections.cursor() as cursor:
            cursor.execute("""
                SELECT review_text, review_score 
                FROM product_reviews 
                WHERE review_id = %s AND user_id = %s AND product_id = %s
            """, [self.review_id, self.user_id, self.product_id])
            review_after = cursor.fetchone()
            
        print(f"\nReview after deletion: {review_after}")
        self.assertIsNone(review_after, "Review should not exist after deletion")

class AddProductReviewTests(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user_id = uuid.uuid4()
        cls.user = User(
            user_id=cls.user_id,
            email='testuser@example.com',
            jwt_permissions=['cmx_coffee:appuser']
        )
        cls.product_id = 3
        cls.vendor_id = 1
        cls.order_id = uuid.uuid4()  
        cls.payment_id = uuid.uuid4()  
        cls.order_item_id = 27  

        with connections.cursor() as cursor:
            # Insert user into auth_integration
            cursor.execute("""
                INSERT INTO auth_integration (user_id, email)
                VALUES (%s, %s)
            """, [cls.user_id, 'testuser@example.com'])

            # Insert customer territory
            cursor.execute("""
                INSERT INTO customer_approved_territory (
                    territory_id, state_code, country_code, display_name, tax_rate
                )
                VALUES (%s, %s, %s, %s, %s)
            """, ['USA_KS1', 'KS', 'USA', 'Kansas', 9])

            # Insert vendor territory
            cursor.execute("""
                INSERT INTO vendor_approved_territory (
                    territory_id, state_code, country_code, display_name
                )
                VALUES (%s, %s, %s, %s)
            """, ['USA_KS1', 'K1', 'USA', 'Kansas'])

            # Insert vendor using cls.user_id (UUID)
            cursor.execute("""
                INSERT INTO vendor (
                    vendor_id, user_id, business_name, business_email, phone,
                    address_one, city, zip, territory
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, [
                cls.vendor_id, cls.user_id, 'Vendor Name', 'vendor@example.com',
                '1234567890', 'Vendor Address', 'Vendor City', '54321', 'USA_KS1'
            ])

            # Insert product using cls.user_id (UUID)
            cursor.execute("""
                INSERT INTO vendor_product (
                    product_id, vendor_id, listed_by, product_name,
                    description, initial_price, status
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, [
                cls.product_id, cls.vendor_id, cls.user_id, 'Product to Review',
                'Description', 20.00, 'A'
            ])

            # Insert payment to simulate payment
            cursor.execute("""
                INSERT INTO mock_payment (
                    payment_id, user_id, payment_method, nickname, billing_address_territory
                )
                VALUES (%s,%s,%s,%s,%s)
            """, [
                cls.payment_id, cls.user_id, 'crcard', 'will', 'USA_KS1' 
            ])

            # Insert order to simulate purchase
            cursor.execute("""
                INSERT INTO mock_order (
                    order_id, user_id, payment_id, payment_status, status,
                    subtotal, tax_rate, tax, total
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, [
                cls.order_id, cls.user_id, cls.payment_id, 'paid', 'shipped',
                20.00, 9, 1.80, 21.80
            ])

            # Insert order item to link product to order
            cursor.execute("""
                INSERT INTO mock_order_item (
                    order_item_id, order_id, product_id, quantity, each_price
                )
                VALUES (%s, %s, %s, %s, %s)
            """, [
                cls.order_item_id, cls.order_id, cls.product_id, 1, 20.00
            ])

    def setUp(self):
        self.user = User(
            user_id=self.user_id,
            email='testuser@example.com',
            jwt_permissions=['cmx_coffee:appuser']
        )
        self.client.force_authenticate(user=self.user)

    def test_add_product_review_success(self):
        print(f"Testing with user_id: {self.user_id}")
        print(f"User permissions: {self.user.permissions}")
        print(f"User is_authenticated: {self.user.is_authenticated}")
        
        review_data = {
            "review_text": "Great coffee product!",
            "review_score": 5
        }
        
        url = f'/s/product/{self.product_id}/reviews'
        
        # Make POST request to add review
        response = self.client.post(
            url,
            data=review_data,
            format='json'
        )
        
        print(f"\nAPI Response:")
        print(f"Response status: {response.status_code}")
        print(f"Response data: {getattr(response, 'data', None)}")
        print(f"Response content: {response.content.decode()}")
        
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        
        # Verify review was added to database
        with connections.cursor() as cursor:
            cursor.execute("""
                SELECT review_text, review_score 
                FROM product_reviews 
                WHERE user_id = %s AND product_id = %s
            """, [self.user_id, self.product_id])
            review = cursor.fetchone()
            
            print(f"Retrieved review: {review}")
            
        self.assertIsNotNone(review, "No review was found in the database after insertion")
        # Access dictionary values by column names instead of indices
        self.assertEqual(review['review_text'], "Great coffee product!")
        self.assertEqual(review['review_score'], 5)


class GetProductReviewStatsTests(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.product_id = 2
        cls.user_id = uuid.uuid4()
        cls.vendor_id = 3

        with connections.cursor() as cursor:
            # Insert territory with 'state_code' as 'KS'
            cursor.execute("""
                INSERT INTO vendor_approved_territory (
                    territory_id, state_code, country_code, display_name
                )
                VALUES (%s, %s, %s, %s)
            """, ['USA_KS3', 'K3', 'US', 'Kansas'])

            # Insert user
            cursor.execute("""
                INSERT INTO auth_integration (user_id, email)
                VALUES (%s, %s)
            """, [cls.user_id, 'testuser@example.com'])

            # Insert vendor with 'territory' matching 'territory_id'
            cursor.execute("""
                INSERT INTO vendor (
                    vendor_id, user_id, business_name, business_email, phone,
                    address_one, city, zip, territory
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, [
                cls.vendor_id, cls.user_id, 'Vendor Name', 'vendor@example.com',
                '1234567890', 'Vendor Address', 'Vendor City', '54321', 'USA_KS3'
            ])

            # Insert product
            cursor.execute("""
                INSERT INTO vendor_product (
                    product_id, vendor_id, listed_by, product_name,
                    description, initial_price, status
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, [
                cls.product_id, cls.vendor_id, cls.user_id, 'Another Test Product',
                'Description', 15.00, 'A'
            ])

            # Insert reviews
            cursor.executemany("""
                INSERT INTO product_reviews (
                    review_id, user_id, product_id, review_text, review_score
                )
                VALUES (%s, %s, %s, %s, %s)
            """, [
                [2, cls.user_id, cls.product_id, 'Good product.', 4],
                [3, cls.user_id, cls.product_id, 'Not bad.', 3]
            ])

    def setUp(self):
        # Authenticate user for API requests
        self.user = User(user_id=self.user_id)
        self.client.force_authenticate(user=self.user)

    def test_get_product_review_stats_success(self):
        response = self.client.get(f'/product/{self.product_id}/review-stats')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['review_count'], 2)
        self.assertAlmostEqual(float(response.data['average_review_score']), 3.5)


class GetProductReviewsTests(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.product_id = 1
        cls.user_id = uuid.uuid4()
        cls.vendor_id = 4

        with connections.cursor() as cursor:
            # Insert territory with 'state_code' as 'KS'
            cursor.execute("""
                INSERT INTO vendor_approved_territory (
                    territory_id, state_code, country_code, display_name
                )
                VALUES (%s, %s, %s, %s)
            """, ['USA_KS4', 'K4', 'US', 'Kansas'])

            # Insert user
            cursor.execute("""
                INSERT INTO auth_integration (user_id, email)
                VALUES (%s, %s)
            """, [cls.user_id, 'testuser@example.com'])

            # Insert vendor with 'territory' matching 'territory_id'
            cursor.execute("""
                INSERT INTO vendor (
                    vendor_id, user_id, business_name, business_email, phone,
                    address_one, city, zip, territory
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, [
                cls.vendor_id, cls.user_id, 'Vendor Name', 'vendor@example.com',
                '1234567890', 'Vendor Address', 'Vendor City', '54321', 'USA_KS4'
            ])

            # Insert product
            cursor.execute("""
                INSERT INTO vendor_product (
                    product_id, vendor_id, listed_by, product_name,
                    description, initial_price, status
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, [
                cls.product_id, cls.vendor_id, cls.user_id, 'Test Product',
                'Description', 10.00, 'A'
            ])

            # Insert a review
            cursor.execute("""
                INSERT INTO product_reviews (
                    review_id, user_id, product_id, review_text, review_score
                )
                VALUES (%s, %s, %s, %s, %s)
            """, [1, cls.user_id, cls.product_id, 'Great product!', 5])

    def setUp(self):
        # Authenticate user for API requests
        self.user = User(user_id=self.user_id)
        self.client.force_authenticate(user=self.user)

    def test_get_product_reviews_success(self):
        response = self.client.get(f'/product/{self.product_id}/reviews')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['review_text'], 'Great product!')


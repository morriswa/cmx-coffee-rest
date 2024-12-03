
import uuid

from unittest.mock import patch
from rest_framework.test import APITestCase

from app.authentication import User

from customer.models import CartItem, CustomerPreferences


class CustomerPreferencesViewTests(APITestCase):
    @patch('customer.daos.get_customer_preferences')
    def test_get_customer_preferences_200(self, mock_get_customer_preferences):

        mock_get_customer_preferences.return_value = CustomerPreferences(
            strength_mild = 'y',
            strength_med = 'n',
            strength_bold = 'n',
            blonde = 'y',
            caffinated = 'n',
            decaf = 'y',
            flavored = 'y',
            single_origin = 'y',
            origin_blend = 'n',
            newsletter_subscription = 'y'
        )
        
        self.client.force_authenticate(
            user=User(
                user_id=uuid.uuid4(),
                email='test@morriswa.org',
                username='test@morriswa.org',
                vendor_id=None,
                jwt_permissions=[]
            )
        )

        self.client.force_authenticate(User(
            user_id=uuid.uuid4(),
            email='test@morriswa.org',
            username='test@morriswa.org',
            vendor_id=None,
            jwt_permissions=[]
        ))

        response = self.client.get('/s/profile/product-preferences')

        self.assertEqual(response.status_code, 200, 'customers should get requested data...')
        self.assertEqual(response.data['strength_mild'], 'y')
        self.assertEqual(response.data['strength_med'], 'n')
        self.assertEqual(response.data['strength_bold'], 'n')
        self.assertEqual(response.data['blonde'], 'y')
        self.assertEqual(response.data['caffinated'], 'n')
        self.assertEqual(response.data['decaf'], 'y')
        self.assertEqual(response.data['flavored'], 'y')
        self.assertEqual(response.data['single_origin'], 'y')
        self.assertEqual(response.data['origin_blend'], 'n')
        self.assertEqual(response.data['newsletter_subscription'], 'y')

    @patch('customer.daos.update_customer_preferences')
    def test_update_customer_preferences_204(self, mock_update_customer_preferences):


        self.client.force_authenticate(User(
            user_id=uuid.uuid4(),
            email='test@morriswa.org',
            username='test@morriswa.org',
            vendor_id=None,
            jwt_permissions=[]
        ))

        request_body = {
            'strength_mild': 'y',
            'strength_med': 'n',
            'decaf': 'n'
        }

        response = self.client.patch('/s/profile/product-preferences', data=request_body, format='json')

        # assert
        self.assertEqual(response.status_code, 204, 'customers should not get any data...')


class ShoppingCartViewTests(APITestCase):

    @patch('customer.daos.get_shopping_cart')
    def test_get_shopping_cart_200(self, mock_shopping_cart):

        mock_shopping_cart.return_value = [CartItem(
            product_id=1,
            quantity=1,
            product_name='Coffee',
            description='Coffee',
            vendor_name='Coffee',
            sale_price=1.00
        )]

        self.client.force_authenticate(User(
            user_id=uuid.uuid4(),
            email='test@morriswa.org',
            username='test@morriswa.org',
            vendor_id=None,
            jwt_permissions=[]
        ))

        response = self.client.get('/s/cart')

        self.assertEqual(response.status_code, 200, 'customers should get requested data...')
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['product_name'], 'Coffee')


    @patch('customer.daos.get_shopping_cart', )
    @patch('customer.daos.update_shopping_cart')
    def test_update_shopping_cart_200(self, mock_update_shopping_cart, mock_get_shopping_cart_after_update):

        test_product_id = 1
        test_quantity = 3
        test_product_name = 'Coffee'

        mock_get_shopping_cart_after_update.return_value = [CartItem(
            product_id=test_product_id,
            quantity=test_quantity,
            product_name=test_product_name,
            description='Coffee',
            vendor_name='Coffee',
            sale_price=1.00
        )]

        self.client.force_authenticate(
            user=User(
                user_id=uuid.uuid4(),
                email='test@morriswa.org',
                username='test@morriswa.org',
                vendor_id=None,
                jwt_permissions=[]
            ),
        )

        request_body = [
            {
                'product_id': test_product_id,
                'quantity': test_quantity
            }
        ]

        # execute
        response = self.client.patch('/s/cart', data=request_body, format='json')

        # assert
        self.assertEqual(response.status_code, 200, 'customers should get requested data...')
        self.assertEqual(len(response.data), 1, 'Should return 1 item')
        self.assertEqual(response.data[0]['quantity'], test_quantity, 'Quantity should now be equal to 3')
        self.assertEqual(response.data[0]['product_id'], test_product_id)
        self.assertEqual(response.data[0]['product_name'], test_product_name)



    @patch('customer.daos.reset_shopping_cart')
    def test_delete_shopping_cart_204(self, mock_reset_shopping_cart):

        self.client.force_authenticate(User(
            user_id=uuid.uuid4(),
            email='test@morriswa.org',
            username='test@morriswa.org',
            vendor_id=None,
            jwt_permissions=[]
        ))

        response = self.client.delete('/s/cart')
        self.assertEqual(response.status_code, 204, 'customers should get no data...')

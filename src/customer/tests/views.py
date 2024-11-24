
import uuid

from unittest.mock import patch
from rest_framework.test import APITestCase

from app.authentication import User

from customer.models import CartItem, CustomerPreferences


class CustomerPreferencesViewTests(APITestCase):
    @patch('customer.daos.get_customer_preferences')
    def test_get_customer_preferences_200(self, mock_get_customer_preferences):

        mock_get_customer_preferences.return_value = CustomerPreferences(
            strength_mild = True,
            strength_med = False,
            strength_bold = True,
            blonde = False,
            caffinated = True,
            decaf = False,
            flavored = True,
            single_origin = True,
            origin_blend = False,
            newsletter_subscription = 'daily'
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
        self.assertEqual(response.data['strength_mild'], True)
        self.assertEqual(response.data['strength_med'], False)
        self.assertEqual(response.data['strength_bold'], True)
        self.assertEqual(response.data['blonde'], False)
        self.assertEqual(response.data['caffinated'], True)
        self.assertEqual(response.data['decaf'], False)
        self.assertEqual(response.data['flavored'], True)
        self.assertEqual(response.data['single_origin'], True)
        self.assertEqual(response.data['origin_blend'], False)
        self.assertEqual(response.data['newsletter_subscription'], 'daily')


    @patch('customer.daos.update_customer_preferences')
    def test_update_customer_preferences_204(self, mock_update_customer_preferences):

        strength_mild = False
        strength_med = True
        decaf = True

        self.client.force_authenticate(User(
            user_id=uuid.uuid4(),
            email='test@morriswa.org',
            username='test@morriswa.org',
            vendor_id=None,
            jwt_permissions=[]
        ))

        request_body = {
            'strength_mild': 'y',
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

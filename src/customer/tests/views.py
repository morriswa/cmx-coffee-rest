from django.test import TestCase, Client
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from app.authentication import User
import customer.daos as dao
import uuid
from unittest.mock import patch
from customer.models import CartItem

class CustomerViewTest(APITestCase):

    def mock_shopping_cart(user_id):
        return [
            CartItem(
                product_id=1,
                quantity=1,
                product_name='Coffee',
                description='Coffee',
                vendor_name='Coffee',
                sale_price=1.00
            )
        ]

    @patch('customer.daos.get_shopping_cart', side_effect=mock_shopping_cart)
    def test_get_shopping_cart_200(self, mock_get_shopping_cart):
        self.client.force_authenticate(
            user=User(
                user_id=uuid.uuid4(),
                email='test@morriswa.org',
                username='test@morriswa.org',
                vendor_id=None,
                jwt_permissions=['cmx_coffee:customer']
            ),
        )

        response = self.client.get('/s/cart')

        self.assertEqual(response.status_code, 200, 'customers should get requested data...')
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['product_name'], 'Coffee')
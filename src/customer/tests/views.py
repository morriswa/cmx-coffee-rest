

from django.test import TestCase, Client
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from app.authentication import User
from customer.models import CustomerPreferences, CartItem
import customer.daos as dao
import uuid

class CustomerPreferencesViewTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(email='testuser@example.com', password='testpassword')
        self.client.force_authenticate(user=self.user)
        self.preferences_url = reverse('customer-preferences')

    def test_get_customer_preferences(self):
        # Setup initial preferences
        dao.update_customer_preferences(self.user.user_id, CustomerPreferences(
            strength_mild=True,
            strength_med=False,
            strength_bold=True,
            blonde=False,
            caffinated=True,
            decaf=False,
            flavored=True,
            single_origin=False,
            origin_blend=True,
            newsletter_subscription=True
        ))

        response = self.client.get(self.preferences_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['strength_mild'], True)

    def test_patch_customer_preferences(self):
        new_preferences = {
            'strength_mild': False,
            'strength_med': True,
            'strength_bold': False,
            'blonde': True,
            'caffinated': False,
            'decaf': True,
            'flavored': False,
            'single_origin': True,
            'origin_blend': False,
            'newsletter_subscription': False
        }

        response = self.client.patch(self.preferences_url, new_preferences, format='json')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        updated_preferences = dao.get_customer_preferences(self.user.user_id)
        self.assertEqual(updated_preferences.strength_mild, False)
        self.assertEqual(updated_preferences.strength_med, True)


class ShoppingCartViewTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(email='testuser@example.com', password='testpassword')
        self.client.force_authenticate(user=self.user)
        self.cart_url = reverse('shopping-cart')

    def test_get_shopping_cart(self):
        # Setup initial cart items
        dao.update_shopping_cart(self.user.user_id, [(1, 2), (2, 3)])

        response = self.client.get(self.cart_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_patch_shopping_cart(self):
        new_items = [
            {'product_id': 1, 'quantity': 5},
            {'product_id': 2, 'quantity': 1}
        ]

        response = self.client.patch(self.cart_url, new_items, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        updated_cart = dao.get_shopping_cart(self.user.user_id)
        self.assertEqual(len(updated_cart), 2)
        self.assertEqual(updated_cart[0].quantity, 5)
        self.assertEqual(updated_cart[1].quantity, 1)

    def test_delete_shopping_cart(self):
        # Setup initial cart items
        dao.update_shopping_cart(self.user.user_id, [(1, 2), (2, 3)])

        response = self.client.delete(self.cart_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        updated_cart = dao.get_shopping_cart(self.user.user_id)
        self.assertEqual(len(updated_cart), 0)
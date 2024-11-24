import uuid
from django.test import TestCase
from app import connections
from customer.models import CustomerPreferences, CartItem
import customer.daos as dao

class CustomerDAOTest(TestCase):
    def setUp(self):
        self.user_id = uuid.uuid4()

    def test_get_customer_preferences(self):
        # Setup initial preferences
        with connections.cursor() as cur:
            cur.execute("""
                INSERT INTO customer_preferences (
                    user_id, p_cb_strength_mild, p_cb_strength_med, p_cb_strength_bold,
                    p_cb_strength_blonde, p_cb_caf, p_cb_decaf, p_cb_flavored,
                    p_cb_origin_single, p_cb_origin_blend, p_cb_keywords, n_newsletter_subscription
                ) VALUES (
                    %(user_id)s, TRUE, FALSE, TRUE, FALSE, TRUE, FALSE, TRUE, FALSE, TRUE, '', TRUE
                )
            """, {'user_id': self.user_id})

        preferences = dao.get_customer_preferences(self.user_id)
        self.assertIsNotNone(preferences)
        self.assertTrue(preferences.strength_mild)

    def test_update_customer_preferences(self):
        new_preferences = CustomerPreferences(
            strength_mild=False,
            strength_med=True,
            strength_bold=False,
            blonde=True,
            caffinated=False,
            decaf=True,
            flavored=False,
            single_origin=True,
            origin_blend=False,
            newsletter_subscription=False
        )

        dao.update_customer_preferences(self.user_id, new_preferences)

        updated_preferences = dao.get_customer_preferences(self.user_id)
        self.assertIsNotNone(updated_preferences)
        self.assertFalse(updated_preferences.strength_mild)
        self.assertTrue(updated_preferences.strength_med)

    def test_get_shopping_cart(self):
        # Setup initial cart items
        with connections.cursor() as cur:
            cur.execute("""
                INSERT INTO shopping_cart (user_id, product_id, quantity)
                VALUES (%(user_id)s, 1, 2), (%(user_id)s, 2, 3)
            """, {'user_id': self.user_id})

        cart = dao.get_shopping_cart(self.user_id)
        self.assertEqual(len(cart), 2)
        self.assertEqual(cart[0].product_id, 1)
        self.assertEqual(cart[0].quantity, 2)

    def test_update_shopping_cart(self):
        new_items = [(1, 5), (2, 1)]

        dao.update_shopping_cart(self.user_id, new_items)

        updated_cart = dao.get_shopping_cart(self.user_id)
        self.assertEqual(len(updated_cart), 2)
        self.assertEqual(updated_cart[0].quantity, 5)
        self.assertEqual(updated_cart[1].quantity, 1)

    def test_reset_shopping_cart(self):
        # Setup initial cart items
        with connections.cursor() as cur:
            cur.execute("""
                INSERT INTO shopping_cart (user_id, product_id, quantity)
                VALUES (%(user_id)s, 1, 2), (%(user_id)s, 2, 3)
            """, {'user_id': self.user_id})

        dao.reset_shopping_cart(self.user_id)

        updated_cart = dao.get_shopping_cart(self.user_id)
        self.assertEqual(len(updated_cart), 0)
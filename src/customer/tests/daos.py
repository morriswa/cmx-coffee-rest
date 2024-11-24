import uuid
from django.test import TestCase
from app import connections
from customer.models import CustomerPreferences, CartItem
import customer.daos as dao

class CustomerDAOTest(TestCase):
    def setUp(self):
        self.user_id = uuid.uuid4()

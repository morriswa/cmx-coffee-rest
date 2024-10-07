"""
    Vendor-related django unit tests go here
"""

from django.test import TestCase
from django.conf import settings

class VendorTests(TestCase):

    def test_app_in_test_runtime(self):
        #Get the runtime environment
        runtime = settings.RUNTIME_ENVIRONMENT
        #Assert that the runtime environemnt is test
        self.assertEqual(runtime, 'test', 'Application should have been bootstrapped in test runtime')

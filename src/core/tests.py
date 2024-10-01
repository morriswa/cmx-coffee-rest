from django.test import TestCase
from django.conf import settings

#Test case class for the CoreAppTest application
class CoreAppTest(TestCase):
    #Checks if the application is in the test runtime
    def test_app_in_test_runtime(self):
        #Get the runtime environment
        runtime = settings.RUNTIME_ENVIRONMENT
        #Assert that the runtime environemnt is test
        self.assertEqual(runtime, 'test', 'Application should have been bootstrapped in test runtime')

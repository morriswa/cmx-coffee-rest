import uuid

from django.test import TestCase
from django.conf import settings

from rest_framework.test import APITestCase

from app.authentication import User


class RuntimeTests(TestCase):
    def test_app_in_test_runtime(self):
        """ simple test to ensure test environment is setup correctly """

        #Assert that the runtime environemnt is test
        self.assertEqual(
            settings.RUNTIME_ENVIRONMENT,
            'test',
            'Application should have been bootstrapped in test runtime'
        )
        self.assertEqual(
            settings.AWS_S3_ENVIRONMENT,
            'test',
            'S3 should have been bootstrapped in test environment'
        )


class HealthEndpointTests(APITestCase):
    def test_health_endpoint_200(self):
        """ ensure health endpoint produces desired ouput """

        # submit mock http request to health endpoint
        response = self.client.get('/health')
        # assert response status and body is correct
        self.assertEqual(response.status_code, 200, 'should get desired status code')
        self.assertEqual(response.data, {'msg': 'hello world!'}, 'should get desired response')

class UserPermissionsEndpointTests(APITestCase):
    def test_user_permissions_endpoint_401(self):
        """ ensure only authenticated users can access secure user permissions endpoint"""

        # submit mock http request to health endpoint
        response = self.client.get('/s/permissions')
        # assert response status and body is correct
        self.assertEqual(response.status_code, 401, 'not authorized if no auth header is present')
        self.assertEqual(
            response.data,
            {"msg": "Failed to provide Authorization header"},
            'should get correct error response'
        )

    def test_user_permissions_endpoint_200(self):
        """ ensure authenticated users can get an accurate list of their permissions """

        # setup
        self.client.force_authenticate(
            user=User(
                user_id=uuid.uuid4(),
                email='test@morriswa.org',
                username='test@morriswa.org',
                vendor_id=None,
                jwt_permissions=[]
            ),
        )

        # submit mock http request to health endpoint
        response = self.client.get('/s/permissions')

        # assert response status and body is correct
        self.assertEqual(response.status_code, 200, 'authorized if auth header is present')
        self.assertSetEqual(
            set(response.data),
            {'cmx_coffee:appuser'},
            'returns correct permissions set'
        )

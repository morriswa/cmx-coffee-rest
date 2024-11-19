import uuid
import jwt

from unittest import mock
from django.test import TestCase
from django.conf import settings

from rest_framework.request import Request
from rest_framework.test import APITestCase
from rest_framework import exceptions

from app.authentication import *
from app.authentication.utils import *


class UserAuthenticationWithJwtTests(TestCase):

    @mock.patch('app.authentication.jwt_decode_token')
    @mock.patch('app.authentication.get_user_info')
    def test_successfully_authenticate_user(self, mock_get_user_info_from_db, mock_jwt_decode_token):

        # setup
        mock_user_id = uuid.uuid4()
        mock_get_user_info_from_db.return_value = mock_user_id, None
        mock_jwt_decode_token.return_value = {
            'permissions': [],
            'email': 'test@morriswa.org',
        }

        request = type('test_request', (object,), {})
        request.META = {
            'HTTP_AUTHORIZATION': 'Bearer Test'
        }

        auth = UserAuthenticationWithJwt()

        # execute
        user, token = auth.authenticate(request)

        # assert
        self.assertEqual(user.user_id, mock_user_id, 'user id should match')
        self.assertIsNone(user.vendor_id, 'no vendor id was provided, should be none')
        self.assertSetEqual(set(user.permissions), {'cmx_coffee:appuser'}, 'should only have default auth, no elevated permissions')

    def test_reject_user_no_auth_header(self):
        # setup
        request = type('test_request', (object,), {})
        request.META = {}

        auth = UserAuthenticationWithJwt()

        # execute
        try:
            auth_response = auth.authenticate(request)
        # assert
        except Exception as e:
            self.assertTrue(isinstance(e, exceptions.AuthenticationFailed), 'correct exception should be thrown')
            self.assertEqual(e.detail, 'Failed to provide Authorization header')
            self.assertEqual(e.status_code, 401, 'correct http code returned')

    @mock.patch('app.authentication.jwt_decode_token')
    def test_reject_user_expired_token(self, mock_jwt_decode_token):
        # setup
        mock_jwt_decode_token.side_effect = jwt.ExpiredSignatureError()

        request = type('test_request', (object,), {})
        request.META = {
            'HTTP_AUTHORIZATION': 'Bearer Test'
        }

        auth = UserAuthenticationWithJwt()

        # execute
        try:
            auth_response = auth.authenticate(request)
        # assert
        except Exception as e:
            self.assertTrue(isinstance(e, exceptions.AuthenticationFailed), 'correct exception should be thrown')
            self.assertEqual(e.detail, 'Token has expired.', 'correct message is displayed')
            self.assertEqual(e.status_code, 401, 'correct http code returned')

    @mock.patch('app.authentication.jwt_decode_token')
    def test_reject_user_invalid_token_decode_error(self, mock_jwt_decode_token):
        # setup
        mock_jwt_decode_token.side_effect = jwt.DecodeError()

        request = type('test_request', (object,), {})
        request.META = {
            'HTTP_AUTHORIZATION': 'Bearer Test'
        }

        auth = UserAuthenticationWithJwt()

        # execute
        try:
            auth_response = auth.authenticate(request)
        # assert
        except Exception as e:
            self.assertTrue(isinstance(e, exceptions.AuthenticationFailed), 'correct exception should be thrown')
            self.assertEqual(e.detail, 'Error decoding token.', 'correct message is displayed')
            self.assertEqual(e.status_code, 401, 'correct http code returned')

    @mock.patch('app.authentication.jwt_decode_token')
    def test_reject_user_invalid_token(self, mock_jwt_decode_token):
        # setup
        mock_jwt_decode_token.side_effect = jwt.InvalidTokenError()

        request = type('test_request', (object,), {})
        request.META = {
            'HTTP_AUTHORIZATION': 'Bearer Test'
        }

        auth = UserAuthenticationWithJwt()

        # execute
        try:
            auth_response = auth.authenticate(request)
        # assert
        except Exception as e:
            self.assertTrue(isinstance(e, exceptions.AuthenticationFailed), 'correct exception should be thrown')
            self.assertEqual(e.detail, 'Invalid token.', 'correct message is displayed')
            self.assertEqual(e.status_code, 401, 'correct http code returned')

    @mock.patch('app.authentication.jwt_decode_token')
    def test_reject_user_any_error(self, mock_jwt_decode_token):
        # setup
        mock_jwt_decode_token.side_effect = Exception()

        request = type('test_request', (object,), {})
        request.META = {
            'HTTP_AUTHORIZATION': 'Bearer Test'
        }

        auth = UserAuthenticationWithJwt()

        # execute
        try:
            auth_response = auth.authenticate(request)
        # assert
        except Exception as e:
            self.assertTrue(isinstance(e, exceptions.AuthenticationFailed), 'correct exception should be thrown')
            self.assertEqual(e.detail, 'Failed to authenticate, no further details.', 'correct message is displayed')
            self.assertEqual(e.status_code, 401, 'correct http code returned')


class AppAuthenticationUtilsTests(TestCase):

    test_token = {
        'scope': "test_one test_two test_three",
        'permissions': ["test_one", "test_two", "test_three"],
    }

    def test_scope_empty_jwt_one_requirements(self):
        res = jwt_has_scope({'scope':''}, ['test_one'])
        self.assertFalse(res, 'if one scopes is required but none are provided, user cannot have access')

    def test_permission_empty_jwt_one_requirements(self):
        res = jwt_has_permissions({'permissions':[]}, ['test_one'])
        self.assertFalse(res, 'if one permission is required but none are provided, user cannot have access')

    def test_jwt_has_scope_no_requirements(self):
        res = jwt_has_scope(self.test_token, [])
        self.assertTrue(res, 'if no scopes are required, user can have access')

    def test_jwt_has_scope_one_requirement(self):
        res = jwt_has_scope(self.test_token, ['test_one'])
        self.assertTrue(res, 'if one scopes is required and present, user can have access')

    def test_jwt_has_scope_missing_one_requirement(self):
        res = jwt_has_scope(self.test_token, ['test_four'])
        self.assertFalse(res, 'if one scope is missing, user can NOT access')

    def test_jwt_has_scope_two_requirements(self):
        res = jwt_has_scope(self.test_token, ['test_one', 'test_three'])
        self.assertTrue(res, 'if multiple scopes are required and present, user can have access')

    def test_jwt_has_scope_two_requirements_missing_one(self):
        res = jwt_has_scope(self.test_token, ['test_one', 'test_four'])
        self.assertFalse(res, 'if one scope is missing, user can NOT access')

    def test_jwt_has_permission_no_requirements(self):
        res = jwt_has_scope(self.test_token, [])
        self.assertTrue(res, 'if no scopes are required, user can have access')

    def test_jwt_has_permission_one_requirement(self):
        res = jwt_has_scope(self.test_token, ['test_one'])
        self.assertTrue(res, 'if one scopes is required and present, user can have access')

    def test_jwt_has_permission_missing_one_requirement(self):
        res = jwt_has_scope(self.test_token, ['test_four'])
        self.assertFalse(res, 'if one scope is missing, user can NOT access')

    def test_jwt_has_permission_two_requirements(self):
        res = jwt_has_scope(self.test_token, ['test_one', 'test_three'])
        self.assertTrue(res, 'if multiple scopes are required and present, user can have access')

    def test_jwt_has_permission_two_requirements_missing_one(self):
        res = jwt_has_scope(self.test_token, ['test_one', 'test_four'])
        self.assertFalse(res, 'if one scope is missing, user can NOT access')

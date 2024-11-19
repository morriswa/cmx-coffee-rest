import datetime
import uuid

from rest_framework.test import APITestCase
from unittest.mock import patch

from app.authentication import User
from app.exceptions import BadRequestException

from admin.models import AdminVendorInfo
from vendor.models import VendorApplicationResponse

class ApplicationForVendorTest(APITestCase):
    '''Test for applying for vendor'''
    def test_apply_for_vendor(self):
        '''Test for applying for vendor'''
        # setup

        self.client.force_authenticate(
            user=User(
                user_id=uuid.uuid4(),
                business_name='test business',
                business_email='test@yahoo.com',
                business_phone='1234567890',
                business_address1='1234 test street',
                business_address2='apt 123',
                business_city='test city',
                business_state='test state',
                business_zip='12345',
                business_country='test country',
            )
        )
        #submit mock http request to apply for vendor
        response = self.client.post('/s/forms/vendor-application')

        # assert
        self.assertEqual(response.status_code, 403, 'default users are not allowed...')
        self.assertEqual(
            response.data,
            {'msg': 'You do not have permission to perform this action.'},
            'correct body'
        )
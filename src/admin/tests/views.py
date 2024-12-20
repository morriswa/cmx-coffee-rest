import datetime
import uuid

from rest_framework.test import APITestCase
from unittest.mock import patch

from app.authentication import User
from app.exceptions import BadRequestException

from admin.models import AdminVendorInfo
from vendor.models import VendorApplicationResponse



class PendingVendorApplicationEndpointTests(APITestCase):
    def test_get_pending_vendor_applications_403(self):
        """ ensure users without admin permission are denied access to this endpoint """

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
        response = self.client.get('/s/admin/vendor-applications')

        # assert
        self.assertEqual(response.status_code, 403, 'default users are not allowed...')
        self.assertEqual(
            response.data,
            {'msg': 'You do not have permission to perform this action.'},
            'correct body'
        )

    def test_get_pending_vendor_applications_401(self):
        """ ensure users with no authentication header are denied access to this endpoint """

        # execute
        response = self.client.get('/s/admin/vendor-applications')

        # assert
        self.assertEqual(response.status_code, 401, 'anon users are not allowed...')
        self.assertEqual(
            response.data,
            {'msg': 'Failed to provide Authorization header'},
            'correct body'
        )

    @staticmethod
    def mock_get_pending_vendor_applications():
        """ unittest mock for admin.daos.get_pending_vendor_applications """
        apps = []
        apps.append(VendorApplicationResponse(
            application_id=1,
            status='N',
            application_date=datetime.date.today(),
            state_code='CA',
            country_code='USA',
            business_name='test application 1',
            business_email='biz@morriswa.org',
            phone='1231231234',
            address_one='1234 Happy St',
            city='City',
            zip='55555',
            territory='TEST_CASE'
        ))
        return apps

    @patch(  # replace dao function with mock to test view in isolation
        'admin.daos.get_pending_vendor_applications', mock_get_pending_vendor_applications
    )
    def test_get_pending_vendor_applications_200(self):
        # setup
        self.client.force_authenticate(
            user=User(
                user_id=uuid.uuid4(),
                email='test@morriswa.org',
                username='test@morriswa.org',
                vendor_id=None,
                jwt_permissions=['cmx_coffee:admin']
            ),
        )

        # execute
        response = self.client.get('/s/admin/vendor-applications')

        # assert
        self.assertEqual(response.status_code, 200, 'admin users should get requested data...')
        self.assertTrue(
            isinstance(response.data, list),
            'correct body format (json list)'
        )
        self.assertEqual(
            len(response.data),
            1,
            '1 application in db'
        )
        self.assertEqual(
            response.data[0]['business_name'],
            'test application 1',
            'correct value retrieved from db'
        )


class ProcessPendingVendorApplicationEndpointTests(APITestCase):
    @patch(
        'admin.daos.approve_vendor_application'
    )
    def test_approve_pending_vendor_application_200(self, mock_approve_vendor_application):
        """ ensure admins can approve vendors """

        # setup
        self.client.force_authenticate(
            user=User(
                user_id=uuid.uuid4(),
                email='test@morriswa.org',
                username='test@morriswa.org',
                vendor_id=None,
                jwt_permissions=['cmx_coffee:admin']
            ),
        )
        app_id = 1234
        applicant_user_id = uuid.uuid4()

        # execute
        response = self.client.put(
            f"/s/admin/vendor-application/{app_id}?action=approve"
        )

        # assert
        self.assertEqual(response.status_code, 204, 'good')

    @patch(
        'admin.daos.approve_vendor_application',
    )
    def test_approve_pending_vendor_application_400_no_such_application(self, approve_vendor_application):
        """ ensure admins get correct error response if application does not exist """

        # setup
        self.client.force_authenticate(
            user=User(
                user_id=uuid.uuid4(),
                email='test@morriswa.org',
                username='test@morriswa.org',
                vendor_id=None,
                jwt_permissions=['cmx_coffee:admin']
            ),
        )
        application_id = 1234
        err_msg = f'could not retrieve application {application_id}, not approving...'
        approve_vendor_application.side_effect = BadRequestException(err_msg)

        # action
        response = self.client.put(
            f"/s/admin/vendor-application/{application_id}?action=approve"
        )

        # assert
        self.assertEqual(response.status_code, 400, 'should get bad response')
        self.assertEqual(
            response.data,
            {'msg': err_msg},
            'not found error'
        )

    def test_reject_pending_vendor_application_200(self):
        """ ensure admins can reject vendors """

        # setup
        self.client.force_authenticate(
            user=User(
                user_id=uuid.uuid4(),
                email='test@morriswa.org',
                username='test@morriswa.org',
                vendor_id=None,
                jwt_permissions=['cmx_coffee:admin']
            ),
        )
        app_id = 1234

        # execute
        response = self.client.put(
            f"/s/admin/vendor-application/{app_id}?action=reject"
        )

        # assert
        self.assertEqual(response.status_code, 204, 'good')

    def test_process_pending_vendor_application_400_invalid_action(self):
        """ ensure admins recieve correct error is they input an invalid application action """

        # setup
        self.client.force_authenticate(
            user=User(
                user_id=uuid.uuid4(),
                email='test@morriswa.org',
                username='test@morriswa.org',
                vendor_id=None,
                jwt_permissions=['cmx_coffee:admin']
            ),
        )
        app_id = 1234

        # execute
        response = self.client.put(
            f"/s/admin/vendor-application/{app_id}?action=nonsense"
        )

        # assert
        self.assertEqual(response.status_code, 400, 'should get 400')
        self.assertEqual(response.data, {'msg': 'invalid action'}, 'correct error')


class GetVendorEndpointTests(APITestCase):

    @staticmethod
    def mock_get_all_vendors():
        """ mock unittest method for admin.daos.get_all_vendors """

        apps = []
        apps.append(AdminVendorInfo(
            vendor_id=1,
            join_date=datetime.date.today(),
            state_code='CA',
            country_code='USA',
            business_name='test application 1',
            business_email='biz@morriswa.org',
            phone='1231231234',
            address_one='1234 Happy St',
            city='City',
            zip='55555',
            territory='TEST_CASE',
            approver_email='approver@morriswa.org'
        ))
        return apps

    @patch('admin.daos.get_all_vendors', mock_get_all_vendors)
    def test_get_vendors_200(self):
        """ ensure admin/vendor view is working as expected when provided with a valid database response """

        # execute
        self.client.force_authenticate(
            user=User(
                user_id=uuid.uuid4(),
                email='test@morriswa.org',
                username='test@morriswa.org',
                vendor_id=None,
                jwt_permissions=['cmx_coffee:admin']
            ),
        )
        response = self.client.get(f"/s/admin/vendors")

        # assert
        res_vendor = response.data[0]
        self.assertEqual(res_vendor['vendor_id'], 1, 'should have correct id')
        self.assertEqual(res_vendor['approver_email'], 'approver@morriswa.org', 'should have correct email')

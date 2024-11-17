import uuid

from django.test import TestCase
from django.conf import settings

from rest_framework.test import APITestCase

from app.authentication import User
from app import connections


class PendingVendorApplicationEndpointTests(APITestCase):
    def test_get_pending_vendor_applications_403(self):
        # submit mock http request to health endpoint
        self.client.force_authenticate(
            user=User(
                user_id=uuid.uuid4(),
                email='test@morriswa.org',
                username='test@morriswa.org',
                vendor_id=None,
                jwt_permissions=[]
            ),
        )
        response = self.client.get('/s/admin/vendor-applications')
        self.assertEqual(response.status_code, 403, 'default users are not allowed...')
        self.assertEqual(
            response.data,
            {'msg': 'You do not have permission to perform this action.'},
            'correct body'
        )

    def test_get_pending_vendor_applications_401(self):
        response = self.client.get('/s/admin/vendor-applications')
        self.assertEqual(response.status_code, 401, 'anon users are not allowed...')
        self.assertEqual(
            response.data,
            {'msg': 'Failed to provide Authorization header'},
            'correct body'
        )

    def __setup_get_pending_vendor_applications_200(self):

        with connections.cursor() as cur:
            applicant_user_id = uuid.uuid4();
            admin_user_id = uuid.uuid4();
            cur.execute("""
                insert into auth_integration
                    (user_id, email)
                values
                    (%(applicant_id)s, 'applicant@morriswa.org');

                insert into vendor_approved_territory
                    (territory_id, state_code, country_code, display_name)
                values
                    ('TEST_CASE', 'CA', 'USA', 'Test Case USA');

                insert into vendor_applicant
                    (user_id,
                    business_name, business_email, phone,
                    address_one, address_two, city, zip, territory_id)
                values
                    (%(applicant_id)s,
                     'test application 1', 'applicant@morriswa.org', '1231231234',
                     '1234 Address Line One', NULL, 'City', '55555','TEST_CASE')
            """, {
                'applicant_id': applicant_user_id
            })

        self.client.force_authenticate(
            user=User(
                user_id=admin_user_id,
                email='test@morriswa.org',
                username='test@morriswa.org',
                vendor_id=None,
                jwt_permissions=['cmx_coffee:admin']
            ),
        )

    def test_get_pending_vendor_applications_200(self):

        self.__setup_get_pending_vendor_applications_200()

        response = self.client.get('/s/admin/vendor-applications')
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
    def __setup_process_pending_vendor_application_200(self):
        gen_application_id = None
        applicant_user_id = uuid.uuid4();
        admin_user_id = uuid.uuid4();
        with connections.cursor() as cur:
            cur.execute("""
                insert into auth_integration
                    (user_id, email)
                values
                    (%(applicant_id)s, 'applicant@morriswa.org'),
                    (%(admin_id)s, 'admin@morriswa.org');

                insert into vendor_approved_territory
                    (territory_id, state_code, country_code, display_name)
                values
                    ('TEST_CASE', 'CA', 'USA', 'Test Case USA');

                insert into vendor_applicant
                    (user_id,
                    business_name, business_email, phone,
                    address_one, address_two, city, zip, territory_id)
                values
                    (%(applicant_id)s,
                     'test application 1', 'applicant@morriswa.org', '1231231234',
                     '1234 Address Line One', NULL, 'City', '55555','TEST_CASE')
                returning application_id;
            """, {
                'applicant_id': applicant_user_id,
                'admin_id': admin_user_id
            })
            gen_application_id = cur.fetchone()['application_id']

        self.client.force_authenticate(
            user=User(
                user_id=admin_user_id,
                email='test@morriswa.org',
                username='test@morriswa.org',
                vendor_id=None,
                jwt_permissions=['cmx_coffee:admin']
            ),
        )

        return gen_application_id, applicant_user_id

    def test_approve_pending_vendor_application_200(self):
        app_id, applicant_user_id = self.__setup_process_pending_vendor_application_200()

        response = self.client.put(
            f"/s/admin/vendor-application/{app_id}?action=approve"
        )

        self.assertEqual(response.status_code, 204, 'good')

        with connections.cursor() as cur:
            cur.execute("""
                select * from vendor_applicant where application_id = %(app_id)s
            """, {'app_id': app_id})
            res = cur.fetchone()
            self.assertIsNone(res, 'application should have been deleted after approval')

            cur.execute("""
                select * from vendor where user_id = %(applicant_user_id)s
            """, {'applicant_user_id': applicant_user_id})
            res = cur.fetchone()
            self.assertIsNotNone(res, 'vendor should have been created after approval')
            self.assertEqual(res['business_name'], 'test application 1', 'data should be correct')

    def test_approve_pending_vendor_application_400_no_such_application(self):
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
        response = self.client.put(
            f"/s/admin/vendor-application/{application_id}?action=approve"
        )
        self.assertEqual(response.status_code, 400, 'should get bad response')
        self.assertEqual(
            response.data,
            {'msg': f'could not retrieve application {application_id}, not approving...'},
            'not found error'
        )

    def test_reject_pending_vendor_application_200(self):
        app_id, applicant_user_id = self.__setup_process_pending_vendor_application_200()

        response = self.client.put(
            f"/s/admin/vendor-application/{app_id}?action=reject"
        )

        self.assertEqual(response.status_code, 204, 'good')

        with connections.cursor() as cur:
            cur.execute("""
                select * from vendor_applicant where application_id = %(app_id)s
            """, {'app_id': app_id})
            res = cur.fetchone()
            self.assertIsNone(res, 'application should have been deleted after approval')

            cur.execute("""
                select * from vendor where user_id = %(applicant_user_id)s
            """, {'applicant_user_id': applicant_user_id})
            res = cur.fetchone()
            self.assertIsNone(res, 'vendor should NOT have been created after reject')

    def test_process_pending_vendor_application_400_invalid_action(self):
        app_id, applicant_user_id = self.__setup_process_pending_vendor_application_200()

        response = self.client.put(
            f"/s/admin/vendor-application/{app_id}?action=nonsense"
        )

        self.assertEqual(response.status_code, 400, 'should get 400')
        self.assertEqual(response.data, {'msg': 'invalid action'}, 'correct error')


class GetVendorEndpointTests(APITestCase):

    def __setup_get_vendors_200(self):
        user_id_vendor = uuid.uuid4()
        user_id_approver = uuid.uuid4()
        vendor_id = None
        with connections.cursor() as cur:
            cur.execute("""
                insert into auth_integration
                    (user_id, email)
                values
                    (%(user_id_vendor)s, 'vendor@morriswa.org'),
                    (%(user_id_approver)s, 'approver@morriswa.org');

                insert into vendor_approved_territory
                    (territory_id, state_code, country_code, display_name)
                values ('USA_TEST', 'CA', 'USA', 'Test Case USA');

                insert into vendor
                    (user_id, business_name, business_email, phone,
                    address_one, city, zip, territory, approved_by)
                values
                    (%(user_id_vendor)s, 'Business Name', 'vendor@vendor.org', '1231231234',
                    'address line 1', 'city', '55555', 'USA_TEST', %(user_id_approver)s)
                returning vendor_id;
            """, {
                'user_id_vendor': user_id_vendor,
                'user_id_approver': user_id_approver
            })
            vendor_id = cur.fetchone()['vendor_id']

        self.client.force_authenticate(
            user=User(
                user_id=uuid.uuid4(),
                email='test@morriswa.org',
                username='test@morriswa.org',
                vendor_id=None,
                jwt_permissions=['cmx_coffee:admin']
            ),
        )
        return vendor_id

    def test_get_vendors_200(self):
        vendor_id = self.__setup_get_vendors_200()

        response = self.client.get('/s/admin/vendors')
        self.assertEqual(response.status_code, 200, 'good')
        self.assertEqual(len(response.data), 1, '1 vendor in db')
        res_vendor = response.data[0]
        self.assertEqual(res_vendor['vendor_id'], vendor_id, 'should have correct id')
        self.assertEqual(res_vendor['approver_email'], 'approver@morriswa.org', 'should have correct email')

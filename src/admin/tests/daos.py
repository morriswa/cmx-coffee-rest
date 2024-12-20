
import uuid

from django.test import TestCase

from app.authentication import User
from app import connections
from app.exceptions import BadRequestException

import admin.daos as admin_dao


class PendingVendorApplicationDAOTests(TestCase):
    def __setup_get_pending_vendor_applications(self):
        """ database setup for get_pending_vendor_applications test """
        with connections.cursor() as cur:
            applicant_user_id = uuid.uuid4();
            admin_user_id = uuid.uuid4();
            cur.execute("""
                insert into auth_integration
                    (user_id, email)
                values
                    (%(applicant_id)s, 'applicant@morriswa.org');

                insert into vendor_applicant
                    (user_id,
                    business_name, business_email, phone,
                    address_one, address_two, city, zip, territory_id)
                values
                    (%(applicant_id)s,
                     'test application 1', 'applicant@morriswa.org', '1231231234',
                     '1234 Address Line One', NULL, 'City', '55555','USA_KS')
            """, {
                'applicant_id': applicant_user_id
            })

    def test_get_pending_vendor_applications(self):
        """ ensure dao correctly retrieves vendors from tables"""

        # setup
        self.__setup_get_pending_vendor_applications()

        # execute
        response = admin_dao.get_pending_vendor_applications()

        # assert
        self.assertTrue(
            isinstance(response, list),
            'correct body format (json list)'
        )
        self.assertEqual(
            len(response),
            1,
            '1 application in db'
        )
        self.assertEqual(
            response[0].business_name,
            'test application 1',
            'correct value retrieved from db'
        )


class ProcessPendingVendorApplicationDAOTests(TestCase):
    def __setup_process_pending_vendor_application(self):
        """ database setup for approve_pending_vendor_application test """

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

                insert into vendor_applicant
                    (user_id,
                    business_name, business_email, phone,
                    address_one, address_two, city, zip, territory_id)
                values
                    (%(applicant_id)s,
                     'test application 1', 'applicant@morriswa.org', '1231231234',
                     '1234 Address Line One', NULL, 'City', '55555','USA_OK')
                returning application_id;
            """, {
                'applicant_id': applicant_user_id,
                'admin_id': admin_user_id
            })
            gen_application_id = cur.fetchone()['application_id']

        return gen_application_id, applicant_user_id

    def test_approve_pending_vendor_application(self):
        """ ensure dao completes necessary steps in application approval process """

        # setup
        app_id, applicant_user_id = self.__setup_process_pending_vendor_application()

        # execute
        admin_dao.approve_vendor_application(applicant_user_id, app_id)

        # assert
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

    def test_approve_pending_vendor_application_no_such_application(self):
        """ ensure dao behaves correctly if given an invalid application_id """

        # setup
        application_id = 1234
        try:
            # execute
            admin_dao.approve_vendor_application(uuid.uuid4(), application_id)
        except BadRequestException as bre:
            self.assertEqual(
                bre.json(),
                {'msg': f'could not retrieve application {application_id}, not approving...'},
                'should get bad response'
            )

    def test_reject_pending_vendor_application(self):
        """ ensure dao completes necessary steps in application reject process """

        # setup
        app_id, applicant_user_id = self.__setup_process_pending_vendor_application()

        # execute
        admin_dao.reject_vendor_application(app_id)

        # assert
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


class GetVendorDAOTests(TestCase):

    def __setup_get_vendors(self):
        """ database setup for get_vendors test"""

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

                insert into vendor
                    (user_id, business_name, business_email, phone,
                    address_one, city, zip, territory, approved_by)
                values
                    (%(user_id_vendor)s, 'Business Name', 'vendor@vendor.org', '1231231234',
                    'address line 1', 'city', '55555', 'USA_MO', %(user_id_approver)s)
                returning vendor_id;
            """, {
                'user_id_vendor': user_id_vendor,
                'user_id_approver': user_id_approver
            })
            vendor_id = cur.fetchone()['vendor_id']

        return vendor_id

    def test_get_vendors(self):
        """ ensure dao correctly maps vendor table to datamodels """
        # setup
        vendor_id = self.__setup_get_vendors()

        # execute
        response = admin_dao.get_all_vendors()

        # assert
        self.assertEqual(len(response), 1, '1 vendor in db')
        res_vendor = response[0]
        self.assertEqual(res_vendor.vendor_id, vendor_id, 'should have correct id')
        self.assertEqual(res_vendor.approver_email, 'approver@morriswa.org', 'should have correct email')

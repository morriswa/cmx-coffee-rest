import uuid

from django.test import TestCase

from app.authentication import User
from app import connections
from app.exceptions import BadRequestException
from vendor.models import VendorApplicationResponse
from admin.models import AdminVendorInfo
import admin.daos as admin_dao



class ApplicationForVendorDAOTest(TestCase):
    def __setup_apply_for_vendor(self):
        """ database setup for apply_for_vendor test """
        with connections.cursor() as cur:
            applicant_user_id = uuid.uuid4();
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

    def test_apply_for_vendor(self):
        """ ensure dao correctly applies for vendor """
        
        # setup
        applicant_user_id = self.__setup_apply_for_vendor()
        vendor_application = VendorApplicationResponse(
            business_name='test application 1',
            business_email='test email',
            phone='1231231234',
            address_one='1234 Address Line One',
            address_two=None,
            city='City',
            zip='55555',
            territory_id='TEST_CASE'
        )

        #execute 
        VendorApplicationResponse = admin_dao.apply_for_vendor(vendor_application)

        #asset 
        self.assertTrue(
            isinstance(VendorApplicationResponse, VendorApplicationResponse),
            'correct body format (json list)'
        )

        self.assertEqual(
            VendorApplicationResponse.business_name,
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
                    (%(applicant_id)s, """)
            

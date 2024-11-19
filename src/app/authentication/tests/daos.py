

from django.conf import settings

from django.test import TestCase
from unittest import mock

from psycopg2.extras import RealDictCursor

from app.authentication.daos import *
from app import connections
from app.exceptions import APIException



class RegisterUserDAOTests(TestCase):
    def test_successfully_register_user(self):
        test_email = 'test@morriswa.org'
        new_user_id = register_user(test_email)

        with connections.cursor() as cur:
            cur.execute("""select user_id from auth_integration where email = 'test@morriswa.org'""")
            res = cur.fetchone()
            self.assertIsNotNone(res, 'should retrieve new user row from db')
            self.assertEqual(new_user_id, res['user_id'])

    @mock.patch('app.connections.cursor')
    def test_unsuccessfully_register_user(self, mock_cur):
        class __MockCursor:
            def __enter__(self):
                return self

            def __exit__(self, exc_type, exc_val, exc_tb):
                pass

            def execute(*args):
                pass

            def fetchone(*args):
                return None

        mock_cur.return_value = __MockCursor()

        test_email = 'test@morriswa.org'
        try:
            new_user_id = register_user(test_email)
        except Exception as e:
            self.assertTrue(isinstance(e, APIException), 'ensure correct error is thrown')
            self.assertEqual(
                e.error,
                f'failed to register user with email {test_email}',
                'ensure correct error is thrown'
            )

class GetUserInfoDAOTests(TestCase):

    def __setup_get_user(self):
        print(settings.DATABASES['default']['HOST'])
        user_id = uuid.uuid4()
        test_email = 'test@morriswa.org'
        with connections.cursor() as cur:
            cur.execute("""
                insert into auth_integration (user_id, email)
                values (%(user_id)s, %(email)s)
            """, {'user_id': user_id, 'email': test_email})

        return user_id, test_email

    def test_get_user(self):

        user_id, test_email = self.__setup_get_user()

        res = get_user_info(test_email)

        self.assertIsNotNone(res, 'should get response')
        self.assertEqual(res[0], user_id, 'user_id should be returned')
        self.assertIsNone(res[1], 'vendor_id should not be returned')

    def __setup_get_user_vendor(self):
        user_id = uuid.uuid4()
        test_email = 'test@morriswa.org'
        with connections.cursor() as cur:
            cur.execute("select * from vendor_approved_territory")
            print(cur.fetchall())
            cur.execute("""
                insert into auth_integration (user_id, email)
                values
                    (%(user_id)s, %(email)s);

                insert into vendor
                    (user_id, business_name, business_email, phone,
                    address_one, city, zip, territory,
                    approved_by)
                values
                    (%(user_id)s, 'vendor', 'vendor@morriswa.org', '5555555555',
                    'address line one', 'city', '55555', 'USA_KS',
                    %(user_id)s)
                returning vendor_id;
            """, {'user_id': user_id, 'email': test_email})

            res = cur.fetchone()
            return user_id, test_email, res['vendor_id']

    def test_get_user_vendor(self):
        user_id, test_email, vendor_id = self.__setup_get_user_vendor()

        res = get_user_info(test_email)

        self.assertIsNotNone(res, 'should get response')
        self.assertEqual(res[0], user_id, 'user_id should be returned')
        self.assertEqual(res[1], vendor_id, 'vendor_id should be returned')

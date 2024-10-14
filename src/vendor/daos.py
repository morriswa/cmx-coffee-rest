"""
    Vendor-related database functions go here
"""
from psycopg2 import errors

from app.connections import cursor
from app.exceptions import BadRequestException

from .models import VendorApplicationRequest


def apply_for_vendor(user_id, vendor_application: VendorApplicationRequest):
    try:
        with cursor() as cur:
            cur.execute("""
                insert into vendor_applicant
                    (user_id,
                    business_name, business_email, phone,
                    address_one, address_two, city, state,
                    zip, country)
                values
                    (%(user_id)s,
                    %(name)s, %(email)s, %(phone)s,
                    %(address_one)s, %(address_two)s, %(city)s, %(state)s,
                    %(zip)s, %(country)s)
            """,{
                'user_id': user_id,
                'name': vendor_application.business_name,
                'email': vendor_application.business_email,
                'phone': vendor_application.phone,
                'address_one': vendor_application.address_line_one,
                'address_two': vendor_application.address_line_two,
                'city': vendor_application.city,
                'state': vendor_application.state,
                'zip': vendor_application.zip,
                'country': vendor_application.country
            })
    except errors.UniqueViolation:
        raise BadRequestException('you have already applied with this account!')

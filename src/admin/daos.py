"""
    Admin-related database functions go here
"""

import logging

from app import connections
from app.exceptions import BadRequestException

from vendor.models import VendorApplicationResponse


def get_pending_vendor_applications() -> list[VendorApplicationResponse]:
    with connections.cursor() as db:
        db.execute("select * from vendor_applicant")
        results = db.fetchall()
        assert results is not None
        return [VendorApplicationResponse(**result) for result in results]


def approve_vendor_application(user_id, application_id):
    with connections.cursor() as cur:
        cur.execute(
            "select * from vendor_applicant where application_id = %(application_id)s",
            {'application_id': application_id}
        )
        application_data = cur.fetchone()
        if application_data is None:
            msg = f'could not retrieve application {application_id}, not approving...'
            logging.error(msg)
            raise BadRequestException(msg)

        cur.execute("""
            insert into vendor
               (user_id, business_name, business_email,
                phone, address_one, address_two, city,
                state, zip, country, approved_by)
            values
               (%(user_id)s, %(business_name)s, %(business_email)s,
                %(phone)s, %(address_one)s, %(address_two)s, %(city)s,
                %(state)s, %(zip)s, %(country)s, %(approved_by)s)
        """, {
            **application_data,
            'approved_by': user_id
        })
        cur.execute(
            "delete from vendor_applicant where application_id = %(application_id)s",
            {'application_id': application_id}
        )

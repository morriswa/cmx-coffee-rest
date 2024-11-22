"""
    Admin-related database functions go here
"""

import logging

from app import connections
from app.exceptions import BadRequestException

from vendor.models import VendorApplicationResponse
from admin.models import AdminVendorInfo
from customer.models import CustomerPreferences




def get_pending_vendor_applications() -> list[VendorApplicationResponse]:
    with connections.cursor() as db:
        db.execute("""
            select
                *
            from vendor_applicant apps
                left join vendor_approved_territory tr
                    on apps.territory_id = tr.territory_id
        """)
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
                zip, territory, approved_by)
            values
               (%(user_id)s, %(business_name)s, %(business_email)s,
                %(phone)s, %(address_one)s, %(address_two)s, %(city)s,
                %(zip)s, %(territory_id)s, %(approved_by)s)
        """, {
            **application_data,
            'approved_by': user_id
        })
        cur.execute(
            "delete from vendor_applicant where application_id = %(application_id)s",
            {'application_id': application_id}
        )

def reject_vendor_application(application_id):
    with connections.cursor() as cur:
        cur.execute("""
            delete from vendor_applicant
            where application_id = %(application_id)s
        """,{
            'application_id': application_id
        })

def get_all_vendors() -> list[AdminVendorInfo]:
    with connections.cursor() as cur:
        cur.execute("""
            select
                *,
                usr.email as approver_email
            from vendor ven
                left join auth_integration usr
                    on ven.approved_by = usr.user_id
                left join vendor_approved_territory t
                    on ven.territory = t.territory_id
        """)
        res = cur.fetchall()
        return [AdminVendorInfo(**data) for data in res]

def get_all_newsletter_subscriber_emails() -> list[CustomerPreferences]:
    with connections.cursor() as cur:
        cur.execute(
            """
            select auth.email
            from auth_integration auth
                left join customer_preferences cus
                    on auth.user_id = cus.user_id
            where
                cus.n_newsletter_subscription = 'y'
            """)
        res = cur.fetchall()
        return [CustomerPreferences(**data) for data in res];

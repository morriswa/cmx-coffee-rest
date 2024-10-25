"""
    Vendor-related database functions go here
"""
import logging
from psycopg2 import errors

from app.connections import cursor
from app.exceptions import BadRequestException

from .models import VendorApplicationRequest, CreateProductRequest, VendorProductResponse


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


def get_vendor_id_associated_with_user(user_id) -> int:
    with cursor() as cur:
        cur.execute("select vendor_id from vendor where user_id = %(user_id)s", {'user_id': user_id})
        res = cur.fetchone()
        if res is None:
            msg = f'could not find vendor associated with user_id {user_id}'
            logging.error(msg)
            raise BadRequestException(msg)
        return res['vendor_id']


def list_product(vendor_id, user_id, product: CreateProductRequest):
    with cursor() as cur:
        cur.execute("""
            insert into vendor_product
               (vendor_id, listed_by, product_name,
                description, initial_price)
            values
               (%(vendor_id)s, %(user_id)s, %(product_name)s,
                %(description)s, %(initial_price)s)
        """, {
            'vendor_id': vendor_id,
            'user_id': user_id,
            'product_name': product.product_name,
            'description': product.description,
            'initial_price': product.initial_price
        })


def get_products(vendor_id: int) -> list[VendorProductResponse]:
    with cursor() as cur:
        cur.execute(
            "select * from vendor_product where vendor_id = %(vendor_id)s",
            {'vendor_id': vendor_id}
        )
        res = cur.fetchall()
        return [VendorProductResponse(**product) for product in res]

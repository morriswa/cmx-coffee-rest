"""
    Vendor-related database functions go here
"""
import logging
from psycopg2 import errors
from rest_framework import exceptions

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


def get_product_details(vendor_id: int, product_id: int):
    with cursor() as cur:
        cur.execute(
            "select * from vendor_product where vendor_id = %(vendor_id)s and product_id = %(product_id)s",
            {'vendor_id': vendor_id, 'product_id': product_id}
        )
        res = cur.fetchone()
        if res is None:
            raise BadRequestException(f'could not find product #{product_id} with vendor {vendor_id}')
        return VendorProductResponse(**res)


def assert_vendor_owns_product(vendor_id: int, product_id: int):
    with cursor() as cur:
        cur.execute(
            "select 1 from vendor_product where vendor_id = %(vendor_id)s and product_id = %(product_id)s",
            {'vendor_id': vendor_id, 'product_id': product_id}
        )
        res = cur.fetchone()
        if res is None:
            raise exceptions.PermissionDenied()
        

def updated_existing_product(product_id: int, request_data: dict):
    with cursor() as cur:
        cur.execute(
            'SELECT * from product_characteristics WHERE product_id = %(product_id)s',
            {'product_id': product_id},
                    
        )
        
        res = cur.fetchone(); 
        if res is None:
            cur.execute("""
            INSERT INTO product_characteristics
            (product_id, cb_taste_strength, cb_decaf, cb_flavored, cb_single_origin, cb_regions, cb_keywords)
            VALUES
            (%(product_id)s, 
            %(cb_taste_strength)s, 
            %(cb_decaf)s, 
            %(cb_flavored)s, 
            %(cb_single_origin)s, 
            %(cb_regions)s, 
            %(bb_keywords)s)
            """,
            {
            'product_id': product_id,
            'cb_taste_strength': request_data.get('coffee_bean_characteristics').get('taste_strength'),
            'cb_decaf': request_data.get('coffee_bean_characteristics').get('decaf'),
            'cb_flavored': request_data.get('coffee_bean_characteristics').get('flavored'),
            'cb_single_origin': request_data.get('coffee_bean_characteristics').get('single_origin'),
            'cb_regions': request_data.get('coffee_bean_characteristics').get('regions'),
            'bb_keywords': request_data.get('coffee_bean_characteristics').get('keywords')
            }
            )

        else:
            cur.execute("""
            UPDATE product_characteristics
            SET
                product_id = COALESCE(%(product_id)s, product_id),
                cb_taste_strength  = COALESCE(%(cb_taste_strength)s, cb_taste_strength),
                cb_decaf = COALESCE(%(cb_decaf)s, cb_decaf),
                cb_flavored =   COALESCE(%(cb_flavored)s, cb_flavored),
                cb_single_origin = COALESCE(%(cb_single_origin)s, cb_single_origin),
                cb_regions = COALESCE(%(cb_regions)s, cb_regions),
                cb_keywords = COALESCE(%(cb_keywords)s, cb_keywords)
            WHERE product_id = %(product_id)s
        """,{
            'product_id': product_id,
            'cb_taste_strength': request_data.get('coffee_bean_characteristics').get('taste_strength'),
            'cb_decaf': request_data.get('coffee_bean_characteristics').get('decaf'),
            'cb_flavored': request_data.get('coffee_bean_characteristics').get('flavored'),
            'cb_single_origin': request_data.get('coffee_bean_characteristics').get('single_origin'),
            'cb_regions': request_data.get('coffee_bean_characteristics').get('regions'),
            'cb_keywords': request_data.get('coffee_bean_characteristics').get('keywords') 
            })  
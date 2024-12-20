"""
    provides core authentication utils
    author: William Morris [morriswa]
"""

import logging
import uuid
from typing import Optional


import app.connections
from app.exceptions import APIException



def register_user(email:str):
    with app.connections.cursor() as cursor:
        cursor.execute(
            "insert into auth_integration (email) values (%(email)s) returning user_id;",
            {'email': email}
        )
        result = cursor.fetchone()
        if result is None:
            msg = f'failed to register user with email {email}'
            logging.error(msg)
            raise APIException(msg)

        user_id = result.get('user_id')
        logging.info(f'successfully registered user {user_id} with email {email}')
        return user_id

def get_user_info(email: str) -> tuple[uuid, Optional[int]]:
    user_id = None
    vendor_id = None
    with app.connections.cursor() as cursor:
        cursor.execute(
            "select user_id from auth_integration where email = %(email)s",
            {'email': email}
        )
        result = cursor.fetchone()
        if result is None:
            logging.info(f'did not find database entry for user with email {email}, attemping registration')
            return register_user(email), None

        user_id = result['user_id']

        cursor.execute(
            "select vendor_id from vendor where user_id = %(user_id)s",
            {'user_id': user_id}
        )
        result = cursor.fetchone()
        if result is not None:
            vendor_id = result['vendor_id']

    return user_id, vendor_id


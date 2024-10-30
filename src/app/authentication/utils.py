"""
    provides core authentication utils
    author: William Morris [morriswa]
"""

import json
import jwt
import logging
import os
import requests
import uuid
from functools import wraps
from typing import override, Optional

from django.conf import settings
from django.contrib.auth import authenticate
from rest_framework.authentication import BaseAuthentication
from rest_framework import exceptions

import app.connections
from app.exceptions import BadRequestException


def jwt_decode_token(token) -> dict:
    """
        provides core authentication utils
        source: https://auth0.com/docs/quickstart/backend/django/01-authorization
    """
    header = jwt.get_unverified_header(token)
    jwks = requests.get(f'{settings.JWT_ISSUER}/.well-known/jwks.json').json()
    public_key = None
    for jwk in jwks['keys']:
        if jwk['kid'] == header['kid']:
            decoded_jwk = json.dumps(jwk)
            public_key = jwt.algorithms.RSAAlgorithm.from_jwk(decoded_jwk)

    if public_key is None:
        raise Exception('Public key not found.')

    return jwt.decode(
        token,
        public_key,
        audience=settings.JWT_AUDIENCE,
        issuer=settings.JWT_ISSUER,
        algorithms=settings.JWT_ALGORITHM
    )

def get_token_auth_header(request):
    """
        Obtains the Access Token from the Authorization Header
        source: https://auth0.com/docs/quickstart/backend/django/01-authorization
    """
    auth = request.META.get("HTTP_AUTHORIZATION", None)
    if auth is None:
        raise exceptions.AuthenticationFailed('Failed to provide Authorization header', code=401)
    parts = auth.split()
    token = parts[1]

    return token

def register_user_in_db(email:str):
    with app.connections.cursor() as cursor:
        cursor.execute(
            "insert into auth_integration (email) values (%(email)s)",
            {'email': email}
        )
        cursor.execute(
            "select user_id from auth_integration where email = (%(email)s)",
            {'email': email}
        )
        result = cursor.fetchone()
        if result is None:
            logging.error(f'failed to register user with email {email}')
            raise Exception('bad stuff happened')

        user_id = result.get('user_id')
        logging.info(f'successfully registered user {user_id} with email {email}')
        return user_id

def get_user_info_from_db(email: str) -> tuple[uuid, Optional[int]]:
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
            return register_user_in_db(email), None

        user_id = result['user_id']

        cursor.execute(
            "select vendor_id from vendor where user_id = %(user_id)s",
            {'user_id': user_id}
        )
        result = cursor.fetchone()
        if result is not None:
            vendor_id = result['vendor_id']

    return user_id, vendor_id


def jwt_has_scope(decoded_token, required_scopes: list[str]) -> bool:
    # retrieve scope string from token
    token_scope_str = decoded_token.get("scope")

    has_all_scopes = True

    if token_scope_str:  # if scope was present
        token_scopes = token_scope_str.split()  # split on whitespace
        for token_scope in required_scopes:
            # make sure all required scopes are present in token's provided scopes
            if token_scope not in token_scopes:
                has_all_scopes = False

    return has_all_scopes

def jwt_has_permissions(decoded_token, required_permissions: list[str]) -> bool:
    # retrieve scope string from
    token_permissions = decoded_token.get('permissions') or []

    has_all_permissions = True

    for permission in required_permissions:
        # make sure all required permissions are present in token's provided permission array
        if permission not in token_permissions:
            has_all_permissions = False

    return has_all_permissions

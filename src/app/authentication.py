"""
    provides core authentication utils
    author: William Morris [morriswa]
"""

import json
import jwt
import logging
import os
import requests
from functools import wraps
from typing import override, Optional

from django.conf import settings
from django.contrib.auth import authenticate
from rest_framework.authentication import BaseAuthentication
from rest_framework import exceptions

import app.connections

def _jwt_decode_token(token) -> dict:
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

def _get_token_auth_header(request):
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

def _get_email_decoded_jwt(payload):
    """
        gets email from decoded jwt
    """
    email = payload.get('email')
    authenticate(remote_user=email)
    return email


def _get_user_id_from_db(email: str):
    with app.connections.cursor() as cursor:
        cursor.execute(
            "select user_id from auth_integration where email = %(email)s",
            {'email': email}
        )
        result = cursor.fetchone()
        if result is None:
            raise exceptions.AuthenticationFailed('could not find user id, have you registered?')
        else:
            return result['user_id']


# publics
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

class JwtUser:
    """ stores token info """
    def __init__(self, token: dict):
        self.username = _get_email_decoded_jwt(token)
        self.token: dict = token
        self.is_authenticated = True


class JwtAuthentication(BaseAuthentication):
    """ provides jwt authentication filter, imported in drf """
    @override
    def authenticate(self, request) -> Optional[tuple[JwtUser, dict]]:
        """ :return None if auth request was rejected, else User, Auth tuple """
        token = _get_token_auth_header(request)
        if token is None:
            return None

        try:
            payload = _jwt_decode_token(token)
            return JwtUser(payload), payload
        except jwt.ExpiredSignatureError:
            raise exceptions.AuthenticationFailed('Token has expired.')
        except jwt.DecodeError:
            raise exceptions.AuthenticationFailed('Error decoding token.')
        except jwt.InvalidTokenError:
            raise exceptions.AuthenticationFailed('Invalid token.')

class User:
    """ stores token info """
    def __init__(self, email: str, user_id):
        self.email = email
        self.user_id = user_id
        self.username = self.email
        self.is_authenticated = True


class UserAuthenticationWithJwt(BaseAuthentication):
    """ provides jwt authentication filter, imported in drf """
    @override
    def authenticate(self, request) -> Optional[tuple[JwtUser, dict]]:
        """ :return None if auth request was rejected, else User, Auth tuple """
        token = _get_token_auth_header(request)
        if token is None:
            return None

        try:
            payload = _jwt_decode_token(token)

            email = _get_email_decoded_jwt(payload)
            user_id = _get_user_id_from_db(email)

            return User(email, user_id), payload
        except jwt.ExpiredSignatureError:
            raise exceptions.AuthenticationFailed('Token has expired.')
        except jwt.DecodeError:
            raise exceptions.AuthenticationFailed('Error decoding token.')
        except jwt.InvalidTokenError:
            raise exceptions.AuthenticationFailed('Invalid token.')

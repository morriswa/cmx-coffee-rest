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


# publics
def jwt_has_scope(decoded_token, required_scopes) -> bool:
    token_scope_str = decoded_token.get("scope")
    if token_scope_str:
        token_scopes = token_scope_str.split()
        for token_scope in token_scopes:
            if token_scope in required_scopes:
                return True
    return False


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

"""
    provides core authentication utils
    author: William Morris [morriswa]
"""

import json
import os
import jwt
import logging
import requests
from typing import override

from django.conf import settings
from django.contrib.auth import authenticate
from rest_framework.authentication import BaseAuthentication
from rest_framework import exceptions
from functools import wraps


def _jwt_get_username_from_payload_handler(payload):
    """
        provides core authentication utils
        source: https://auth0.com/docs/quickstart/backend/django/01-authorization
    """
    username = payload.get('sub').replace('|', '.')
    authenticate(remote_user=username)
    return username


def _jwt_decode_token(token):
    """
        provides core authentication utils
        source: https://auth0.com/docs/quickstart/backend/django/01-authorization
    """
    header = jwt.get_unverified_header(token)
    jwks = requests.get(f'{settings.JWT_AUTH['JWT_ISSUER']}/.well-known/jwks.json').json()
    public_key = None
    for jwk in jwks['keys']:
        if jwk['kid'] == header['kid']:
            public_key = jwt.algorithms.RSAAlgorithm.from_jwk(json.dumps(jwk))

    if public_key is None:
        raise Exception('Public key not found.')

    issuer = settings.JWT_AUTH['JWT_ISSUER']
    return jwt.decode(token, public_key, audience=settings.JWT_AUTH['JWT_AUDIENCE'], issuer=issuer, algorithms=['RS256'])


def _get_token_auth_header(request):
    """
        Obtains the Access Token from the Authorization Header
        source: https://auth0.com/docs/quickstart/backend/django/01-authorization
    """
    auth = request.META.get("HTTP_AUTHORIZATION", None)
    parts = auth.split()
    token = parts[1]

    return token


class User:
    def __init__(self, token):
        self.username = _jwt_get_username_from_payload_handler(token)
        self.token = token
        self.is_authenticated = True


class JwtAuthentication(BaseAuthentication):
    @override
    def authenticate(self, request):
        token = _get_token_auth_header(request)
        if token is None:
            return None

        try:
            payload = _jwt_decode_token(token)
            return User(payload), payload
        except jwt.ExpiredSignatureError:
            msg = _('Token has expired.')
            raise exceptions.AuthenticationFailed(msg)
        except jwt.DecodeError:
            msg = _('Error decoding token.')
            raise exceptions.AuthenticationFailed(msg)
        except jwt.InvalidTokenError:
            msg = _('Invalid token.')
            raise exceptions.AuthenticationFailed(msg)

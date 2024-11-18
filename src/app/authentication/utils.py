"""
    provides core authentication utils
    author: William Morris [morriswa]
"""

import json
import jwt
import requests

from django.conf import settings
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
        return None
    parts = auth.split()
    token = parts[1]

    return token


def jwt_has_scope(decoded_token, required_scopes: set[str]) -> bool:
    # retrieve scope string from token
    token_scope_str = decoded_token.get("scope")

    if token_scope_str:  # if scope was present
        # split on whitespace to get set of token scopes
        token_scopes = set(token_scope_str.split())
        # if token scopes contains all items in required scopes, return true
        return set(token_scopes).issuperset(required_scopes)

    # else false
    return False

def jwt_has_permissions(decoded_token, required_permissions: set[str]) -> bool:
    # retrieve scope string from
    token_permissions = set(decoded_token.get('permissions') or [])

    return set(token_permissions).issuperset(required_permissions)


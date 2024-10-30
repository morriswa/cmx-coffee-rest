
import jwt
from typing import override, Optional

from django.conf import settings
from rest_framework.authentication import BaseAuthentication
from rest_framework import exceptions

from .utils import *
from .models import *


class UserAuthenticationWithJwt(BaseAuthentication):
    """ provides jwt authentication filter, imported in drf """
    @override
    def authenticate(self, request) -> Optional[tuple[User, dict]]:
        """ :return None if auth request was rejected, else User, Auth tuple """
        token = get_token_auth_header(request)
        if token is None:  # if no auth header is found the user is not authenticated
            return None

        try:
            # attempt decoding auth header as jwt
            payload = jwt_decode_token(token)
            # extract token permissions and email
            jwt_permissions:list = payload.get('permissions')
            email = payload.get('email')

            # attempt retrieving user info from db using authentication email
            user_id, vendor_id = get_user_info_from_db(email)

            # create custom django user with retrieved info
            user = User(email=email, user_id=user_id, vendor_id=vendor_id, jwt_permissions=jwt_permissions)
            logging.info(f'successfully authenticated user {user.user_id} '
                         f'with email {user.email} and granted permissions {user.permissions}')
            return user, payload

        # handle common jwt errors
        except jwt.ExpiredSignatureError:
            raise exceptions.AuthenticationFailed('Token has expired.')
        except jwt.DecodeError:
            raise exceptions.AuthenticationFailed('Error decoding token.')
        except jwt.InvalidTokenError:
            raise exceptions.AuthenticationFailed('Invalid token.')

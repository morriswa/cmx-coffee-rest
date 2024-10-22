
import jwt

from typing import override, Optional
from rest_framework.authentication import BaseAuthentication
from rest_framework import exceptions
from django.conf import settings

from .utils import *
from .models import *


# publics
class UserAuthenticationWithJwt(BaseAuthentication):
    """ provides jwt authentication filter, imported in drf """
    @override
    def authenticate(self, request) -> Optional[tuple[User, dict]]:
        """ :return None if auth request was rejected, else User, Auth tuple """
        token = get_token_auth_header(request)
        if token is None:
            return None

        try:
            payload = jwt_decode_token(token)
            jwt_permissions:list = payload.get('permissions')

            email = get_email_decoded_jwt(payload)
            user_id, db_permissions = get_user_info_from_db(email)

            all_permissions = jwt_permissions + db_permissions + settings.USER_PERMISSIONS

            logging.info(f'successfully authenticated user {user_id} with email {email} and granted permissions {all_permissions}')
            return User(email, user_id, all_permissions), payload
        except jwt.ExpiredSignatureError:
            raise exceptions.AuthenticationFailed('Token has expired.')
        except jwt.DecodeError:
            raise exceptions.AuthenticationFailed('Error decoding token.')
        except jwt.InvalidTokenError:
            raise exceptions.AuthenticationFailed('Invalid token.')

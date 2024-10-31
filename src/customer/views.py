
from rest_framework.request import Request
from rest_framework.response import Response

from app.decorators import user_view
from app.authentication import User


@user_view(['GET'])
def get_customer_profile(request: Request) -> Response:

    user: User = request.user
    return Response(status=200, data=user.json())

@user_view(['PATCH'])
def update_customer_product_preferences(request: Request) -> Response:
    # build datamodel from request.data

    # pass datamodel to dao
    # update existing database row, or create one

    # return 204 no content response
    pass

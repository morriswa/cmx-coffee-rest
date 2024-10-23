
from rest_framework.request import Request
from rest_framework.response import Response

from app.decorators import user_view
from app.authentication import User


@user_view(['GET'])
def get_customer_profile(request: Request) -> Response:

    user: User = request.user
    return Response(status=200, data=user.json())

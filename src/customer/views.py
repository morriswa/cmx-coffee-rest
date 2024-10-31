import logging

from rest_framework.request import Request
from rest_framework.response import Response

from app.decorators import user_view
from app.authentication import User
from app.views import UserView

from .models import CartItem
import customer.daos as dao


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


class ShoppingCartView(UserView):

    @staticmethod
    def get(request: Request) -> Response:
        cart = dao.get_shopping_cart(request.user.user_id)
        return Response(status=200, data=[item.json() for item in cart])

    @staticmethod
    def patch(request: Request) -> Response:
        # create datamodel from json request
        items = [
            CartItem(props.get('product_id'), props.get('quantity'))
            for props in request.data
        ]
        # update shopping cart
        dao.update_shopping_cart(request.user.user_id, items)
        cart = dao.get_shopping_cart(request.user.user_id)
        # and return
        return Response(status=200, data=[item.json() for item in cart])

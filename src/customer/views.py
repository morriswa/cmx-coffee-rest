import logging

from rest_framework.request import Request
from rest_framework.response import Response

from app.decorators import user_view
from app.authentication import User
from app.views import UserView

from .models import CartItem, CustomerPreferences
import customer.daos as dao



class CustomerPreferencesView(UserView):

    @staticmethod
    def get(request: Request) -> Response:
        user_id = request.user.user_id
        preferences = dao.get_customer_preferences(user_id)
        return Response(status=200, data=vars(preferences))

    @staticmethod
    def patch(request: Request) -> Response:
        # create the datamodel
        preferences = CustomerPreferences(**request.data)  # directly use the request data dictionary

        # Call the DAO function to update customer preferences with the user ID and preferences data
        user_id = request.user.user_id
        dao.update_customer_preferences(user_id, preferences)

        return Response(status=204)

    @staticmethod
    def patch(request: Request) -> Response:
        #create the datamodel
        update_subscription = CustomerPreferences(**request.data)  #directly use the request data dictionary.

        #Call the DAO function to update customer preferences with the user ID and preferences data.
        user_id = request.user.user_id
        dao.update_customer_preferences(user_id, update_subscription)

        return Response(status=204)


class ShoppingCartView(UserView):

    @staticmethod
    def get(request: Request) -> Response:
        cart = dao.get_shopping_cart(request.user.user_id)
        return Response(status=200, data=[item.json() for item in cart])

    @staticmethod
    def patch(request: Request) -> Response:
        # create datamodel from json request
        items = [
            (props.get('product_id'), props.get('quantity'))
            for props in request.data
        ]
        # update shopping cart
        dao.update_shopping_cart(request.user.user_id, items)
        cart = dao.get_shopping_cart(request.user.user_id)
        # and return
        return Response(status=200, data=[item.json() for item in cart])

    @staticmethod
    def delete(request: Request) -> Response:
        dao.reset_shopping_cart(request.user.user_id)
        return Response(status=204)

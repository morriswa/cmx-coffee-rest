
from rest_framework.request import Request
from rest_framework.response import Response

from app.decorators import user_view
from app.exceptions import BadRequestException
from app.views import UserView

import customer_order.daos as dao


@user_view(['POST'])
def create_order(request):
    items = dao.collect_shopping_cart(request.user.user_id)
    order_id = dao.create_order(request.user.user_id, items)
    return Response(status=200, data={
        'order_id': order_id
    })


class OrderDraftView(UserView):
    @staticmethod
    def get(request, order_id):
        draft = dao.review_order(request.user.user_id, order_id)
        return Response(status=200, data=draft.json())

    @staticmethod
    def post(request, order_id):
        payment_id = request.query_params.get('payment_id')
        if payment_id is None:
            raise BadRequestException('payment_id required query param')
        dao.submit_order(request.user.user_id, order_id, payment_id)
        return Response(status=204)

    @staticmethod
    def delete(request, order_id):
        dao.delete_order_draft(request.user.user_id, order_id)
        return Response(status=204)


@user_view(['GET'])
def get_orders(request):
    orders = dao.get_customer_orders(request.user.user_id)
    return Response(status=200, data=[order.json() for order in orders])

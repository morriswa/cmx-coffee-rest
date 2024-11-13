
from rest_framework.request import Request
from rest_framework.response import Response

from app.decorators import user_view
from app.views import UserView

import customer_order.daos as dao


@user_view(['POST'])
def create_order(request):
    # TODO add payment validations
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
    def post(request):
        raise NotImplementedError('submit order endpoint')

    @staticmethod
    def delete(request, order_id):
        dao.delete_order_draft(request.user.user_id, order_id)
        return Response(status=204)


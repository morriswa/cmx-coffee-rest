

from rest_framework.request import Request
from rest_framework.response import Response

from app.decorators import user_view
from app.views import UserView

from payment.models import CreateMockPaymentRequest
import payment.daos as dao


class PaymentView(UserView):
    @staticmethod
    def get(request: Request) -> Response:
        payment_methods = dao.get_saved_payment_methods(request.user.user_id)
        return Response(status=200, data=[pay.json() for pay in payment_methods])

    @staticmethod
    def post(request: Request) -> Response:
        pm = CreateMockPaymentRequest(**request.data)
        dao.save_payment_method(request.user.user_id, pm)
        return Response(status=204)

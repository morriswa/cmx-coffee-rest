

from app import connections

from payment.models import MockPaymentResponse, CreateMockPaymentRequest


def get_saved_payment_methods(user_id) -> list[MockPaymentResponse]:
    with connections.cursor() as cur:
        cur.execute(
            "select * from mock_payment where user_id = %(user_id)s",
            {'user_id': user_id}
        )
        res = cur.fetchall()
        return [MockPaymentResponse(**data) for data in res]

def save_payment_method(user_id, payment_method: CreateMockPaymentRequest):
    with connections.cursor() as cur:

        cur.execute("""
        insert into mock_payment
            (user_id, nickname, billing_address_territory)
        values
            (%(user_id)s, %(nickname)s, %(territory_id)s)
        """,{
            'user_id': user_id,
            'nickname': payment_method.nickname,
            'territory_id': payment_method.territory
        })

def delete_payment_method(user_id, payment_id):
    with connections.cursor() as cur:
        cur.execute(
            "delete from mock_payment where user_id = %(user_id)s and payment_id = %(payment_id)s",
            {'user_id': user_id, 'payment_id': payment_id}
        )

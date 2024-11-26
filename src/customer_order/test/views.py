
import uuid

from unittest import mock
from rest_framework.test import APITestCase

from app.authentication import User

from customer_order.models import CreateOrderItem, Order, OrderItem


class CreateOrderViewTests(APITestCase):

    @mock.patch('customer_order.daos.create_order')
    def test_create_order_200(self, mock_create_order):

        mock_create_order.return_value = uuid.uuid4()

        self.client.force_authenticate(User(
            user_id=uuid.uuid4(),
            email='test@morriswa.org',
            username='test@morriswa.org',
            vendor_id=None,
            jwt_permissions=[]
        ))

        # execute
        response = self.client.post('/s/checkout')

        self.assertEqual(response.status_code, 200, 'should be successful')
        self.assertEqual(mock_create_order.return_value, response.data['order_id'], 'should return new order id')


class GetOrdersViewTests(APITestCase):
    @mock.patch('customer_order.daos.get_customer_orders')
    def test_get_orders_200(self, mock_get_customer_orders):
        mock_get_customer_orders.return_value = [
            Order(order_id=uuid.uuid4(), payment_id=uuid.uuid4(), payment_status='none', status='process',
                  subtotal=10, tax_rate=0, tax=0, total=10, items=[
                    OrderItem(product_id=1, product_name='Product Name', quantity=1,
                              each_price=10, vendor_id=1, vendor_name='Vendor Name')
                ])
        ]

        self.client.force_authenticate(User(
            user_id=uuid.uuid4(),
            email='test@morriswa.org',
            username='test@morriswa.org',
            vendor_id=None,
            jwt_permissions=[]
        ))

        # execute
        response = self.client.get('/s/orders')

        self.assertEqual(response.status_code, 200, 'should get no error')
        self.assertEqual(response.data[0]['subtotal'], 10, 'should get correct subtotal')
        self.assertEqual(len(response.data[0]['items']), 1, 'should get correct number of items')
        self.assertEqual(response.data[0]['items'][0]['each_price'], 10, 'should get correct item price')
        self.assertEqual(response.data[0]['items'][0]['quantity'], 1, 'should get correct item quantity')


class SubmitOrderViewTests(APITestCase):
    @mock.patch('customer_order.daos.submit_order')
    def test_create_order_204(self, mock_submit_order):

        draft_id = uuid.uuid4()
        payment_id = uuid.uuid4()

        self.client.force_authenticate(User(
            user_id=uuid.uuid4(),
            email='test@morriswa.org',
            username='test@morriswa.org',
            vendor_id=None,
            jwt_permissions=[]
        ))

        # execute
        response = self.client.post(f'/s/checkout/{draft_id}?payment_id={payment_id}')

        self.assertEqual(response.status_code, 204, 'should get no error')

    @mock.patch('customer_order.daos.submit_order')
    def test_create_order_400_missing_payment(self, mock_submit_order):

        draft_id = uuid.uuid4()

        self.client.force_authenticate(User(
            user_id=uuid.uuid4(),
            email='test@morriswa.org',
            username='test@morriswa.org',
            vendor_id=None,
            jwt_permissions=[]
        ))

        # execute
        response = self.client.post(f'/s/checkout/{draft_id}')

        self.assertEqual(response.status_code, 400, 'should get error')
        self.assertEqual(response.data['msg'], 'payment_id required query param')

class DeleteOrderDraftViewTests(APITestCase):
    @mock.patch('customer_order.daos.delete_order_draft')
    def test_delete_order_draft_204(self, mock_delete_order_draft):

        draft_id = uuid.uuid4()

        self.client.force_authenticate(User(
            user_id=uuid.uuid4(),
            email='test@morriswa.org',
            username='test@morriswa.org',
            vendor_id=None,
            jwt_permissions=[]
        ))

        # execute
        response = self.client.delete(f'/s/checkout/{draft_id}')

        self.assertEqual(response.status_code, 204, 'should get no error')


class ViewOrderDraftViewTests(APITestCase):
    @mock.patch('customer_order.daos.review_order')
    def test_get_order_draft_200(self, mock_review_order):

        draft_id = uuid.uuid4()
        mock_review_order.return_value = Order(
            order_id=uuid.uuid4(),
            payment_id=uuid.uuid4(),
            payment_status='none',
            status='incompl',
            subtotal=10, tax_rate=0, tax=0, total=10,
            items=[
                OrderItem(product_id=1, product_name='Product Name', quantity=1,
                          each_price=10, vendor_id=1, vendor_name='Vendor Name')
            ])

        self.client.force_authenticate(User(
            user_id=uuid.uuid4(),
            email='test@morriswa.org',
            username='test@morriswa.org',
            vendor_id=None,
            jwt_permissions=[]
        ))

        # execute
        response = self.client.get(f'/s/checkout/{draft_id}')

        self.assertEqual(response.status_code, 200, 'should get no error')
        self.assertEqual(response.data['subtotal'], 10, 'should get correct subtotal')
        self.assertEqual(len(response.data['items']), 1, 'should get correct number of items')
        self.assertEqual(response.data['items'][0]['each_price'], 10, 'should get correct item price')
        self.assertEqual(response.data['items'][0]['quantity'], 1, 'should get correct item quantity')

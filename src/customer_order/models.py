
from typing import override
from app.validation import ValidatedDataModel


class CreateOrderItem(ValidatedDataModel):
    def __init__(self, **kwargs):
        self.product_id = kwargs.get('product_id')
        self.quantity = kwargs.get('quantity')
        self.each_price = kwargs.get('each_price')

        self.validate()

    @override
    def validate(self) -> None:
        if self.product_id is None:
            raise ValueError('product_id may never be none')

        if self.quantity is None:
            raise ValueError('quantity may never be none')
        elif self.quantity < 1:
            raise ValueError('quantity must be at least 1')

        if self.each_price is None:
            raise ValueError('each_price may never be none')


class OrderItem(ValidatedDataModel):
    def __init__(self, **kwargs):
        self.product_id = kwargs.get('product_id')
        self.product_name = kwargs.get('product_name')

        self.quantity = kwargs.get('quantity')
        self.each_price = kwargs.get('each_price')

        self.vendor_id = kwargs.get('vendor_id')
        self.vendor_name = kwargs.get('vendor_name')

        self.validate()

    @override
    def validate(self) -> None:
        if self.product_id is None:
            raise ValueError('product_id may never be none')

        if self.quantity is None:
            raise ValueError('quantity may never be none')

        if self.each_price is None:
            raise ValueError('each_price may never be none')

class Order(ValidatedDataModel):
    def __init__(self, **kwargs):
        self.order_id = kwargs.get('order_id')
        self.payment_id = kwargs.get('payment_id')
        self.payment_status = kwargs.get('payment_status')
        self.status = kwargs.get('status')
        self.subtotal = kwargs.get('subtotal')
        self.tax_rate = kwargs.get('tax_rate')
        self.tax = kwargs.get('tax')
        self.total = kwargs.get('total')
        self.items: list[OrderItem] = kwargs.get('items')

    @override
    def json(self) -> dict:
        return {
            **vars(self),
            'items': [item.json() for item in self.items]
        }

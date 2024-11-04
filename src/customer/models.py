
from typing import override

from app.exceptions import ValidationException
from app.validation import ValidatedDataModel


class CartItem(ValidatedDataModel):
    def __init__(self, product_id, quantity):
        self.product_id = product_id
        self.quantity = quantity

        self.validate()

    @override
    def validate(self) -> None:
        excs = []
        if self.product_id is None:
            excs.append(('product_id', 'cannot be null'))

        if self.quantity is None:
            excs.append(('quantity', 'cannot be null'))

        if len(excs) > 0:
            raise ValidationException(excs)
        



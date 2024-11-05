
from typing import override
from app.validation import ValidatedDataModel


class BaseProduct(ValidatedDataModel):
    def __init__(self, **kwargs):
        self.product_id = kwargs.get('product_id')
        self.product_name = kwargs.get('product_name')
        self.description = kwargs.get('description')
        self.price = kwargs.get('price')

        self.vendor_id = kwargs.get('vendor_id')
        self.vendor = kwargs.get('business_name') or kwargs.get('vendor_name')

        self.review_score = kwargs.get('review_score')

        self.taste_strength = kwargs.get('taste_strength')
        self.decaf = kwargs.get('decaf')
        self.flavored = kwargs.get('flavored')
        self.single_origin = kwargs.get('single_origin')

    @override
    def validate(self) -> None:
        if self.product_id is None:
            raise ValueError('product_id cannot be None')

        if self.product_name is None:
            raise ValueError('product_name cannot be None')

        if self.description is None:
            raise ValueError('description cannot be None')

        if self.price is None:
            raise ValueError('price cannot be None')

        if self.vendor_id is None:
            raise ValueError('vendor_id cannot be None')

        if self.vendor is None:
            raise ValueError('[business_name or vendor_name] cannot be None')

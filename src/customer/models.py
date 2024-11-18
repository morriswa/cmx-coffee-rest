
from typing import override
from decimal import Decimal

from app.exceptions import ValidationException
from app.validation import ValidatedDataModel


class CartItem(ValidatedDataModel):
    def __init__(self, **kwargs):
        self.product_id = kwargs.get('product_id')
        self.quantity = kwargs.get('quantity')
        self.product_name = kwargs.get('product_name')
        self.description = kwargs.get('description')
        self.vendor_name = kwargs.get('vendor_name')
        self.sale_price: Decimal = kwargs.get('sale_price')

        self.validate()

    @override
    def validate(self) -> None:
        if self.product_id is None:
            raise ValueError('product_id can never be none')

        if self.quantity is None:
            raise ValueError('quantity can never be none')

        if self.product_name is None:
            raise ValueError('product_name can never be none')

        if self.vendor_name is None:
            raise ValueError('vendor_name can never be none')

        if self.sale_price is None:
            raise ValueError('sale_price can never be none')


class CustomerPreferences(ValidatedDataModel):
    def __init__(self, **kwargs):
        self.strength_mild = kwargs.get('strength_mild')
        self.strength_med = kwargs.get('strength_med')
        self.strength_bold = kwargs.get('strength_bold')
        self.blonde = kwargs.get('blonde')
        self.caffinated = kwargs.get('caffinated')
        self.decaf = kwargs.get('decaf')
        self.flavored = kwargs.get('flavored')
        self.single_origin = kwargs.get('single_origin')
        self.origin_blend = kwargs.get('origin_blend')
        self.newsletter_subscription = kwargs.get('newsletter_subscription')

    @override
    def validate(self) -> None:
        if self.strength_mild is not None and \
            self.strength_mild not in ['y', 'n']:
            excs.append(('strength_mild',
                         "valid values are ['y','n']"))

        if self.strength_med is not None and \
            self.strength_med not in ['y', 'n']:
            excs.append(('strength_med',
                         "valid values are ['y','n']"))

        if self.strength_bold is not None and \
            self.strength_bold not in ['y', 'n']:
            excs.append(('strength_bold',
                         "valid values are ['y','n']"))

        if self.blonde is not None and \
            self.blonde not in ['y', 'n']:
            excs.append(('blonde',
                         "valid values are ['y','n']"))

        if self.caffinated is not None and \
            self.caffinated not in ['y', 'n']:
            excs.append(('caffinated',
                         "valid values are ['y','n']"))

        if self.decaf is not None and \
            self.decaf not in ['y', 'n']:
            excs.append(('decaf',
                         "valid values are ['y','n']"))

        if self.flavored is not None and \
            self.flavored not in ['y', 'n']:
            excs.append(('flavored',
                         "valid values are ['y','n']"))

        if self.single_origin is not None and \
            self.single_origin not in ['y', 'n']:
            excs.append(('single_origin',
                         "valid values are ['y','n']"))

        if self.origin_blend is not None and \
            self.origin_blend not in ['y', 'n']:
            excs.append(('origin_blend',
                         "valid values are ['y','n']"))

        if self.newsletter_subscription is not None and \
            self.newsletter_subscription not in ['y', 'n']:
            excs.append(('newsletter_subscription',
                          "valid values are ['y', 'n']"))

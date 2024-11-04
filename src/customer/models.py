
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

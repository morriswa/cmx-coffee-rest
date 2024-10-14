"""
    Vendor-related data models go here
"""
from typing import override

from app.exceptions import ValidationException, BadRequestException
from app.validation import ValidatedDataModel


class VendorApplicationRequest(ValidatedDataModel):
    def __init__(self, **kwargs):
        self.business_name = kwargs.get('business_name')
        self.address_line_one = kwargs.get('address_line_one')
        self.address_line_two = kwargs.get('address_line_two')
        self.city = kwargs.get('city')
        self.state = kwargs.get('state')
        self.zip = kwargs.get('zip')
        self.country = kwargs.get('country')
        self.business_email = kwargs.get('business_email')
        self.phone = kwargs.get('phone')

        self.validate()

    @override
    def validate(self):
        validation_exceptions = []

        if self.business_name is None:
            validation_exceptions.append(('business_name','not null'))

        if self.address_line_one is None:
            validation_exceptions.append(('address_line_one','not null'))

        if self.city is None:
            validation_exceptions.append(('city','not null'))

        if self.state is None:
            validation_exceptions.append(('state','not null'))

        if self.zip is None:
            validation_exceptions.append(('zip','not null'))

        if self.country is None:
            validation_exceptions.append(('country','not null'))

        if self.business_email is None:
            validation_exceptions.append(('business_email', 'not null'))

        if self.phone is None:
            validation_exceptions.append(('phone', 'not null'))

        if len(validation_exceptions) > 0:
            raise ValidationException(validation_exceptions)

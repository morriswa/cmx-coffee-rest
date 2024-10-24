"""
    Vendor-related data models go here
"""
from typing import override

from app.exceptions import ValidationException, BadRequestException
from app.validation import ValidatedDataModel


class VendorApplicationRequest(ValidatedDataModel):
    def __init__(self, **kwargs):
        self.business_name = kwargs.get('business_name')
        self.address_line_one = kwargs.get('address_line_one') or kwargs.get('address_one')
        self.address_line_two = kwargs.get('address_line_two') or kwargs.get('address_two')
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



class VendorApplicationResponse(VendorApplicationRequest):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        super().validate()

        self.application_id = kwargs.get('application_id')
        self.status = kwargs.get('status')
        self.application_date = kwargs.get('application_date')
        self.formatted_address = (f"{self.address_line_one}, "
                                  f"{self.address_line_two + ', ' if self.address_line_two is not None else ''}"
                                  f"{self.city}, "
                                  f"{self.state} {self.zip}, {self.country}")

        if self.application_id is None:
            raise ValueError('application_id should never be null')

        if self.status is None:
            raise ValueError('status should never be null')

        if self.application_date is None:
            raise ValueError('application_date should never be null')

"""
    Vendor-related data models go here
"""
from typing import override

from app.exceptions import ValidationException, BadRequestException
from app.validation import ValidatedDataModel


class BaseApplication(ValidatedDataModel):
    def __init__(self, **kwargs):
        self.business_name = kwargs.get('business_name')
        self.business_email = kwargs.get('business_email')
        self.phone = kwargs.get('phone')

        self.address_line_one = kwargs.get('address_line_one') or kwargs.get('address_one')
        self.address_line_two = kwargs.get('address_line_two') or kwargs.get('address_two')
        self.city = kwargs.get('city')
        self.zip = kwargs.get('zip')
        self.territory = kwargs.get('territory')

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

        if self.zip is None:
            validation_exceptions.append(('zip','not null'))

        if self.business_email is None:
            validation_exceptions.append(('business_email', 'not null'))

        if self.phone is None:
            validation_exceptions.append(('phone', 'not null'))

        if len(validation_exceptions) > 0:
            raise ValidationException(validation_exceptions)

class VendorApplicationRequest(BaseApplication):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
    @override
    def validate(self):
        validation_exceptions = []

        # Collect errors from super().validate()
        try:
            super().validate()
        except ValidationException as e:#line 60
            validation_exceptions.extend(e.errors)#line 61

        if self.territory is None:
            validation_exceptions.append(('territory', 'not null'))

        if len(validation_exceptions) > 0:
            raise ValidationException(validation_exceptions)

    '''
    @override
    def validate(self):

        super().validate()

        if self.territory is None:
            validation_exceptions.append(('territory','not null'))
    '''

class VendorApplicationResponse(BaseApplication):
    def __init__(self, **kwargs):

        super().__init__(**kwargs)
        super().validate()

        self.application_id = kwargs.get('application_id')
        self.status = kwargs.get('status')
        self.application_date = kwargs.get('application_date')
        self.state = kwargs.get('state_code')
        self.country = kwargs.get('country_code')
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


class CoffeeBeanCharacteristics(ValidatedDataModel):
    def __init__(self, **kwargs):
        self.taste_strength = kwargs.get('taste_strength')
        self.decaf = kwargs.get('decaf')
        self.flavored = kwargs.get('flavored')
        self.single_origin = kwargs.get('single_origin')
        self.regions = kwargs.get('regions')
        self.keywords = kwargs.get('keywords')

        self.validate()

    @override
    def validate(self) -> None:
        excs = []

        valid_taste_strength_values = [str(i) for i in range(10)]
        if self.taste_strength is not None and \
            self.taste_strength not in valid_taste_strength_values:
            excs.append(('coffee_bean_characteristics.taste_strength',
                         f"valid values are {valid_taste_strength_values}"))

        if self.decaf is not None and \
            ['y', 'n'].count(self.decaf) != 1:
            excs.append(('coffee_bean_characteristics.decaf',
                         "valid values are ['y','n']"))

        if self.flavored is not None and \
            ['y', 'n'].count(self.flavored) != 1:
            excs.append(('coffee_bean_characteristics.flavored',
                         "valid values are ['y','n']"))

        if self.single_origin is not None and \
            ['y', 'n'].count(self.single_origin) != 1:
            excs.append(('coffee_bean_characteristics.single_origin',
                         "valid values are ['y','n']"))

        if self.regions is not None and len(self.regions) > 100:
            excs.append(('coffee_bean_characteristics.regions',
                         'cannot be longer than 100 chars'))

        if self.keywords is not None and len(self.keywords) > 1_000:
            excs.append(('coffee_bean_characteristics.keywords',
                         'cannot be longer than 1000 chars'))

        if len(excs) > 0:
            raise ValidationException(excs)



class VendorProduct(ValidatedDataModel):
    def __init__(self, **kwargs):
        self.product_id = kwargs.get('product_id')
        self.product_name: str = kwargs.get('product_name')
        self.description: str = kwargs.get('description')
        self.initial_price: int = kwargs.get('initial_price')
        #self.coffee_bean_characteristics: CoffeeBeanCharacteristics = \
            #CoffeeBeanCharacteristics(**kwargs.get('coffee_bean_characteristics', {}))
        cbc_data = kwargs.get('coffee_bean_characteristics')
        if cbc_data and any(value is not None for value in cbc_data.values()):
            self.coffee_bean_characteristics = CoffeeBeanCharacteristics(**cbc_data)
        else:
            self.coffee_bean_characteristics = None


class CreateProductRequest(VendorProduct):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.validate()


    @override
    def validate(self) -> None:

        validation_errors = []

        if self.product_name is None:
            validation_errors.append(('product_name', 'should not be null'))
        elif not 4 <= len(self.product_name) <= 128:
            validation_errors.append(('product_name', 'should be 4-128 characters'))

        if self.description is not None \
            and len(self.description) > 10_000:
            validation_errors.append(('description', 'may not be more than 10_000 chars'))

        if self.initial_price is None:
            validation_errors.append(('initial_price', 'should not be null'))
        elif not 0 <= self.initial_price <= 999.99:
            validation_errors.append(('initial_price', 'should be in range [0, 999.99]'))

        if len(validation_errors) > 0:
            raise ValidationException(validation_errors)


class UpdateProductRequest(VendorProduct):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.validate()


    @override
    def validate(self) -> None:

        validation_errors = []

        if self.initial_price is not None \
            and not 0 <= self.initial_price <= 999.99:
            validation_errors.append(('initial_price', 'should be in range [0, 999.99]'))

        if self.description is not None \
            and len(self.description) > 10_000:
            validation_errors.append(('description', 'may not be more than 10_000 chars'))

        if len(validation_errors) > 0:
            raise ValidationException(validation_errors)


class VendorProductResponse(CreateProductRequest):

    def __init__(self, **kwargs):
        self.status = kwargs.get('status')
        self.date_created = kwargs.get('date_created')

        super().__init__(**kwargs)
        super().validate()

        self.validate()

    @override
    def validate(self) -> None:
        if self.product_id is None:
            raise ValueError('should never be null')

        if self.status is None:
            raise ValueError('should never be null')

        if self.date_created is None:
            raise ValueError('should never be null')

    @override
    def json(self):
        return {
            **vars(self),
            'coffee_bean_characteristics': (
                self.coffee_bean_characteristics.json() if self.coffee_bean_characteristics else None
            )
        }

class VendorInformation(ValidatedDataModel):
    def __init__(self, **kwargs):
        self.vendor_id = kwargs.get('vendor_id')
        self.business_name = kwargs.get('business_name')
        self.business_email = kwargs.get('business_email')
        self.phone = kwargs.get('phone')
        self.address_line_one = kwargs.get('address_line_one') or kwargs.get('address_one')
        self.address_line_two = kwargs.get('address_line_two') or kwargs.get('address_two')
        self.city = kwargs.get('city')
        self.state = kwargs.get('state_code')
        self.zip = kwargs.get('zip')
        self.country = kwargs.get('country_code')
        self.formatted_address = (  f"{self.address_line_one}, "
                                    f"{self.address_line_two + ', ' if self.address_line_two is not None else ''}"
                                    f"{self.city}, "
                                    f"{self.state} {self.zip}, {self.country}")
        self.join_date = kwargs.get('join_date') or kwargs.get('creation_date')

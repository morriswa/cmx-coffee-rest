# src/vendor/tests/models.py

from decimal import Decimal

from django.test import TestCase

from app.exceptions import ValidationException

from vendor.models import (
    BaseApplication,
    VendorApplicationRequest,
    VendorApplicationResponse,
    CoffeeBeanCharacteristics,
    CreateProductRequest,
    UpdateProductRequest,
    VendorProductResponse,
    VendorInformation,
)


class BaseApplicationModelTests(TestCase):

    def test_base_application_missing_fields(self):
        # Missing all required fields
        with self.assertRaises(ValidationException) as context:
            BaseApplication()
        self.assertEqual(len(context.exception.errors), 6)
        error_fields = [error[0] for error in context.exception.errors]
        self.assertIn('business_name', error_fields)
        self.assertIn('address_line_one', error_fields)
        self.assertIn('city', error_fields)
        self.assertIn('zip', error_fields)
        self.assertIn('business_email', error_fields)
        self.assertIn('phone', error_fields)

    def test_base_application_all_fields(self):
        # All required fields provided
        app = BaseApplication(
            business_name='Test Business',
            business_email='test@business.com',
            phone='1234567890',
            address_line_one='123 Main St',
            city='Testville',
            zip='12345',
            territory='USA_KS'
        )
        self.assertEqual(app.business_name, 'Test Business')
        self.assertEqual(app.business_email, 'test@business.com')


class VendorApplicationRequestTests(TestCase):

    def test_vendor_application_request_super_and_territory_validation(self):
        # Missing required fields from BaseApplication and 'territory' is None
        with self.assertRaises(ValidationException) as context:
            VendorApplicationRequest()  # No fields provided
        # The exception should contain errors from both super().validate() and the current validate()
        error_fields = [error[0] for error in context.exception.errors]
        self.assertIn('business_name', error_fields)
        self.assertIn('address_line_one', error_fields)
        self.assertIn('city', error_fields)
        self.assertIn('zip', error_fields)
        self.assertIn('business_email', error_fields)
        self.assertIn('phone', error_fields)
        self.assertIn('territory', error_fields)


    def test_vendor_application_request_missing_territory(self):
        # Missing territory field
        with self.assertRaises(ValidationException) as context:
            VendorApplicationRequest(
                business_name='Test Business',
                business_email='test@business.com',
                phone='1234567890',
                address_line_one='123 Main St',
                city='Testville',
                zip='12345'
            )
        self.assertEqual(len(context.exception.errors), 1)
        self.assertEqual(context.exception.errors[0][0], 'territory')
        self.assertEqual(context.exception.errors[0][1], 'not null')

    def test_vendor_application_request_all_fields(self):
        # All required fields provided
        app = VendorApplicationRequest(
            business_name='Test Business',
            business_email='test@business.com',
            phone='1234567890',
            address_line_one='123 Main St',
            city='Testville',
            zip='12345',
            territory='USA_KS'
        )
        self.assertEqual(app.territory, 'USA_KS')


class VendorApplicationResponseTests(TestCase):

    def test_vendor_application_response_missing_status(self):
        # Missing 'status'
        with self.assertRaises(ValueError) as context:
            VendorApplicationResponse(
                business_name='Test Business',
                business_email='test@business.com',
                phone='1234567890',
                address_line_one='123 Main St',
                city='Testville',
                zip='12345',
                territory='USA_KS',
                application_id=1,
                status=None,  # Missing status
                application_date='2023-01-01',
                state_code='KS',
                country_code='USA'
            )
        self.assertEqual(str(context.exception), 'status should never be null')

    def test_vendor_application_response_missing_application_date(self):
        # Missing 'application_date'
        with self.assertRaises(ValueError) as context:
            VendorApplicationResponse(
                business_name='Test Business',
                business_email='test@business.com',
                phone='1234567890',
                address_line_one='123 Main St',
                city='Testville',
                zip='12345',
                territory='USA_KS',
                application_id=1,
                status='Pending',
                application_date=None,  # Missing application_date
                state_code='KS',
                country_code='USA'
            )
        self.assertEqual(str(context.exception), 'application_date should never be null')


    def test_vendor_application_response_missing_fields(self):
        # Missing required fields
        with self.assertRaises(ValueError) as context:
            VendorApplicationResponse(
                business_name='Test Business',
                business_email='test@business.com',
                phone='1234567890',
                address_line_one='123 Main St',
                city='Testville',
                zip='12345',
                territory='USA_KS',
                application_id=None,
                status=None,
                application_date=None,
                state_code='KS',
                country_code='USA'
            )
        self.assertEqual(str(context.exception), 'application_id should never be null')

    def test_vendor_application_response_all_fields(self):
        # All required fields provided
        app = VendorApplicationResponse(
            business_name='Test Business',
            business_email='test@business.com',
            phone='1234567890',
            address_line_one='123 Main St',
            city='Testville',
            zip='12345',
            territory='USA_KS',
            application_id=1,
            status='Pending',
            application_date='2023-01-01',
            state_code='KS',
            country_code='USA'
        )
        self.assertEqual(app.application_id, 1)
        self.assertEqual(app.status, 'Pending')
        self.assertIsNotNone(app.formatted_address)


class CoffeeBeanCharacteristicsTests(TestCase):

    def test_coffee_bean_characteristics_invalid_taste_strength(self):
        with self.assertRaises(ValidationException) as context:
            CoffeeBeanCharacteristics(taste_strength='10')  # Invalid value
        self.assertEqual(len(context.exception.errors), 1)
        self.assertIn('coffee_bean_characteristics.taste_strength', context.exception.errors[0][0])

    def test_coffee_bean_characteristics_invalid_decaf(self):
        with self.assertRaises(ValidationException) as context:
            CoffeeBeanCharacteristics(decaf='maybe')  # Invalid value
        self.assertEqual(len(context.exception.errors), 1)
        self.assertIn('coffee_bean_characteristics.decaf', context.exception.errors[0][0])

    def test_coffee_bean_characteristics_invalid_flavored(self):
        with self.assertRaises(ValidationException) as context:
            CoffeeBeanCharacteristics(flavored='yes')  # Invalid value
        self.assertEqual(len(context.exception.errors), 1)
        self.assertIn('coffee_bean_characteristics.flavored', context.exception.errors[0][0])

    def test_coffee_bean_characteristics_invalid_single_origin(self):
        with self.assertRaises(ValidationException) as context:
            CoffeeBeanCharacteristics(single_origin='nope')  # Invalid value
        self.assertEqual(len(context.exception.errors), 1)
        self.assertIn('coffee_bean_characteristics.single_origin', context.exception.errors[0][0])

    def test_coffee_bean_characteristics_regions_too_long(self):
        with self.assertRaises(ValidationException) as context:
            CoffeeBeanCharacteristics(regions='a' * 101)
        self.assertEqual(len(context.exception.errors), 1)
        self.assertIn('coffee_bean_characteristics.regions', context.exception.errors[0][0])

    def test_coffee_bean_characteristics_keywords_too_long(self):
        with self.assertRaises(ValidationException) as context:
            CoffeeBeanCharacteristics(keywords='a' * 1001)
        self.assertEqual(len(context.exception.errors), 1)
        self.assertIn('coffee_bean_characteristics.keywords', context.exception.errors[0][0])

    def test_coffee_bean_characteristics_valid(self):
        cbc = CoffeeBeanCharacteristics(
            taste_strength='5',
            decaf='n',
            flavored='y',
            single_origin='n',
            regions='Region1',
            keywords='keyword1,keyword2'
        )
        self.assertEqual(cbc.taste_strength, '5')


class CreateProductRequestTests(TestCase):

    def test_create_product_request_missing_product_name(self):
        with self.assertRaises(ValidationException) as context:
            CreateProductRequest(
                description='A great product',
                initial_price=9.99
            )
        self.assertEqual(len(context.exception.errors), 1)
        self.assertIn('product_name', context.exception.errors[0][0])

    def test_create_product_request_product_name_too_short(self):
        with self.assertRaises(ValidationException) as context:
            CreateProductRequest(
                product_name='abc',
                description='A great product',
                initial_price=9.99
            )
        self.assertEqual(len(context.exception.errors), 1)
        self.assertIn('product_name', context.exception.errors[0][0])

    def test_create_product_request_description_too_long(self):
        with self.assertRaises(ValidationException) as context:
            CreateProductRequest(
                product_name='Valid Name',
                description='a' * 10001,  # Exceeds 10,000 characters
                initial_price=9.99
            )
        self.assertEqual(len(context.exception.errors), 1)
        self.assertIn('description', context.exception.errors[0][0])

    def test_create_product_request_missing_initial_price(self):
        with self.assertRaises(ValidationException) as context:
            CreateProductRequest(
                product_name='Valid Name',
                description='A great product'
            )
        self.assertEqual(len(context.exception.errors), 1)
        self.assertIn('initial_price', context.exception.errors[0][0])

    def test_create_product_request_initial_price_out_of_range(self):
        with self.assertRaises(ValidationException) as context:
            CreateProductRequest(
                product_name='Valid Name',
                description='A great product',
                initial_price=1000.00  # Exceeds max price
            )
        self.assertEqual(len(context.exception.errors), 1)
        self.assertIn('initial_price', context.exception.errors[0][0])

    def test_create_product_request_valid(self):
        product = CreateProductRequest(
            product_name='Valid Name',
            description='A great product',
            initial_price=99.99
        )
        self.assertEqual(product.product_name, 'Valid Name')
        self.assertEqual(product.initial_price, 99.99)


class UpdateProductRequestTests(TestCase):

    def test_update_product_request_initial_price_out_of_range(self):
        with self.assertRaises(ValidationException) as context:
            UpdateProductRequest(
                initial_price=1000.00  # Exceeds max price
            )
        self.assertEqual(len(context.exception.errors), 1)
        self.assertIn('initial_price', context.exception.errors[0][0])

    def test_update_product_request_description_too_long(self):
        with self.assertRaises(ValidationException) as context:
            UpdateProductRequest(
                description='a' * 10001  # Exceeds 10,000 characters
            )
        self.assertEqual(len(context.exception.errors), 1)
        self.assertIn('description', context.exception.errors[0][0])

    def test_update_product_request_valid(self):
        product = UpdateProductRequest(
            product_name='Updated Name',
            description='Updated description',
            initial_price=49.99
        )
        self.assertEqual(product.product_name, 'Updated Name')
        self.assertEqual(product.initial_price, 49.99)


class VendorProductResponseTests(TestCase):

    def test_vendor_product_response_missing_product_id(self):
        with self.assertRaises(ValueError) as context:
            VendorProductResponse(
                product_name='Product',
                description='Description',
                initial_price=9.99,
                status='Active',
                date_created='2023-01-01',
                product_id=None
            )
        self.assertEqual(str(context.exception), 'should never be null')

    def test_vendor_product_response_missing_status(self):
        with self.assertRaises(ValueError) as context:
            VendorProductResponse(
                product_name='Product',
                description='Description',
                initial_price=9.99,
                product_id=1,
                date_created='2023-01-01',
                status=None
            )
        self.assertEqual(str(context.exception), 'should never be null')

    def test_vendor_product_response_missing_date_created(self):
        with self.assertRaises(ValueError) as context:
            VendorProductResponse(
                product_name='Product',
                description='Description',
                initial_price=9.99,
                product_id=1,
                status='Active',
                date_created=None
            )
        self.assertEqual(str(context.exception), 'should never be null')

    def test_vendor_product_response_valid(self):
        product = VendorProductResponse(
            product_name='Product',
            description='Description',
            initial_price=9.99,
            product_id=1,
            status='Active',
            date_created='2023-01-01'
        )
        self.assertEqual(product.product_id, 1)
        self.assertEqual(product.status, 'Active')


class VendorInformationTests(TestCase):

    def test_vendor_information_all_fields(self):
        vendor_info = VendorInformation(
            vendor_id=1,
            business_name='Vendor Name',
            business_email='vendor@test.com',
            phone='1234567890',
            address_line_one='123 Vendor St',
            city='Vendor City',
            state_code='VC',
            zip='54321',
            country_code='USA',
            join_date='2023-01-01'
        )
        self.assertEqual(vendor_info.vendor_id, 1)
        self.assertEqual(vendor_info.business_name, 'Vendor Name')
        self.assertIsNotNone(vendor_info.formatted_address)

    def test_vendor_information_missing_fields(self):
        # Test with minimal required fields
        vendor_info = VendorInformation(
            vendor_id=1,
            business_name='Vendor Name',
            business_email='vendor@test.com',
            phone='1234567890',
            address_line_one='123 Vendor St',
            city='Vendor City',
            state_code='VC',
            zip='54321',
            country_code='USA'
        )
        self.assertEqual(vendor_info.vendor_id, 1)
        self.assertIsNotNone(vendor_info.formatted_address)

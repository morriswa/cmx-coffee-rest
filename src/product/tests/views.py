
from unittest.mock import patch
from rest_framework.test import APITestCase

from product.models import BaseProduct


class GetProductDetailsEndpointTests(APITestCase):
    @patch('product.daos.get_product_details')
    def test_get_product_details_200(self, mock_get_product_details):
        product_id = 1
        vendor_id = 1
        mock_get_product_details.return_value = BaseProduct(
            product_id=product_id,
            product_name='test product',
            description='test product description',
            price=10.00,
            vendor_id=vendor_id,
            review_score=4.5,
            taste_strength=3,
            decaf='n',
            flavored='y',
            single_origin='n',
            first_image='test_image.jpg'
        )

        response = self.client.get(f'/product/{product_id}')

        self.assertEqual(response.status_code, 200, 'customers should get requested data...')
        self.assertEqual(response.data['product_id'],product_id )
        self.assertEqual(response.data['product_name'],'test product')
        self.assertEqual(response.data['description'],'test product description')
        self.assertEqual(response.data['price'],10.00)
        self.assertEqual(response.data['vendor_id'],vendor_id)
        self.assertEqual(response.data['review_score'],4.5)
        self.assertEqual(response.data['taste_strength'],3)
        self.assertEqual(response.data['decaf'],'n')
        self.assertEqual(response.data['flavored'],'y')
        self.assertEqual(response.data['single_origin'],'n')
        self.assertEqual(response.data['first_image'],'test_image.jpg')


import os
import random

from typing import Optional

from django.conf import settings

from app import s3client


def get_product_images_with_keys(product_id) -> list:
    """ WARNING: assumes request has ALREADY BEEN AUTHORIZED """

    keylist: list[str] = s3client.list(f'{settings.AWS_S3_ENVIRONMENT}/coffee/public/product/{product_id}')
    return [{'id': key.split('/')[-1], 'url': s3client.get(key)} for key in keylist]

def upload_product_image(product_id, image):
    """ WARNING: assumes request has ALREADY BEEN AUTHORIZED """

    # count images that belong to product
    product_prefix = f'{settings.AWS_S3_ENVIRONMENT}/coffee/public/product/{product_id}'
    image_count = len(s3client.list(product_prefix))
    if image_count >= 10:  # and throw error if the max has been reached
        raise BadRequestException('cannot have more than 10 images for a product, not uploading...')

    # generate uuid for image
    image_id = uuid.uuid4()
    s3client.upload(  # and upload
        image,
        f'{product_prefix}/{image_id}'
    )
    return image_id

def delete_product_image(product_id, image_id):
    """ WARNING: assumes request has ALREADY BEEN AUTHORIZED """

    s3client.delete(f'cmx/coffee/public/product/{product_id}/{image_id}')


import os
import random
import uuid

from typing import Optional
from app import s3client


def get_product_images_with_keys(product_id) -> list:
    """ WARNING: assumes request has ALREADY BEEN AUTHORIZED """

    image_ids: list[str] = s3client.list(f'coffee/public/product/{product_id}')
    return [
        {
            'id': image_id,
            'url': s3client.get(f'coffee/public/product/{product_id}/{image_id}')
        }
        for image_id in image_ids
    ]

def upload_product_image(product_id, image):
    """ WARNING: assumes request has ALREADY BEEN AUTHORIZED """

    # count images that belong to product
    product_prefix = f'coffee/public/product/{product_id}'
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

    s3client.delete(f'coffee/public/product/{product_id}/{image_id}')

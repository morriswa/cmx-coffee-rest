
import os
import random

from typing import Optional

from django.conf import settings

from app import s3client


def get_random_product_image(product_id) -> Optional[str]:
    keys = s3client.list(f'{settings.AWS_S3_ENVIRONMENT}/coffee/public/product/{product.product_id}')
    if len(keys) > 0:
        key = random.choice(keys)
        return s3client.get(key)
    return None

def get_product_images(product_id) -> list[str]:
    keylist = s3client.list(f'cmx/coffee/public/product/{product_id}')
    return [s3client.get(key) for key in keylist]

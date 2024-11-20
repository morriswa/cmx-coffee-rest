
import os
import random

from typing import Optional

from app import s3client


def get_random_product_image(product_id) -> Optional[str]:
    image_ids = s3client.list(f'coffee/public/product/{product_id}')
    if len(image_ids) > 0:
        image_id = random.choice(image_ids)
        return s3client.get(f'coffee/public/product/{product_id}/{image_id}')
    return None

def get_product_images(product_id) -> list[str]:
    image_ids = s3client.list(f'coffee/public/product/{product_id}')
    return [
        s3client.get(f'coffee/public/product/{product_id}/{image_id}')
        for image_id in image_ids
    ]

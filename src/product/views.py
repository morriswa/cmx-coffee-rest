
from rest_framework.request import Request
from rest_framework.response import Response

from app import s3client
from app.decorators import user_view


@user_view(['GET'])
def get_product_images(request: Request, product_id: int) -> Response:
    keylist = s3client.list(f'cmx/coffee/public/product/{product_id}')
    images = [s3client.get(key) for key in keylist]
    return Response(status=200, data=images)

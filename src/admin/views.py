"""
    Admin-related django views (http request actions) go here
"""
import logging
from rest_framework.request import Request
from rest_framework.response import Response

from app.decorators import admin_view
from app.exceptions import BadRequestException

import admin.daos as admin_dao


@admin_view(['GET'])
def get_pending_vendor_applications(request: Request) -> Response:
    apps = admin_dao.get_pending_vendor_applications()
    return Response(status=200, data=[app.json() for app in apps])

@admin_view(['PUT'])
def process_pending_vendor_application(request: Request, application_id: int) -> Response:
    requested_action = request.query_params.get('action')
    match requested_action:
        case 'approve':
            admin_dao.approve_vendor_application(request.user.user_id, application_id)
            return Response(status=204)
        case 'reject':
            logging.info(f'implement me! reject app#{application_id}')
            return Response(status=204)
        case _:
            raise BadRequestException('invalid action')

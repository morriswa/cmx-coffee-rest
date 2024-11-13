
from rest_framework.request import Request
from rest_framework.response import Response

from app.decorators import any_view, user_view

import core.daos as dao


@any_view(['GET'])
def health(request: Request) -> Response:
    """ health endpoint to test any_view """
    #returns a simple JSON response with message hello world
    return Response({
        "msg": "hello world!"
    }, status=200)

@any_view(['GET'])
def aux(request: Request) -> Response:
    territories = dao.get_approved_territories()
    return Response(status=200, data={
        'territories': [territory.json() for territory in territories]
    })

@user_view(['GET'])
def permissions(request: Request) -> Response:
    return Response(request.user.permissions, status=200)

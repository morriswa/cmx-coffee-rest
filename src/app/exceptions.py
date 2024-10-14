import logging
from abc import abstractmethod, ABC
from functools import wraps
from typing import override, Self

from rest_framework.response import Response
from rest_framework import exceptions


class _APIException(ABC):
    """ abstract class to define api exception functions
        :author William Morris
    """
    @abstractmethod
    def json(self) -> dict:
        """ return exception in json format """
        pass

    @abstractmethod
    def response(self) -> Response:
        """ return exception in json body of http response with appropriate error code attached """
        pass


class APIException(Exception, _APIException):
    """ exception to raise for internal server errors
        :author William Morris
    """

    def __init__(self, error: str): self.error = error

    @override
    def json(self): return {
        "error": self.error
    }

    @override
    def response(self) -> Response: return Response(self.json(), status=500)


class BadRequestException(APIException):
    """ exception to raise for errors caused by a bad user request
        :author William Morris
    """
    def __init__(self, error: str): super().__init__(error)

    @override
    def response(self) -> Response: return Response(self.json(), status=400)


class ValidationException(BadRequestException):
    """ exception to raise for model validation errors
        :author William Morris
    """
    def __init__(self, errors):
        self.errors = errors
        super().__init__('A Validation Exception has Occured!')

    @override
    def json(self): return [{'field':error[0], 'error': error[1]} for error in self.errors]

def app_exception_handler(exc, context):
    """ application exception handler, passed to drf in settings.py """

    if isinstance(exc, APIException):
        return exc.response()

    if isinstance(exc, exceptions.AuthenticationFailed) or isinstance(exc, exceptions.PermissionDenied):
        return Response({"msg": exc.detail}, status=exc.status_code)

    # default case
    logging.error(f"encountered unexpected exception {exc.__class__.__name__}: {str(exc)}")
    return Response({"msg": "Unexpected server error, please contact your system administrator."}, status=500)

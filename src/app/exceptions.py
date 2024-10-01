import logging
from abc import abstractmethod, ABC
from functools import wraps
from typing import override

from rest_framework.response import Response


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
    def __init__(self, field, error):
        self.field = field
        super().__init__(error)

    @override
    def json(self): return {
        "field": self.field,
        "error": self.error
    }

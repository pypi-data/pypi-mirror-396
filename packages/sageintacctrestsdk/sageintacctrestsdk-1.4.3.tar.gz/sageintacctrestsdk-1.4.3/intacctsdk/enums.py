from enum import Enum


class RESTMethodEnum(str, Enum):
    """
    REST Method Enum
    """
    GET = 'GET'
    POST = 'POST'
    PATCH = 'PATCH'
    DELETE = 'DELETE'

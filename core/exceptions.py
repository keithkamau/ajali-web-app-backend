"""
Custom exception handling for the API
"""
from rest_framework.views import exception_handler


def custom_exception_handler(exc, context):
    """
    Wraps DRF's default exception handler to return a consistent
    error response shape across the API.
    """
    response = exception_handler(exc, context)

    if response is not None:
        response.data = {
            'error': True,
            'message': str(exc),
            'details': response.data,
            'status_code': response.status_code,
        }

    return response
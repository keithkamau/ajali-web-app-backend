"""
Custom pagination classes for the API
"""
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.views import exception_handler

class CustomPagination(PageNumberPagination):
    """
    Custom pagination with page size query parameter
    """
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100

    def get_paginated_response(self, data):
        return Response({
            'count': self.page.paginator.count,
            'next': self.get_next_link(),
            'previous': self.get_previous_link(),
            'page': self.page.number,
            'total_pages': self.page.paginator.num_pages,
            'results': data
        })
    
def custom_exception_handler(exc, context):
        response = exception_handler(exc, context)

        if response is not None:
            response.data = {
                "error": True,
                "status_code": response.status_code,
                "details": response.data,
            }

        return response
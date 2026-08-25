import logging
import json
from django.utils.deprecation import MiddlewareMixin
from django.http import JsonResponse
from django.core.exceptions import ValidationError
from django.db import IntegrityError

logger = logging.getLogger(__name__)

class ExceptionHandlingMiddleware(MiddlewareMixin):
    """
    Global exception handling middleware
    """
    def process_exception(self, request, exception):
        """
        Handle exceptions globally
        """
        if isinstance(exception, ValidationError):
            return JsonResponse({
                'error': 'Validation error',
                'details': exception.message_dict
            }, status=400)
        
        if isinstance(exception, IntegrityError):
            return JsonResponse({
                'error': 'Database integrity error',
                'details': str(exception)
            }, status=400)
        
        if isinstance(exception, ValueError):
            return JsonResponse({
                'error': str(exception)
            }, status=400)
        
        # Log unexpected errors
        logger.error(f'Unhandled exception: {exception}')
        
        return JsonResponse({
            'error': 'Internal server error'
        }, status=500)

class RequestLoggingMiddleware(MiddlewareMixin):
    """
    Log all API requests
    """
    def process_request(self, request):
        """
        Log incoming requests
        """
        if request.path.startswith('/api/'):
            logger.info(f'Request: {request.method} {request.path}')
            if request.body:
                try:
                    body = json.loads(request.body)
                    # Remove sensitive data
                    if 'password' in body:
                        body['password'] = '***'
                    logger.debug(f'Request body: {body}')
                except:
                    pass

    def process_response(self, request, response):
        """
        Log outgoing responses
        """
        if request.path.startswith('/api/'):
            logger.info(f'Response: {response.status_code} {request.path}')
        return response

class RateLimitingMiddleware(MiddlewareMixin):
    """
    Simple rate limiting middleware
    """
    def __init__(self, get_response):
        self.get_response = get_response
        self.requests = {}
    
    def __call__(self, request):
        if request.path.startswith('/api/auth/'):
            ip = self.get_client_ip(request)
            self.check_rate_limit(ip)
        return self.get_response(request)
    
    def get_client_ip(self, request):
        """
        Get client IP address
        """
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
    
    def check_rate_limit(self, ip):
        """
        Check if rate limit exceeded
        """
        from django.utils import timezone
        from datetime import timedelta
        
        now = timezone.now()
        if ip in self.requests:
            requests = self.requests[ip]
            # Remove old requests
            requests = [r for r in requests if now - r < timedelta(minutes=1)]
            if len(requests) >= 60:  # 60 requests per minute
                raise Exception('Rate limit exceeded')
            requests.append(now)
            self.requests[ip] = requests
        else:
            self.requests[ip] = [now]
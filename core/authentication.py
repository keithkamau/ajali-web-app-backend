"""
Custom authentication classes for the API
"""
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from django.contrib.auth import get_user_model

User = get_user_model()

class CustomJWTAuthentication(JWTAuthentication):
    """
    Custom JWT authentication class with additional validation
    """
    def authenticate(self, request):
        try:
            return super().authenticate(request)
        except InvalidToken:
            raise InvalidToken('Invalid or expired token')
        except TokenError:
            raise TokenError('Token error occurred')

    def get_user(self, validated_token):
        """
        Override to check if user is active
        """
        user_id = validated_token.get('user_id')
        try:
            user = User.objects.get(id=user_id, is_active=True)
        except User.DoesNotExist:
            raise InvalidToken('User not found or inactive')
        return user
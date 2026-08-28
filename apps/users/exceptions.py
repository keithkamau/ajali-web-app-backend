from rest_framework.exceptions import APIException
from rest_framework import status

class UserNotFoundError(APIException):
    status_code = status.HTTP_404_NOT_FOUND
    default_detail = 'User not found'
    default_code = 'user_not_found'

class UserInactiveError(APIException):
    status_code = status.HTTP_403_FORBIDDEN
    default_detail = 'User account is inactive'
    default_code = 'user_inactive'

class InvalidCredentialsError(APIException):
    status_code = status.HTTP_401_UNAUTHORIZED
    default_detail = 'Invalid email or password'
    default_code = 'invalid_credentials'

class TokenExpiredError(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'Token has expired'
    default_code = 'token_expired'

class TokenInvalidError(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'Invalid token'
    default_code = 'token_invalid'

class EmailAlreadyExistsError(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'Email already registered'
    default_code = 'email_exists'

class PasswordValidationError(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'Password validation failed'
    default_code = 'password_validation_failed'

class PhoneNumberInvalidError(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'Invalid phone number format'
    default_code = 'phone_invalid'
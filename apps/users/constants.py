from django.db import models

class UserRoles:
    USER = 'user'
    ADMIN = 'admin'
    
    CHOICES = [
        (USER, 'User'),
        (ADMIN, 'Admin'),
    ]

class UserStatus:
    ACTIVE = 'active'
    INACTIVE = 'inactive'
    SUSPENDED = 'suspended'
    
    CHOICES = [
        (ACTIVE, 'Active'),
        (INACTIVE, 'Inactive'),
        (SUSPENDED, 'Suspended'),
    ]

class TokenTypes:
    RESET_PASSWORD = 'reset_password'
    EMAIL_VERIFICATION = 'email_verification'
    
    CHOICES = [
        (RESET_PASSWORD, 'Password Reset'),
        (EMAIL_VERIFICATION, 'Email Verification'),
    ]

class ActivityActions:
    LOGIN = 'login'
    LOGOUT = 'logout'
    REGISTER = 'register'
    PASSWORD_CHANGE = 'password_change'
    PROFILE_UPDATE = 'profile_update'
    PASSWORD_RESET_REQUEST = 'password_reset_request'
    PASSWORD_RESET = 'password_reset'
    EMAIL_VERIFICATION = 'email_verification'
    
    CHOICES = [
        (LOGIN, 'Login'),
        (LOGOUT, 'Logout'),
        (REGISTER, 'Register'),
        (PASSWORD_CHANGE, 'Password Change'),
        (PROFILE_UPDATE, 'Profile Update'),
        (PASSWORD_RESET_REQUEST, 'Password Reset Request'),
        (PASSWORD_RESET, 'Password Reset'),
        (EMAIL_VERIFICATION, 'Email Verification'),
    ]
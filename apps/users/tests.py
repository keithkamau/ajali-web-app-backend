from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from .models import PasswordResetToken

User = get_user_model()

class AuthTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.register_url = reverse('register')
        self.login_url = reverse('login')
        self.user_data = {
            'email': 'test@example.com',
            'password': 'Test@123456',
            'full_name': 'Test User',
            'phone_number': '0712345678'
        }
    
    def test_user_registration(self):
        """Test user registration"""
        response = self.client.post(self.register_url, self.user_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(User.objects.first().email, 'test@example.com')
    
    def test_duplicate_email_registration(self):
        """Test registration with duplicate email"""
        self.client.post(self.register_url, self.user_data)
        response = self.client.post(self.register_url, self.user_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('email', response.data)
    
    def test_user_login(self):
        """Test user login"""
        self.client.post(self.register_url, self.user_data)
        response = self.client.post(self.login_url, {
            'email': 'test@example.com',
            'password': 'Test@123456'
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access_token', response.data)
        self.assertIn('refresh_token', response.data)
    
    def test_login_invalid_credentials(self):
        """Test login with invalid credentials"""
        response = self.client.post(self.login_url, {
            'email': 'wrong@example.com',
            'password': 'WrongPassword'
        })
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_get_current_user(self):
        """Test getting current user profile"""
        # Register and login
        self.client.post(self.register_url, self.user_data)
        login_response = self.client.post(self.login_url, {
            'email': 'test@example.com',
            'password': 'Test@123456'
        })
        token = login_response.data['access_token']
        
        # Get profile
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        response = self.client.get(reverse('current-user'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['email'], 'test@example.com')
    
    def test_change_password(self):
        """Test changing password"""
        # Register and login
        self.client.post(self.register_url, self.user_data)
        login_response = self.client.post(self.login_url, {
            'email': 'test@example.com',
            'password': 'Test@123456'
        })
        token = login_response.data['access_token']
        
        # Change password
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        response = self.client.post(reverse('change-password'), {
            'current_password': 'Test@123456',
            'new_password': 'NewTest@123456'
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Login with new password
        response = self.client.post(self.login_url, {
            'email': 'test@example.com',
            'password': 'NewTest@123456'
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_forgot_password(self):
        """Test forgot password request"""
        self.client.post(self.register_url, self.user_data)
        response = self.client.post(reverse('forgot-password'), {
            'email': 'test@example.com'
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('reset_token', response.data)
    
    def test_reset_password(self):
        """Test resetting password with token"""
        # Register and request reset
        self.client.post(self.register_url, self.user_data)
        forgot_response = self.client.post(reverse('forgot-password'), {
            'email': 'test@example.com'
        })
        token = forgot_response.data['reset_token']
        
        # Reset password
        response = self.client.post(reverse('reset-password'), {
            'token': token,
            'new_password': 'ResetTest@123456'
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Login with new password
        response = self.client.post(self.login_url, {
            'email': 'test@example.com',
            'password': 'ResetTest@123456'
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_invalid_reset_token(self):
        """Test reset with invalid token"""
        response = self.client.post(reverse('reset-password'), {
            'token': 'invalid-token',
            'new_password': 'ResetTest@123456'
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
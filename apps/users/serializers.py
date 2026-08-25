from rest_framework import serializers
from django.contrib.auth import authenticate
from .models import User
from .validators import validate_kenyan_phone, validate_password_strength, validate_email_unique

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True,
        required=True,
        validators=[validate_password_strength]
    )
    email = serializers.EmailField(
        required=True,
        validators=[validate_email_unique]
    )
    phone_number = serializers.CharField(
        required=False,
        allow_blank=True,
        allow_null=True,
        validators=[validate_kenyan_phone]
    )
    
    class Meta:
        model = User
        fields = ('id', 'email', 'password', 'full_name', 'phone_number', 'role')
        extra_kwargs = {
            'full_name': {'required': True},
            'role': {'read_only': True},
        }
    
    def create(self, validated_data):
        user = User.objects.create_user(
            email=validated_data['email'],
            password=validated_data['password'],
            full_name=validated_data['full_name'],
            phone_number=validated_data.get('phone_number', ''),
            role='user'
        )
        return user

class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(required=True, write_only=True)

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            'id', 'email', 'full_name', 'phone_number', 
            'role', 'is_active', 'is_verified', 
            'created_at', 'updated_at'
        )
        read_only_fields = (
            'id', 'role', 'is_active', 'is_verified', 
            'created_at', 'updated_at'
        )

class ChangePasswordSerializer(serializers.Serializer):
    current_password = serializers.CharField(required=True, write_only=True)
    new_password = serializers.CharField(
        required=True,
        write_only=True,
        validators=[validate_password_strength]
    )

class ForgotPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)

class ResetPasswordSerializer(serializers.Serializer):
    token = serializers.CharField(required=True)
    new_password = serializers.CharField(
        required=True,
        write_only=True,
        validators=[validate_password_strength]
    )
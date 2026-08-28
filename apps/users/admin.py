from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _
from .models import User, PasswordResetToken

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('email', 'full_name', 'role', 'is_active', 'is_verified', 'created_at')
    list_filter = ('role', 'is_active', 'is_verified')
    search_fields = ('email', 'full_name', 'phone_number')
    ordering = ('-created_at',)
    
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (_('Personal Info'), {'fields': ('full_name', 'phone_number')}),
        (_('Permissions'), {
            'fields': ('role', 'is_active', 'is_verified', 'groups', 'user_permissions'),
        }),
        (_('Important Dates'), {'fields': ('last_login', 'created_at', 'updated_at')}),
    )
    
    readonly_fields = ('created_at', 'updated_at', 'last_login')
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'full_name', 'password1', 'password2', 'role'),
        }),
    )
    
    def save_model(self, request, obj, form, change):
        if not change:  # New user
            obj.set_password(form.cleaned_data['password1'])
        super().save_model(request, obj, form, change)

@admin.register(PasswordResetToken)
class PasswordResetTokenAdmin(admin.ModelAdmin):
    list_display = ('user', 'token', 'expires_at', 'used', 'created_at')
    list_filter = ('used',)
    search_fields = ('user__email', 'token')
    readonly_fields = ('created_at',)
    ordering = ('-created_at',)
from django.contrib import admin
from .models import AdminActionLog

@admin.register(AdminActionLog)
class AdminActionLogAdmin(admin.ModelAdmin):
    list_display = ('id', 'admin', 'action', 'created_at')
    list_filter = ('action', 'created_at')
    search_fields = ('admin__email', 'action', 'details')
    readonly_fields = ('id', 'created_at')
    ordering = ('-created_at',)
    
    fieldsets = (
        (None, {
            'fields': ('admin', 'action', 'details')
        }),
        ('Metadata', {
            'fields': ('ip_address', 'user_agent', 'created_at')
        }),
    )
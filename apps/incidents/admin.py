from django.contrib import admin
from .models import Incident, IncidentStatusHistory, IncidentMedia

@admin.register(Incident)
class IncidentAdmin(admin.ModelAdmin):
    list_display = ('title', 'type', 'status', 'user', 'created_at')
    list_filter = ('type', 'status', 'is_anonymous')
    search_fields = ('title', 'description', 'location_address')
    readonly_fields = ('created_at', 'updated_at')

@admin.register(IncidentStatusHistory)
class IncidentStatusHistoryAdmin(admin.ModelAdmin):
    list_display = ('incident', 'new_status', 'changed_by', 'created_at')
    list_filter = ('new_status',)
    readonly_fields = ('created_at',)

@admin.register(IncidentMedia)
class IncidentMediaAdmin(admin.ModelAdmin):
    list_display = ('incident', 'media_type', 'uploaded_at')
    list_filter = ('media_type',)
    readonly_fields = ('uploaded_at',)
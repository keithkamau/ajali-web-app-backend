from django.contrib import admin
from .models import Incident, IncidentStatusHistory, IncidentMedia


class IncidentStatusHistoryInline(admin.TabularInline):
    model = IncidentStatusHistory
    extra = 0
    fields = ('old_status', 'new_status', 'changed_by', 'comment', 'changed_at')
    readonly_fields = ('changed_at',)
    ordering = ('-sequence',)


@admin.register(Incident)
class IncidentAdmin(admin.ModelAdmin):
    list_display = ('title', 'type', 'status', 'user', 'is_anonymous', 'created_at')
    list_filter = ('type', 'status', 'is_anonymous')
    search_fields = ('title', 'description', 'location_address')
    readonly_fields = ('created_at', 'updated_at')
    date_hierarchy = 'created_at'
    ordering = ('-created_at',)
    inlines = [IncidentStatusHistoryInline]


@admin.register(IncidentStatusHistory)
class IncidentStatusHistoryAdmin(admin.ModelAdmin):
    list_display = ('incident', 'old_status', 'new_status', 'changed_by', 'changed_at')
    list_filter = ('new_status',)
    search_fields = ('incident__title', 'comment')
    readonly_fields = ('changed_at',)


@admin.register(IncidentMedia)
class IncidentMediaAdmin(admin.ModelAdmin):
    list_display = ('incident', 'media_type', 'uploaded_at')
    list_filter = ('media_type',)
    search_fields = ('incident__title',)
    readonly_fields = ('uploaded_at',)
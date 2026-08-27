from django.contrib import admin

from .models import AdminActionLog


@admin.register(AdminActionLog)
class AdminActionLogAdmin(admin.ModelAdmin):
    list_display = (
        "admin",
        "action",
        "timestamp",
    )

    list_filter = (
        "action",
        "timestamp",
    )

    search_fields = (
        "admin__email",
        "admin__full_name",
        "action",
    )

    readonly_fields = (
        "id",
        "admin",
        "action",
        "timestamp",
        "details",
    )
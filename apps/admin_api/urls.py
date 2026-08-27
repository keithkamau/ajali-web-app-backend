from django.urls import path

from .views import (
    AdminActionLogListView,
    AdminUserDetailView,
    AdminIncidentDetailView,
    AdminIncidentListView,
    AdminIncidentStatusUpdateView,
    AdminIncidentStatusHistoryView,
    AdminBulkIncidentStatusView,
    AdminStatsView,
    # AdminUserListView,
    AdminUserRoleUpdateView,
)
from rest_framework.generics import RetrieveDestroyAPIView

urlpatterns = [
    path(
        "actions/",
        AdminActionLogListView.as_view(),
        name="admin-action-list",
    ),

    # path(
    #     "users/",
    #     AdminUserListView.as_view(),
    #     name="admin-user-list",
    # ),

    path(
    "incidents/stats/",
    AdminStatsView.as_view(),
    name="admin-incident-stats",
    ),

    path(
        "users/<uuid:id>/",
        AdminUserDetailView.as_view(),
        name="admin-user-detail",
    ),

    path(
        "users/<uuid:id>/role/",
        AdminUserRoleUpdateView.as_view(),
        name="admin-user-role-update",
    ),

    path(
        "incidents/",
        AdminIncidentListView.as_view(),
        name="admin-incident-list",
    ),

    path(
        "incidents/bulk-status/",
        AdminBulkIncidentStatusView.as_view(),
        name="admin-bulk-incident-status",
    ),

    path(
        "incidents/<uuid:pk>/",
        AdminIncidentDetailView.as_view(),
        name="admin-incident-detail",
    ),

    path(
        "incidents/<uuid:pk>/status/",
        AdminIncidentStatusUpdateView.as_view(),
        name="admin-incident-status-update",
    ),

    path(
    "incidents/<uuid:pk>/status-history/",
    AdminIncidentStatusHistoryView.as_view(),
    name="admin-incident-status-history",
    ),

]
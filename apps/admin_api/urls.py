from django.urls import path

from .views import (
    AdminActionLogListView,
    AdminUserDetailView,
    AdminUserListView,
    AdminUserRoleUpdateView,
)
from rest_framework.generics import RetrieveDestroyAPIView

urlpatterns = [
    path(
        "actions/",
        AdminActionLogListView.as_view(),
        name="admin-action-list",
    ),

    path(
        "users/",
        AdminUserListView.as_view(),
        name="admin-user-list",
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
]
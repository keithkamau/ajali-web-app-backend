from django.urls import path
from . import views

urlpatterns = [
    path('incidents/', views.AdminIncidentListView.as_view(), name='admin-incident-list'),
    path('incidents/<uuid:id>/', views.AdminIncidentDetailView.as_view(), name='admin-incident-detail'),
    path('incidents/<uuid:id>/status/', views.AdminIncidentStatusUpdateView.as_view(), name='admin-incident-status-update'),
    path('incidents/stats/', views.AdminIncidentStatsView.as_view(), name='admin-incident-stats'),
]
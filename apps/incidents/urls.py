from django.urls import path
from . import views

urlpatterns = [
    path('', views.IncidentListCreateView.as_view(), name='incident-list-create'),
    path('<uuid:pk>/', views.IncidentDetailView.as_view(), name='incident-detail'),
    path('<uuid:pk>/status-history/', views.IncidentStatusHistoryView.as_view(), name='incident-status-history'),
    path('<uuid:pk>/status/', views.IncidentStatusUpdateView.as_view(), name='incident-status-update'),
    path('<uuid:pk>/images/', views.IncidentImageUploadView.as_view(), name='incident-image-upload'),
    path('<uuid:pk>/videos/', views.IncidentVideoUploadView.as_view(), name='incident-video-upload'),
    path('public/', views.PublicIncidentListView.as_view(), name='public-incidents'),
]
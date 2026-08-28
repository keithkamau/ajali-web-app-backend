from django.urls import path
from . import views

urlpatterns = [
    path('', views.IncidentListCreateView.as_view(), name='incident-list-create'),
    path('search/', views.IncidentSearchView.as_view(), name='incident-search'),
    path('filter/', views.IncidentFilterView.as_view(), name='incident-filter'),
    path('<uuid:pk>/', views.IncidentDetailView.as_view(), name='incident-detail'),
    path('<uuid:pk>/status-history/', views.IncidentStatusHistoryView.as_view(), name='incident-status-history'),
    path('<uuid:pk>/status/', views.IncidentStatusUpdateView.as_view(), name='incident-status-update'),
    path('<uuid:pk>/images/', views.IncidentImageUploadView.as_view(), name='incident-image-upload'),
    path('<uuid:pk>/images/<uuid:media_id>/', views.IncidentImageDeleteView.as_view(), name='incident-image-delete'),
    path('<uuid:pk>/videos/', views.IncidentVideoUploadView.as_view(), name='incident-video-upload'),
    path('<uuid:pk>/videos/<uuid:media_id>/', views.IncidentVideoDeleteView.as_view(), name='incident-video-delete'),
    path('public/', views.PublicIncidentListView.as_view(), name='public-incidents'),
    path('geocode/reverse/', views.ReverseGeocodeView.as_view(), name='geocode-reverse'),
    path('geocode/forward/', views.ForwardGeocodeView.as_view(), name='geocode-forward'),
    path('<uuid:pk>/upload-signature/', views.CloudinaryUploadSignatureView.as_view(), name='incident-upload-signature'),
]
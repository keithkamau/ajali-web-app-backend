# ajali/urls.py
from django.contrib import admin
from django.urls import include, path, re_path
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions

# Simple root view
def root_view(request):
    return JsonResponse({
        "message": "Ajali API is running",
        "endpoints": {
            "health": "/api/health/",
            "auth": "/api/auth/",
            "incidents": "/api/incidents/",
            "admin": "/api/admin/",
            "notifications": "/api/notifications/",
            "swagger": "/swagger/",
            "redoc": "/redoc/"
        }
    })

@csrf_exempt
def health_check(request):
    return JsonResponse({
        "status": "healthy",
        "message": "Ajali! API is running",
        "version": "1.0.0"
    })

schema_view = get_schema_view(
    openapi.Info(
        title="Ajali API",
        default_version="v1",
        description="Incident reporting API",
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    # Root - returns API info
    path('', root_view, name='root'),
    
    # Admin
    path('admin/', admin.site.urls),
    
    # Health check
    path('api/health/', health_check, name='health_check'),
    
    # API endpoints
    path('api/auth/', include('apps.users.urls')),
    path('api/incidents/', include('apps.incidents.urls')),
    path('api/admin/', include('apps.admin_api.urls')),
    path('api/notifications/', include('apps.notifications.urls')),
    
    # API Documentation
    re_path(r'^swagger(?P<format>\.json|\.yaml)$', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]
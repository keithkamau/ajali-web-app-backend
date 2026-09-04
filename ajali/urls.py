from django.contrib import admin
from django.urls import include, path, re_path
from django.conf import settings
from django.conf.urls.static import static
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework import permissions
from drf_yasg import openapi
from drf_yasg.views import get_schema_view


@csrf_exempt
def root_view(request):
    return JsonResponse({
        "message": "Ajali API is running",
        "version": "1.0.0",
        "endpoints": {
            "health": "/health/",
            "api_health": "/api/health/",
            "auth": "/api/auth/",
            "incidents": "/api/incidents/",
            "admin": "/api/admin/",
            "notifications": "/api/notifications/",
            "swagger": "/swagger/",
            "redoc": "/redoc/"
        }
    })


@csrf_exempt
def simple_health(request):
    return JsonResponse({
        "status": "ok",
        "message": "Ajali API is healthy",
        "timestamp": "2026-08-29"
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
    # Root
    path('', root_view, name='root'),
    
    # Admin
    path('admin/', admin.site.urls),
    
    # Health
    path('health/', simple_health, name='health'),
    path('api/health/', simple_health, name='api_health'),
    
    # API endpoints
    path('api/auth/', include('apps.users.urls')),
    path('api/incidents/', include('apps.incidents.urls')),
    path('api/admin/', include('apps.admin_api.urls')),
    path('api/notifications/', include('apps.notifications.urls')),
    
    # API Documentation
    re_path(r'^swagger(?P<format>\.json|\.yaml)$', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    path('docs/', include_docs_urls(title='Ajali API')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
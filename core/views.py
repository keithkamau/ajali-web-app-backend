from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

@csrf_exempt
@require_http_methods(["GET", "HEAD"])
def health_check(request):
    return JsonResponse({
        "status": "ok",
        "message": "Ajali API is running",
        "method": request.method
    }, status=200)
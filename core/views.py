from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def health_check(request):
    return JsonResponse({
        "status": "healthy",
        "message": "Ajali! API is running",
        "version": "1.0.0"
    })
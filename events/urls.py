from django.http import JsonResponse

def root_redirect(request):
    return JsonResponse({
        "message": "Welcome to Event Management API",
        "documentation": "/api/",
        "admin": "/admin/"
    })

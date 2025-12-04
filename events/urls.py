from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    EventViewSet,
    UserProfileViewSet,
    register_user,
)

# Router for ViewSets
router = DefaultRouter()
router.register(r'events', EventViewSet, basename='event')
router.register(r'profiles', UserProfileViewSet, basename='profile')

urlpatterns = [
    path('auth/register/', register_user, name='register'),
    path('', include(router.urls)),
]

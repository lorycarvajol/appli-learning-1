from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import AdminOverviewViewSet, AdminTrainerViewSet, AdminUserViewSet

router = DefaultRouter()
router.register(r'overview', AdminOverviewViewSet, basename='admin-overview')
router.register(r'trainers', AdminTrainerViewSet, basename='admin-trainer')
router.register(r'users', AdminUserViewSet, basename='admin-user')

urlpatterns = [
    path('', include(router.urls)),
]

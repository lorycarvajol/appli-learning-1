from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    AdminOverviewViewSet,
    AdminTrainerViewSet,
    AdminUserViewSet,
    AuditLogViewSet,
)

router = DefaultRouter()
router.register(r'overview', AdminOverviewViewSet, basename='admin-overview')
router.register(r'trainers', AdminTrainerViewSet, basename='admin-trainer')
router.register(r'users', AdminUserViewSet, basename='admin-user')
router.register(r'audit', AuditLogViewSet, basename='admin-audit')

urlpatterns = [
    path('', include(router.urls)),
]

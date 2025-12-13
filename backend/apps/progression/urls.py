from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    ChapterAccessViewSet,
    UserProgressViewSet,
    ActivityLogViewSet,
    TrainerDashboardViewSet
)

router = DefaultRouter()
router.register(r'chapter-access', ChapterAccessViewSet, basename='chapter-access')
router.register(r'progress', UserProgressViewSet, basename='progress')
router.register(r'activity', ActivityLogViewSet, basename='activity')
router.register(r'trainer-dashboard', TrainerDashboardViewSet, basename='trainer-dashboard')

urlpatterns = [
    path('', include(router.urls)),
]

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import BadgeViewSet, GamificationSummaryViewSet, PointTransactionViewSet

router = DefaultRouter()
router.register(r'badges', BadgeViewSet, basename='badge')
router.register(r'summary', GamificationSummaryViewSet, basename='gamification-summary')
router.register(r'points', PointTransactionViewSet, basename='point-transaction')

urlpatterns = [
    path('', include(router.urls)),
]

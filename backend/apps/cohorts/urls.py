from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    CohortInviteViewSet,
    CohortViewSet,
    InviteAcceptView,
    InviteDetailView,
    InviteJoinView,
)

router = DefaultRouter()
router.register(r'cohorts', CohortViewSet, basename='cohort')
router.register(r'invites', CohortInviteViewSet, basename='cohort-invite')

urlpatterns = [
    # Parcours public, sous un préfixe distinct de `invites/` : le routeur y
    # expose déjà `invites/<pk>/` pour les formateurs, et un jeton opaque s'y
    # confondrait avec une clé primaire.
    path('join/<str:token>/', InviteDetailView.as_view(), name='invite_detail'),
    path('join/<str:token>/register/', InviteAcceptView.as_view(), name='invite_accept'),
    path('join/<str:token>/attach/', InviteJoinView.as_view(), name='invite_join'),

    path('', include(router.urls)),
]

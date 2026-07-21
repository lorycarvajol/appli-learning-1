"""
URL configuration for authentication endpoints.
"""
from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from .views import (
    AvatarCatalogView,
    RegisterView,
    CurrentUserView,
    ProfileView,
    ChangePasswordView,
    LogoutView,
    PasswordResetRequestView,
    PasswordResetValidateView,
    PasswordResetConfirmView,
)

app_name = 'accounts'

urlpatterns = [
    # Authentication
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', TokenObtainPairView.as_view(), name='login'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('logout/', LogoutView.as_view(), name='logout'),

    # Mot de passe oublié (public)
    path('password-reset/', PasswordResetRequestView.as_view(), name='password_reset'),
    path(
        'password-reset/validate/',
        PasswordResetValidateView.as_view(),
        name='password_reset_validate'
    ),
    path(
        'password-reset/confirm/',
        PasswordResetConfirmView.as_view(),
        name='password_reset_confirm'
    ),

    # User & Profile
    path('me/', CurrentUserView.as_view(), name='current_user'),
    path('profile/', ProfileView.as_view(), name='profile'),
    path('avatars/', AvatarCatalogView.as_view(), name='avatar_catalog'),
    path('change-password/', ChangePasswordView.as_view(), name='change_password'),
]

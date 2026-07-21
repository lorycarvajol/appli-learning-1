"""
Views for user authentication and profile management.
"""
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model

from .models import User, Profile
from .serializers import (
    RegisterSerializer,
    UserSerializer,
    ProfileSerializer,
    ChangePasswordSerializer,
    PasswordResetRequestSerializer,
    PasswordResetConfirmSerializer,
)
from .services import (
    resolve_reset_token,
    revoke_refresh_tokens,
    send_password_reset_email,
)

User = get_user_model()


class RegisterView(generics.CreateAPIView):
    """
    Register a new user.
    POST /api/auth/register/
    """
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        # Generate tokens for the new user
        refresh = RefreshToken.for_user(user)

        return Response({
            'user': UserSerializer(user).data,
            'tokens': {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            },
            'message': 'User registered successfully'
        }, status=status.HTTP_201_CREATED)


class CurrentUserView(generics.RetrieveUpdateAPIView):
    """
    Get or update the current authenticated user.
    GET/PUT/PATCH /api/auth/me/
    """
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user


class ProfileView(generics.RetrieveUpdateAPIView):
    """
    Get or update the current user's profile.
    GET/PUT/PATCH /api/auth/profile/
    """
    serializer_class = ProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user.profile


class ChangePasswordView(APIView):
    """
    Change user password.
    POST /api/auth/change-password/
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = ChangePasswordSerializer(
            data=request.data,
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response({
            'message': 'Password changed successfully'
        }, status=status.HTTP_200_OK)


# Réponse volontairement identique que le compte existe ou non.
RESET_REQUEST_MESSAGE = (
    "Si un compte est associé à cette adresse, un lien de réinitialisation "
    "vient d'être envoyé. Pensez à vérifier vos spams."
)


class PasswordResetRequestView(APIView):
    """
    Demande un lien de réinitialisation.
    POST /api/auth/password-reset/

    Répond **toujours** 200 avec le même message, que l'email corresponde à un
    compte ou non : une réponse différenciée transformerait cet endpoint en
    annuaire des inscrits. Le throttle limite par ailleurs l'usage massif.
    """
    permission_classes = [AllowAny]
    throttle_scope = 'password_reset'

    def post(self, request):
        serializer = PasswordResetRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data['email']
        user = User.objects.filter(email__iexact=email, is_active=True).first()

        if user is not None:
            send_password_reset_email(user)

        return Response({'message': RESET_REQUEST_MESSAGE}, status=status.HTTP_200_OK)


class PasswordResetValidateView(APIView):
    """
    Vérifie un lien avant d'afficher le formulaire.
    GET /api/auth/password-reset/validate/?uid=...&token=...

    Évite de faire saisir deux fois un mot de passe pour apprendre ensuite que
    le lien avait expiré.
    """
    permission_classes = [AllowAny]
    throttle_scope = 'password_reset'

    def get(self, request):
        user = resolve_reset_token(
            request.query_params.get('uid', ''),
            request.query_params.get('token', ''),
        )
        if user is None:
            return Response({'valid': False}, status=status.HTTP_200_OK)

        # On confirme l'email pour rassurer l'utilisateur sur le compte visé,
        # mais le lien ne s'obtient que depuis sa boîte mail.
        return Response({'valid': True, 'email': user.email}, status=status.HTTP_200_OK)


class PasswordResetConfirmView(APIView):
    """
    Définit le nouveau mot de passe.
    POST /api/auth/password-reset/confirm/
    """
    permission_classes = [AllowAny]
    throttle_scope = 'password_reset'

    def post(self, request):
        serializer = PasswordResetConfirmSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.validated_data['user']
        user.set_password(serializer.validated_data['new_password'])
        user.save()

        # Le changement de mot de passe invalide déjà le jeton (il est signé
        # à partir de l'ancien hash), mais pas les sessions JWT ouvertes :
        # sans ça, un attaquant déjà connecté le resterait 7 jours.
        revoke_refresh_tokens(user)

        return Response(
            {'message': 'Mot de passe réinitialisé. Vous pouvez vous connecter.'},
            status=status.HTTP_200_OK
        )


class LogoutView(APIView):
    """
    Logout user by blacklisting the refresh token.
    POST /api/auth/logout/
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data.get('refresh')
            if not refresh_token:
                return Response({
                    'error': 'Refresh token is required'
                }, status=status.HTTP_400_BAD_REQUEST)

            token = RefreshToken(refresh_token)
            token.blacklist()

            return Response({
                'message': 'Logged out successfully'
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                'error': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)

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

from .avatars import VISAGES, PALETTES, avatar_choices
from .models import User, Profile
from .throttling import FailedLoginThrottle
from .serializers import (
    RegisterSerializer,
    UserSerializer,
    ProfileSerializer,
    ChangePasswordSerializer,
    PasswordResetRequestSerializer,
    PasswordResetConfirmSerializer,
)
from .services import (
    build_user_export,
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


class LoginView(TokenObtainPairView):
    """
    Connexion.
    POST /api/auth/login/

    Identique à la vue de SimpleJWT, à ceci près que les **échecs** sont
    comptés par compte visé (cf. `throttling.FailedLoginThrottle`). Sans cela,
    la seule limite était le plafond anonyme global de 100 requêtes par heure,
    qui laisse largement passer une attaque par dictionnaire.
    """
    throttle_classes = [FailedLoginThrottle]

    def check_throttles(self, request):
        """Conserve les instances de throttle pour pouvoir les alimenter après.

        `APIView.check_throttles` les crée, les consulte et les jette. Or on ne
        sait qu'après l'appel s'il faut décompter une tentative — il faut donc
        retrouver l'objet qui porte la clé et l'historique déjà calculés.
        """
        self._throttles = self.get_throttles()
        durations = [
            throttle.wait()
            for throttle in self._throttles
            if not throttle.allow_request(request, self)
        ]
        if durations:
            known = [d for d in durations if d]
            self.throttled(request, max(known, default=None))

    def post(self, request, *args, **kwargs):
        try:
            response = super().post(request, *args, **kwargs)
        except Exception:
            # Identifiants refusés : c'est la tentative qu'on décompte.
            for throttle in getattr(self, '_throttles', []):
                if hasattr(throttle, 'record_failure'):
                    throttle.record_failure()
            raise

        # Réussite : on efface l'ardoise, pour que quelques fautes de frappe
        # ne laissent pas l'apprenant à un essai du blocage.
        for throttle in getattr(self, '_throttles', []):
            if hasattr(throttle, 'reset'):
                throttle.reset()

        return response


class ProfileView(generics.RetrieveUpdateAPIView):
    """
    Get or update the current user's profile.
    GET/PUT/PATCH /api/auth/profile/
    """
    serializer_class = ProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user.profile


class AvatarCatalogView(APIView):
    """
    GET /api/auth/avatars/

    Visages et palettes disponibles. Le client fait le rendu en SVG à partir de
    ces deux listes ; le serveur reste l'autorité sur ce qui est acceptable
    (cf. `ProfileSerializer.validate_avatar_key`).
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response({
            'visages': list(VISAGES),
            'palettes': list(PALETTES),
            'keys': avatar_choices(),
        })


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


class DataExportView(APIView):
    """
    Export de toutes les données personnelles du compte courant (RGPD, portabilité).
    GET /api/auth/export/

    Renvoie un JSON téléchargeable. Réservé au compte lui-même : chacun exporte
    ses propres données, jamais celles d'un tiers.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        data = build_user_export(request.user)
        response = Response(data)
        # En-tête de téléchargement : le navigateur propose d'enregistrer le
        # fichier plutôt que de l'afficher.
        response['Content-Disposition'] = (
            'attachment; filename="mes-donnees-codeacademy.json"'
        )
        return response


class DeleteAccountView(APIView):
    """
    Suppression (anonymisation) du compte courant, à l'initiative de l'apprenant.
    POST /api/auth/delete-account/

    Droit à l'effacement en self-service. **Irréversible.** On exige le mot de
    passe courant : sans lui, un poste laissé ouvert suffirait à détruire un
    compte. La logique d'effacement et sa trace d'audit vivent dans
    `apps.administration.services` (chemin unique et audité).
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        from apps.administration.services import AdminActionError, self_delete_account

        password = request.data.get('password', '')
        if not request.user.check_password(password):
            return Response(
                {'password': ["Mot de passe incorrect."]},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            self_delete_account(request.user)
        except AdminActionError as exc:
            return Response(
                {'detail': str(exc)},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(
            {'message': 'Votre compte a été supprimé. Vos données personnelles '
                        'ont été effacées.'},
            status=status.HTTP_200_OK,
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

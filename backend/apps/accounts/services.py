"""
Logique métier des comptes : réinitialisation de mot de passe.

Choix de conception : on s'appuie sur `default_token_generator` de Django
plutôt que sur un modèle de jeton maison. Ce générateur est **sans état** —
le jeton est signé à partir du hash du mot de passe et de `last_login` de
l'utilisateur. Deux propriétés en découlent gratuitement :

- **usage unique** : dès que le mot de passe change, le jeton devient invalide
- **invalidation à la connexion** : si l'utilisateur retrouve son mot de passe
  et se connecte entre-temps, le lien envoyé cesse de fonctionner

C'est le contraire du choix fait pour les liens d'invitation de classe, qui
eux sont stockés en clair parce que le formateur doit pouvoir les réafficher.
Ici le lien est délivré une fois par email et jamais réaffiché : rien à
stocker, donc rien à voler dans la base.
"""
import logging

from django.conf import settings
from django.contrib.auth.tokens import default_token_generator
from django.core.exceptions import ValidationError
from django.core.mail import send_mail
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode

from .models import User

logger = logging.getLogger(__name__)


def build_reset_url(user):
    """Construit l'URL de réinitialisation destinée à l'apprenant."""
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    token = default_token_generator.make_token(user)
    base = settings.FRONTEND_URL.rstrip('/')
    return f"{base}/reset-password/{uid}/{token}", uid, token


def resolve_reset_token(uid, token):
    """Retourne l'utilisateur si le couple (uid, token) est valide, sinon None.

    Ne lève jamais : un uid malformé, un utilisateur supprimé ou un jeton
    périmé donnent tous le même résultat, pour ne rien révéler à l'appelant.
    """
    try:
        user_id = force_str(urlsafe_base64_decode(uid))
        user = User.objects.get(pk=user_id)
    except (TypeError, ValueError, OverflowError, ValidationError, User.DoesNotExist):
        # ValidationError : la clé primaire est un UUID, un uid bricolé le fait
        # échouer à la conversion plutôt qu'à la recherche.
        return None

    if not default_token_generator.check_token(user, token):
        return None

    return user


def send_password_reset_email(user):
    """Envoie le lien de réinitialisation.

    Envoi synchrone assumé : une réinitialisation est un événement rare, et
    passer par Celery rendrait un échec d'envoi invisible pour l'appelant.
    Le risque de blocage du worker est borné par le throttle sur la vue.
    """
    reset_url, _, _ = build_reset_url(user)
    minutes = settings.PASSWORD_RESET_TIMEOUT // 60

    subject = "Réinitialisation de votre mot de passe — CodeAcademy"
    message = (
        f"Bonjour {user.first_name or ''},\n\n"
        "Vous avez demandé à réinitialiser votre mot de passe.\n\n"
        f"Cliquez sur ce lien pour en choisir un nouveau :\n{reset_url}\n\n"
        f"Ce lien expire dans {minutes} minutes et ne fonctionne qu'une fois.\n\n"
        "Si vous n'êtes pas à l'origine de cette demande, ignorez ce message : "
        "votre mot de passe actuel reste valable.\n\n"
        "— L'équipe CodeAcademy"
    )

    try:
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
            fail_silently=False,
        )
        return True
    except Exception:
        # L'appelant renvoie une réponse identique quoi qu'il arrive (pour ne
        # pas révéler l'existence du compte) : la trace ne doit pas se perdre.
        logger.exception("Échec de l'envoi du mail de réinitialisation")
        return False


def revoke_refresh_tokens(user):
    """Blackliste tous les refresh tokens en cours de l'utilisateur.

    Indispensable après une réinitialisation : si le compte était compromis,
    changer le mot de passe sans révoquer les sessions laisserait l'attaquant
    connecté jusqu'à expiration de son refresh token (7 jours).
    """
    from rest_framework_simplejwt.token_blacklist.models import (
        BlacklistedToken,
        OutstandingToken,
    )

    revoked = 0
    for token in OutstandingToken.objects.filter(user=user):
        _, created = BlacklistedToken.objects.get_or_create(token=token)
        if created:
            revoked += 1
    return revoked

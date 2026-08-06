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


def build_user_export(user):
    """Rassemble toutes les données personnelles d'un compte (droit à la portabilité).

    Retourne un dictionnaire JSON-sérialisable couvrant le compte, le profil,
    la progression, le grand livre de points, les badges obtenus, la série de
    jours et l'historique d'activité. C'est ce que la personne peut emporter si
    elle quitte la plateforme.

    Les modèles des autres apps sont importés **localement** : `accounts` ne
    doit pas dépendre au niveau module de `progression` ni de `gamification`
    (ordre de chargement des apps), et l'export est un chemin froid.
    """
    from django.utils import timezone

    profile = getattr(user, 'profile', None)

    def iso(value):
        return value.isoformat() if value else None

    data = {
        'export_generated_at': timezone.now().isoformat(),
        'compte': {
            'id': str(user.pk),
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'role': user.role,
            'date_joined': iso(user.date_joined),
            'last_login': iso(user.last_login),
        },
        'profil': None,
        'progression': [],
        'points': [],
        'badges': [],
        'serie_de_jours': None,
        'activite': [],
    }

    if profile is not None:
        data['profil'] = {
            'bio': profile.bio,
            'github_username': profile.github_username,
            'theme': profile.theme,
            'timezone': profile.timezone,
            'avatar_key': profile.avatar_key,
            'total_points': profile.total_points,
            'level': profile.level,
            'visible_au_classement': profile.show_in_leaderboard,
            'classe': profile.cohort.name if profile.cohort else None,
            'consentement_accepte_le': iso(profile.terms_accepted_at),
            'cree_le': iso(profile.created_at),
        }

    # --- Progression -------------------------------------------------------
    try:
        from apps.progression.models import ActivityLog, UserProgress

        data['progression'] = [
            {
                'lecon': getattr(p.lesson, 'title', None),
                'statut': p.status,
                'tentatives': p.attempts,
                'reussi': p.is_passed,
                'score': p.score,
                'temps_passe_secondes': p.time_spent,
                'termine_le': iso(p.completed_at),
            }
            for p in UserProgress.objects.filter(user=user).select_related('lesson')
        ]
        data['activite'] = [
            {
                'type': a.activity_type,
                'lecon': getattr(a.lesson, 'title', None),
                'chapitre': getattr(a.chapter, 'title', None),
                'date': iso(a.created_at),
            }
            for a in ActivityLog.objects.filter(user=user)
            .select_related('lesson', 'chapter')
        ]
    except Exception:  # pragma: no cover - l'app peut être absente en test isolé
        logger.exception("Export : progression indisponible")

    # --- Gamification ------------------------------------------------------
    try:
        from apps.gamification.models import PointTransaction, UserBadge, UserStreak

        data['points'] = [
            {
                'montant': t.amount,
                'raison': t.reason,
                'source': t.source_key,
                'date': iso(t.created_at),
            }
            for t in PointTransaction.objects.filter(user=user)
        ]
        data['badges'] = [
            {
                'badge': b.badge.name,
                'code': b.badge.code,
                'obtenu_le': iso(b.earned_at),
            }
            for b in UserBadge.objects.filter(user=user).select_related('badge')
        ]
        streak = UserStreak.objects.filter(user=user).first()
        if streak is not None:
            data['serie_de_jours'] = {
                'serie_actuelle': streak.current_streak,
                'meilleure_serie': streak.longest_streak,
                'derniere_activite': iso(streak.last_activity_date),
            }
    except Exception:  # pragma: no cover
        logger.exception("Export : gamification indisponible")

    return data


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

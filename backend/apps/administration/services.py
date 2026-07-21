"""
Cycle de vie des comptes, côté administration.

Choix RGPD : **anonymisation plutôt que suppression en cascade**. Le droit à
l'effacement porte sur les données personnelles, pas sur les agrégats. Effacer
en cascade fausserait rétroactivement les statistiques des classes — un
formateur verrait le taux de complétion de sa promo changer sans explication.
On vide donc l'identité et on conserve la progression, désormais rattachée à
un compte qui ne désigne plus personne.
"""
import uuid

from django.db import transaction
from django.utils import timezone

from apps.accounts.models import User

ANONYMIZED_DOMAIN = 'anonymized.invalid'


class AdminActionError(Exception):
    """Action d'administration refusée pour une raison métier."""


def _assert_not_last_admin(user):
    """Empêche de se retrouver sans aucun administrateur actif.

    Sans ce garde-fou, une plateforme peut devenir impilotable en un clic.
    """
    remaining = User.objects.filter(
        role=User.Role.ADMIN, is_active=True
    ).exclude(pk=user.pk).exists()
    if not remaining:
        raise AdminActionError(
            "Impossible : ce compte est le dernier administrateur actif."
        )


def set_role(actor, user, role):
    """Change le rôle d'un compte.

    `User.save()` réaligne `is_staff` : promouvoir en ADMIN ouvre l'admin
    Django, rétrograder le referme.
    """
    if role not in User.Role.values:
        raise AdminActionError("Rôle inconnu.")

    if user.pk == actor.pk:
        raise AdminActionError("Vous ne pouvez pas modifier votre propre rôle.")

    if user.role == User.Role.ADMIN and role != User.Role.ADMIN:
        _assert_not_last_admin(user)

    user.role = role
    user.save(update_fields=['role', 'is_staff'])
    return user


def set_active(actor, user, is_active):
    """Active ou désactive un compte.

    Un compte désactivé ne peut plus se connecter, mais toutes ses données
    restent intactes : c'est réversible, contrairement à l'anonymisation.
    """
    if user.pk == actor.pk:
        raise AdminActionError("Vous ne pouvez pas désactiver votre propre compte.")

    if not is_active and user.role == User.Role.ADMIN:
        _assert_not_last_admin(user)

    user.is_active = is_active
    user.save(update_fields=['is_active'])

    if not is_active:
        _revoke_sessions(user)

    return user


def anonymize(actor, user):
    """Exerce le droit à l'effacement. **Irréversible.**

    Ce qui disparaît : email, nom, prénom, bio, avatar, pseudo GitHub, mot de
    passe. Ce qui reste : progression, points, badges, activité — désormais
    rattachés à un compte anonyme, donc inexploitables pour ré-identifier.
    """
    if user.pk == actor.pk:
        raise AdminActionError("Vous ne pouvez pas anonymiser votre propre compte.")

    if user.role == User.Role.ADMIN:
        _assert_not_last_admin(user)

    profile = getattr(user, 'profile', None)
    if profile is not None and profile.anonymized_at is not None:
        raise AdminActionError("Ce compte est déjà anonymisé.")

    with transaction.atomic():
        user.email = f'anonyme-{uuid.uuid4().hex[:12]}@{ANONYMIZED_DOMAIN}'
        user.first_name = ''
        user.last_name = ''
        user.is_active = False
        user.set_unusable_password()
        user.save()

        if profile is not None:
            profile.bio = ''
            profile.github_username = ''
            profile.avatar = None
            profile.cohort = None
            profile.anonymized_at = timezone.now()
            profile.save()

        _revoke_sessions(user)

    return user


def _revoke_sessions(user):
    """Blackliste les refresh tokens : la désactivation doit être immédiate."""
    from rest_framework_simplejwt.token_blacklist.models import (
        BlacklistedToken,
        OutstandingToken,
    )

    for token in OutstandingToken.objects.filter(user=user):
        BlacklistedToken.objects.get_or_create(token=token)

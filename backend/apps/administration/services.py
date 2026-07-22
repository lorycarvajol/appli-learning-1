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

from .audit import label_for, record
from .models import AuditLog

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

    with transaction.atomic():
        before = user.role
        user.role = role
        user.save(update_fields=['role', 'is_staff'])
        record(
            actor, AuditLog.Action.SET_ROLE, user,
            changes={'before': before, 'after': role},
        )
    return user


def assign_cohort(actor, user, cohort):
    """Rattache un apprenant à une classe, ou l'en détache si `cohort` est nul.

    Sert surtout à récupérer les apprenants autonomes, qu'aucun formateur ne
    voit. Conformément à la règle générale de la plateforme, cela ne retire
    jamais un accès de chapitre déjà obtenu.
    """
    if user.role != User.Role.LEARNER:
        raise AdminActionError("Seul un apprenant peut être rattaché à une classe.")

    profile = getattr(user, 'profile', None)
    if profile is None:
        raise AdminActionError("Ce compte n'a pas de profil.")

    with transaction.atomic():
        before = profile.cohort
        profile.cohort = cohort
        profile.save(update_fields=['cohort', 'updated_at'])
        record(
            actor, AuditLog.Action.ASSIGN_COHORT, user,
            changes={'before': label_for(before), 'after': label_for(cohort)},
        )

    user.refresh_from_db()
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

    with transaction.atomic():
        before = user.is_active
        user.is_active = is_active
        user.save(update_fields=['is_active'])

        if not is_active:
            _revoke_sessions(user)

        record(
            actor, AuditLog.Action.SET_ACTIVE, user,
            changes={'before': before, 'after': is_active},
        )

    return user


def _erase_identity(user):
    """Écrase les données personnelles d'un compte, en place.

    Cœur partagé entre l'anonymisation par un administrateur (`anonymize`) et
    la suppression que l'apprenant déclenche lui-même (`self_delete_account`) :
    les deux effacent exactement les mêmes champs et révoquent les sessions.
    La seule différence est l'auteur et la trace d'audit, laissés à l'appelant.

    Ce qui disparaît : email, nom, prénom, bio, avatar, pseudo GitHub, mot de
    passe. Ce qui reste : progression, points, badges, activité — désormais
    rattachés à un compte anonyme, donc inexploitables pour ré-identifier.
    """
    profile = getattr(user, 'profile', None)

    user.email = f'anonyme-{uuid.uuid4().hex[:12]}@{ANONYMIZED_DOMAIN}'
    user.first_name = ''
    user.last_name = ''
    user.is_active = False
    user.set_unusable_password()
    user.save()

    if profile is not None:
        profile.bio = ''
        profile.github_username = ''
        # L'avatar effectif est le choix de catalogue (`avatar_key`) ; le vider
        # fait retomber le compte sur des initiales génériques.
        profile.avatar_key = ''
        profile.cohort = None
        profile.anonymized_at = timezone.now()
        profile.save()

    _revoke_sessions(user)


def anonymize(actor, user):
    """Exerce le droit à l'effacement pour le compte d'un tiers. **Irréversible.**"""
    if user.pk == actor.pk:
        raise AdminActionError("Vous ne pouvez pas anonymiser votre propre compte.")

    if user.role == User.Role.ADMIN:
        _assert_not_last_admin(user)

    profile = getattr(user, 'profile', None)
    if profile is not None and profile.anonymized_at is not None:
        raise AdminActionError("Ce compte est déjà anonymisé.")

    # Figer l'identité **avant** de l'écraser : c'est tout l'intérêt de la
    # trace. Journalisée après coup, elle enregistrerait l'adresse anonymisée
    # et ne prouverait plus quelle demande d'effacement a été honorée.
    identity_before = label_for(user)

    with transaction.atomic():
        _erase_identity(user)
        record(
            actor, AuditLog.Action.ANONYMIZE, user,
            target_label=identity_before,
            changes={'before': identity_before, 'after': user.email},
        )

    return user


def self_delete_account(user):
    """Suppression de compte déclenchée par l'apprenant lui-même (RGPD). **Irréversible.**

    Même effacement que `anonymize`, mais l'auteur *est* la cible — d'où
    l'absence du garde-fou « pas sur soi-même » qui n'aurait aucun sens ici.
    Le garde-fou du **dernier administrateur actif** reste, lui, en vigueur :
    un admin isolé ne doit pas pouvoir rendre la plateforme impilotable d'un
    clic ; il lui faut d'abord promouvoir un remplaçant.

    La trace nomme l'utilisateur comme acteur **et** comme cible : c'est bien
    lui qui a demandé et obtenu son effacement, et le journal doit pouvoir le
    prouver.
    """
    profile = getattr(user, 'profile', None)
    if profile is not None and profile.anonymized_at is not None:
        raise AdminActionError("Ce compte est déjà anonymisé.")

    if user.role == User.Role.ADMIN:
        _assert_not_last_admin(user)

    identity_before = label_for(user)

    with transaction.atomic():
        _erase_identity(user)
        record(
            user, AuditLog.Action.ACCOUNT_DELETED, user,
            target_label=identity_before,
            changes={'before': identity_before, 'after': user.email},
        )

    return user


def _revoke_sessions(user):
    """Blackliste les refresh tokens : la désactivation doit être immédiate."""
    from rest_framework_simplejwt.token_blacklist.models import (
        BlacklistedToken,
        OutstandingToken,
    )

    for token in OutstandingToken.objects.filter(user=user):
        BlacklistedToken.objects.get_or_create(token=token)

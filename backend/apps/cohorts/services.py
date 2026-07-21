"""
Logique des invitations de classe.

Point de vigilance central : **ni le rôle ni la classe ne viennent du
formulaire**. Ils sont déduits du jeton côté serveur. C'est la même discipline
que le `read_only` sur `role` dans `UserSerializer` — sans elle, l'inscription
par invitation deviendrait un moyen de se déclarer formateur.
"""
from django.conf import settings
from django.db import transaction
from django.db.models import F

from apps.accounts.models import User

from .models import CohortInvite


def build_invite_url(invite):
    """URL à diffuser par le formateur (Teams, Discord, email…)."""
    base = settings.FRONTEND_URL.rstrip('/')
    return f"{base}/rejoindre/{invite.token}"


def resolve_usable_invite(token):
    """Retourne l'invitation si elle est utilisable, sinon None.

    Volontairement binaire : la vue publique ne doit pas distinguer « révoquée »
    de « expirée » ni de « inexistante », sous peine de confirmer qu'un jeton a
    existé. Le détail reste disponible côté formateur via `invalid_reason()`.
    """
    if not token:
        return None

    invite = (
        CohortInvite.objects.select_related('cohort', 'cohort__trainer')
        .filter(token=token)
        .first()
    )
    if invite is None or not invite.is_usable:
        return None

    return invite


@transaction.atomic
def consume_invite(user, invite):
    """Rattache l'utilisateur et décompte un usage.

    Le verrou sur l'invitation rend le contrôle de `max_uses` sûr en
    concurrence : sans lui, deux clics simultanés sur le dernier usage
    disponible passeraient tous les deux.
    """
    locked = CohortInvite.objects.select_for_update().get(pk=invite.pk)
    if not locked.is_usable:
        return False

    if locked.role == User.Role.TRAINER:
        # Une invitation formateur ne rattache à aucune classe : elle promeut.
        user.role = User.Role.TRAINER
        user.save(update_fields=['role'])
    else:
        profile = user.profile
        profile.cohort = locked.cohort
        profile.save(update_fields=['cohort', 'updated_at'])

    CohortInvite.objects.filter(pk=locked.pk).update(uses_count=F('uses_count') + 1)
    return True

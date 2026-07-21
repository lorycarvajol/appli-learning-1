"""
Écriture du journal d'audit.

Module séparé de `services.py` volontairement : `apps/progression` et
`apps/cohorts` doivent pouvoir journaliser sans importer le cycle de vie des
comptes, qui dépend lui-même de `apps.accounts`. Un module sans dépendance
métier reste importable de partout.
"""
from .models import AuditLog


def label_for(obj):
    """Désignation lisible et stable d'un objet visé par une action.

    Un identifiant seul ne dit rien à qui relit le journal six mois plus tard.
    On préfère l'email pour un compte, le nom pour une classe ou un chapitre.
    """
    if obj is None:
        return ''
    for attribute in ('email', 'name', 'title'):
        value = getattr(obj, attribute, None)
        if value:
            return str(value)
    return str(getattr(obj, 'pk', obj))


def record(actor, action, target=None, *, target_label=None, changes=None):
    """Consigne une action d'administration.

    À appeler **dans la même transaction que l'action auditée** : une action
    effectuée sans trace vaut une action non tracée, et c'est précisément ce
    qu'on cherche à rendre impossible.

    `target_label` peut être forcé quand la cible est sur le point de perdre
    son identité — cas de l'anonymisation, où il faut figer l'email *avant*
    de l'écraser, sinon le journal enregistre l'adresse anonymisée et ne
    prouve plus rien.
    """
    return AuditLog.objects.create(
        actor=actor,
        actor_label=label_for(actor),
        action=action,
        target_id=getattr(target, 'pk', None),
        target_label=target_label if target_label is not None else label_for(target),
        changes=changes or {},
    )

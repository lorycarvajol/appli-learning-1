"""
Journal d'audit des actions d'administration.

Pourquoi ce modèle existe : `set_role`, `set_active`, `anonymize` et
`assign_cohort` sont les opérations les plus lourdes de la plateforme — dont
une strictement irréversible — et ne laissaient jusqu'ici **aucune trace**.
Impossible de répondre à « qui a anonymisé ce compte, et quand ? ». L'admin
Django tient bien un `LogEntry`, mais l'espace React le court-circuite
entièrement : tout ce qui passe par `/api/administration/` lui échappait.

Le journal sert deux usages distincts :

- **redevabilité** — « tout pouvoir » n'est acceptable que si l'exercice du
  pouvoir est consultable ;
- **preuve RGPD** — il faut pouvoir démontrer qu'une demande d'effacement a
  bien été honorée, à telle date, par tel administrateur.
"""
import uuid

from django.conf import settings
from django.db import models


class AuditLog(models.Model):
    """Une action d'administration, figée telle qu'elle a eu lieu.

    ### Pourquoi les libellés sont dénormalisés

    `actor` et le compte cible sont conservés en clé étrangère *et* recopiés en
    texte (`actor_label`, `target_label`). Ce n'est pas une redondance
    accidentelle :

    - La cible d'une **anonymisation** perd son email par définition. Sans
      libellé figé au moment de l'acte, le journal dirait « un compte anonyme a
      été anonymisé » — il ne prouverait plus rien.
    - Un acteur supprimé de la base emporterait ses lignes avec lui si la clé
      était en `CASCADE`. Un journal qui s'efface quand on efface l'auteur ne
      vaut rien, d'où le `SET_NULL` doublé du libellé.

    ### Immuabilité

    Rien n'expose ce modèle en écriture : `AuditLogViewSet` est en lecture
    seule et le modèle n'est pas enregistré dans l'admin Django. Un journal
    modifiable par ceux qu'il surveille n'est pas un journal.
    """

    class Action(models.TextChoices):
        SET_ROLE = 'SET_ROLE', 'Changement de rôle'
        SET_ACTIVE = 'SET_ACTIVE', 'Activation / désactivation'
        ANONYMIZE = 'ANONYMIZE', 'Anonymisation (RGPD)'
        ACCOUNT_DELETED = 'ACCOUNT_DELETED', 'Suppression de compte (self-service RGPD)'
        ASSIGN_COHORT = 'ASSIGN_COHORT', 'Rattachement à une classe'
        UNLOCK_CHAPTER = 'UNLOCK_CHAPTER', 'Déblocage de chapitre'
        LOCK_CHAPTER = 'LOCK_CHAPTER', 'Reverrouillage de chapitre'
        CREATE_COHORT = 'CREATE_COHORT', 'Création de classe'
        ASSIGN_TRAINER = 'ASSIGN_TRAINER', 'Affectation de formateur'
        INVITE_CREATED = 'INVITE_CREATED', 'Invitation émise'
        INVITE_REVOKED = 'INVITE_REVOKED', 'Invitation révoquée'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='audit_actions',
        help_text="Auteur de l'action. Nul si le compte a disparu depuis.",
    )
    actor_label = models.CharField(
        max_length=255,
        help_text="Identité de l'auteur au moment de l'action (figée).",
    )

    action = models.CharField(max_length=30, choices=Action.choices)

    target_id = models.UUIDField(
        null=True,
        blank=True,
        help_text="Identifiant de l'objet visé (compte, classe, chapitre).",
    )
    target_label = models.CharField(
        max_length=255,
        blank=True,
        help_text="Désignation de la cible au moment de l'action (figée). "
                  "Survit à une anonymisation, c'est tout son intérêt.",
    )

    changes = models.JSONField(
        default=dict,
        blank=True,
        help_text="Avant / après, au format {'before': …, 'after': …}.",
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'administration_audit_log'
        verbose_name = "Entrée de journal"
        verbose_name_plural = "Journal d'audit"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['-created_at'], name='idx_audit_created'),
            models.Index(fields=['action', '-created_at'], name='idx_audit_action'),
            models.Index(fields=['actor', '-created_at'], name='idx_audit_actor'),
        ]

    def __str__(self):
        return f'{self.get_action_display()} — {self.target_label or "?"}'

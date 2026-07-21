"""
Classes (cohortes) et liens d'invitation.

Modèle d'organisation : un formateur crée une classe, génère un lien, et le
diffuse par le canal de son choix (Teams, Discord, email…). L'application
n'envoie rien — elle produit une URL. Aucune dépendance SMTP.

Un apprenant appartient à **une seule classe** (`Profile.cohort`), ce qui garde
le déblocage de chapitre non ambigu : un seul formateur donne le tempo.
"""
import secrets
import uuid
from datetime import timedelta

from django.conf import settings
from django.db import models
from django.utils import timezone

INVITE_TOKEN_BYTES = 32
DEFAULT_INVITE_DAYS = 30


def generate_invite_token():
    """Jeton d'invitation : 256 bits d'entropie, sûr pour une URL."""
    return secrets.token_urlsafe(INVITE_TOKEN_BYTES)


def default_invite_expiry():
    return timezone.now() + timedelta(days=DEFAULT_INVITE_DAYS)


class Cohort(models.Model):
    """Une classe animée par un formateur."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)

    trainer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='cohorts',
        help_text="Formateur responsable. Une classe orpheline reste gérable par un admin."
    )

    is_active = models.BooleanField(
        default=True,
        help_text="Une classe archivée n'accepte plus de nouveaux membres."
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'cohorts_cohort'
        verbose_name = 'Classe'
        verbose_name_plural = 'Classes'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['trainer', 'is_active']),
        ]

    def __str__(self):
        return self.name

    @property
    def member_count(self):
        return self.members.count()


class CohortInvite(models.Model):
    """Lien d'invitation vers une classe (ou vers le rôle formateur).

    Le jeton est stocké **en clair**, contrairement à celui de la
    réinitialisation de mot de passe. C'est délibéré : le formateur doit
    pouvoir réafficher son lien pour le recopier, ce qu'un hachage
    interdirait. Le compromis est acceptable parce que le pouvoir du jeton est
    minuscule — il ne donne que « devenir apprenant dans cette classe », jamais
    de droits élevés — et parce qu'expiration et révocation sont obligatoires.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    token = models.CharField(
        max_length=64,
        unique=True,
        db_index=True,
        default=generate_invite_token,
    )

    cohort = models.ForeignKey(
        Cohort,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='invites',
        help_text="Vide pour une invitation de formateur (réservée aux admins)."
    )

    role = models.CharField(
        max_length=20,
        default='LEARNER',
        help_text="Rôle attribué à l'arrivée. TRAINER n'est émissible que par un admin."
    )

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_invites',
    )

    expires_at = models.DateTimeField(default=default_invite_expiry)
    max_uses = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Vide = illimité. Utile pour un lien nominatif."
    )
    uses_count = models.PositiveIntegerField(default=0)
    is_revoked = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'cohorts_invite'
        verbose_name = "Lien d'invitation"
        verbose_name_plural = "Liens d'invitation"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['cohort', 'is_revoked']),
        ]

    def __str__(self):
        target = self.cohort.name if self.cohort else f'rôle {self.role}'
        return f"Invitation → {target}"

    @property
    def is_expired(self):
        return timezone.now() >= self.expires_at

    @property
    def is_exhausted(self):
        return self.max_uses is not None and self.uses_count >= self.max_uses

    def invalid_reason(self):
        """Retourne la raison d'invalidité, ou None si le lien est utilisable.

        Utilisé côté formateur pour afficher l'état d'un lien. La vue publique,
        elle, ne renvoie jamais ce détail : un lien inutilisable est simplement
        « invalide », pour ne pas confirmer qu'il a existé.
        """
        if self.is_revoked:
            return 'revoked'
        if self.is_expired:
            return 'expired'
        if self.is_exhausted:
            return 'exhausted'
        if self.cohort and not self.cohort.is_active:
            return 'cohort_archived'
        return None

    @property
    def is_usable(self):
        return self.invalid_reason() is None

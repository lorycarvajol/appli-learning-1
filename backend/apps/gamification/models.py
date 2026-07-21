"""
Modèles de gamification : badges (dont objectifs secrets), grand livre des
points et série de jours consécutifs.

Principe directeur : **aucun achievement ne peut être validé deux fois**.
Cette garantie ne repose pas sur du code applicatif prudent mais sur deux
contraintes d'unicité en base :

- ``UserBadge (user, badge)``          → un badge est gagné au plus une fois
- ``PointTransaction (user, source_key)`` → une source ne crédite qu'une fois

Toute règle de badge est par ailleurs *monotone* : elle compare un compteur
cumulatif à un seuil. Réévaluer l'ensemble des badges est donc idempotent et
ne peut jamais faire régresser un apprenant.
"""
import uuid

from django.conf import settings
from django.db import models


class Badge(models.Model):
    """Définition d'un badge (objectif) attribuable aux apprenants."""

    class RuleType(models.TextChoices):
        LESSONS_COMPLETED = 'LESSONS_COMPLETED', 'Leçons complétées'
        CHAPTERS_COMPLETED = 'CHAPTERS_COMPLETED', 'Chapitres terminés'
        CHAPTER_MASTERED = 'CHAPTER_MASTERED', 'Chapitre précis terminé'
        EXERCISES_PASSED = 'EXERCISES_PASSED', 'Exercices réussis'
        QUIZZES_PASSED = 'QUIZZES_PASSED', 'Quiz réussis'
        PERFECT_QUIZZES = 'PERFECT_QUIZZES', 'Quiz sans faute (100%)'
        FIRST_TRY_QUIZZES = 'FIRST_TRY_QUIZZES', 'Quiz réussis du premier coup'
        PERSEVERANCE = 'PERSEVERANCE', 'Réussite après N tentatives'
        POINTS_TOTAL = 'POINTS_TOTAL', 'Total de points atteint'
        STREAK_DAYS = 'STREAK_DAYS', 'Jours consécutifs'
        TIME_SPENT = 'TIME_SPENT', "Temps d'apprentissage cumulé"
        FAST_LESSONS = 'FAST_LESSONS', 'Leçons bouclées rapidement'
        NIGHT_OWL = 'NIGHT_OWL', 'Activités nocturnes'
        EARLY_BIRD = 'EARLY_BIRD', 'Activités matinales'
        WEEKEND_LEARNER = 'WEEKEND_LEARNER', 'Activités le week-end'

    class Tier(models.TextChoices):
        BRONZE = 'BRONZE', 'Bronze'
        SILVER = 'SILVER', 'Argent'
        GOLD = 'GOLD', 'Or'
        LEGENDARY = 'LEGENDARY', 'Légendaire'

    class Category(models.TextChoices):
        PROGRESSION = 'PROGRESSION', 'Progression'
        MASTERY = 'MASTERY', 'Maîtrise'
        REGULARITY = 'REGULARITY', 'Régularité'
        EXPLORATION = 'EXPLORATION', 'Exploration'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    code = models.SlugField(
        max_length=60,
        unique=True,
        help_text="Identifiant stable utilisé par le code et le grand livre de points"
    )
    name = models.CharField(max_length=100)
    description = models.CharField(
        max_length=255,
        help_text="Texte révélé une fois le badge obtenu"
    )
    icon = models.CharField(max_length=8, default='🏅', help_text="Emoji du badge")

    category = models.CharField(
        max_length=20,
        choices=Category.choices,
        default=Category.PROGRESSION
    )
    tier = models.CharField(max_length=20, choices=Tier.choices, default=Tier.BRONZE)

    rule_type = models.CharField(max_length=30, choices=RuleType.choices)
    criteria = models.JSONField(
        default=dict,
        blank=True,
        help_text='Paramètres de la règle, ex: {"count": 5}'
    )

    points_reward = models.PositiveIntegerField(
        default=0,
        help_text="Points crédités une seule fois, à la première obtention"
    )

    is_secret = models.BooleanField(
        default=False,
        help_text="Masqué (nom, description, critère) tant qu'il n'est pas obtenu"
    )
    hint = models.CharField(
        max_length=255,
        blank=True,
        help_text="Énigme affichée à la place de la description quand le badge est secret"
    )

    is_active = models.BooleanField(default=True)
    order_index = models.PositiveIntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'gamification_badge'
        verbose_name = 'Badge'
        verbose_name_plural = 'Badges'
        ordering = ['order_index', 'name']
        indexes = [
            models.Index(fields=['is_active', 'order_index']),
            models.Index(fields=['category']),
        ]

    def __str__(self):
        return f"{self.icon} {self.name}"


class UserBadge(models.Model):
    """Badge effectivement obtenu par un apprenant.

    L'unicité ``(user, badge)`` est la garantie anti-double-validation : même
    si l'évaluation est déclenchée dix fois en parallèle, une seule ligne
    peut exister, donc une seule récompense est distribuée.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='badges'
    )
    badge = models.ForeignKey(Badge, on_delete=models.CASCADE, related_name='awards')

    earned_at = models.DateTimeField(auto_now_add=True)
    is_seen = models.BooleanField(
        default=False,
        help_text="Passe à True une fois l'animation de révélation affichée"
    )
    context = models.JSONField(
        default=dict,
        blank=True,
        help_text="Valeur du compteur au moment du déclenchement (traçabilité)"
    )

    class Meta:
        db_table = 'gamification_user_badge'
        verbose_name = 'Badge obtenu'
        verbose_name_plural = 'Badges obtenus'
        ordering = ['-earned_at']
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'badge'],
                name='unique_badge_per_user'
            ),
        ]
        indexes = [
            models.Index(fields=['user', '-earned_at']),
            models.Index(fields=['user', 'is_seen']),
        ]

    def __str__(self):
        return f"{self.user.email} → {self.badge.name}"


class PointTransaction(models.Model):
    """Grand livre des points : chaque crédit est tracé et idempotent.

    ``source_key`` identifie *ce qui* a généré les points (``lesson:<uuid>``,
    ``badge:<code>``…). L'unicité ``(user, source_key)`` empêche qu'une même
    source crédite deux fois, quelle que soit la route qui la déclenche.
    Le solde ``Profile.total_points`` est donc toujours reconstructible par
    simple somme de ce grand livre.
    """

    class Reason(models.TextChoices):
        LESSON_COMPLETED = 'LESSON_COMPLETED', 'Leçon terminée'
        QUIZ_PASSED = 'QUIZ_PASSED', 'Quiz réussi'
        EXERCISE_PASSED = 'EXERCISE_PASSED', 'Exercice réussi'
        BADGE_EARNED = 'BADGE_EARNED', 'Badge obtenu'
        LEGACY = 'LEGACY', 'Report de solde antérieur'
        MANUAL = 'MANUAL', 'Ajustement manuel'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='point_transactions'
    )
    amount = models.IntegerField(help_text="Peut être négatif pour un ajustement")
    reason = models.CharField(max_length=30, choices=Reason.choices)
    source_key = models.CharField(
        max_length=120,
        help_text="Clé d'idempotence, ex: lesson:<uuid> ou badge:<code>"
    )
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'gamification_point_transaction'
        verbose_name = 'Transaction de points'
        verbose_name_plural = 'Transactions de points'
        ordering = ['-created_at']
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'source_key'],
                name='unique_point_source_per_user'
            ),
        ]
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['reason']),
        ]

    def __str__(self):
        return f"{self.user.email} {self.amount:+d} pts ({self.source_key})"


class UserStreak(models.Model):
    """Série de jours consécutifs avec au moins une activité.

    Mise à jour idempotente : plusieurs activités le même jour ne comptent
    qu'une fois, et ``longest_streak`` ne décroît jamais.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='streak'
    )
    current_streak = models.PositiveIntegerField(default=0)
    longest_streak = models.PositiveIntegerField(default=0)
    last_activity_date = models.DateField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'gamification_user_streak'
        verbose_name = 'Série'
        verbose_name_plural = 'Séries'

    def __str__(self):
        return f"{self.user.email} - {self.current_streak} jour(s)"

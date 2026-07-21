import uuid
from django.db import models
from django.conf import settings
from apps.courses.models import Chapter, Lesson


class ChapterAccess(models.Model):
    """Contrôle d'accès aux chapitres - Débloqué par le trainer"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='chapter_accesses'
    )
    chapter = models.ForeignKey(
        Chapter,
        on_delete=models.CASCADE,
        related_name='user_accesses'
    )
    is_unlocked = models.BooleanField(default=False)
    unlocked_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='unlocked_chapters',
        help_text="Trainer qui a débloqué ce chapitre"
    )
    unlocked_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'progression_chapter_access'
        unique_together = ('user', 'chapter')
        verbose_name = 'Chapter Access'
        verbose_name_plural = 'Chapter Accesses'
        ordering = ['chapter__order_index']
        indexes = [
            models.Index(fields=['user', 'is_unlocked']),
            models.Index(fields=['chapter']),
        ]

    def __str__(self):
        status = "Unlocked" if self.is_unlocked else "Locked"
        return f"{self.user.email} - {self.chapter.title} ({status})"


class UserProgress(models.Model):
    """Progression de l'utilisateur sur une leçon"""

    class ProgressStatus(models.TextChoices):
        NOT_STARTED = 'NOT_STARTED', 'Not Started'
        IN_PROGRESS = 'IN_PROGRESS', 'In Progress'
        COMPLETED = 'COMPLETED', 'Completed'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='lesson_progress'
    )
    lesson = models.ForeignKey(
        Lesson,
        on_delete=models.CASCADE,
        related_name='user_progress'
    )
    status = models.CharField(
        max_length=20,
        choices=ProgressStatus.choices,
        default=ProgressStatus.NOT_STARTED
    )

    # Pour les exercices
    last_code = models.TextField(blank=True, default='')
    attempts = models.IntegerField(default=0)
    is_passed = models.BooleanField(default=False)
    score = models.IntegerField(null=True, blank=True, help_text="Score sur 100")

    # Pour les quiz : réponses sauvegardées au fur et à mesure ({question_id: [indices]})
    quiz_answers = models.JSONField(default=dict, blank=True)

    # Empêche l'attribution des points de la leçon plus d'une fois
    points_awarded = models.BooleanField(default=False)

    # Temps passé en secondes
    time_spent = models.IntegerField(default=0, help_text="Time spent in seconds")

    completed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'progression_user_progress'
        unique_together = ('user', 'lesson')
        verbose_name = 'User Progress'
        verbose_name_plural = 'User Progress'
        ordering = ['-updated_at']
        indexes = [
            models.Index(fields=['user', 'status']),
            models.Index(fields=['lesson']),
            models.Index(fields=['-updated_at']),
        ]

    def __str__(self):
        return f"{self.user.email} - {self.lesson.title} ({self.status})"


class ActivityLog(models.Model):
    """Historique des activités des utilisateurs"""

    class ActivityType(models.TextChoices):
        LESSON_STARTED = 'LESSON_STARTED', 'Lesson Started'
        LESSON_COMPLETED = 'LESSON_COMPLETED', 'Lesson Completed'
        EXERCISE_SUBMITTED = 'EXERCISE_SUBMITTED', 'Exercise Submitted'
        QUIZ_COMPLETED = 'QUIZ_COMPLETED', 'Quiz Completed'
        CHAPTER_UNLOCKED = 'CHAPTER_UNLOCKED', 'Chapter Unlocked'
        BADGE_EARNED = 'BADGE_EARNED', 'Badge Earned'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='activities'
    )
    activity_type = models.CharField(
        max_length=30,
        choices=ActivityType.choices
    )
    lesson = models.ForeignKey(
        Lesson,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='activities'
    )
    chapter = models.ForeignKey(
        Chapter,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='activities'
    )
    metadata = models.JSONField(
        default=dict,
        blank=True,
        help_text="Additional data (score, time, etc.)"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'progression_activity_log'
        verbose_name = 'Activity Log'
        verbose_name_plural = 'Activity Logs'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['activity_type']),
            models.Index(fields=['-created_at']),
        ]

    def __str__(self):
        return f"{self.user.email} - {self.activity_type} at {self.created_at}"

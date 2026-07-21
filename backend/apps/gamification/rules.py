"""
Moteur de règles des badges.

Toutes les règles sont **monotones** : elles comparent un compteur cumulatif
calculé depuis l'état actuel de la base à un seuil. Conséquences directes :

- réévaluer tous les badges à tout moment donne le même résultat (idempotence)
- un badge déjà obtenu ne peut jamais « se dévalider » puis se revalider
- aucune règle ne dépend d'un événement ponctuel qu'on pourrait rejouer

Chaque règle expose aussi une *progression* (valeur courante / cible), ce qui
permet d'afficher des barres d'avancement sur les objectifs visibles.
"""
from dataclasses import dataclass, field

from django.db.models import Count, Q
from django.db.models.functions import ExtractHour, ExtractIsoWeekDay

from apps.accounts.models import Profile
from apps.courses.models import Chapter
from apps.progression.models import ActivityLog, UserProgress

from .models import Badge, UserStreak


@dataclass
class UserStats:
    """Photographie des compteurs d'un apprenant, calculée en quelques requêtes."""
    lessons_completed: int = 0
    exercises_passed: int = 0
    quizzes_passed: int = 0
    perfect_quizzes: int = 0
    first_try_quizzes: int = 0
    chapters_completed: int = 0
    completed_chapter_slugs: set = field(default_factory=set)
    total_points: int = 0
    current_streak: int = 0
    longest_streak: int = 0
    total_time_spent: int = 0  # secondes
    best_attempts_on_success: int = 0
    night_activities: int = 0
    early_activities: int = 0
    weekend_activities: int = 0
    completed_durations: list = field(default_factory=list)  # secondes, > 0 seulement


def build_user_stats(user):
    """Calcule tous les compteurs d'un apprenant à partir de l'état en base."""
    stats = UserStats()

    progress_qs = UserProgress.objects.filter(user=user).select_related('lesson')
    completed = [p for p in progress_qs if p.status == UserProgress.ProgressStatus.COMPLETED]

    stats.lessons_completed = len(completed)
    stats.total_time_spent = sum(p.time_spent or 0 for p in progress_qs)
    stats.completed_durations = [p.time_spent for p in completed if (p.time_spent or 0) > 0]

    for p in completed:
        lesson_type = p.lesson.lesson_type
        if lesson_type == 'EXERCISE':
            stats.exercises_passed += 1
        elif lesson_type == 'QUIZ':
            stats.quizzes_passed += 1
            if p.score == 100:
                stats.perfect_quizzes += 1
            if p.attempts == 1:
                stats.first_try_quizzes += 1

    stats.best_attempts_on_success = max(
        (p.attempts for p in progress_qs if p.is_passed),
        default=0
    )

    # Chapitres entièrement terminés : toutes les leçons publiées complétées.
    completed_lesson_ids = {p.lesson_id for p in completed}
    chapters = Chapter.objects.filter(is_published=True).prefetch_related('lessons')
    for chapter in chapters:
        lesson_ids = [l.id for l in chapter.lessons.all() if l.is_published]
        if lesson_ids and all(lid in completed_lesson_ids for lid in lesson_ids):
            stats.chapters_completed += 1
            stats.completed_chapter_slugs.add(chapter.slug)

    # Relecture en base plutôt que via ``user.profile`` / ``user.streak`` :
    # ces objets liés peuvent avoir été chargés avant un crédit de points ou
    # une mise à jour de série, et seraient donc périmés.
    stats.total_points = Profile.objects.filter(user=user).values_list(
        'total_points', flat=True
    ).first() or 0

    streak_values = UserStreak.objects.filter(user=user).values(
        'current_streak', 'longest_streak'
    ).first()
    if streak_values:
        stats.current_streak = streak_values['current_streak']
        stats.longest_streak = streak_values['longest_streak']

    # Horaires d'activité : une seule requête agrégée.
    time_buckets = ActivityLog.objects.filter(user=user).annotate(
        hour=ExtractHour('created_at'),
        weekday=ExtractIsoWeekDay('created_at'),
    ).aggregate(
        night=Count('id', filter=Q(hour__gte=22) | Q(hour__lt=5)),
        early=Count('id', filter=Q(hour__gte=5, hour__lt=8)),
        weekend=Count('id', filter=Q(weekday__gte=6)),
    )
    stats.night_activities = time_buckets['night'] or 0
    stats.early_activities = time_buckets['early'] or 0
    stats.weekend_activities = time_buckets['weekend'] or 0

    return stats


def _count_fast_lessons(stats, max_minutes):
    limit = max_minutes * 60
    return sum(1 for d in stats.completed_durations if d <= limit)


# Chaque règle renvoie (valeur_courante, cible). Le badge est acquis dès que
# valeur_courante >= cible. Retourner cible=0 signifie « règle inapplicable ».
RULES = {
    Badge.RuleType.LESSONS_COMPLETED:
        lambda s, c: (s.lessons_completed, c.get('count', 1)),
    Badge.RuleType.CHAPTERS_COMPLETED:
        lambda s, c: (s.chapters_completed, c.get('count', 1)),
    Badge.RuleType.CHAPTER_MASTERED:
        lambda s, c: (1 if c.get('chapter_slug') in s.completed_chapter_slugs else 0, 1),
    Badge.RuleType.EXERCISES_PASSED:
        lambda s, c: (s.exercises_passed, c.get('count', 1)),
    Badge.RuleType.QUIZZES_PASSED:
        lambda s, c: (s.quizzes_passed, c.get('count', 1)),
    Badge.RuleType.PERFECT_QUIZZES:
        lambda s, c: (s.perfect_quizzes, c.get('count', 1)),
    Badge.RuleType.FIRST_TRY_QUIZZES:
        lambda s, c: (s.first_try_quizzes, c.get('count', 1)),
    Badge.RuleType.PERSEVERANCE:
        lambda s, c: (s.best_attempts_on_success, c.get('attempts', 5)),
    Badge.RuleType.POINTS_TOTAL:
        lambda s, c: (s.total_points, c.get('points', 100)),
    Badge.RuleType.STREAK_DAYS:
        lambda s, c: (max(s.current_streak, s.longest_streak), c.get('days', 3)),
    Badge.RuleType.TIME_SPENT:
        lambda s, c: (s.total_time_spent // 60, c.get('minutes', 60)),
    Badge.RuleType.FAST_LESSONS:
        lambda s, c: (_count_fast_lessons(s, c.get('max_minutes', 10)), c.get('count', 1)),
    Badge.RuleType.NIGHT_OWL:
        lambda s, c: (s.night_activities, c.get('count', 1)),
    Badge.RuleType.EARLY_BIRD:
        lambda s, c: (s.early_activities, c.get('count', 1)),
    Badge.RuleType.WEEKEND_LEARNER:
        lambda s, c: (s.weekend_activities, c.get('count', 1)),
}


def evaluate_badge(badge, stats):
    """Retourne (est_acquis, valeur_courante, cible) pour un badge donné."""
    rule = RULES.get(badge.rule_type)
    if rule is None:
        return False, 0, 0

    criteria = badge.criteria if isinstance(badge.criteria, dict) else {}
    current, target = rule(stats, criteria)

    if not target:
        return False, current, 0

    return current >= target, min(current, target), target

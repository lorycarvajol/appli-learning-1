"""
Couche métier de la gamification.

Toutes les écritures passent par ici. Deux invariants sont tenus :

1. **Un crédit de points par source.** ``award_points`` s'appuie sur
   l'unicité ``(user, source_key)`` de PointTransaction : rejouer l'appel ne
   crée rien et ne modifie pas le solde.
2. **Un badge obtenu une seule fois.** ``sync_user_gamification`` s'appuie sur
   l'unicité ``(user, badge)`` de UserBadge. Comme les règles sont monotones
   (cf. ``rules.py``), la synchronisation peut être relancée à volonté.

Le solde ``Profile.total_points`` reste donc toujours égal à la somme du
grand livre — ``recompute_profile_points`` permet de le vérifier/réparer.
"""
import logging

from django.db import IntegrityError, transaction
from django.db.models import Sum
from django.utils import timezone

from apps.progression.models import ActivityLog

from .models import Badge, PointTransaction, UserBadge, UserStreak
from .rules import build_user_stats, evaluate_badge

logger = logging.getLogger(__name__)

POINTS_PER_LEVEL = 100


# ---------------------------------------------------------------------------
# Points
# ---------------------------------------------------------------------------

def award_points(user, amount, reason, source_key, metadata=None):
    """Crédite des points **une seule fois** pour une source donnée.

    Args:
        source_key: clé d'idempotence stable, ex. ``lesson:<uuid>``.

    Returns:
        (PointTransaction, created: bool) — ``created=False`` signifie que la
        source avait déjà été créditée : aucun point n'a été ajouté.
    """
    if not amount:
        return None, False

    try:
        with transaction.atomic():
            tx, created = PointTransaction.objects.get_or_create(
                user=user,
                source_key=source_key,
                defaults={
                    'amount': amount,
                    'reason': reason,
                    'metadata': metadata or {},
                },
            )
            if created:
                _apply_balance(user, amount)
            return tx, created
    except IntegrityError:
        # Course entre deux requêtes concurrentes : l'autre a gagné, tant
        # mieux — le crédit a bien eu lieu exactement une fois.
        return PointTransaction.objects.get(user=user, source_key=source_key), False


def _apply_balance(user, amount):
    """Applique un delta au profil, en verrouillant la ligne le temps du calcul."""
    from apps.accounts.models import Profile

    profile = Profile.objects.select_for_update().get(user=user)
    profile.total_points = max(0, profile.total_points + amount)
    profile.level = profile.calculate_level()
    profile.save(update_fields=['total_points', 'level', 'updated_at'])


def get_points(user):
    """Solde à jour, relu en base.

    Nécessaire après un ``award_points`` : celui-ci met à jour une instance
    fraîche de Profile, l'éventuel ``user.profile`` déjà chargé en mémoire
    est donc périmé.
    """
    from apps.accounts.models import Profile

    return Profile.objects.filter(user=user).values_list(
        'total_points', flat=True
    ).first() or 0


def recompute_profile_points(user):
    """Recale le solde du profil sur la somme du grand livre. Réparation."""
    from apps.accounts.models import Profile

    with transaction.atomic():
        total = PointTransaction.objects.filter(user=user).aggregate(
            total=Sum('amount')
        )['total'] or 0
        profile = Profile.objects.select_for_update().get(user=user)
        profile.total_points = max(0, total)
        profile.level = profile.calculate_level()
        profile.save(update_fields=['total_points', 'level', 'updated_at'])
        return profile.total_points


def level_progress(total_points):
    """Détaille l'avancement dans le niveau courant, pour l'affichage."""
    level = 1 + max(0, total_points) // POINTS_PER_LEVEL
    points_in_level = max(0, total_points) % POINTS_PER_LEVEL
    return {
        'level': level,
        'points_in_level': points_in_level,
        'points_for_next': POINTS_PER_LEVEL - points_in_level,
        'level_size': POINTS_PER_LEVEL,
        'percent': round(points_in_level / POINTS_PER_LEVEL * 100),
    }


# ---------------------------------------------------------------------------
# Série de jours consécutifs
# ---------------------------------------------------------------------------

def touch_streak(user, when=None):
    """Enregistre une activité du jour. Idempotent à l'échelle de la journée.

    Plusieurs appels le même jour laissent la série inchangée ; seul le
    passage à un nouveau jour la fait progresser (ou la réinitialise).
    """
    today = (when or timezone.now()).astimezone(timezone.get_current_timezone()).date()

    with transaction.atomic():
        streak, _ = UserStreak.objects.select_for_update().get_or_create(user=user)

        if streak.last_activity_date == today:
            return streak  # déjà comptabilisé aujourd'hui

        if streak.last_activity_date and (today - streak.last_activity_date).days == 1:
            streak.current_streak += 1
        else:
            streak.current_streak = 1

        streak.last_activity_date = today
        streak.longest_streak = max(streak.longest_streak, streak.current_streak)
        streak.save(update_fields=[
            'current_streak', 'longest_streak', 'last_activity_date', 'updated_at'
        ])
        return streak


# ---------------------------------------------------------------------------
# Badges
# ---------------------------------------------------------------------------

def sync_user_gamification(user, touch=True):
    """Met à jour la série puis évalue tous les badges actifs.

    Idempotent : relancer la fonction ne redistribue jamais un badge ni des
    points déjà acquis. Les badges obtenus lors d'un appel précédent sont
    simplement ignorés grâce à la contrainte d'unicité ``(user, badge)``.

    Returns:
        list[UserBadge] — uniquement les badges **nouvellement** débloqués.
    """
    if not user or not user.is_authenticated:
        return []

    if touch:
        touch_streak(user)

    stats = build_user_stats(user)
    earned_ids = set(
        UserBadge.objects.filter(user=user).values_list('badge_id', flat=True)
    )

    newly_earned = []
    candidates = Badge.objects.filter(is_active=True).exclude(id__in=earned_ids)

    for badge in candidates:
        unlocked, current, target = evaluate_badge(badge, stats)
        if not unlocked:
            continue

        user_badge = _grant_badge(user, badge, {'value': current, 'target': target})
        if user_badge is not None:
            newly_earned.append(user_badge)

    # Un badge peut récompenser des points, qui peuvent à leur tour débloquer
    # un badge POINTS_TOTAL. Une seconde passe suffit et reste bornée.
    if newly_earned and any(b.badge.points_reward for b in newly_earned):
        newly_earned.extend(sync_user_gamification(user, touch=False))

    return newly_earned


def _grant_badge(user, badge, context):
    """Attribue un badge. Renvoie None s'il était déjà acquis (aucun effet)."""
    try:
        with transaction.atomic():
            user_badge, created = UserBadge.objects.get_or_create(
                user=user,
                badge=badge,
                defaults={'context': context},
            )
            if not created:
                return None

            if badge.points_reward:
                award_points(
                    user,
                    badge.points_reward,
                    PointTransaction.Reason.BADGE_EARNED,
                    source_key=f'badge:{badge.code}',
                    metadata={'badge_name': badge.name},
                )

            ActivityLog.objects.create(
                user=user,
                activity_type=ActivityLog.ActivityType.BADGE_EARNED,
                metadata={
                    'badge_code': badge.code,
                    'badge_name': badge.name,
                    'points_reward': badge.points_reward,
                },
            )
            return user_badge
    except IntegrityError:
        # Attribution concurrente : l'autre transaction a déjà tout fait.
        return None


def award_lesson_points(user, lesson):
    """Crédite les points d'une leçon, au plus une fois dans la vie du compte.

    La clé d'idempotence est la leçon elle-même : peu importe que l'apprenant
    repasse le quiz, resoumette l'exercice ou reclique « terminé ».
    """
    reason = {
        'QUIZ': PointTransaction.Reason.QUIZ_PASSED,
        'EXERCISE': PointTransaction.Reason.EXERCISE_PASSED,
    }.get(lesson.lesson_type, PointTransaction.Reason.LESSON_COMPLETED)

    _, created = award_points(
        user,
        lesson.points,
        reason,
        source_key=f'lesson:{lesson.id}',
        metadata={'lesson_title': lesson.title},
    )
    return lesson.points if created else 0

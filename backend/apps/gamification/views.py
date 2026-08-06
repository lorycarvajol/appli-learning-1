"""
API de gamification.

- ``GET  /api/gamification/badges/``            catalogue (secrets masqués)
- ``GET  /api/gamification/badges/mine/``       badges obtenus
- ``POST /api/gamification/badges/mark_seen/``  accuse réception d'une révélation
- ``GET  /api/gamification/summary/``           tableau de bord gamifié
- ``POST /api/gamification/sync/``              resynchronise (auto-réparation)
- ``GET  /api/gamification/points/``            grand livre personnel
- ``GET  /api/gamification/leaderboard/``       classement (global ou classe)
"""
from django.utils import timezone
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .leaderboard import DEFAULT_LIMIT, build_leaderboard
from .models import Badge, PointTransaction, UserBadge, UserStreak
from .rules import build_user_stats, evaluate_badge
from .serializers import (
    BadgeSerializer,
    PointTransactionSerializer,
    UserBadgeSerializer,
    UserStreakSerializer,
)
from .services import level_progress, sync_user_gamification

MAX_NEXT_OBJECTIVES = 3


def _earned_map(user):
    return {
        ub.badge_id: ub
        for ub in UserBadge.objects.filter(user=user).select_related('badge')
    }


class BadgeViewSet(viewsets.ViewSet):
    """Catalogue des badges, du point de vue de l'utilisateur connecté."""
    permission_classes = [IsAuthenticated]

    def list(self, request):
        badges = list(Badge.objects.filter(is_active=True))
        earned = _earned_map(request.user)
        stats = build_user_stats(request.user)

        serializer = BadgeSerializer(
            badges,
            many=True,
            context={'earned': earned, 'stats': stats},
        )

        secret_badges = [b for b in badges if b.is_secret]
        return Response({
            'badges': serializer.data,
            'earned_count': len(earned),
            'total_count': len(badges),
            'secret_total': len(secret_badges),
            'secret_found': sum(1 for b in secret_badges if b.id in earned),
        })

    @action(detail=False, methods=['get'])
    def mine(self, request):
        """Badges obtenus, du plus récent au plus ancien."""
        user_badges = UserBadge.objects.filter(
            user=request.user
        ).select_related('badge')
        return Response(UserBadgeSerializer(user_badges, many=True).data)

    @action(detail=False, methods=['post'])
    def mark_seen(self, request):
        """Marque des badges comme « révélation déjà jouée ».

        Permet à l'animation de célébration de ne se déclencher qu'une fois,
        même si l'apprenant recharge la page juste après.
        """
        badge_ids = request.data.get('badge_ids')

        qs = UserBadge.objects.filter(user=request.user, is_seen=False)
        if isinstance(badge_ids, list) and badge_ids:
            qs = qs.filter(id__in=badge_ids)

        updated = qs.update(is_seen=True)
        return Response({'marked_seen': updated}, status=status.HTTP_200_OK)


class GamificationSummaryViewSet(viewsets.ViewSet):
    """Vue agrégée : points, niveau, série, prochains objectifs, révélations."""
    permission_classes = [IsAuthenticated]

    def list(self, request):
        return Response(build_summary(request.user))

    @action(detail=False, methods=['post'])
    def sync(self, request):
        """Resynchronise l'état gamifié de l'utilisateur connecté.

        Sans danger et sans effet de bord indésirable : l'opération est
        idempotente (cf. ``services.sync_user_gamification``). Sert de
        filet de sécurité si un déclencheur a été manqué.
        """
        new_badges = sync_user_gamification(request.user)
        summary = build_summary(request.user)
        summary['newly_earned'] = UserBadgeSerializer(new_badges, many=True).data
        return Response(summary)


class LeaderboardViewSet(viewsets.ViewSet):
    """Classement, en lecture seule.

    Deux portées : ``?scope=global`` (défaut) et ``?scope=cohort`` — sa
    classe. Le filtrage réel, la règle de rang et le masquage des noms vivent
    dans ``leaderboard.py`` ; la vue ne fait que lire les paramètres.
    """
    permission_classes = [IsAuthenticated]

    def list(self, request):
        try:
            limit = int(request.query_params.get('limit', DEFAULT_LIMIT))
        except (TypeError, ValueError):
            # Un `?limit=abc` est une faute de frappe, pas une erreur à
            # remonter : le classement s'affiche avec sa longueur habituelle.
            limit = DEFAULT_LIMIT

        return Response(build_leaderboard(
            request.user,
            scope=request.query_params.get('scope'),
            limit=limit,
        ))


class PointTransactionViewSet(viewsets.ReadOnlyModelViewSet):
    """Grand livre personnel : d'où vient chaque point."""
    serializer_class = PointTransactionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return PointTransaction.objects.filter(user=self.request.user)


def build_summary(user):
    """Construit la charge utile du tableau de bord gamifié."""
    stats = build_user_stats(user)
    earned = _earned_map(user)
    badges = list(Badge.objects.filter(is_active=True))

    # Prochains objectifs : uniquement les objectifs visibles non acquis, du
    # plus proche du but au plus lointain, pour rester encourageant.
    candidates = []
    for badge in badges:
        if badge.is_secret or badge.id in earned:
            continue
        unlocked, current, target = evaluate_badge(badge, stats)
        if unlocked or not target:
            continue
        candidates.append((current / target, badge, current, target))

    candidates.sort(key=lambda item: item[0], reverse=True)
    next_objectives = [
        {
            'code': badge.code,
            'name': badge.name,
            'description': badge.description,
            'icon': badge.icon,
            'tier': badge.tier,
            'points_reward': badge.points_reward,
            'progress': {
                'current': current,
                'target': target,
                'percent': round(current / target * 100),
            },
        }
        for _, badge, current, target in candidates[:MAX_NEXT_OBJECTIVES]
    ]

    streak, _ = UserStreak.objects.get_or_create(user=user)
    today = timezone.now().astimezone(timezone.get_current_timezone()).date()

    unseen = UserBadge.objects.filter(
        user=user, is_seen=False
    ).select_related('badge')

    secret_badges = [b for b in badges if b.is_secret]

    return {
        'points': stats.total_points,
        'level': level_progress(stats.total_points),
        'streak': {
            **UserStreakSerializer(streak).data,
            'active_today': streak.last_activity_date == today,
        },
        'badges': {
            'earned': len(earned),
            'total': len(badges),
            'secret_total': len(secret_badges),
            'secret_found': sum(1 for b in secret_badges if b.id in earned),
        },
        'counters': {
            'lessons_completed': stats.lessons_completed,
            'exercises_passed': stats.exercises_passed,
            'quizzes_passed': stats.quizzes_passed,
            'perfect_quizzes': stats.perfect_quizzes,
            'chapters_completed': stats.chapters_completed,
            'minutes_spent': stats.total_time_spent // 60,
        },
        'next_objectives': next_objectives,
        'unseen_badges': UserBadgeSerializer(unseen, many=True).data,
    }

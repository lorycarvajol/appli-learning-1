"""
Serializers de gamification.

Point clé : **le masquage des objectifs secrets se fait côté serveur**. Un
badge secret non obtenu ne sort jamais de l'API avec son nom, sa description
ni ses critères — impossible de les découvrir en inspectant les réponses
réseau. Seule une énigme (``hint``) est exposée.
"""
from rest_framework import serializers

from .models import Badge, PointTransaction, UserBadge, UserStreak

MASKED_NAME = 'Objectif secret'
MASKED_ICON = '❓'
DEFAULT_HINT = "Personne ne sait comment on le débloque… continuez à explorer !"


class BadgeSerializer(serializers.Serializer):
    """Sérialise un badge du point de vue d'un apprenant donné.

    Attend dans le contexte :
        earned: dict {badge_id: UserBadge}
        stats:  UserStats (optionnel, pour la progression)
    """

    def to_representation(self, badge):
        earned = self.context.get('earned', {})
        user_badge = earned.get(badge.id)
        is_earned = user_badge is not None

        payload = {
            'id': str(badge.id),
            'category': badge.category,
            'tier': badge.tier,
            'is_secret': badge.is_secret,
            'is_earned': is_earned,
            'earned_at': user_badge.earned_at if is_earned else None,
        }

        if badge.is_secret and not is_earned:
            # Rien d'identifiant ne fuit : ni code, ni règle, ni récompense.
            payload.update({
                'code': None,
                'name': MASKED_NAME,
                'description': badge.hint or DEFAULT_HINT,
                'icon': MASKED_ICON,
                'points_reward': None,
                'progress': None,
            })
            return payload

        payload.update({
            'code': badge.code,
            'name': badge.name,
            'description': badge.description,
            'icon': badge.icon,
            'points_reward': badge.points_reward,
            'progress': self._progress(badge, is_earned),
        })
        return payload

    def _progress(self, badge, is_earned):
        """Avancement (courant/cible) — seulement pour les objectifs visibles."""
        stats = self.context.get('stats')
        if stats is None:
            return None

        from .rules import evaluate_badge

        _, current, target = evaluate_badge(badge, stats)
        if not target:
            return None

        if is_earned:
            current = target

        return {
            'current': current,
            'target': target,
            'percent': round(current / target * 100),
        }


class UserBadgeSerializer(serializers.ModelSerializer):
    """Badge obtenu : toujours entièrement révélé, puisqu'il est acquis."""
    code = serializers.CharField(source='badge.code', read_only=True)
    name = serializers.CharField(source='badge.name', read_only=True)
    description = serializers.CharField(source='badge.description', read_only=True)
    icon = serializers.CharField(source='badge.icon', read_only=True)
    tier = serializers.CharField(source='badge.tier', read_only=True)
    category = serializers.CharField(source='badge.category', read_only=True)
    points_reward = serializers.IntegerField(source='badge.points_reward', read_only=True)
    was_secret = serializers.BooleanField(source='badge.is_secret', read_only=True)

    class Meta:
        model = UserBadge
        fields = [
            'id', 'code', 'name', 'description', 'icon', 'tier', 'category',
            'points_reward', 'was_secret', 'earned_at', 'is_seen', 'context',
        ]
        read_only_fields = fields


class PointTransactionSerializer(serializers.ModelSerializer):
    reason_label = serializers.CharField(source='get_reason_display', read_only=True)

    class Meta:
        model = PointTransaction
        fields = ['id', 'amount', 'reason', 'reason_label', 'metadata', 'created_at']
        read_only_fields = fields


class UserStreakSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserStreak
        fields = ['current_streak', 'longest_streak', 'last_activity_date']
        read_only_fields = fields

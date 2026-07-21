"""
Admin Django de la gamification.

Une seule table s'édite ici : `Badge`, le **catalogue** — c'est du contenu, au
même titre qu'un chapitre, et l'espace React ne le gère pas.

Tout le reste est **acquis** : badges obtenus, écritures de points, séries.
Ces tables portent l'invariant central de la gamification — `Profile.total_points`
égale toujours la somme des `PointTransaction`, et un badge ne se gagne qu'une
fois. Une écriture manuelle ferait décrocher le solde sans laisser de trace, et
plus rien n'expliquerait ensuite l'écart constaté par
`services.recompute_profile_points`.

Voies légitimes : `services.award_points`, `sync_user_gamification`, et les
commandes `seed_badges` / `sync_gamification`.
"""
from django.contrib import admin

from apps.administration.admin_readonly import ReadOnlyAdmin

from .models import Badge, PointTransaction, UserBadge, UserStreak


@admin.register(Badge)
class BadgeAdmin(admin.ModelAdmin):
    list_display = [
        'icon', 'name', 'code', 'category', 'tier',
        'rule_type', 'points_reward', 'is_secret', 'is_active', 'order_index',
    ]
    list_filter = ['category', 'tier', 'rule_type', 'is_secret', 'is_active']
    search_fields = ['code', 'name', 'description']
    ordering = ['order_index', 'name']
    fieldsets = (
        ('Identité', {
            'fields': ('code', 'name', 'icon', 'category', 'tier', 'order_index')
        }),
        ('Contenu', {
            'fields': ('description', 'hint'),
            'description': "« hint » n'est affiché qu'aux badges secrets non obtenus."
        }),
        ('Règle de déblocage', {
            'fields': ('rule_type', 'criteria', 'points_reward'),
            'description': "Les règles sont cumulatives : une fois le seuil atteint, "
                           "le badge est acquis définitivement et une seule fois."
        }),
        ('Visibilité', {'fields': ('is_secret', 'is_active')}),
    )


@admin.register(UserBadge)
class UserBadgeAdmin(ReadOnlyAdmin):
    list_display = ['user', 'badge', 'earned_at', 'is_seen']
    list_filter = ['badge', 'is_seen']
    search_fields = ['user__email', 'badge__name']


@admin.register(PointTransaction)
class PointTransactionAdmin(ReadOnlyAdmin):
    """Le grand livre. Il se lit, il ne se corrige pas."""

    list_display = ['user', 'amount', 'reason', 'source_key', 'created_at']
    list_filter = ['reason']
    search_fields = ['user__email', 'source_key']


@admin.register(UserStreak)
class UserStreakAdmin(ReadOnlyAdmin):
    list_display = ['user', 'current_streak', 'longest_streak', 'last_activity_date']
    search_fields = ['user__email']

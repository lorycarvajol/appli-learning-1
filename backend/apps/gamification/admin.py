from django.contrib import admin

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
class UserBadgeAdmin(admin.ModelAdmin):
    list_display = ['user', 'badge', 'earned_at', 'is_seen']
    list_filter = ['badge', 'is_seen']
    search_fields = ['user__email', 'badge__name']
    readonly_fields = ['earned_at', 'context']
    autocomplete_fields = ['badge']


@admin.register(PointTransaction)
class PointTransactionAdmin(admin.ModelAdmin):
    list_display = ['user', 'amount', 'reason', 'source_key', 'created_at']
    list_filter = ['reason']
    search_fields = ['user__email', 'source_key']
    readonly_fields = ['created_at']


@admin.register(UserStreak)
class UserStreakAdmin(admin.ModelAdmin):
    list_display = ['user', 'current_streak', 'longest_streak', 'last_activity_date']
    search_fields = ['user__email']
    readonly_fields = ['created_at', 'updated_at']

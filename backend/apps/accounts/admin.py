"""
Admin Django pour User et Profile — volontairement bridé.

Le pilotage des comptes appartient à l'espace React `/administration`, qui
seul applique les garde-fous métier et écrit le journal d'audit. Ce qui reste
ici est ce que React ne sait pas faire : créer un compte à la main et définir
un mot de passe.

Voir `apps/administration/admin_readonly.py` pour le raisonnement d'ensemble.
"""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from apps.administration.admin_readonly import ReadOnlyAdmin

from .models import Profile, User

#: Champs dont l'espace React est l'unique autorité. Les modifier ici
#: contournerait `services.set_role` / `set_active` : ni journal d'audit, ni
#: règle du « dernier administrateur actif », ni révocation des sessions.
PILOTED_BY_REACT = ['role', 'is_active', 'is_staff', 'is_superuser']


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Consultation, création et mot de passe. Le reste passe par React."""

    list_display = ['email', 'full_name', 'role', 'is_active', 'is_staff', 'date_joined']
    list_filter = ['role', 'is_active', 'is_staff', 'date_joined']
    search_fields = ['email', 'first_name', 'last_name']
    ordering = ['-date_joined']

    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Identité', {'fields': ('first_name', 'last_name')}),
        ('Rôle et accès', {
            'fields': ('role', 'is_active', 'is_staff', 'is_superuser'),
            'description': (
                "Pilotés depuis l'espace React « Administration », qui applique "
                "les garde-fous et journalise chaque changement. "
                "<code>is_staff</code> est de toute façon recalculé à "
                "l'enregistrement à partir du rôle."
            ),
        }),
        ('Permissions Django', {
            'fields': ('groups', 'user_permissions'),
            'classes': ('collapse',),
        }),
        ('Dates', {'fields': ('last_login', 'date_joined')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            # `role` reste saisissable **à la création** : il faut bien un
            # moyen d'amorcer un compte, et aucun état antérieur n'est écrasé.
            'fields': ('email', 'password1', 'password2', 'first_name',
                       'last_name', 'role'),
        }),
    )

    def get_readonly_fields(self, request, obj=None):
        if obj is None:  # formulaire de création
            return ['date_joined', 'last_login']
        return ['date_joined', 'last_login', *PILOTED_BY_REACT]

    def has_delete_permission(self, request, obj=None):
        """Supprimer détruit la progression en cascade.

        Le droit à l'effacement passe par l'anonymisation (React), qui vide
        l'identité mais conserve les agrégats : effacer en cascade fausserait
        rétroactivement les statistiques des classes.
        """
        return False


@admin.register(Profile)
class ProfileAdmin(ReadOnlyAdmin):
    """Lecture seule : `total_points` est un solde, pas une saisie.

    Le solde doit toujours égaler la somme des `PointTransaction`. Le
    corriger à la main le ferait décrocher du grand livre sans laisser de
    trace ; la voie légitime est `gamification.services.award_points`, et
    `recompute_profile_points` pour une reconstruction.
    """

    list_display = ['user_email', 'cohort', 'total_points', 'level', 'anonymized_at']
    list_filter = ['level', 'cohort', 'created_at']
    search_fields = ['user__email', 'user__first_name', 'user__last_name']

    @admin.display(description='Email', ordering='user__email')
    def user_email(self, profile):
        return profile.user.email

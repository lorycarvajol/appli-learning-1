"""
Admin Django de la progression — **observatoire, pas poste de commande.**

Ces trois tables sont des données dérivées : elles se construisent au fil du
parcours de l'apprenant. Les éditer à la main produirait un état que rien dans
l'application n'aurait pu créer, et fausserait au passage les badges qui s'y
adossent (temps passé, leçons complétées).

Les voies légitimes :

- ouvrir un chapitre → espace React, ou `progression.services.unlock_chapter_for`
- corriger une progression → l'apprenant refait la leçon
- consulter → ici, ou la fiche apprenant de l'espace formateur

Le déblocage passé par React est journalisé (`AuditLog`) ; le même geste fait
ici ne laissait aucune trace. Voir `apps/administration/admin_readonly.py`.
"""
from django.contrib import admin

from apps.administration.admin_readonly import ReadOnlyAdmin

from .models import ActivityLog, ChapterAccess, UserProgress


@admin.register(ChapterAccess)
class ChapterAccessAdmin(ReadOnlyAdmin):
    list_display = ['user', 'chapter', 'is_unlocked', 'unlocked_by', 'unlocked_at']
    list_filter = ['is_unlocked', 'created_at']
    search_fields = ['user__email', 'chapter__title']
    raw_id_fields = ['user', 'chapter', 'unlocked_by']


@admin.register(UserProgress)
class UserProgressAdmin(ReadOnlyAdmin):
    list_display = ['user', 'lesson', 'status', 'is_passed', 'score', 'attempts',
                    'time_spent', 'updated_at']
    list_filter = ['status', 'is_passed', 'created_at']
    search_fields = ['user__email', 'lesson__title']
    raw_id_fields = ['user', 'lesson']


@admin.register(ActivityLog)
class ActivityLogAdmin(ReadOnlyAdmin):
    """Journal d'activité : par nature, on n'y écrit pas à la main."""

    list_display = ['user', 'activity_type', 'lesson', 'chapter', 'created_at']
    list_filter = ['activity_type', 'created_at']
    search_fields = ['user__email', 'lesson__title', 'chapter__title']
    raw_id_fields = ['user', 'lesson', 'chapter']

from django.contrib import admin
from .models import ChapterAccess, UserProgress, ActivityLog


@admin.register(ChapterAccess)
class ChapterAccessAdmin(admin.ModelAdmin):
    """Admin minimal pour debug uniquement"""
    list_display = ['user', 'chapter', 'is_unlocked', 'unlocked_by', 'unlocked_at']
    list_filter = ['is_unlocked', 'created_at']
    search_fields = ['user__email', 'chapter__title']
    readonly_fields = ['created_at', 'updated_at']
    raw_id_fields = ['user', 'chapter', 'unlocked_by']


@admin.register(UserProgress)
class UserProgressAdmin(admin.ModelAdmin):
    """Admin minimal pour debug uniquement"""
    list_display = ['user', 'lesson', 'status', 'is_passed', 'score', 'attempts', 'updated_at']
    list_filter = ['status', 'is_passed', 'created_at']
    search_fields = ['user__email', 'lesson__title']
    readonly_fields = ['created_at', 'updated_at']
    raw_id_fields = ['user', 'lesson']


@admin.register(ActivityLog)
class ActivityLogAdmin(admin.ModelAdmin):
    """Admin minimal pour debug uniquement"""
    list_display = ['user', 'activity_type', 'lesson', 'chapter', 'created_at']
    list_filter = ['activity_type', 'created_at']
    search_fields = ['user__email', 'lesson__title', 'chapter__title']
    readonly_fields = ['created_at']
    raw_id_fields = ['user', 'lesson', 'chapter']

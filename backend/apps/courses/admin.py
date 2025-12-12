"""
Admin configuration for courses models.
"""
from django.contrib import admin
from django.utils.html import format_html
from .models import Chapter, Lesson, Exercise, Quiz, Project


@admin.register(Chapter)
class ChapterAdmin(admin.ModelAdmin):
    """Admin for Chapter model."""
    list_display = ['order_index', 'title', 'lesson_count', 'is_published', 'estimated_duration', 'created_at']
    list_filter = ['is_published', 'created_at']
    search_fields = ['title', 'description']
    prepopulated_fields = {'slug': ('title',)}
    ordering = ['order_index']

    fieldsets = (
        ('Content', {
            'fields': ('title', 'slug', 'description', 'estimated_duration')
        }),
        ('Organization', {
            'fields': ('order_index', 'is_published')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    readonly_fields = ['created_at', 'updated_at']


class ExerciseInline(admin.StackedInline):
    """Inline admin for Exercise."""
    model = Exercise
    extra = 0
    fields = ['instructions', 'starter_code', 'solution', 'difficulty', 'tests', 'hints', 'max_attempts', 'time_limit']


class QuizInline(admin.StackedInline):
    """Inline admin for Quiz."""
    model = Quiz
    extra = 0
    fields = ['instructions', 'questions', 'passing_score', 'time_limit', 'max_attempts', 'randomize_questions', 'randomize_options']


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    """Admin for Lesson model."""
    list_display = ['get_full_title', 'chapter', 'lesson_type', 'points', 'is_published', 'estimated_duration']
    list_filter = ['lesson_type', 'is_published', 'chapter']
    search_fields = ['title', 'content']
    prepopulated_fields = {'slug': ('title',)}
    ordering = ['chapter__order_index', 'order_index']

    fieldsets = (
        ('Basic Info', {
            'fields': ('chapter', 'title', 'slug', 'lesson_type', 'order_index')
        }),
        ('Content', {
            'fields': ('content', 'video_url')
        }),
        ('Settings', {
            'fields': ('estimated_duration', 'points', 'is_published')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    readonly_fields = ['created_at', 'updated_at']
    inlines = []

    def get_inline_instances(self, request, obj=None):
        """Dynamically show Exercise or Quiz inline based on lesson type."""
        inlines = []
        if obj:
            if obj.lesson_type == 'EXERCISE':
                inlines = [ExerciseInline(self.model, self.admin_site)]
            elif obj.lesson_type == 'QUIZ':
                inlines = [QuizInline(self.model, self.admin_site)]
        return inlines

    def get_full_title(self, obj):
        """Display full hierarchical title."""
        return f"{obj.chapter.order_index}.{obj.order_index} - {obj.title}"
    get_full_title.short_description = 'Title'
    get_full_title.admin_order_field = 'order_index'


@admin.register(Exercise)
class ExerciseAdmin(admin.ModelAdmin):
    """Admin for Exercise model."""
    list_display = ['lesson', 'difficulty', 'total_points', 'max_attempts', 'created_at']
    list_filter = ['difficulty', 'created_at']
    search_fields = ['lesson__title', 'instructions']

    fieldsets = (
        ('Lesson', {
            'fields': ('lesson',)
        }),
        ('Instructions', {
            'fields': ('instructions', 'difficulty')
        }),
        ('Code', {
            'fields': ('starter_code', 'solution')
        }),
        ('Tests & Validation', {
            'fields': ('tests', 'max_attempts', 'time_limit')
        }),
        ('Help', {
            'fields': ('hints',)
        }),
    )

    readonly_fields = ['created_at', 'updated_at']


@admin.register(Quiz)
class QuizAdmin(admin.ModelAdmin):
    """Admin for Quiz model."""
    list_display = ['lesson', 'question_count', 'total_points', 'passing_score', 'max_attempts', 'created_at']
    list_filter = ['created_at']
    search_fields = ['lesson__title', 'instructions']

    fieldsets = (
        ('Lesson', {
            'fields': ('lesson',)
        }),
        ('Instructions', {
            'fields': ('instructions',)
        }),
        ('Questions', {
            'fields': ('questions',)
        }),
        ('Settings', {
            'fields': ('passing_score', 'time_limit', 'max_attempts', 'randomize_questions', 'randomize_options')
        }),
    )

    readonly_fields = ['created_at', 'updated_at']


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    """Admin for Project model."""
    list_display = ['title', 'chapter', 'points', 'deadline_days', 'is_published', 'created_at']
    list_filter = ['is_published', 'chapter', 'created_at']
    search_fields = ['title', 'description']
    prepopulated_fields = {'slug': ('title',)}

    fieldsets = (
        ('Basic Info', {
            'fields': ('chapter', 'title', 'slug', 'description')
        }),
        ('Requirements', {
            'fields': ('requirements', 'starter_files', 'evaluation_criteria')
        }),
        ('Settings', {
            'fields': ('deadline_days', 'points', 'is_published')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    readonly_fields = ['created_at', 'updated_at']

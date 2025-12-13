from rest_framework import serializers
from .models import ChapterAccess, UserProgress, ActivityLog
from apps.accounts.serializers import UserSerializer


class ChapterAccessSerializer(serializers.ModelSerializer):
    """Serializer pour l'accès aux chapitres"""
    user_email = serializers.EmailField(source='user.email', read_only=True)
    chapter_title = serializers.CharField(source='chapter.title', read_only=True)
    chapter_slug = serializers.SlugField(source='chapter.slug', read_only=True)
    unlocked_by_email = serializers.EmailField(source='unlocked_by.email', read_only=True, allow_null=True)

    class Meta:
        model = ChapterAccess
        fields = [
            'id', 'user', 'user_email', 'chapter', 'chapter_title', 'chapter_slug',
            'is_unlocked', 'unlocked_by', 'unlocked_by_email', 'unlocked_at',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class UserProgressSerializer(serializers.ModelSerializer):
    """Serializer pour la progression utilisateur"""
    user_email = serializers.EmailField(source='user.email', read_only=True)
    lesson_title = serializers.CharField(source='lesson.title', read_only=True)
    lesson_slug = serializers.SlugField(source='lesson.slug', read_only=True)
    lesson_type = serializers.CharField(source='lesson.lesson_type', read_only=True)

    class Meta:
        model = UserProgress
        fields = [
            'id', 'user', 'user_email', 'lesson', 'lesson_title', 'lesson_slug', 'lesson_type',
            'status', 'last_code', 'attempts', 'is_passed', 'score', 'time_spent',
            'completed_at', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'user']


class UserProgressUpdateSerializer(serializers.ModelSerializer):
    """Serializer pour mettre à jour la progression"""
    class Meta:
        model = UserProgress
        fields = ['status', 'last_code', 'time_spent', 'score', 'is_passed']


class ActivityLogSerializer(serializers.ModelSerializer):
    """Serializer pour les logs d'activité"""
    user_email = serializers.EmailField(source='user.email', read_only=True)
    user_full_name = serializers.SerializerMethodField()
    lesson_title = serializers.CharField(source='lesson.title', read_only=True, allow_null=True)
    chapter_title = serializers.CharField(source='chapter.title', read_only=True, allow_null=True)

    class Meta:
        model = ActivityLog
        fields = [
            'id', 'user', 'user_email', 'user_full_name', 'activity_type',
            'lesson', 'lesson_title', 'chapter', 'chapter_title',
            'metadata', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']

    def get_user_full_name(self, obj):
        return f"{obj.user.first_name} {obj.user.last_name}".strip() or obj.user.email


class LearnerProgressSummarySerializer(serializers.Serializer):
    """Résumé de progression pour un apprenant (pour le dashboard trainer)"""
    user = UserSerializer(read_only=True)
    total_chapters = serializers.IntegerField()
    unlocked_chapters = serializers.IntegerField()
    total_lessons = serializers.IntegerField()
    completed_lessons = serializers.IntegerField()
    in_progress_lessons = serializers.IntegerField()
    total_time_spent = serializers.IntegerField()  # en secondes
    average_score = serializers.FloatField(allow_null=True)
    last_activity = serializers.DateTimeField(allow_null=True)
    current_lesson = serializers.CharField(allow_null=True)


class UnlockChapterSerializer(serializers.Serializer):
    """Serializer pour débloquer un chapitre pour un utilisateur"""
    user_id = serializers.UUIDField()
    chapter_id = serializers.UUIDField()

    def validate(self, data):
        from apps.accounts.models import User
        from apps.courses.models import Chapter

        # Vérifier que l'utilisateur existe
        try:
            user = User.objects.get(id=data['user_id'])
            if user.role != User.Role.LEARNER:
                raise serializers.ValidationError("Only learners can have chapters unlocked")
        except User.DoesNotExist:
            raise serializers.ValidationError("User not found")

        # Vérifier que le chapitre existe
        try:
            Chapter.objects.get(id=data['chapter_id'])
        except Chapter.DoesNotExist:
            raise serializers.ValidationError("Chapter not found")

        return data

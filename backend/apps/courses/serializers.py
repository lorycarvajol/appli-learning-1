"""
Serializers for courses models.
"""
from rest_framework import serializers
from .models import Chapter, Lesson, Exercise, Quiz, Project


class AccessibleChapterMixin:
    """Calcule `is_accessible` d'après les accès de l'utilisateur courant.

    Les chapitres verrouillés restent **listés** : masquer la suite du parcours
    priverait l'apprenant de la vue d'ensemble qui lui donne envie d'avancer.
    C'est l'ouverture des leçons qui est réellement bloquée, pas l'affichage
    du sommaire.

    Note : le champ lui-même doit être déclaré sur chaque serializer concret.
    La métaclasse de DRF ne collecte les champs que des bases qui sont
    elles-mêmes des Serializer — un mixin simple passerait inaperçu.
    """

    def get_is_accessible(self, chapter):
        accessible = self.context.get('accessible_chapter_ids')
        if accessible is None:
            return True
        return chapter.id in accessible


class ChapterListSerializer(AccessibleChapterMixin, serializers.ModelSerializer):
    """Serializer for listing chapters (without lessons)."""
    lesson_count = serializers.ReadOnlyField()
    is_accessible = serializers.SerializerMethodField()

    class Meta:
        model = Chapter
        fields = [
            'id', 'title', 'slug', 'description', 'order_index',
            'estimated_duration', 'is_published', 'lesson_count',
            'is_accessible', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class ExerciseSerializer(serializers.ModelSerializer):
    """Serializer for Exercise model."""
    total_points = serializers.ReadOnlyField()

    class Meta:
        model = Exercise
        fields = [
            'id', 'lesson', 'instructions', 'starter_code', 'solution', 'language',
            'tests', 'difficulty', 'max_attempts', 'time_limit', 'hints',
            'total_points', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
        extra_kwargs = {
            'solution': {'write_only': True},  # Hide solution from students
            'tests': {'write_only': True},  # Hide test details from students
        }


class ExerciseDetailSerializer(ExerciseSerializer):
    """Detailed serializer for Exercise (for trainers/admins)."""
    class Meta(ExerciseSerializer.Meta):
        extra_kwargs = {}  # Allow solution and tests to be read


class QuizSerializer(serializers.ModelSerializer):
    """Serializer for Quiz model."""
    total_points = serializers.ReadOnlyField()
    question_count = serializers.ReadOnlyField()

    class Meta:
        model = Quiz
        fields = [
            'id', 'lesson', 'instructions', 'questions', 'passing_score',
            'time_limit', 'max_attempts', 'randomize_questions', 'randomize_options',
            'total_points', 'question_count', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def to_representation(self, instance):
        """Expose les questions sous forme de **liste** normalisée, en masquant
        `correct_answer`/`explanation` aux apprenants.

        Deux corrections cohabitent ici :
        - **Normalisation** : le champ JSONB peut valoir `{'questions': [...]}`.
          Renvoyer ce dictionnaire brut ferait afficher « aucune question » côté
          front (`Array.isArray(quiz.questions)` est faux). On part donc de
          `instance.questions_list`, toujours une liste.
        - **Masquage** : sans cela, un apprenant lirait les bonnes réponses dans
          la réponse réseau avant même de répondre.
        """
        data = super().to_representation(instance)
        request = self.context.get('request')
        user = getattr(request, 'user', None)

        questions = instance.questions_list
        if not (user and getattr(user, 'role', None) in ('TRAINER', 'ADMIN')):
            questions = [
                {k: v for k, v in question.items() if k not in ('correct_answer', 'explanation')}
                for question in questions
            ]
        data['questions'] = questions
        return data


class LessonListSerializer(serializers.ModelSerializer):
    """Serializer for listing lessons (without full content)."""

    class Meta:
        model = Lesson
        fields = [
            'id', 'chapter', 'title', 'slug', 'lesson_type', 'order_index',
            'estimated_duration', 'points', 'is_published', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class LessonDetailSerializer(serializers.ModelSerializer):
    """Detailed serializer for lessons with nested exercise/quiz."""
    exercise = ExerciseSerializer(read_only=True)
    quiz = QuizSerializer(read_only=True)
    chapter_slug = serializers.CharField(source='chapter.slug', read_only=True)

    class Meta:
        model = Lesson
        fields = [
            'id', 'chapter', 'chapter_slug', 'title', 'slug', 'lesson_type', 'order_index',
            'content', 'video_url', 'estimated_duration', 'points',
            'is_published', 'exercise', 'quiz', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class ChapterDetailSerializer(AccessibleChapterMixin, serializers.ModelSerializer):
    """Detailed serializer for chapters with nested lessons."""
    lessons = LessonListSerializer(many=True, read_only=True)
    lesson_count = serializers.ReadOnlyField()
    is_accessible = serializers.SerializerMethodField()

    class Meta:
        model = Chapter
        fields = [
            'id', 'title', 'slug', 'description', 'order_index',
            'estimated_duration', 'is_published', 'lessons', 'lesson_count',
            'is_accessible', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class ProjectSerializer(serializers.ModelSerializer):
    """Serializer for Project model."""

    class Meta:
        model = Project
        fields = [
            'id', 'chapter', 'title', 'slug', 'description', 'requirements',
            'starter_files', 'evaluation_criteria', 'deadline_days', 'points',
            'is_published', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

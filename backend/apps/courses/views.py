"""
API views for courses.
"""
from rest_framework import generics, viewsets, filters, status
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend

from apps.progression.services import accessible_chapter_ids, can_access_lesson

from .models import Chapter, Lesson, Exercise, Quiz, Project
from .serializers import (
    ChapterListSerializer, ChapterDetailSerializer,
    LessonListSerializer, LessonDetailSerializer,
    ExerciseSerializer, ExerciseDetailSerializer,
    QuizSerializer, ProjectSerializer
)


class ChapterViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for listing and retrieving chapters.
    List: Returns all published chapters
    Retrieve: Returns a specific chapter with its lessons
    """
    queryset = Chapter.objects.filter(is_published=True).prefetch_related('lessons')
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    ordering_fields = ['order_index', 'created_at']
    ordering = ['order_index']
    lookup_field = 'slug'

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return ChapterDetailSerializer
        return ChapterListSerializer

    def get_serializer_context(self):
        """Calcule les accès une seule fois par requête plutôt qu'une requête
        SQL par chapitre sérialisé."""
        context = super().get_serializer_context()
        user = self.request.user
        if user and user.is_authenticated:
            context['accessible_chapter_ids'] = accessible_chapter_ids(user)
        return context


class LessonViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for listing and retrieving lessons.
    """
    queryset = Lesson.objects.filter(
        is_published=True,
        chapter__is_published=True
    ).select_related('chapter').prefetch_related('exercise', 'quiz')
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['chapter', 'lesson_type']
    ordering_fields = ['order_index', 'created_at']
    ordering = ['chapter__order_index', 'order_index']
    lookup_field = 'slug'

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return LessonDetailSerializer
        return LessonListSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        chapter_slug = self.request.query_params.get('chapter_slug', None)
        if chapter_slug:
            queryset = queryset.filter(chapter__slug=chapter_slug)
        return queryset

    def retrieve(self, request, *args, **kwargs):
        """Le verrou réel : le contenu d'une leçon d'un chapitre non débloqué
        n'est pas servi. Lister les chapitres reste permis (le sommaire donne
        la vue d'ensemble), mais les ouvrir demande l'accès."""
        lesson = self.get_object()
        if not can_access_lesson(request.user, lesson):
            return Response(
                {
                    'detail': "Ce chapitre n'est pas encore débloqué.",
                    'chapter_slug': lesson.chapter.slug,
                },
                status=status.HTTP_403_FORBIDDEN
            )
        return Response(self.get_serializer(lesson).data)


class ExerciseViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for retrieving exercises.
    Only authenticated users can access exercises.
    """
    queryset = Exercise.objects.select_related('lesson', 'lesson__chapter')
    permission_classes = [IsAuthenticated]
    lookup_field = 'id'

    def get_serializer_class(self):
        # Trainers and admins can see solutions and tests
        if self.request.user.role in ['TRAINER', 'ADMIN']:
            return ExerciseDetailSerializer
        return ExerciseSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        # Filter to only published exercises
        queryset = queryset.filter(
            lesson__is_published=True,
            lesson__chapter__is_published=True
        )
        return queryset


class QuizViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for retrieving quizzes.
    Only authenticated users can access quizzes.
    """
    queryset = Quiz.objects.select_related('lesson', 'lesson__chapter')
    permission_classes = [IsAuthenticated]
    serializer_class = QuizSerializer
    lookup_field = 'id'

    def get_queryset(self):
        queryset = super().get_queryset()
        # Filter to only published quizzes
        queryset = queryset.filter(
            lesson__is_published=True,
            lesson__chapter__is_published=True
        )
        return queryset


class ProjectViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for listing and retrieving projects.
    """
    queryset = Project.objects.filter(
        is_published=True,
        chapter__is_published=True
    ).select_related('chapter')
    permission_classes = [IsAuthenticated]
    serializer_class = ProjectSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['chapter']
    ordering_fields = ['created_at']
    ordering = ['chapter__order_index']
    lookup_field = 'slug'

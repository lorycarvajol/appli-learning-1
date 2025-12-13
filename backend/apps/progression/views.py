from django.utils import timezone
from django.db.models import Count, Avg, Sum, Max, Q
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import ChapterAccess, UserProgress, ActivityLog
from .serializers import (
    ChapterAccessSerializer,
    UserProgressSerializer,
    UserProgressUpdateSerializer,
    ActivityLogSerializer,
    LearnerProgressSummarySerializer,
    UnlockChapterSerializer
)
from apps.accounts.models import User
from apps.courses.models import Chapter, Lesson


class IsTrainerOrAdmin(IsAuthenticated):
    """Permission: seuls les trainers et admins peuvent accéder"""
    def has_permission(self, request, view):
        if not super().has_permission(request, view):
            return False
        return request.user.role in ['TRAINER', 'ADMIN']


class ChapterAccessViewSet(viewsets.ModelViewSet):
    """ViewSet pour gérer les accès aux chapitres"""
    queryset = ChapterAccess.objects.select_related('user', 'chapter', 'unlocked_by')
    serializer_class = ChapterAccessSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        qs = super().get_queryset()

        # Les apprenants ne voient que leurs propres accès
        if user.role == 'LEARNER':
            return qs.filter(user=user)

        # Les trainers/admins voient tout
        return qs

    @action(detail=False, methods=['post'], permission_classes=[IsTrainerOrAdmin])
    def unlock_chapter(self, request):
        """Débloquer un chapitre pour un apprenant"""
        serializer = UnlockChapterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user_id = serializer.validated_data['user_id']
        chapter_id = serializer.validated_data['chapter_id']

        # Créer ou mettre à jour l'accès
        chapter_access, created = ChapterAccess.objects.get_or_create(
            user_id=user_id,
            chapter_id=chapter_id,
            defaults={
                'is_unlocked': True,
                'unlocked_by': request.user,
                'unlocked_at': timezone.now()
            }
        )

        if not created and not chapter_access.is_unlocked:
            chapter_access.is_unlocked = True
            chapter_access.unlocked_by = request.user
            chapter_access.unlocked_at = timezone.now()
            chapter_access.save()

        # Logger l'activité
        ActivityLog.objects.create(
            user_id=user_id,
            activity_type=ActivityLog.ActivityType.CHAPTER_UNLOCKED,
            chapter_id=chapter_id,
            metadata={'unlocked_by': str(request.user.id)}
        )

        return Response(
            ChapterAccessSerializer(chapter_access).data,
            status=status.HTTP_200_OK
        )

    @action(detail=False, methods=['post'], permission_classes=[IsTrainerOrAdmin])
    def lock_chapter(self, request):
        """Verrouiller un chapitre pour un apprenant"""
        serializer = UnlockChapterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user_id = serializer.validated_data['user_id']
        chapter_id = serializer.validated_data['chapter_id']

        try:
            chapter_access = ChapterAccess.objects.get(
                user_id=user_id,
                chapter_id=chapter_id
            )
            chapter_access.is_unlocked = False
            chapter_access.save()

            return Response(
                ChapterAccessSerializer(chapter_access).data,
                status=status.HTTP_200_OK
            )
        except ChapterAccess.DoesNotExist:
            return Response(
                {"error": "Chapter access not found"},
                status=status.HTTP_404_NOT_FOUND
            )

    @action(detail=False, methods=['get'])
    def my_access(self, request):
        """Obtenir les accès de l'utilisateur courant"""
        accesses = ChapterAccess.objects.filter(user=request.user).select_related('chapter')
        serializer = self.get_serializer(accesses, many=True)
        return Response(serializer.data)


class UserProgressViewSet(viewsets.ModelViewSet):
    """ViewSet pour gérer la progression des utilisateurs"""
    queryset = UserProgress.objects.select_related('user', 'lesson', 'lesson__chapter')
    serializer_class = UserProgressSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        qs = super().get_queryset()

        # Les apprenants ne voient que leur propre progression
        if user.role == 'LEARNER':
            return qs.filter(user=user)

        # Les trainers/admins peuvent filtrer par utilisateur
        user_id = self.request.query_params.get('user_id')
        if user_id:
            qs = qs.filter(user_id=user_id)

        return qs

    def get_serializer_class(self):
        if self.action in ['update', 'partial_update']:
            return UserProgressUpdateSerializer
        return UserProgressSerializer

    @action(detail=False, methods=['post'])
    def mark_completed(self, request):
        """Marquer une leçon comme complétée"""
        lesson_id = request.data.get('lesson_id')
        if not lesson_id:
            return Response(
                {"error": "lesson_id is required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            lesson = Lesson.objects.get(id=lesson_id)
        except Lesson.DoesNotExist:
            return Response(
                {"error": "Lesson not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        # Mettre à jour ou créer la progression
        progress, created = UserProgress.objects.get_or_create(
            user=request.user,
            lesson=lesson,
            defaults={
                'status': UserProgress.ProgressStatus.COMPLETED,
                'completed_at': timezone.now()
            }
        )

        if not created and progress.status != UserProgress.ProgressStatus.COMPLETED:
            progress.status = UserProgress.ProgressStatus.COMPLETED
            progress.completed_at = timezone.now()
            progress.save()

        # Logger l'activité
        ActivityLog.objects.create(
            user=request.user,
            activity_type=ActivityLog.ActivityType.LESSON_COMPLETED,
            lesson=lesson,
            chapter=lesson.chapter,
            metadata={'time_spent': progress.time_spent}
        )

        return Response(
            UserProgressSerializer(progress).data,
            status=status.HTTP_200_OK
        )

    @action(detail=False, methods=['get'])
    def my_progress(self, request):
        """Obtenir la progression de l'utilisateur courant"""
        progress = UserProgress.objects.filter(user=request.user).select_related('lesson', 'lesson__chapter')
        serializer = self.get_serializer(progress, many=True)
        return Response(serializer.data)


class ActivityLogViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet pour les logs d'activité (lecture seule)"""
    queryset = ActivityLog.objects.select_related('user', 'lesson', 'chapter')
    serializer_class = ActivityLogSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        qs = super().get_queryset()

        # Les apprenants ne voient que leurs propres activités
        if user.role == 'LEARNER':
            return qs.filter(user=user)

        # Les trainers/admins peuvent filtrer
        user_id = self.request.query_params.get('user_id')
        if user_id:
            qs = qs.filter(user_id=user_id)

        activity_type = self.request.query_params.get('activity_type')
        if activity_type:
            qs = qs.filter(activity_type=activity_type)

        return qs


class TrainerDashboardViewSet(viewsets.ViewSet):
    """ViewSet pour le dashboard trainer/admin"""
    permission_classes = [IsTrainerOrAdmin]

    @action(detail=False, methods=['get'])
    def learners_summary(self, request):
        """Obtenir le résumé de progression de tous les apprenants"""
        learners = User.objects.filter(role='LEARNER')
        total_chapters = Chapter.objects.filter(is_published=True).count()
        total_lessons = Lesson.objects.filter(chapter__is_published=True).count()

        summaries = []
        for learner in learners:
            # Compter les chapitres débloqués
            unlocked_chapters = ChapterAccess.objects.filter(
                user=learner,
                is_unlocked=True
            ).count()

            # Compter les leçons complétées et en cours
            progress_stats = UserProgress.objects.filter(user=learner).aggregate(
                completed=Count('id', filter=Q(status=UserProgress.ProgressStatus.COMPLETED)),
                in_progress=Count('id', filter=Q(status=UserProgress.ProgressStatus.IN_PROGRESS)),
                total_time=Sum('time_spent'),
                avg_score=Avg('score', filter=Q(score__isnull=False))
            )

            # Dernière activité
            last_activity = ActivityLog.objects.filter(user=learner).order_by('-created_at').first()

            # Leçon en cours
            current_progress = UserProgress.objects.filter(
                user=learner,
                status=UserProgress.ProgressStatus.IN_PROGRESS
            ).select_related('lesson').first()

            summaries.append({
                'user': learner,
                'total_chapters': total_chapters,
                'unlocked_chapters': unlocked_chapters,
                'total_lessons': total_lessons,
                'completed_lessons': progress_stats['completed'] or 0,
                'in_progress_lessons': progress_stats['in_progress'] or 0,
                'total_time_spent': progress_stats['total_time'] or 0,
                'average_score': progress_stats['avg_score'],
                'last_activity': last_activity.created_at if last_activity else None,
                'current_lesson': current_progress.lesson.title if current_progress else None
            })

        serializer = LearnerProgressSummarySerializer(summaries, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def recent_activity(self, request):
        """Obtenir l'activité récente de tous les apprenants"""
        limit = int(request.query_params.get('limit', 50))
        activities = ActivityLog.objects.select_related(
            'user', 'lesson', 'chapter'
        ).order_by('-created_at')[:limit]

        serializer = ActivityLogSerializer(activities, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def learner_detail(self, request, pk=None):
        """Obtenir les détails de progression d'un apprenant spécifique"""
        try:
            learner = User.objects.get(id=pk, role='LEARNER')
        except User.DoesNotExist:
            return Response(
                {"error": "Learner not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        # Progression par chapitre
        chapters = Chapter.objects.filter(is_published=True).prefetch_related('lessons')
        chapter_progress = []

        for chapter in chapters:
            # Vérifier l'accès
            try:
                access = ChapterAccess.objects.get(user=learner, chapter=chapter)
                is_unlocked = access.is_unlocked
            except ChapterAccess.DoesNotExist:
                is_unlocked = False

            # Progression des leçons du chapitre
            lesson_ids = chapter.lessons.values_list('id', flat=True)
            progress_stats = UserProgress.objects.filter(
                user=learner,
                lesson_id__in=lesson_ids
            ).aggregate(
                total=Count('id'),
                completed=Count('id', filter=Q(status=UserProgress.ProgressStatus.COMPLETED))
            )

            chapter_progress.append({
                'chapter_id': str(chapter.id),
                'chapter_title': chapter.title,
                'chapter_slug': chapter.slug,
                'is_unlocked': is_unlocked,
                'total_lessons': chapter.lessons.count(),
                'completed_lessons': progress_stats['completed'] or 0,
                'completion_rate': (
                    (progress_stats['completed'] or 0) / chapter.lessons.count() * 100
                    if chapter.lessons.count() > 0 else 0
                )
            })

        # Activités récentes
        recent_activities = ActivityLog.objects.filter(user=learner).order_by('-created_at')[:20]

        return Response({
            'learner': {
                'id': str(learner.id),
                'email': learner.email,
                'first_name': learner.first_name,
                'last_name': learner.last_name,
                'profile': {
                    'points': learner.profile.total_points,
                    'level': learner.profile.level
                }
            },
            'chapter_progress': chapter_progress,
            'recent_activities': ActivityLogSerializer(recent_activities, many=True).data
        })

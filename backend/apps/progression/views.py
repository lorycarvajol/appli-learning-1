from django.utils import timezone
from django.db.models import Count, Avg, F, Sum, Max, Q
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
from apps.courses.models import Chapter, Lesson, Quiz
from apps.gamification.serializers import UserBadgeSerializer
from apps.gamification.services import (
    award_lesson_points,
    get_points,
    sync_user_gamification,
    touch_streak,
)

# Plafond d'un incrément de temps unique. Le client émet toutes les 30 s ;
# cette marge absorbe un flush tardif sans laisser passer d'écart aberrant.
MAX_TIME_INCREMENT_SECONDS = 120


def _grade_quiz(quiz, answers):
    """Note un quiz côté serveur à partir des réponses de l'utilisateur.

    Returns (score: int 0-100, passed: bool, details: list[dict]).
    Les bonnes réponses ne viennent jamais du client : uniquement de
    quiz.questions, jamais exposé tel quel via l'API pour les apprenants.
    """
    questions = quiz.questions if isinstance(quiz.questions, list) else quiz.questions.get('questions', [])
    if not questions:
        return 0, False, []

    correct_count = 0
    details = []

    for question in questions:
        qid = question.get('id')
        correct_answer = question.get('correct_answer')
        user_answer = answers.get(str(qid), answers.get(qid, []))
        if not isinstance(user_answer, list):
            user_answer = [user_answer] if user_answer is not None else []

        if isinstance(correct_answer, list):
            is_correct = (
                sorted(map(str, user_answer)) == sorted(map(str, correct_answer))
            )
        else:
            is_correct = len(user_answer) == 1 and str(user_answer[0]) == str(correct_answer)

        if is_correct:
            correct_count += 1

        details.append({
            'question_id': qid,
            'is_correct': is_correct,
            'user_answer': user_answer,
            'correct_answer': correct_answer,
            'explanation': question.get('explanation', ''),
        })

    score = round((correct_count / len(questions)) * 100)
    passed = score >= quiz.passing_score
    return score, passed, details


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

        was_already_completed = (
            not created and progress.status == UserProgress.ProgressStatus.COMPLETED
        )

        if not created and not was_already_completed:
            progress.status = UserProgress.ProgressStatus.COMPLETED
            progress.completed_at = timezone.now()
            progress.save()

        # Les points de la leçon ne sont crédités qu'une fois dans la vie du
        # compte : la clé d'idempotence est la leçon (cf. award_lesson_points).
        points_earned = award_lesson_points(request.user, lesson)
        if points_earned and not progress.points_awarded:
            progress.points_awarded = True
            progress.save(update_fields=['points_awarded', 'updated_at'])

        # Ne pas polluer l'historique avec un log par reclic sur « terminé ».
        if not was_already_completed:
            ActivityLog.objects.create(
                user=request.user,
                activity_type=ActivityLog.ActivityType.LESSON_COMPLETED,
                lesson=lesson,
                chapter=lesson.chapter,
                metadata={'time_spent': progress.time_spent}
            )

        new_badges = sync_user_gamification(request.user)

        return Response(
            {
                **UserProgressSerializer(progress).data,
                'points_earned': points_earned,
                'total_points': get_points(request.user),
                'new_badges': UserBadgeSerializer(new_badges, many=True).data,
            },
            status=status.HTTP_200_OK
        )

    @action(detail=False, methods=['get'])
    def next_lesson(self, request):
        """Leçon à afficher dans le bloc « Continuer l'apprentissage ».

        Priorité à la leçon **entamée la plus récemment** : c'est le sens de
        « continuer ». À défaut, la première leçon non terminée dans l'ordre
        du programme. Si tout est terminé, on le signale au client plutôt que
        de renvoyer une leçon déjà faite.
        """
        lessons = list(
            Lesson.objects.filter(is_published=True, chapter__is_published=True)
            .select_related('chapter')
            .order_by('chapter__order_index', 'order_index')
        )

        if not lessons:
            return Response({'lesson': None, 'all_completed': False})

        progress_by_lesson = {
            p.lesson_id: p for p in UserProgress.objects.filter(user=request.user)
        }

        def status_of(lesson):
            progress = progress_by_lesson.get(lesson.id)
            return progress.status if progress else UserProgress.ProgressStatus.NOT_STARTED

        started = [
            lesson for lesson in lessons
            if status_of(lesson) == UserProgress.ProgressStatus.IN_PROGRESS
        ]
        if started:
            target = max(started, key=lambda l: progress_by_lesson[l.id].updated_at)
            is_resuming = True
        else:
            unfinished = [
                lesson for lesson in lessons
                if status_of(lesson) != UserProgress.ProgressStatus.COMPLETED
            ]
            if not unfinished:
                return Response({'lesson': None, 'all_completed': True})
            target = unfinished[0]
            is_resuming = False

        chapter_lessons = [l for l in lessons if l.chapter_id == target.chapter_id]
        completed_in_chapter = sum(
            1 for l in chapter_lessons
            if status_of(l) == UserProgress.ProgressStatus.COMPLETED
        )

        return Response({
            'all_completed': False,
            'is_resuming': is_resuming,
            'lesson': {
                'id': str(target.id),
                'title': target.title,
                'slug': target.slug,
                'lesson_type': target.lesson_type,
                'estimated_duration': target.estimated_duration,
                'points': target.points,
            },
            'chapter': {
                'title': target.chapter.title,
                'slug': target.chapter.slug,
            },
            'chapter_progress': {
                'position': chapter_lessons.index(target) + 1,
                'total': len(chapter_lessons),
                'completed': completed_in_chapter,
            },
        })

    @action(detail=False, methods=['post'])
    def track_time(self, request):
        """Ajoute du temps passé sur une leçon.

        C'est un **incrément** (`F('time_spent') + n`) et non une valeur
        absolue : deux onglets ouverts sur la même leçon, ou un rechargement
        en cours de route, ne peuvent pas écraser le compteur.

        L'incrément est plafonné côté serveur. Le client envoie toutes les
        30 s, donc une valeur bien supérieure ne peut être qu'une dérive
        d'horloge ou une falsification — et ce compteur alimente des badges
        (`TIME_SPENT`, `FAST_LESSONS`), donc il doit rester crédible.
        """
        lesson_id = request.data.get('lesson_id')
        seconds = request.data.get('seconds')

        try:
            seconds = int(seconds)
        except (TypeError, ValueError):
            return Response(
                {"error": "seconds doit être un entier"},
                status=status.HTTP_400_BAD_REQUEST
            )

        if not lesson_id or seconds <= 0:
            return Response(
                {"error": "lesson_id et seconds (> 0) sont requis"},
                status=status.HTTP_400_BAD_REQUEST
            )

        seconds = min(seconds, MAX_TIME_INCREMENT_SECONDS)

        try:
            lesson = Lesson.objects.get(id=lesson_id)
        except Lesson.DoesNotExist:
            return Response({"error": "Lesson not found"}, status=status.HTTP_404_NOT_FOUND)

        progress, created = UserProgress.objects.get_or_create(
            user=request.user,
            lesson=lesson,
            defaults={'status': UserProgress.ProgressStatus.IN_PROGRESS},
        )

        # Ouvrir une leçon vaut « commencée » — mais on ne rétrograde jamais
        # une leçon déjà terminée en la relisant.
        update_fields = ['time_spent', 'updated_at']
        if progress.status == UserProgress.ProgressStatus.NOT_STARTED:
            progress.status = UserProgress.ProgressStatus.IN_PROGRESS
            update_fields.append('status')

        progress.time_spent = F('time_spent') + seconds
        progress.save(update_fields=update_fields)
        progress.refresh_from_db(fields=['time_spent'])

        if created:
            ActivityLog.objects.create(
                user=request.user,
                activity_type=ActivityLog.ActivityType.LESSON_STARTED,
                lesson=lesson,
                chapter=lesson.chapter,
            )

        # Lire une leçon est une activité : ça entretient la série de jours,
        # ce que les seules complétions ne faisaient pas.
        # On ne réévalue pas les badges ici (appel toutes les 30 s) : le sync
        # du dashboard et les complétions s'en chargent.
        touch_streak(request.user)

        return Response(
            {'lesson': str(lesson.id), 'time_spent': progress.time_spent},
            status=status.HTTP_200_OK
        )

    @action(detail=False, methods=['get'])
    def my_progress(self, request):
        """Obtenir la progression de l'utilisateur courant"""
        progress = UserProgress.objects.filter(user=request.user).select_related('lesson', 'lesson__chapter')
        serializer = self.get_serializer(progress, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['post'])
    def save_quiz_progress(self, request):
        """Sauvegarde les réponses d'un quiz en cours, sans le noter.

        Appelé au fur et à mesure que l'apprenant répond aux questions, pour
        que rien ne soit perdu en cas de rechargement/navigation.
        """
        lesson_id = request.data.get('lesson_id')
        answers = request.data.get('answers')

        if not lesson_id or not isinstance(answers, dict):
            return Response(
                {"error": "lesson_id et answers (objet) sont requis"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            lesson = Lesson.objects.get(id=lesson_id, lesson_type='QUIZ')
        except Lesson.DoesNotExist:
            return Response({"error": "Quiz introuvable"}, status=status.HTTP_404_NOT_FOUND)

        progress, created = UserProgress.objects.get_or_create(
            user=request.user,
            lesson=lesson,
            defaults={'status': UserProgress.ProgressStatus.IN_PROGRESS}
        )

        # Ne jamais écraser un quiz déjà réussi avec un brouillon en cours
        if progress.status != UserProgress.ProgressStatus.COMPLETED:
            progress.status = UserProgress.ProgressStatus.IN_PROGRESS
        progress.quiz_answers = answers
        progress.save(update_fields=['status', 'quiz_answers', 'updated_at'])

        return Response(UserProgressSerializer(progress).data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'])
    def submit_quiz(self, request):
        """Note un quiz côté serveur et attribue les points une seule fois.

        La notation se fait exclusivement à partir de quiz.questions côté
        serveur (jamais des données envoyées par le client), et les points
        de la leçon ne sont crédités qu'à la toute première réussite grâce
        au flag UserProgress.points_awarded.
        """
        lesson_id = request.data.get('lesson_id')
        answers = request.data.get('answers')

        if not lesson_id or not isinstance(answers, dict):
            return Response(
                {"error": "lesson_id et answers (objet) sont requis"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            lesson = Lesson.objects.select_related('quiz', 'chapter').get(
                id=lesson_id, lesson_type='QUIZ'
            )
            quiz = lesson.quiz
        except (Lesson.DoesNotExist, Quiz.DoesNotExist):
            return Response({"error": "Quiz introuvable"}, status=status.HTTP_404_NOT_FOUND)

        progress, _ = UserProgress.objects.get_or_create(user=request.user, lesson=lesson)

        if quiz.max_attempts and progress.attempts >= quiz.max_attempts and not progress.is_passed:
            return Response(
                {"error": f"Nombre maximum de tentatives atteint ({quiz.max_attempts})"},
                status=status.HTTP_403_FORBIDDEN
            )

        score, passed, details = _grade_quiz(quiz, answers)

        progress.attempts += 1
        progress.quiz_answers = answers
        progress.score = score
        progress.is_passed = progress.is_passed or passed

        points_earned = 0
        if passed:
            was_first_success = not progress.points_awarded
            progress.status = UserProgress.ProgressStatus.COMPLETED
            if not progress.completed_at:
                progress.completed_at = timezone.now()

            # Les points ne sont crédités qu'une fois, quel que soit le nombre
            # de fois où l'apprenant repasse (et réussit) le quiz. La garantie
            # vient du grand livre : la source `lesson:<id>` est unique.
            points_earned = award_lesson_points(request.user, lesson)
            progress.points_awarded = True

            if was_first_success:
                ActivityLog.objects.create(
                    user=request.user,
                    activity_type=ActivityLog.ActivityType.QUIZ_COMPLETED,
                    lesson=lesson,
                    chapter=lesson.chapter,
                    metadata={'score': score}
                )
        else:
            progress.status = UserProgress.ProgressStatus.IN_PROGRESS

        progress.save()

        new_badges = sync_user_gamification(request.user)

        return Response({
            'score': score,
            'passing_score': quiz.passing_score,
            'passed': passed,
            'attempts': progress.attempts,
            'max_attempts': quiz.max_attempts,
            'points_earned': points_earned,
            'total_points': get_points(request.user),
            'new_badges': UserBadgeSerializer(new_badges, many=True).data,
            'details': details,
        }, status=status.HTTP_200_OK)


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

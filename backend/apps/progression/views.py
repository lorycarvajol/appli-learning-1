from django.utils import timezone
from django.db.models import Count, Avg, F, Sum, Max, Q
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import ChapterAccess, UserProgress, ActivityLog
from .services import accessible_chapter_ids, can_access_lesson, complete_lesson
from .serializers import (
    ChapterAccessSerializer,
    UserProgressSerializer,
    UserProgressUpdateSerializer,
    ActivityLogSerializer,
    LearnerProgressSummarySerializer,
    UnlockChapterSerializer
)
from apps.accounts.models import User
from apps.accounts.permissions import IsTrainerOrAdmin
from apps.administration.audit import label_for, record
from apps.administration.models import AuditLog
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


def _refus_si_chapitre_verrouille(user, lesson):
    """Rend une réponse 403 si la leçon appartient à un chapitre non ouvert.

    ⚠️ **Le verrou de chapitre ne protégeait que la lecture.**
    `LessonViewSet.retrieve` renvoyait bien 403, mais `mark_completed`,
    `track_time` et `submit_quiz` acceptaient n'importe quelle leçon. Mesuré
    sur un compte neuf : 68 appels à `mark_completed`, aucun refusé, et le
    compte passait de 1 à 4 chapitres accessibles, 0 à 1485 points, 0 à
    11 badges — **sans jamais ouvrir une seule leçon**.

    Les trois invariants centraux du projet tombaient ensemble : la
    progression contrôlée par le formateur (un apprenant autonome se
    déverrouillait tout seul), le grand livre de points, et les badges. Pour un
    apprenant en classe, l'effet était plus discret mais réel : il n'ouvrait
    aucun chapitre, mais affichait une progression fictive dans le tableau de
    bord de son formateur.

    La décision d'accès vit déjà dans `progression.services` — elle n'était
    simplement pas consultée ici.
    """
    if can_access_lesson(user, lesson):
        return None
    return Response(
        {"error": "Ce chapitre ne vous est pas encore ouvert."},
        status=status.HTTP_403_FORBIDDEN,
    )


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


def visible_learners(staff_user):
    """Apprenants qu'un membre de l'encadrement a le droit de voir.

    Un formateur ne voit que **ses** classes. Avant l'introduction des classes,
    `learners_summary` renvoyait tous les apprenants de la plateforme à
    n'importe quel formateur, et `unlock_chapter` autorisait n'importe qui à
    débloquer pour n'importe qui.

    Les apprenants autonomes (sans classe) ne sont visibles que par un admin :
    ils n'ont, par définition, pas de formateur référent.
    """
    learners = User.objects.filter(role=User.Role.LEARNER)
    if staff_user.role == User.Role.ADMIN:
        return learners
    return learners.filter(profile__cohort__trainer=staff_user)


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

        if not visible_learners(request.user).filter(id=user_id).exists():
            return Response(
                {"error": "Cet apprenant n'est pas dans vos classes."},
                status=status.HTTP_403_FORBIDDEN
            )

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

        # Le journal d'activité dit ce qui est arrivé à l'apprenant ; le
        # journal d'audit dit qui en a décidé. Les deux sont nécessaires.
        record(
            request.user, AuditLog.Action.UNLOCK_CHAPTER, chapter_access.chapter,
            changes={'after': {'learner': label_for(chapter_access.user)}},
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

        if not visible_learners(request.user).filter(id=user_id).exists():
            return Response(
                {"error": "Cet apprenant n'est pas dans vos classes."},
                status=status.HTTP_403_FORBIDDEN
            )

        try:
            chapter_access = ChapterAccess.objects.get(
                user_id=user_id,
                chapter_id=chapter_id
            )
            chapter_access.is_unlocked = False
            chapter_access.save()

            record(
                request.user, AuditLog.Action.LOCK_CHAPTER, chapter_access.chapter,
                changes={'after': {'learner': label_for(chapter_access.user)}},
            )

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
        if user.role == User.Role.LEARNER:
            return qs.filter(user=user)

        # L'encadrement est borné à ses classes, y compris via ?user_id=
        qs = qs.filter(user__in=visible_learners(user))
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
        """Marque une leçon **de théorie** comme terminée.

        ⚠️ Cette route acceptait n'importe quel type de leçon, y compris les
        exercices et les quiz — et créditait leurs points. C'était une porte
        dérobée sur les deux seuls contenus dont la réussite est *objectivement
        vérifiable* : un exercice se valide quand ses tests passent
        (`apps/validation`), un quiz quand le score requis est atteint
        (`submit_quiz`, qui note côté serveur). Les déclarer terminés par un
        simple appel revenait à s'attribuer les points sans le travail.

        Une leçon de théorie, elle, n'a pas de critère vérifiable : on ne peut
        pas prouver qu'elle a été lue. La déclaration est donc le seul
        mécanisme possible, et le front la déclenche automatiquement en bas de
        page (`useScrollCompletion`).
        """
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

        refus = _refus_si_chapitre_verrouille(request.user, lesson)
        if refus:
            return refus

        if lesson.lesson_type != 'THEORY':
            return Response(
                {
                    "error": (
                        "Cette leçon se valide en la réussissant, pas en la "
                        "déclarant terminée."
                    ),
                    "lesson_type": lesson.lesson_type,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Logique partagée avec la validation d'exercice (cf. `complete_lesson`).
        progress, points_earned, _ = complete_lesson(request.user, lesson)

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

        **La première leçon non terminée du programme, parmi les chapitres
        ouverts.** L'ordre du parcours fait autorité : on n'apprend pas à
        mettre un site en ligne avant d'avoir écrit une balise.

        ⚠️ Deux défauts corrigés ici, tous deux constatés sur la base de
        développement.

        **1. La leçon la plus récemment entamée gagnait sur l'ordre du
        programme.** Un compte qui avait ouvert une leçon du dernier chapitre —
        ce que fait tout auteur ou formateur qui relit son contenu — se voyait
        proposer « Mettre son site en ligne » alors que le chapitre 1 était
        intact. L'intention (« reprendre où l'on en était ») était bonne, mais
        « où l'on en était » ne peut pas être plus loin que le premier trou du
        parcours : c'est ce trou qu'il faut combler d'abord. On reprend donc la
        première leçon inachevée, et `is_resuming` dit simplement si elle était
        déjà entamée.

        **2. Le verrou de chapitre n'était pas consulté.** La vue proposait la
        première leçon non terminée *tous chapitres confondus*, y compris
        verrouillés : le bouton « Commencer » menait droit à un 403. Passer par
        `accessible_chapter_ids` corrige ça et, effet voulu, ouvre au passage
        le chapitre 1 d'un apprenant au rythme libre qui n'a encore rien fait
        (`ensure_self_paced_access`) — le tableau de bord d'un compte neuf a
        donc toujours quelque chose à proposer, et c'est le début du parcours.

        Trois absences distinctes, que le client doit pouvoir distinguer :
        aucun contenu publié, rien d'ouvert (`locked`), et tout est terminé
        (`all_completed`).
        """
        accessible = accessible_chapter_ids(request.user)

        lessons = list(
            Lesson.objects.filter(is_published=True, chapter__is_published=True)
            .select_related('chapter')
            .order_by('chapter__order_index', 'order_index')
        )

        if not lessons:
            return Response({'lesson': None, 'all_completed': False, 'locked': False})

        progress_by_lesson = {
            p.lesson_id: p for p in UserProgress.objects.filter(user=request.user)
        }

        def status_of(lesson):
            progress = progress_by_lesson.get(lesson.id)
            return progress.status if progress else UserProgress.ProgressStatus.NOT_STARTED

        def unfinished(candidates):
            return [
                lesson for lesson in candidates
                if status_of(lesson) != UserProgress.ProgressStatus.COMPLETED
            ]

        ouvertes = [lesson for lesson in lessons if lesson.chapter_id in accessible]
        restantes = unfinished(ouvertes)

        if not restantes:
            # Deux situations très différentes derrière la même liste vide :
            # avoir fini le parcours, ou avoir fini tout ce qui est ouvert et
            # attendre son formateur. Les confondre ferait annoncer « parcours
            # terminé » à un apprenant qui n'a vu qu'un chapitre sur quatre.
            en_attente = bool(unfinished(lessons))
            return Response({
                'lesson': None,
                'all_completed': not en_attente,
                'locked': en_attente,
            })

        target = restantes[0]
        is_resuming = status_of(target) == UserProgress.ProgressStatus.IN_PROGRESS

        chapter_lessons = [l for l in lessons if l.chapter_id == target.chapter_id]
        completed_in_chapter = sum(
            1 for l in chapter_lessons
            if status_of(l) == UserProgress.ProgressStatus.COMPLETED
        )

        return Response({
            'all_completed': False,
            'locked': False,
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

        refus = _refus_si_chapitre_verrouille(request.user, lesson)
        if refus:
            return refus

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
    def overview(self, request):
        """Avancement réel : terminé **sur l'ensemble du programme**.

        Le tableau de bord calculait sa « progression globale » côté client, à
        partir des seules leçons déjà touchées
        (`terminées / (terminées + en cours)`). Une leçon terminée et aucune en
        cours affichait donc **100 %** dès la première leçon lue — le chiffre
        montait quand on ouvrait une leçon et redescendait quand on la
        finissait. Le dénominateur manquant (le nombre de leçons publiées)
        n'était tout simplement pas dans le magasin du client.

        Il est calculé ici parce que le serveur est le seul à connaître le
        périmètre exact : `is_published` sur la leçon **et** sur son chapitre —
        le même filtre que `next_lesson`, sans quoi les deux blocs du tableau
        de bord se contrediraient. (`Chapter.lesson_count`, lui, compte aussi
        les leçons non publiées : ne pas s'en servir pour un pourcentage.)

        Le détail par chapitre accompagne le total : « 12 sur 68 » ne dit pas
        où l'on en est, « chapitre 2 à moitié fait » si.

        Coût : trois requêtes, indépendantes du volume.
        """
        lessons = list(
            Lesson.objects
            .filter(is_published=True, chapter__is_published=True)
            .values(
                'id', 'chapter_id',
                'chapter__title', 'chapter__slug', 'chapter__order_index',
            )
            .order_by('chapter__order_index', 'order_index')
        )

        progress_by_lesson = {
            row['lesson_id']: row
            for row in UserProgress.objects
            .filter(user=request.user)
            .values('lesson_id', 'status', 'score', 'time_spent')
        }

        accessible = accessible_chapter_ids(request.user)

        completed = in_progress = time_spent = 0
        scores = []
        chapters = {}

        for lesson in lessons:
            chapter_id = lesson['chapter_id']
            chapter = chapters.setdefault(chapter_id, {
                'title': lesson['chapter__title'],
                'slug': lesson['chapter__slug'],
                'order_index': lesson['chapter__order_index'],
                'is_accessible': chapter_id in accessible,
                'total': 0,
                'completed': 0,
            })
            chapter['total'] += 1

            row = progress_by_lesson.get(lesson['id'])
            if row is None:
                continue

            time_spent += row['time_spent'] or 0

            # `score` est nul sur une leçon de théorie : elle n'a rien à noter.
            # Les compter comme des zéros écrasait la moyenne — un apprenant
            # avec deux quiz parfaits et huit leçons lues affichait 20 %.
            if row['score'] is not None:
                scores.append(row['score'])

            if row['status'] == UserProgress.ProgressStatus.COMPLETED:
                completed += 1
                chapter['completed'] += 1
            elif row['status'] == UserProgress.ProgressStatus.IN_PROGRESS:
                in_progress += 1

        total = len(lessons)

        return Response({
            'lessons': {
                'total': total,
                'completed': completed,
                'in_progress': in_progress,
                'percent': round(completed / total * 100) if total else 0,
            },
            'chapters': [
                {
                    **chapter,
                    'percent': (
                        round(chapter['completed'] / chapter['total'] * 100)
                        if chapter['total'] else 0
                    ),
                }
                for chapter in sorted(
                    chapters.values(), key=lambda c: c['order_index']
                )
            ],
            'time_spent_seconds': time_spent,
            # `None` — et non `0` — quand rien n'est encore noté : le client
            # affiche un tiret plutôt qu'un score nul, qui se lirait comme un
            # échec.
            'average_score': round(sum(scores) / len(scores)) if scores else None,
            'graded_count': len(scores),
        })

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

        refus = _refus_si_chapitre_verrouille(request.user, lesson)
        if refus:
            return refus

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
        if user.role == User.Role.LEARNER:
            return qs.filter(user=user)

        qs = qs.filter(user__in=visible_learners(user))
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
        """Résumé de progression des apprenants encadrés par l'appelant."""
        learners = visible_learners(request.user).select_related('profile')
        total_chapters = Chapter.objects.filter(is_published=True).count()
        total_lessons = Lesson.objects.filter(chapter__is_published=True).count()

        # Cette vue faisait quatre requêtes par apprenant. Pour un formateur
        # c'est supportable ; pour un **admin**, `visible_learners` renvoie
        # toute la plateforme — la vue dégénérait donc exactement là où elle
        # sert le plus. On agrège une fois par métrique, puis on assemble.
        progress_by_user = {
            row['user_id']: row
            for row in UserProgress.objects.filter(user__in=learners)
            .values('user_id')
            .annotate(
                completed=Count('id', filter=Q(
                    status=UserProgress.ProgressStatus.COMPLETED)),
                in_progress=Count('id', filter=Q(
                    status=UserProgress.ProgressStatus.IN_PROGRESS)),
                total_time=Sum('time_spent'),
                avg_score=Avg('score', filter=Q(score__isnull=False)),
            )
        }

        unlocked_by_user = {
            row['user_id']: row['total']
            for row in ChapterAccess.objects.filter(user__in=learners, is_unlocked=True)
            .values('user_id')
            .annotate(total=Count('id'))
        }

        last_activity_by_user = {
            row['user_id']: row['last_at']
            for row in ActivityLog.objects.filter(user__in=learners)
            .values('user_id')
            .annotate(last_at=Max('created_at'))
        }

        # Une seule leçon en cours est affichée par apprenant. On parcourt le
        # lot dans l'ordre de la base et on ne garde que la première vue, ce
        # qui reproduit le `.first()` d'origine sans requête par apprenant.
        current_lesson_by_user = {}
        for progress in UserProgress.objects.filter(
            user__in=learners, status=UserProgress.ProgressStatus.IN_PROGRESS
        ).select_related('lesson'):
            current_lesson_by_user.setdefault(progress.user_id, progress.lesson.title)

        summaries = []
        for learner in learners:
            stats = progress_by_user.get(learner.id, {})
            summaries.append({
                'user': learner,
                'total_chapters': total_chapters,
                'unlocked_chapters': unlocked_by_user.get(learner.id, 0),
                'total_lessons': total_lessons,
                'completed_lessons': stats.get('completed') or 0,
                'in_progress_lessons': stats.get('in_progress') or 0,
                'total_time_spent': stats.get('total_time') or 0,
                'average_score': stats.get('avg_score'),
                'last_activity': last_activity_by_user.get(learner.id),
                'current_lesson': current_lesson_by_user.get(learner.id),
            })

        serializer = LearnerProgressSummarySerializer(summaries, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def recent_activity(self, request):
        """Activité récente des apprenants encadrés par l'appelant."""
        limit = int(request.query_params.get('limit', 50))
        activities = ActivityLog.objects.filter(
            user__in=visible_learners(request.user)
        ).select_related('user', 'lesson', 'chapter').order_by('-created_at')[:limit]

        serializer = ActivityLogSerializer(activities, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def learner_detail(self, request, pk=None):
        """Obtenir les détails de progression d'un apprenant spécifique"""
        # Le filtrage par classe est appliqué ici aussi : sans lui, connaître
        # un identifiant suffirait à contourner le cloisonnement de la liste.
        learner = visible_learners(request.user).filter(id=pk).first()
        if learner is None:
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

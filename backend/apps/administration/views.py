"""
API de l'espace administration.

Volontairement **complémentaire de l'admin Django**, pas concurrente : le CRUD
de contenu (chapitres, leçons, badges…) reste dans `/admin/`, qui le fait mieux
et gratuitement. On expose ici ce que l'admin Django ne sait pas faire — vue
d'ensemble chiffrée, pilotage des formateurs, rattrapage des apprenants sans
classe — et le cycle de vie des comptes, qui demande des garde-fous métier.
"""
from datetime import timedelta

from django.db.models import Count, Max, Prefetch, Q
from django.db.models.functions import TruncDate
from django.utils import timezone
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.accounts.models import User
from apps.accounts.permissions import IsAdmin
from apps.cohorts.models import Cohort
from apps.courses.models import Chapter, Lesson
from apps.progression.models import ActivityLog, UserProgress

from .models import AuditLog
from .serializers import (
    AdminUserSerializer,
    AssignCohortSerializer,
    AuditLogSerializer,
    SetActiveSerializer,
    SetRoleSerializer,
    TrainerSerializer,
)
from .services import (
    AdminActionError,
    anonymize,
    assign_cohort,
    set_active,
    set_role,
)

#: Fenêtre de la courbe de tendance affichée dans le pilotage.
TREND_DAYS = 30

#: Au-delà de ce silence, on considère qu'un apprenant a décroché. Deux
#: semaines : assez long pour absorber des vacances, assez court pour agir.
STALLED_AFTER_DAYS = 14


class AdminOverviewViewSet(viewsets.ViewSet):
    """Chiffres de pilotage de la plateforme."""
    permission_classes = [IsAdmin]

    def list(self, request):
        learners = User.objects.filter(role=User.Role.LEARNER)
        cohorts = Cohort.objects.all()
        total_lessons = Lesson.objects.filter(
            is_published=True, chapter__is_published=True
        ).count()

        completed = UserProgress.objects.filter(
            status=UserProgress.ProgressStatus.COMPLETED
        ).count()

        # Le nombre d'apprenants sans classe est le chiffre à surveiller :
        # ils ne sont visibles d'aucun formateur, et s'accumulent en silence.
        unassigned = learners.filter(profile__cohort__isnull=True).count()

        return Response({
            'users': {
                'learners': learners.count(),
                'trainers': User.objects.filter(role=User.Role.TRAINER).count(),
                'admins': User.objects.filter(role=User.Role.ADMIN).count(),
                'inactive': User.objects.filter(is_active=False).count(),
                'unassigned_learners': unassigned,
            },
            'cohorts': {
                'total': cohorts.count(),
                'active': cohorts.filter(is_active=True).count(),
                'without_trainer': cohorts.filter(trainer__isnull=True).count(),
            },
            'content': {
                'chapters': Chapter.objects.filter(is_published=True).count(),
                'lessons': total_lessons,
            },
            'activity': {
                'lessons_completed': completed,
                'last_7_days': ActivityLog.objects.filter(
                    created_at__gte=timezone.now() - timedelta(days=7)
                ).count(),
                'trend': _activity_trend(),
                **_engagement(learners),
            },
            'per_cohort': _per_cohort(total_lessons),
        })


def _activity_trend():
    """Activité quotidienne sur la fenêtre de tendance, en une requête.

    Les jours sans activité sont réintroduits côté Python : la base ne renvoie
    que les jours présents, et une courbe à trous se lit comme une courbe qui
    remonte — exactement le contresens qu'on veut éviter.
    """
    since = timezone.now() - timedelta(days=TREND_DAYS)
    rows = (
        ActivityLog.objects.filter(created_at__gte=since)
        .annotate(day=TruncDate('created_at'))
        .values('day')
        .annotate(count=Count('id'))
    )
    counts = {row['day']: row['count'] for row in rows}

    today = timezone.localdate()
    return [
        {
            'date': (day := today - timedelta(days=offset)).isoformat(),
            'count': counts.get(day, 0),
        }
        for offset in range(TREND_DAYS - 1, -1, -1)
    ]


def _engagement(learners):
    """Décrochage et comptes jamais démarrés.

    Ce sont les deux chiffres qui désignent des personnes plutôt que des
    volumes : un total d'activités qui monte peut très bien masquer une moitié
    de promo à l'arrêt.
    """
    cutoff = timezone.now() - timedelta(days=STALLED_AFTER_DAYS)
    rows = learners.annotate(last_seen=Max('activities__created_at')).values_list(
        'last_seen', flat=True
    )

    stalled = sum(1 for last_seen in rows if last_seen is not None and last_seen < cutoff)
    never_started = sum(1 for last_seen in rows if last_seen is None)

    return {
        'stalled_learners': stalled,
        'never_started_learners': never_started,
        'stalled_after_days': STALLED_AFTER_DAYS,
    }


def _per_cohort(total_lessons):
    """Avancement de chaque classe, en deux requêtes quel qu'en soit le nombre.

    La version précédente bouclait sur les classes en faisant deux requêtes
    chacune. Ce n'était pas un détail de style : cette vue est celle de
    l'administrateur, donc la seule qui porte sur *toutes* les classes à la
    fois — c'est-à-dire précisément celle qui dégénère en premier.
    """
    members = (
        User.objects.filter(profile__cohort__isnull=False)
        .values('profile__cohort')
        .annotate(total=Count('id'))
    )
    member_counts = {row['profile__cohort']: row['total'] for row in members}

    done = (
        UserProgress.objects.filter(
            status=UserProgress.ProgressStatus.COMPLETED,
            user__profile__cohort__isnull=False,
        )
        .values('user__profile__cohort')
        .annotate(total=Count('id'))
    )
    done_counts = {row['user__profile__cohort']: row['total'] for row in done}

    per_cohort = []
    for cohort in Cohort.objects.select_related('trainer'):
        member_count = member_counts.get(cohort.id, 0)
        # Taux rapporté au total réalisable par la classe entière, pour
        # comparer des promos d'effectifs différents.
        possible = member_count * total_lessons
        per_cohort.append({
            'id': str(cohort.id),
            'name': cohort.name,
            'trainer_name': cohort.trainer.full_name if cohort.trainer else None,
            'trainer_id': str(cohort.trainer_id) if cohort.trainer_id else None,
            'is_active': cohort.is_active,
            'member_count': member_count,
            'completion_rate': (
                round(done_counts.get(cohort.id, 0) / possible * 100) if possible else 0
            ),
        })
    return per_cohort


class AdminTrainerViewSet(viewsets.ViewSet):
    """Formateurs, leurs classes et leurs effectifs."""
    permission_classes = [IsAdmin]

    def list(self, request):
        # `Cohort.member_count` est une propriété qui compte en base : la
        # laisser jouer dans le sérialiseur produisait une requête par classe.
        # On annote une fois pour toutes, la propriété reste le repli ailleurs.
        cohorts = Cohort.objects.annotate(members_total=Count('members'))
        trainers = (
            User.objects.filter(role=User.Role.TRAINER)
            .prefetch_related(Prefetch('cohorts', queryset=cohorts))
            .order_by('email')
        )
        return Response(TrainerSerializer(trainers, many=True).data)


class AuditLogViewSet(viewsets.ReadOnlyModelViewSet):
    """Journal d'audit — **lecture seule, sans exception**.

    Aucune route d'écriture ni de suppression n'est exposée, y compris à un
    administrateur : un journal que peuvent réécrire ceux qu'il surveille ne
    prouve rien. Pour la même raison, le modèle n'est pas enregistré dans
    l'admin Django.
    """
    serializer_class = AuditLogSerializer
    permission_classes = [IsAdmin]

    def get_queryset(self):
        qs = AuditLog.objects.select_related('actor')

        action_filter = self.request.query_params.get('action')
        if action_filter:
            qs = qs.filter(action=action_filter)

        actor = self.request.query_params.get('actor')
        if actor:
            qs = qs.filter(actor_id=actor)

        return qs

    @action(detail=False, methods=['get'])
    def actions(self, request):
        """Libellés des types d'action, pour alimenter le filtre côté front."""
        return Response([
            {'value': value, 'label': label}
            for value, label in AuditLog.Action.choices
        ])


class AdminUserViewSet(viewsets.ReadOnlyModelViewSet):
    """Comptes de la plateforme, avec les actions de cycle de vie."""
    serializer_class = AdminUserSerializer
    permission_classes = [IsAdmin]

    def get_queryset(self):
        qs = User.objects.select_related('profile', 'profile__cohort').order_by('email')

        role = self.request.query_params.get('role')
        if role:
            qs = qs.filter(role=role)

        if self.request.query_params.get('unassigned') == 'true':
            qs = qs.filter(role=User.Role.LEARNER, profile__cohort__isnull=True)

        search = self.request.query_params.get('search')
        if search:
            qs = qs.filter(
                Q(email__icontains=search)
                | Q(first_name__icontains=search)
                | Q(last_name__icontains=search)
            )

        return qs

    def _run(self, func, *args):
        """Traduit une erreur métier en 400 plutôt qu'en 500."""
        try:
            return Response(AdminUserSerializer(func(*args)).data)
        except AdminActionError as exc:
            return Response({'detail': str(exc)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def assign_cohort(self, request, pk=None):
        """Rattache un apprenant à une classe (ou l'en détache)."""
        serializer = AssignCohortSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        cohort_id = serializer.validated_data.get('cohort_id')
        cohort = None
        if cohort_id:
            cohort = Cohort.objects.filter(id=cohort_id).first()
            if cohort is None:
                return Response(
                    {'detail': 'Classe introuvable.'},
                    status=status.HTTP_404_NOT_FOUND
                )

        return self._run(assign_cohort, request.user, self.get_object(), cohort)

    @action(detail=True, methods=['post'])
    def set_role(self, request, pk=None):
        serializer = SetRoleSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return self._run(
            set_role, request.user, self.get_object(), serializer.validated_data['role']
        )

    @action(detail=True, methods=['post'])
    def set_active(self, request, pk=None):
        serializer = SetActiveSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return self._run(
            set_active, request.user, self.get_object(),
            serializer.validated_data['is_active'],
        )

    @action(detail=True, methods=['post'])
    def anonymize(self, request, pk=None):
        """Droit à l'effacement (RGPD). Irréversible."""
        return self._run(anonymize, request.user, self.get_object())

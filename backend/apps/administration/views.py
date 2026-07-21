"""
API de l'espace administration.

Volontairement **complémentaire de l'admin Django**, pas concurrente : le CRUD
de contenu (chapitres, leçons, badges…) reste dans `/admin/`, qui le fait mieux
et gratuitement. On expose ici ce que l'admin Django ne sait pas faire — vue
d'ensemble chiffrée, pilotage des formateurs, rattrapage des apprenants sans
classe — et le cycle de vie des comptes, qui demande des garde-fous métier.
"""
from django.db.models import Q
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.accounts.models import User
from apps.accounts.permissions import IsAdmin
from apps.cohorts.models import Cohort
from apps.courses.models import Chapter, Lesson
from apps.progression.models import ActivityLog, UserProgress

from .serializers import (
    AdminUserSerializer,
    AssignCohortSerializer,
    SetActiveSerializer,
    SetRoleSerializer,
    TrainerSerializer,
)
from .services import AdminActionError, anonymize, set_active, set_role


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

        per_cohort = []
        for cohort in cohorts.select_related('trainer'):
            member_ids = list(
                User.objects.filter(profile__cohort=cohort).values_list('id', flat=True)
            )
            done = UserProgress.objects.filter(
                user_id__in=member_ids,
                status=UserProgress.ProgressStatus.COMPLETED,
            ).count()
            # Taux rapporté au total réalisable par la classe entière, pour
            # comparer des promos d'effectifs différents.
            possible = len(member_ids) * total_lessons
            per_cohort.append({
                'id': str(cohort.id),
                'name': cohort.name,
                'trainer_name': cohort.trainer.full_name if cohort.trainer else None,
                'is_active': cohort.is_active,
                'member_count': len(member_ids),
                'completion_rate': round(done / possible * 100) if possible else 0,
            })

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
                    created_at__gte=_seven_days_ago()
                ).count(),
            },
            'per_cohort': per_cohort,
        })


def _seven_days_ago():
    from datetime import timedelta

    from django.utils import timezone

    return timezone.now() - timedelta(days=7)


class AdminTrainerViewSet(viewsets.ViewSet):
    """Formateurs, leurs classes et leurs effectifs."""
    permission_classes = [IsAdmin]

    def list(self, request):
        trainers = (
            User.objects.filter(role=User.Role.TRAINER)
            .prefetch_related('cohorts')
            .order_by('email')
        )
        return Response(TrainerSerializer(trainers, many=True).data)


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
        """Rattache un apprenant à une classe (ou l'en détache).

        Sert surtout à récupérer les apprenants autonomes, qu'aucun formateur
        ne voit. Conformément à la règle générale, cela ne retire jamais un
        accès de chapitre déjà obtenu.
        """
        user = self.get_object()
        serializer = AssignCohortSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        if user.role != User.Role.LEARNER:
            return Response(
                {'detail': "Seul un apprenant peut être rattaché à une classe."},
                status=status.HTTP_400_BAD_REQUEST
            )

        cohort_id = serializer.validated_data.get('cohort_id')
        cohort = None
        if cohort_id:
            cohort = Cohort.objects.filter(id=cohort_id).first()
            if cohort is None:
                return Response(
                    {'detail': 'Classe introuvable.'},
                    status=status.HTTP_404_NOT_FOUND
                )

        user.profile.cohort = cohort
        user.profile.save(update_fields=['cohort', 'updated_at'])
        user.refresh_from_db()
        return Response(AdminUserSerializer(user).data)

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

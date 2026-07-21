"""
API des classes et invitations.

Cloisonnement : un formateur ne voit et ne pilote **que ses propres classes**.
Seul un admin voit tout. C'est ce qui manquait jusqu'ici — `learners_summary`
renvoyait tous les apprenants de la plateforme à n'importe quel formateur.
"""
from django.db import transaction
from rest_framework import serializers, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from apps.accounts.models import User
from apps.accounts.permissions import IsAdmin, IsTrainerOrAdmin
from apps.administration.audit import label_for, record
from apps.administration.models import AuditLog
from apps.accounts.serializers import UserSerializer
from apps.courses.models import Chapter
from apps.progression.services import unlock_chapter_for

from .models import Cohort, CohortInvite
from .serializers import (
    CohortInviteSerializer,
    CohortMemberSerializer,
    CohortSerializer,
    InviteAcceptSerializer,
    PublicInviteSerializer,
)
from .services import consume_invite, resolve_usable_invite


def _trainer_or_400(trainer_id):
    """Résout un formateur, en refusant tout compte qui n'en est pas un.

    Sans cette vérification, un admin pourrait confier une classe à un
    apprenant : il hériterait alors, via `visible_learners`, de la vue sur ses
    propres camarades.
    """
    trainer = User.objects.filter(id=trainer_id, role=User.Role.TRAINER).first()
    if trainer is None:
        raise serializers.ValidationError(
            {'trainer_id': "Ce compte n'existe pas ou n'est pas formateur."}
        )
    return trainer


class CohortViewSet(viewsets.ModelViewSet):
    """Classes du formateur connecté (toutes, pour un admin)."""
    serializer_class = CohortSerializer
    permission_classes = [IsTrainerOrAdmin]

    def get_queryset(self):
        qs = Cohort.objects.select_related('trainer')
        if self.request.user.role == User.Role.ADMIN:
            return qs
        return qs.filter(trainer=self.request.user)

    def perform_create(self, serializer):
        """Crée la classe et lui affecte un formateur.

        Pour un **formateur**, le titulaire est déduit de la requête et jamais
        du corps : sinon il pourrait créer une classe au nom d'un collègue.

        Pour un **admin**, ce raccourci était un défaut : il devenait formateur
        de chaque classe qu'il créait, sans aucun moyen d'en désigner un autre.
        Il peut donc passer un `trainer_id` — c'est précisément son rôle que de
        répartir les promos entre les formateurs.
        """
        cohort = serializer.save(trainer=self._requested_trainer())
        record(
            self.request.user, AuditLog.Action.CREATE_COHORT, cohort,
            changes={'after': {'trainer': label_for(cohort.trainer)}},
        )

    def _requested_trainer(self):
        if self.request.user.role != User.Role.ADMIN:
            return self.request.user

        trainer_id = self.request.data.get('trainer_id')
        if not trainer_id:
            # Un admin peut aussi créer une classe orpheline et l'affecter
            # ensuite ; le pilotage compte déjà les classes sans formateur.
            return None
        return _trainer_or_400(trainer_id)

    @action(detail=True, methods=['post'], permission_classes=[IsAdmin])
    def set_trainer(self, request, pk=None):
        """Affecte (ou retire) le formateur d'une classe. **Admin seulement.**

        Résout le compteur « classes orphelines » du pilotage, qui signalait le
        problème sans offrir aucun moyen de le corriger. Réservé à l'admin :
        laisser un formateur se réaffecter une classe casserait le
        cloisonnement que `get_queryset` met en place.
        """
        cohort = self.get_object()
        trainer_id = request.data.get('trainer_id')
        trainer = _trainer_or_400(trainer_id) if trainer_id else None

        before = label_for(cohort.trainer)
        with transaction.atomic():
            cohort.trainer = trainer
            cohort.save(update_fields=['trainer', 'updated_at'])
            record(
                request.user, AuditLog.Action.ASSIGN_TRAINER, cohort,
                changes={'before': before, 'after': label_for(trainer)},
            )

        return Response(CohortSerializer(cohort).data)

    @action(detail=True, methods=['get'])
    def members(self, request, pk=None):
        cohort = self.get_object()
        learners = User.objects.filter(
            profile__cohort=cohort
        ).select_related('profile').order_by('first_name', 'email')
        return Response(CohortMemberSerializer(learners, many=True).data)

    @action(detail=True, methods=['post'])
    def remove_member(self, request, pk=None):
        """Retire un apprenant de la classe.

        Il redevient autonome : ses accès déjà obtenus sont conservés (on ne
        reverrouille jamais) et il repasse au rythme libre pour la suite.
        """
        cohort = self.get_object()
        user_id = request.data.get('user_id')

        learner = User.objects.filter(id=user_id, profile__cohort=cohort).first()
        if learner is None:
            return Response(
                {'error': "Cet apprenant n'appartient pas à cette classe."},
                status=status.HTTP_404_NOT_FOUND
            )

        learner.profile.cohort = None
        learner.profile.save(update_fields=['cohort', 'updated_at'])
        return Response({'removed': str(learner.id)}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'])
    def unlock_chapter(self, request, pk=None):
        """Débloque un chapitre pour toute la classe d'un coup.

        C'est le geste réel d'un formateur : ouvrir le chapitre 3 à sa promo,
        pas répéter l'opération apprenant par apprenant.
        """
        cohort = self.get_object()
        chapter_id = request.data.get('chapter_id')

        chapter = Chapter.objects.filter(id=chapter_id, is_published=True).first()
        if chapter is None:
            return Response(
                {'error': 'Chapitre introuvable ou non publié.'},
                status=status.HTTP_404_NOT_FOUND
            )

        learners = User.objects.filter(profile__cohort=cohort)
        opened = 0
        with transaction.atomic():
            for learner in learners:
                _, newly = unlock_chapter_for(learner, chapter, unlocked_by=request.user)
                if newly:
                    opened += 1

            record(
                request.user, AuditLog.Action.UNLOCK_CHAPTER, chapter,
                changes={
                    'after': {
                        'cohort': cohort.name,
                        'newly_unlocked': opened,
                    }
                },
            )

        return Response({
            'chapter': str(chapter.id),
            'members': learners.count(),
            'newly_unlocked': opened,
        }, status=status.HTTP_200_OK)


class CohortInviteViewSet(viewsets.ModelViewSet):
    """Liens d'invitation. Un formateur ne gère que ceux de ses classes."""
    serializer_class = CohortInviteSerializer
    permission_classes = [IsTrainerOrAdmin]
    http_method_names = ['get', 'post', 'delete', 'head', 'options']

    def get_queryset(self):
        qs = CohortInvite.objects.select_related('cohort', 'cohort__trainer')
        if self.request.user.role == User.Role.ADMIN:
            return qs
        return qs.filter(cohort__trainer=self.request.user)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        role = serializer.validated_data.get('role', User.Role.LEARNER)
        cohort = serializer.validated_data.get('cohort')

        # Seul un admin peut fabriquer un formateur : sans cette règle, un
        # formateur pourrait s'auto-répliquer et le rôle perdrait tout sens.
        if role == User.Role.TRAINER:
            if request.user.role != User.Role.ADMIN:
                return Response(
                    {'role': "Seul un administrateur peut inviter un formateur."},
                    status=status.HTTP_403_FORBIDDEN
                )
            if cohort is not None:
                return Response(
                    {'cohort': "Une invitation de formateur ne vise pas de classe."},
                    status=status.HTTP_400_BAD_REQUEST
                )
        else:
            if cohort is None:
                return Response(
                    {'cohort': "Une invitation d'apprenant doit viser une classe."},
                    status=status.HTTP_400_BAD_REQUEST
                )
            if request.user.role != User.Role.ADMIN and cohort.trainer_id != request.user.id:
                return Response(
                    {'cohort': "Cette classe ne vous appartient pas."},
                    status=status.HTTP_403_FORBIDDEN
                )

        with transaction.atomic():
            invite = serializer.save(created_by=request.user)
            # Une invitation est un pouvoir diffusable : elle crée des comptes,
            # et pour un rôle TRAINER elle crée un encadrant. Le jeton lui-même
            # n'est jamais journalisé — le journal se lit à plusieurs.
            record(
                request.user, AuditLog.Action.INVITE_CREATED, invite.cohort,
                target_label=label_for(invite.cohort) or 'invitation formateur',
                changes={'after': {'role': invite.role}},
            )

        return Response(
            self.get_serializer(invite).data, status=status.HTTP_201_CREATED
        )

    def perform_destroy(self, instance):
        """Révoque au lieu de supprimer : garde une trace du lien diffusé."""
        with transaction.atomic():
            instance.is_revoked = True
            instance.save(update_fields=['is_revoked'])
            record(
                self.request.user, AuditLog.Action.INVITE_REVOKED, instance.cohort,
                target_label=label_for(instance.cohort) or 'invitation formateur',
                changes={'after': {'role': instance.role}},
            )


# ---------------------------------------------------------------------------
# Parcours public : cliquer sur le lien
# ---------------------------------------------------------------------------

INVALID_INVITE = {'valid': False}


class InviteDetailView(APIView):
    """
    GET /api/cohorts/invites/<token>/

    Affiche « vous rejoignez telle classe » avant tout formulaire. Public, donc
    limité en débit : sans throttle, on pourrait énumérer les jetons.
    """
    permission_classes = [AllowAny]
    throttle_scope = 'invite'

    def get(self, request, token):
        invite = resolve_usable_invite(token)
        if invite is None:
            return Response(INVALID_INVITE, status=status.HTTP_200_OK)
        return Response(PublicInviteSerializer(invite).data, status=status.HTTP_200_OK)


class InviteAcceptView(APIView):
    """
    POST /api/cohorts/invites/<token>/accept/

    Crée le compte et le rattache. Le rôle et la classe viennent du jeton.
    """
    permission_classes = [AllowAny]
    throttle_scope = 'invite'

    def post(self, request, token):
        invite = resolve_usable_invite(token)
        if invite is None:
            return Response(
                {'token': "Ce lien est invalide, expiré ou révoqué."},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = InviteAcceptSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        with transaction.atomic():
            user = serializer.save()
            if not consume_invite(user, invite):
                # Dernier usage pris entre la résolution et la consommation.
                transaction.set_rollback(True)
                return Response(
                    {'token': "Ce lien n'est plus utilisable."},
                    status=status.HTTP_400_BAD_REQUEST
                )

        user.refresh_from_db()
        refresh = RefreshToken.for_user(user)
        return Response({
            'user': UserSerializer(user).data,
            'tokens': {'refresh': str(refresh), 'access': str(refresh.access_token)},
        }, status=status.HTTP_201_CREATED)


class InviteJoinView(APIView):
    """
    POST /api/cohorts/invites/<token>/join/

    Rattache un utilisateur **déjà connecté**. C'est le cas de l'apprenant
    inscrit en autonomie qui reçoit un lien plus tard : il ne doit pas avoir à
    recréer un compte.
    """
    permission_classes = [IsAuthenticated]
    throttle_scope = 'invite'

    def post(self, request, token):
        invite = resolve_usable_invite(token)
        if invite is None:
            return Response(
                {'token': "Ce lien est invalide, expiré ou révoqué."},
                status=status.HTTP_400_BAD_REQUEST
            )

        if not consume_invite(request.user, invite):
            return Response(
                {'token': "Ce lien n'est plus utilisable."},
                status=status.HTTP_400_BAD_REQUEST
            )

        request.user.refresh_from_db()
        return Response(UserSerializer(request.user).data, status=status.HTTP_200_OK)

"""Serializers de l'espace administration."""
from rest_framework import serializers

from apps.accounts.models import User


class AdminUserSerializer(serializers.ModelSerializer):
    """Vue administrateur d'un compte, avec son rattachement et son état."""
    full_name = serializers.CharField(read_only=True)
    cohort_id = serializers.UUIDField(source='profile.cohort_id', read_only=True)
    cohort_name = serializers.CharField(
        source='profile.cohort.name', read_only=True, default=None
    )
    total_points = serializers.IntegerField(source='profile.total_points', read_only=True)
    is_anonymized = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            'id', 'email', 'first_name', 'last_name', 'full_name', 'role',
            'is_active', 'is_staff', 'is_anonymized', 'cohort_id', 'cohort_name',
            'total_points', 'date_joined', 'last_login',
        ]
        read_only_fields = fields

    def get_is_anonymized(self, user):
        profile = getattr(user, 'profile', None)
        return bool(profile and profile.anonymized_at)


class TrainerSerializer(serializers.ModelSerializer):
    """Un formateur avec ses classes et leurs effectifs."""
    full_name = serializers.CharField(read_only=True)
    cohorts = serializers.SerializerMethodField()
    learner_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'email', 'full_name', 'is_active', 'date_joined',
                  'cohorts', 'learner_count']
        read_only_fields = fields

    def get_cohorts(self, trainer):
        return [
            {
                'id': str(cohort.id),
                'name': cohort.name,
                'is_active': cohort.is_active,
                'member_count': cohort.member_count,
            }
            for cohort in trainer.cohorts.all()
        ]

    def get_learner_count(self, trainer):
        return sum(cohort.member_count for cohort in trainer.cohorts.all())


class AssignCohortSerializer(serializers.Serializer):
    """`cohort_id` vide détache l'apprenant (il redevient autonome)."""
    cohort_id = serializers.UUIDField(required=False, allow_null=True)


class SetRoleSerializer(serializers.Serializer):
    role = serializers.ChoiceField(choices=User.Role.choices)


class SetActiveSerializer(serializers.Serializer):
    is_active = serializers.BooleanField()

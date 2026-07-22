"""Serializers des classes et invitations."""
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

from apps.accounts.models import User

from .models import Cohort, CohortInvite
from .services import build_invite_url


class CohortMemberSerializer(serializers.ModelSerializer):
    """Un apprenant vu depuis sa classe."""
    full_name = serializers.CharField(read_only=True)
    total_points = serializers.IntegerField(source='profile.total_points', read_only=True)
    level = serializers.IntegerField(source='profile.level', read_only=True)

    class Meta:
        model = User
        fields = ['id', 'email', 'first_name', 'last_name', 'full_name',
                  'total_points', 'level', 'date_joined']
        read_only_fields = fields


class CohortSerializer(serializers.ModelSerializer):
    trainer_name = serializers.CharField(source='trainer.full_name', read_only=True)
    member_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Cohort
        fields = ['id', 'name', 'description', 'trainer', 'trainer_name',
                  'member_count', 'is_active', 'created_at', 'updated_at']
        # `trainer` est imposé par la vue (le créateur), jamais par le client :
        # sinon un formateur pourrait créer une classe au nom d'un autre.
        read_only_fields = ['id', 'trainer', 'created_at', 'updated_at']


class CohortInviteSerializer(serializers.ModelSerializer):
    """Vue formateur d'une invitation : le lien complet et son état."""
    url = serializers.SerializerMethodField()
    cohort_name = serializers.CharField(source='cohort.name', read_only=True, default=None)
    is_usable = serializers.BooleanField(read_only=True)
    invalid_reason = serializers.SerializerMethodField()

    class Meta:
        model = CohortInvite
        fields = ['id', 'token', 'url', 'cohort', 'cohort_name', 'role',
                  'expires_at', 'max_uses', 'uses_count', 'is_revoked',
                  'is_usable', 'invalid_reason', 'created_at']
        read_only_fields = ['id', 'token', 'uses_count', 'created_at']

    def get_url(self, invite):
        return build_invite_url(invite)

    def get_invalid_reason(self, invite):
        return invite.invalid_reason()


class PublicInviteSerializer(serializers.Serializer):
    """Ce que voit un visiteur qui clique sur le lien.

    Strictement le minimum permettant de reconnaître l'invitation : le nom de
    la classe et celui du formateur. Jamais la liste des membres, ni les
    compteurs d'usage, ni l'identité de l'émetteur.
    """

    def to_representation(self, invite):
        return {
            'valid': True,
            'role': invite.role,
            'cohort_name': invite.cohort.name if invite.cohort else None,
            'trainer_name': (
                invite.cohort.trainer.full_name
                if invite.cohort and invite.cohort.trainer
                else None
            ),
        }


class InviteAcceptSerializer(serializers.Serializer):
    """Création de compte depuis un lien d'invitation.

    Aucun champ `role` ni `cohort` : ils viennent du jeton, résolu par la vue.
    """
    email = serializers.EmailField(required=True)
    password = serializers.CharField(required=True, write_only=True)
    password_confirm = serializers.CharField(required=True, write_only=True)
    first_name = serializers.CharField(required=False, allow_blank=True, default='')
    last_name = serializers.CharField(required=False, allow_blank=True, default='')
    # Consentement RGPD, exigé pour toute création de compte, y compris par
    # invitation (cf. RegisterSerializer côté accounts).
    accept_terms = serializers.BooleanField(required=True)

    def validate_accept_terms(self, value):
        if value is not True:
            raise serializers.ValidationError(
                "Vous devez accepter la politique de confidentialité et les "
                "conditions d'utilisation pour créer un compte."
            )
        return value

    def validate_email(self, value):
        email = value.strip().lower()
        if User.objects.filter(email__iexact=email).exists():
            raise serializers.ValidationError(
                "Un compte existe déjà avec cette adresse. "
                "Connectez-vous, le rattachement se fera automatiquement."
            )
        return email

    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError({
                "password": "Les deux mots de passe ne correspondent pas."
            })
        return attrs

    def create(self, validated_data):
        from django.utils import timezone

        validated_data.pop('password_confirm')
        validated_data.pop('accept_terms')
        password = validated_data.pop('password')

        user = User(
            email=validated_data['email'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', ''),
        )
        # Validation avec l'utilisateur en contexte : refuse aussi un mot de
        # passe trop proche de l'email ou du nom.
        validate_password(password, user)
        user.set_password(password)
        user.save()

        # Horodatage du consentement (le profil est créé par signal).
        profile = getattr(user, 'profile', None)
        if profile is not None:
            profile.terms_accepted_at = timezone.now()
            profile.save(update_fields=['terms_accepted_at', 'updated_at'])

        return user

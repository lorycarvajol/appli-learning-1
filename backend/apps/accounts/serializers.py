"""
Serializers for User and Profile models.
"""
from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from django.db import transaction

from .avatars import is_valid_avatar_key
from .models import User, Profile

#: Seuls champs du profil qu'un apprenant peut écrire lui-même.
#:
#: Cette liste est le garde-fou central de l'écriture imbriquée : `total_points`
#: et `level` sont des soldes dérivés du grand livre, `cohort` relève du
#: formateur, `anonymized_at` du RGPD. Aucun ne doit pouvoir bouger depuis un
#: formulaire de profil.
EDITABLE_PROFILE_FIELDS = (
    'bio', 'avatar_key', 'theme', 'timezone', 'github_username',
    'show_in_leaderboard',
)


class ProfileSerializer(serializers.ModelSerializer):
    """Serializer for user profile."""

    #: Nom de la classe, en lecture seule. L'en-tête du profil l'affichait déjà
    #: (`user.profile.cohort_name`) mais il n'était pas sérialisé : la ligne
    #: était morte, aucun apprenant n'a jamais vu sa classe sur cette page.
    #:
    #: ⚠️ En lecture seule et **sans** `cohort` en écriture : le rattachement à
    #: une classe passe par une invitation ou par un admin
    #: (`assign_cohort`, audité), jamais par un formulaire de profil.
    cohort_name = serializers.CharField(
        source='cohort.name', read_only=True, default=None,
    )

    class Meta:
        model = Profile
        fields = [
            'bio', 'avatar_key', 'theme', 'total_points', 'level',
            'timezone', 'github_username', 'show_in_leaderboard',
            'cohort_name', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'total_points', 'level', 'cohort_name', 'created_at', 'updated_at'
        ]

    def validate_avatar_key(self, value):
        """Refuse toute clé absente du catalogue.

        Sans cette validation, un `PATCH` pourrait poser une chaîne arbitraire
        qui finirait interpolée dans le rendu SVG du client.
        """
        if not is_valid_avatar_key(value):
            raise serializers.ValidationError(
                "Cet avatar ne fait pas partie du catalogue."
            )
        return value

    def validate_bio(self, value):
        if len(value) > 500:
            raise serializers.ValidationError(
                "La biographie ne peut pas dépasser 500 caractères."
            )
        return value


class UserSerializer(serializers.ModelSerializer):
    """Compte et profil, avec écriture imbriquée du profil.

    ⚠️ L'écriture imbriquée demande une précaution particulière ici. Un signal
    `post_save` qui sauvait `instance.profile` a déjà écrasé des points en
    mémoire par le passé (cf. `signals.py`). On ne réenregistre donc **jamais
    le profil en entier** : seuls les champs effectivement reçus sont écrits,
    via `update_fields`. Un solde mis à jour en parallèle par
    `award_points` ne peut pas être écrasé par un formulaire de profil.
    """
    profile = ProfileSerializer(required=False)

    class Meta:
        model = User
        fields = [
            'id', 'email', 'first_name', 'last_name', 'role',
            'is_active', 'date_joined', 'last_login', 'profile'
        ]
        read_only_fields = ['id', 'date_joined', 'last_login', 'role', 'is_active']

    def update(self, instance, validated_data):
        profile_data = validated_data.pop('profile', None)

        with transaction.atomic():
            user = super().update(instance, validated_data)

            if profile_data:
                profile = user.profile
                touched = [
                    field for field in EDITABLE_PROFILE_FIELDS
                    if field in profile_data
                ]
                for field in touched:
                    setattr(profile, field, profile_data[field])
                if touched:
                    profile.save(update_fields=[*touched, 'updated_at'])

        return user


class RegisterSerializer(serializers.ModelSerializer):
    """Serializer for user registration."""
    password = serializers.CharField(
        write_only=True,
        required=True,
        validators=[validate_password],
        style={'input_type': 'password'}
    )
    password_confirm = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'}
    )
    # Consentement RGPD : l'inscription vaut acceptation explicite de la
    # politique de confidentialité et des CGU. `write_only` (rien à renvoyer),
    # obligatoire, et `True` refusé s'il n'est pas coché — sans quoi la case
    # serait cosmétique. La date d'acceptation est figée dans le profil pour
    # servir de preuve.
    accept_terms = serializers.BooleanField(write_only=True, required=True)

    class Meta:
        model = User
        fields = [
            'email', 'password', 'password_confirm',
            'first_name', 'last_name', 'accept_terms',
        ]

    def validate(self, attrs):
        """Validate that passwords match."""
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError({
                "password": "Password fields didn't match."
            })
        return attrs

    def validate_accept_terms(self, value):
        if value is not True:
            raise serializers.ValidationError(
                "Vous devez accepter la politique de confidentialité et les "
                "conditions d'utilisation pour créer un compte."
            )
        return value

    def create(self, validated_data):
        """Create user with validated data."""
        from django.utils import timezone

        validated_data.pop('password_confirm')
        validated_data.pop('accept_terms')

        user = User.objects.create_user(
            email=validated_data['email'],
            password=validated_data['password'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', ''),
        )

        # Le profil est créé par signal `post_save`. On y horodate le
        # consentement sans réenregistrer le User (cf. signals.py).
        profile = getattr(user, 'profile', None)
        if profile is not None:
            profile.terms_accepted_at = timezone.now()
            profile.save(update_fields=['terms_accepted_at', 'updated_at'])

        return user


class PasswordResetRequestSerializer(serializers.Serializer):
    """Demande de réinitialisation. Ne valide que la forme de l'email.

    On ne vérifie surtout pas que le compte existe : la vue doit répondre à
    l'identique dans tous les cas, sinon l'endpoint devient un oracle
    permettant de savoir qui est inscrit sur la plateforme.
    """
    email = serializers.EmailField(required=True)


class PasswordResetConfirmSerializer(serializers.Serializer):
    """Choix du nouveau mot de passe à partir du lien reçu."""
    uid = serializers.CharField(required=True)
    token = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True, write_only=True)
    new_password_confirm = serializers.CharField(required=True, write_only=True)

    def validate(self, attrs):
        from .services import resolve_reset_token

        if attrs['new_password'] != attrs['new_password_confirm']:
            raise serializers.ValidationError({
                "new_password": "Les deux mots de passe ne correspondent pas."
            })

        user = resolve_reset_token(attrs['uid'], attrs['token'])
        if user is None:
            raise serializers.ValidationError({
                "token": "Ce lien est invalide ou a expiré. Demandez-en un nouveau."
            })

        # Validation avec l'utilisateur en contexte : permet aussi de refuser
        # un mot de passe trop proche de l'email ou du nom.
        validate_password(attrs['new_password'], user)

        attrs['user'] = user
        return attrs


class ChangePasswordSerializer(serializers.Serializer):
    """Serializer for password change."""
    old_password = serializers.CharField(required=True, write_only=True)
    new_password = serializers.CharField(
        required=True,
        write_only=True,
        validators=[validate_password]
    )
    new_password_confirm = serializers.CharField(required=True, write_only=True)

    def validate(self, attrs):
        """Validate that new passwords match."""
        if attrs['new_password'] != attrs['new_password_confirm']:
            raise serializers.ValidationError({
                "new_password": "Password fields didn't match."
            })
        return attrs

    def validate_old_password(self, value):
        """Validate that old password is correct."""
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError("Old password is incorrect.")
        return value

    def save(self):
        """Save the new password."""
        user = self.context['request'].user
        user.set_password(self.validated_data['new_password'])
        user.save()
        return user

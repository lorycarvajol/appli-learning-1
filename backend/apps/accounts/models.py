"""
User models for the learning platform.
Custom User model with UUID primary key and role-based access.
"""
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.db import models
from django.db.models.functions import Lower
import uuid


class UserManager(BaseUserManager):
    """Custom user manager for email-based authentication."""

    def create_user(self, email, password=None, **extra_fields):
        """Create and save a regular user with the given email and password."""
        if not email:
            raise ValueError('The Email field must be set')

        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def get_by_natural_key(self, username):
        """Look up a user by email, case-insensitively.

        Les emails sont stockés en minuscules (cf. `User.save`), mais un
        apprenant qui tape « Prenom.Nom@ecole.fr » doit pouvoir se connecter.
        Sans ça, la normalisation à l'écriture rendrait son compte
        inaccessible depuis son propre clavier.
        """
        return self.get(**{f'{self.model.USERNAME_FIELD}__iexact': username})

    def create_superuser(self, email, password=None, **extra_fields):
        """Create and save a superuser with the given email and password."""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('role', 'ADMIN')

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    """
    Custom User model with email authentication and role-based access.
    """
    class Role(models.TextChoices):
        LEARNER = 'LEARNER', 'Apprenant'
        TRAINER = 'TRAINER', 'Formateur'
        ADMIN = 'ADMIN', 'Administrateur'

    # Conservé pour compatibilité : `Role.choices` est la source de vérité.
    ROLE_CHOICES = Role.choices

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True, db_index=True)
    first_name = models.CharField(max_length=150, blank=True)
    last_name = models.CharField(max_length=150, blank=True)
    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.LEARNER,
        db_index=True
    )

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    date_joined = models.DateTimeField(auto_now_add=True)
    last_login = models.DateTimeField(null=True, blank=True)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    class Meta:
        db_table = 'accounts_user'
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        ordering = ['-date_joined']
        constraints = [
            # Garde en base : `save()` normalise déjà, mais un `update()` ou
            # un `bulk_create` court-circuite le modèle. Sans cette contrainte,
            # deux comptes pour le même email restent possibles.
            models.UniqueConstraint(
                Lower('email'),
                name='unique_user_email_ci',
            ),
        ]

    def save(self, *args, **kwargs):
        """Normalise l'email et aligne `is_staff` sur le rôle.

        **Email** : `BaseUserManager.normalize_email` ne met en minuscules que
        le domaine. « Loryc@example.com » et « loryc@example.com » créeraient
        deux comptes distincts, et l'apprenant perdrait sa progression en se
        connectant « au mauvais ».

        **is_staff** : l'application avait deux notions d'administrateur qui
        pouvaient diverger — `role == ADMIN` (privilèges API) et `is_staff`
        (accès à /admin/). Rien ne les synchronisait : promouvoir quelqu'un en
        ADMIN produisait un administrateur incapable d'ouvrir l'admin Django,
        et rétrograder un admin lui laissait cet accès.

        Le rôle fait autorité. Conséquence assumée : cocher `is_staff` à la
        main dans l'admin Django sur un non-ADMIN ne tient pas — il faut
        changer le rôle. Les superutilisateurs conservent l'accès quoi qu'il
        arrive, pour ne jamais s'enfermer dehors.
        """
        if self.email:
            self.email = self.email.strip().lower()

        self.is_staff = bool(self.is_superuser) or self.role == self.Role.ADMIN

        super().save(*args, **kwargs)

    def __str__(self):
        return self.email

    @property
    def full_name(self):
        """Return the user's full name."""
        return f"{self.first_name} {self.last_name}".strip() or self.email

    def is_learner(self):
        """Check if user is a learner."""
        return self.role == 'LEARNER'

    def is_trainer(self):
        """Check if user is a trainer."""
        return self.role == 'TRAINER'

    def is_admin(self):
        """Check if user is an admin."""
        return self.role == 'ADMIN'


class Profile(models.Model):
    """
    User profile with additional information and gamification data.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')

    bio = models.TextField(blank=True)

    # Conservé pour ne pas perdre les données d'éventuels téléversements
    # historiques, mais **non alimenté** : le choix d'avatar se fait par
    # catalogue (`avatar_key`). Voir `apps/accounts/avatars.py` pour le
    # raisonnement — modération, formats, stockage.
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)

    avatar_key = models.CharField(
        max_length=40,
        blank=True,
        help_text="Clé du catalogue (« motif-palette »). Vide = initiales.",
    )

    class Theme(models.TextChoices):
        AUTO = 'AUTO', 'Selon le système'
        LIGHT = 'LIGHT', 'Clair'
        DARK = 'DARK', 'Sombre'

    theme = models.CharField(
        max_length=10,
        choices=Theme.choices,
        default=Theme.AUTO,
        help_text="Préférence d'affichage, rattachée au compte plutôt qu'au "
                  "navigateur : elle suit l'apprenant d'un poste à l'autre.",
    )

    # Une seule classe active par apprenant : le déblocage de chapitre reste
    # non ambigu, un seul formateur donne le tempo. Vide = apprenant autonome,
    # qui progresse alors en rythme libre (cf. apps.progression.services).
    cohort = models.ForeignKey(
        'cohorts.Cohort',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='members',
    )

    total_points = models.IntegerField(default=0)
    level = models.IntegerField(default=1)
    anonymized_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Date d'exercice du droit à l'effacement (RGPD)."
    )
    terms_accepted_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Date d'acceptation de la politique de confidentialité et "
                  "des CGU à l'inscription. Preuve du consentement (RGPD)."
    )
    timezone = models.CharField(max_length=50, default='Europe/Paris')
    github_username = models.CharField(max_length=100, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'accounts_profile'
        verbose_name = 'User Profile'
        verbose_name_plural = 'User Profiles'

    def __str__(self):
        return f"Profile of {self.user.email}"

    def calculate_level(self):
        """Calculate user level based on total points (100 points per level).

        Level 1 = 0-99 pts, level 2 = 100-199 pts, etc.
        """
        return 1 + max(0, self.total_points) // 100

    def add_points(self, points, reason=''):
        """Add points to user profile and update level.

        Prefer ``apps.gamification.services.award_points`` : celui-ci passe par
        le grand livre et garantit qu'une même source ne crédite qu'une fois.
        Cette méthode reste pour les ajustements directs (admin, tests).
        """
        self.total_points += points
        self.level = self.calculate_level()
        self.save()

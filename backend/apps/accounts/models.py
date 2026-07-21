"""
User models for the learning platform.
Custom User model with UUID primary key and role-based access.
"""
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.db import models
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
    ROLE_CHOICES = [
        ('LEARNER', 'Apprenant'),
        ('TRAINER', 'Formateur'),
        ('ADMIN', 'Administrateur'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True, db_index=True)
    first_name = models.CharField(max_length=150, blank=True)
    last_name = models.CharField(max_length=150, blank=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='LEARNER', db_index=True)

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
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)
    total_points = models.IntegerField(default=0)
    level = models.IntegerField(default=1)
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

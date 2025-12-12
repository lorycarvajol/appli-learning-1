"""
Tests for User and Profile models.
"""
import pytest
from django.contrib.auth import get_user_model

User = get_user_model()


@pytest.mark.django_db
class TestUserModel:
    """Test User model."""

    def test_create_user(self):
        """Test creating a regular user."""
        user = User.objects.create_user(
            email='test@example.com',
            password='testpass123',
            first_name='Test',
            last_name='User'
        )

        assert user.email == 'test@example.com'
        assert user.check_password('testpass123')
        assert user.role == 'LEARNER'
        assert user.is_active is True
        assert user.is_staff is False
        assert user.full_name == 'Test User'

    def test_create_superuser(self):
        """Test creating a superuser."""
        user = User.objects.create_superuser(
            email='admin@example.com',
            password='adminpass123',
            first_name='Admin',
            last_name='User'
        )

        assert user.is_staff is True
        assert user.is_superuser is True
        assert user.role == 'ADMIN'

    def test_user_profile_created_automatically(self):
        """Test that profile is created when user is created."""
        user = User.objects.create_user(
            email='test@example.com',
            password='testpass123'
        )

        assert hasattr(user, 'profile')
        assert user.profile.total_points == 0
        assert user.profile.level == 1

    def test_user_str(self):
        """Test user string representation."""
        user = User.objects.create_user(
            email='test@example.com',
            password='testpass123'
        )

        assert str(user) == 'test@example.com'

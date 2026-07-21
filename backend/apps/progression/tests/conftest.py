"""Fixtures partagées des tests de progression."""
import pytest
from rest_framework.test import APIClient

from apps.accounts.models import User
from apps.cohorts.models import Cohort
from apps.courses.models import Chapter, Lesson

TEST_PASSWORD = 'fixture-pwd-not-a-real-secret'


@pytest.fixture
def client_for():
    def _build(user):
        client = APIClient()
        client.force_authenticate(user=user)
        return client
    return _build


@pytest.fixture
def learner():
    """Apprenant **autonome** : sans classe, donc au rythme libre."""
    return User.objects.create_user(
        email='eleve@example.com', password=TEST_PASSWORD, first_name='Eve',
    )


@pytest.fixture
def trainer():
    return User.objects.create_user(
        email='formateur@example.com', password=TEST_PASSWORD,
        role=User.Role.TRAINER,
    )


@pytest.fixture
def cohort(trainer):
    return Cohort.objects.create(name='Promo 2026', trainer=trainer)


@pytest.fixture
def cohort_learner(cohort):
    """Apprenant **en classe** : c'est le formateur qui ouvre les chapitres."""
    user = User.objects.create_user(
        email='encadre@example.com', password=TEST_PASSWORD, first_name='Léo',
    )
    user.profile.cohort = cohort
    user.profile.save(update_fields=['cohort'])
    return user


@pytest.fixture
def parcours():
    """Trois chapitres publiés de deux leçons chacun.

    Trois suffisent à distinguer « le premier est ouvert » de « le suivant
    s'ouvre quand le précédent est fini » — avec deux, les deux règles se
    confondent.
    """
    chapters = []
    for index in range(1, 4):
        chapter = Chapter.objects.create(
            title=f'Chapitre {index}', slug=f'chapitre-{index}',
            order_index=index, estimated_duration=60, is_published=True,
        )
        for lesson_index in range(1, 3):
            Lesson.objects.create(
                chapter=chapter,
                title=f'Leçon {index}.{lesson_index}',
                slug=f'lecon-{index}-{lesson_index}',
                order_index=lesson_index,
                lesson_type='THEORY',
                points=10,
                is_published=True,
            )
        chapters.append(chapter)
    return chapters

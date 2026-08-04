"""
Désactivation de l'exécution de code (`settings.CODE_EXECUTION_ENABLED`).

Le drapeau existe pour pouvoir ouvrir la plateforme sur un **hôte mutualisé**
sans monter `/var/run/docker.sock` dans le worker Celery — qui contrôle ce
worker contrôle le démon Docker, donc l'hôte, donc tous les projets qui y
vivent.

Deux effets, et le second est celui qu'on oublie :

1. l'API refuse la soumission proprement, au lieu de laisser une tâche partir
   vers un worker sans démon Docker et échouer en `DockerException` ;
2. les leçons d'exercice cessent de conditionner l'ouverture du chapitre
   suivant — sinon un exercice devenu insoumettable resterait éternellement
   inachevé, et le chapitre 1 comptant 8 exercices sur 18 leçons, **aucun
   apprenant au rythme libre n'atteindrait le chapitre 2**.
"""
from unittest.mock import patch

import pytest
from django.test import override_settings
from rest_framework.test import APIClient

from apps.accounts.models import User
from apps.courses.models import Chapter, Exercise, Lesson
from apps.progression.models import UserProgress
from apps.progression.services import accessible_chapter_ids

pytestmark = pytest.mark.django_db

TEST_PASSWORD = 'fixture-pwd-not-a-real-secret'


@pytest.fixture
def learner():
    return User.objects.create_user(
        email='eleve@example.com', password=TEST_PASSWORD, first_name='Eve'
    )


@pytest.fixture
def client(learner):
    api = APIClient()
    api.force_authenticate(user=learner)
    return api


@pytest.fixture
def parcours():
    """Deux chapitres ; le premier mêle théorie et exercice."""
    chapitre1 = Chapter.objects.create(
        title='HTML', slug='html', order_index=1,
        estimated_duration=60, is_published=True,
    )
    theorie = Lesson.objects.create(
        chapter=chapitre1, title='Les balises', slug='les-balises',
        lesson_type='THEORY', order_index=1, content='…', is_published=True,
    )
    exercice = Lesson.objects.create(
        chapter=chapitre1, title='Exercice', slug='exercice-html',
        lesson_type='EXERCISE', order_index=2, content='', is_published=True,
    )
    Exercise.objects.create(
        lesson=exercice, instructions='…', starter_code='',
        solution='', tests={'tests': []},
    )
    chapitre2 = Chapter.objects.create(
        title='CSS', slug='css', order_index=2,
        estimated_duration=60, is_published=True,
    )
    return chapitre1, chapitre2, theorie, exercice


# ---------------------------------------------------------------------------
# 1. L'API refuse la soumission
# ---------------------------------------------------------------------------

@override_settings(CODE_EXECUTION_ENABLED=False)
def test_la_soumission_est_refusee_avec_un_message_explicite(client, parcours):
    _, _, _, exercice = parcours
    exercise_id = exercice.exercise.id

    with patch('apps.validation.views.run_code_validation') as tache:
        reponse = client.post(
            f'/api/validation/exercises/{exercise_id}/submit/',
            {'code': 'print(1)'}, format='json',
        )

    assert reponse.status_code == 503
    # Rien ne doit partir en file : le worker n'a pas de démon Docker.
    tache.apply_async.assert_not_called()

    corps = reponse.json()
    assert corps['success'] is False
    # Le message doit rassurer sur la progression, pas ressembler à une panne.
    assert 'progression' in corps['error']


@override_settings(CODE_EXECUTION_ENABLED=True)
def test_la_soumission_passe_quand_l_execution_est_active(client, parcours):
    """Le garde-fou ne doit pas gêner une instance correctement isolée."""
    _, _, _, exercice = parcours
    exercise_id = exercice.exercise.id

    with patch('apps.validation.views.run_code_validation') as tache:
        tache.apply_async.return_value.id = 'tache-1'
        reponse = client.post(
            f'/api/validation/exercises/{exercise_id}/submit/',
            {'code': 'print(1)'}, format='json',
        )

    assert reponse.status_code == 202
    tache.apply_async.assert_called_once()


# ---------------------------------------------------------------------------
# 2. La progression ne se bloque pas
# ---------------------------------------------------------------------------

@override_settings(CODE_EXECUTION_ENABLED=False)
def test_un_exercice_insoumettable_ne_bloque_pas_le_chapitre_suivant(
    learner, parcours
):
    """Le cœur du piège : sans cette règle, le parcours se referme sur tous."""
    chapitre1, chapitre2, theorie, _ = parcours

    UserProgress.objects.create(
        user=learner, lesson=theorie,
        status=UserProgress.ProgressStatus.COMPLETED,
    )

    accessibles = accessible_chapter_ids(learner)
    assert chapitre2.id in accessibles, (
        "Le chapitre 2 doit s'ouvrir : seule la théorie était exigible, "
        "l'exercice ne pouvant plus être soumis."
    )


@override_settings(CODE_EXECUTION_ENABLED=True)
def test_l_exercice_reste_exigible_quand_l_execution_est_active(
    learner, parcours
):
    """La règle d'origine ne doit pas être affaiblie au passage."""
    chapitre1, chapitre2, theorie, exercice = parcours

    UserProgress.objects.create(
        user=learner, lesson=theorie,
        status=UserProgress.ProgressStatus.COMPLETED,
    )

    assert chapitre2.id not in accessible_chapter_ids(learner)

    UserProgress.objects.create(
        user=learner, lesson=exercice,
        status=UserProgress.ProgressStatus.COMPLETED,
    )

    assert chapitre2.id in accessible_chapter_ids(learner)

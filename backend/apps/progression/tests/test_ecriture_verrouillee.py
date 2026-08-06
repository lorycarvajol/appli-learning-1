"""
Le verrou de chapitre s'applique aussi aux **écritures**.

⚠️ Il ne protégeait que la lecture. `LessonViewSet.retrieve` renvoyait bien
403, mais `mark_completed`, `track_time` et `submit_quiz` acceptaient n'importe
quelle leçon, et `mark_completed` acceptait n'importe quel *type* de leçon —
exercice et quiz compris, dont il créditait les points.

Mesuré sur un compte neuf avant correction : 68 appels à `mark_completed`,
**aucun refusé**, le compte passant de 1 à 4 chapitres accessibles, de 0 à
1485 points et de 0 à 11 badges — sans jamais ouvrir une leçon. Les trois
invariants centraux du projet tombaient ensemble : progression contrôlée par le
formateur, grand livre de points, badges.

Deux règles distinctes en découlent, et il faut les deux :

1. **Le chapitre doit être ouvert** — sinon on agit sur du contenu verrouillé.
2. **Seule la théorie se déclare terminée** — un exercice se valide en passant
   ses tests, un quiz en atteignant son score. Ce sont les deux seuls contenus
   dont la réussite est objectivement vérifiable ; les déclarer terminés
   revenait à s'en attribuer les points sans le travail.
"""
import pytest
from rest_framework.test import APIClient

from apps.accounts.models import User
from apps.courses.models import Chapter, Exercise, Lesson, Quiz
from apps.progression.models import UserProgress
from apps.progression.services import accessible_chapter_ids

pytestmark = pytest.mark.django_db


@pytest.fixture
def apprenant():
    return User.objects.create_user(email='eleve@example.com', password='x' * 14)


@pytest.fixture
def client(apprenant):
    api = APIClient()
    api.force_authenticate(user=apprenant)
    return api


@pytest.fixture
def parcours():
    """Deux chapitres ; le second est verrouillé pour un compte neuf."""
    chapitres = []
    for index, slug in enumerate(['html', 'css'], start=1):
        chapitre = Chapter.objects.create(
            title=slug.upper(), slug=slug, order_index=index,
            estimated_duration=60, is_published=True,
        )
        Lesson.objects.create(
            chapter=chapitre, title='Théorie', slug=f'{slug}-theorie',
            lesson_type='THEORY', order_index=1, content='…',
            points=10, is_published=True,
        )
        exercice = Lesson.objects.create(
            chapter=chapitre, title='Exercice', slug=f'{slug}-exercice',
            lesson_type='EXERCISE', order_index=2, content='',
            points=50, is_published=True,
        )
        Exercise.objects.create(
            lesson=exercice, instructions='…', starter_code='',
            solution='', tests={'tests': []},
        )
        quiz_lecon = Lesson.objects.create(
            chapter=chapitre, title='Quiz', slug=f'{slug}-quiz',
            lesson_type='QUIZ', order_index=3, content='',
            points=30, is_published=True,
        )
        Quiz.objects.create(
            lesson=quiz_lecon, instructions='…',
            questions={'questions': []}, passing_score=70,
        )
        chapitres.append(chapitre)
    return chapitres


# ---------------------------------------------------------------------------
# 1. Le chapitre doit être ouvert
# ---------------------------------------------------------------------------

@pytest.mark.parametrize('route,charge', [
    ('mark_completed', {}),
    ('track_time', {'seconds': 60}),
])
def test_ecrire_sur_un_chapitre_verrouille_est_refuse(client, parcours, route, charge):
    _, verrouille = parcours
    lecon = verrouille.lessons.get(lesson_type='THEORY')

    reponse = client.post(
        f'/api/progression/progress/{route}/',
        {'lesson_id': str(lecon.id), **charge}, format='json',
    )

    assert reponse.status_code == 403
    assert not UserProgress.objects.filter(lesson=lecon).exists()


def test_soumettre_le_quiz_dun_chapitre_verrouille_est_refuse(client, parcours):
    _, verrouille = parcours
    quiz_lecon = verrouille.lessons.get(lesson_type='QUIZ')

    reponse = client.post(
        '/api/progression/progress/submit_quiz/',
        {'lesson_id': str(quiz_lecon.id), 'answers': {}}, format='json',
    )

    assert reponse.status_code == 403


def test_le_chapitre_ouvert_reste_accessible(client, parcours):
    """Le garde-fou ne doit pas gêner l'usage légitime."""
    ouvert, _ = parcours
    lecon = ouvert.lessons.get(lesson_type='THEORY')

    reponse = client.post(
        '/api/progression/progress/mark_completed/',
        {'lesson_id': str(lecon.id)}, format='json',
    )

    assert reponse.status_code == 200


# ---------------------------------------------------------------------------
# 2. Seule la théorie se déclare terminée
# ---------------------------------------------------------------------------

@pytest.mark.parametrize('type_lecon', ['EXERCISE', 'QUIZ'])
def test_un_exercice_ou_un_quiz_ne_se_declare_pas_termine(
    client, apprenant, parcours, type_lecon
):
    """La porte dérobée sur les points : ces deux types ont un critère objectif."""
    ouvert, _ = parcours
    lecon = ouvert.lessons.get(lesson_type=type_lecon)

    reponse = client.post(
        '/api/progression/progress/mark_completed/',
        {'lesson_id': str(lecon.id)}, format='json',
    )

    assert reponse.status_code == 400
    apprenant.profile.refresh_from_db()
    assert apprenant.profile.total_points == 0, "aucun point ne doit être crédité"


def test_le_deverrouillage_en_cascade_est_ferme(client, apprenant, parcours):
    """Le scénario complet, tel qu'il a été mesuré.

    Déclarer terminées *toutes* les leçons ne doit plus ouvrir le chapitre
    suivant : les exercices et les quiz du premier restent inachevés, donc la
    condition d'ouverture au rythme libre n'est pas remplie.
    """
    ouvert, verrouille = parcours

    for lecon in Lesson.objects.filter(is_published=True):
        client.post(
            '/api/progression/progress/mark_completed/',
            {'lesson_id': str(lecon.id)}, format='json',
        )

    assert verrouille.id not in accessible_chapter_ids(apprenant)

    apprenant.profile.refresh_from_db()
    # Seule la théorie du chapitre ouvert : 10 points, pas 90.
    assert apprenant.profile.total_points == 10

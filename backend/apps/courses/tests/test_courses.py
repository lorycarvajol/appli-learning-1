"""
Tests de l'app `courses` — jusqu'ici le seul module backend sans couverture.

Deux familles d'invariants sont verrouillées ici, choisies parce qu'elles ont
un coût réel si elles cassent, pas pour la couverture de ligne :

1. **La normalisation du champ JSONB `tests`.** C'est là que vivait le bug
   `Exercise.total_points` (il itérait les *clés* du dictionnaire `{'tests':…}`
   et levait `AttributeError`, rendant la liste des exercices de l'admin Django
   inaccessible). On vérifie les deux formes qui coexistent en base.

2. **Le masquage du contenu sensible côté apprenant.** La solution d'un
   exercice, ses tests, et les bonnes réponses d'un quiz ne doivent jamais
   sortir de l'API pour un apprenant — sinon la plateforme se contourne en
   lisant les requêtes réseau. Formateurs et admins, eux, voient tout.
"""
import pytest
from rest_framework.test import APIClient

from apps.accounts.models import User
from apps.courses.models import Chapter, Exercise, Lesson, Project, Quiz

pytestmark = pytest.mark.django_db

TEST_PASSWORD = 'fixture-pwd-not-a-real-secret'


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def learner():
    return User.objects.create_user(
        email='eleve@example.com', password=TEST_PASSWORD, first_name='Eve'
    )


@pytest.fixture
def trainer():
    return User.objects.create_user(
        email='formateur@example.com', password=TEST_PASSWORD,
        role=User.Role.TRAINER,
    )


@pytest.fixture
def chapter():
    # order_index=0 : premier chapitre, donc accessible à un apprenant
    # autonome (rythme libre) sans avoir à débloquer quoi que ce soit.
    return Chapter.objects.create(
        title='HTML', slug='html', description='Les bases',
        order_index=0, estimated_duration=60, is_published=True,
    )


@pytest.fixture
def lesson(chapter):
    return Lesson.objects.create(
        chapter=chapter, title='Les balises', slug='les-balises',
        lesson_type='EXERCISE', order_index=0, is_published=True,
    )


@pytest.fixture
def exercise(lesson):
    return Exercise.objects.create(
        lesson=lesson,
        instructions='Écris un titre',
        starter_code='<h1></h1>',
        solution='<h1>Bonjour</h1>',
        language='html',
        # Forme enveloppée `{'tests': [...]}` — celle produite par l'admin.
        tests={'tests': [
            {'name': 'Test 1', 'code': 'assert True', 'points': 10},
            {'name': 'Test 2', 'code': 'assert True', 'points': 5},
        ]},
    )


@pytest.fixture
def quiz(lesson_quiz):
    return Quiz.objects.create(
        lesson=lesson_quiz,
        instructions='Choisis la bonne réponse',
        # Forme **enveloppée** `{'questions': [...]}` — celle produite par les
        # commandes de seed (`load_section_*`). C'est la forme réelle en base ;
        # la tester ici aurait attrapé le bug `Quiz.total_points`.
        questions={'questions': [
            {
                'text': 'Que signifie HTML ?',
                'options': ['a', 'b', 'c'],
                'correct_answer': 0,
                'explanation': 'HyperText Markup Language',
                'points': 2,
            },
        ]},
    )


@pytest.fixture
def lesson_quiz(chapter):
    return Lesson.objects.create(
        chapter=chapter, title='Quiz HTML', slug='quiz-html',
        lesson_type='QUIZ', order_index=1, is_published=True,
    )


def client_for(user):
    client = APIClient()
    client.force_authenticate(user=user)
    return client


# ---------------------------------------------------------------------------
# 1. Normalisation du champ JSONB `tests` (le bug historique)
# ---------------------------------------------------------------------------

def test_test_cases_normalise_la_forme_enveloppee(exercise):
    """`{'tests': [...]}` doit rendre la liste, pas les clés du dictionnaire."""
    cases = exercise.test_cases
    assert isinstance(cases, list)
    assert len(cases) == 2
    assert cases[0]['name'] == 'Test 1'


def test_test_cases_accepte_la_forme_liste_directe(lesson):
    """Forme historique : `[...]` directement, sans enveloppe."""
    ex = Exercise.objects.create(
        lesson=lesson, instructions='x', starter_code='', solution='',
        tests=[{'name': 'T', 'points': 3}],
    )
    assert ex.test_cases == [{'name': 'T', 'points': 3}]


def test_test_cases_ignore_les_entrees_non_dict(lesson):
    """Une entrée mal formée (chaîne, nombre) ne doit pas casser la lecture."""
    ex = Exercise.objects.create(
        lesson=lesson, instructions='x', starter_code='', solution='',
        tests={'tests': [{'name': 'ok', 'points': 1}, 'parasite', 42]},
    )
    assert ex.test_cases == [{'name': 'ok', 'points': 1}]


def test_total_points_somme_sans_lever_sur_la_forme_enveloppee(exercise):
    """Régression directe : cette somme levait `AttributeError`."""
    assert exercise.total_points == 15


def test_total_points_vaut_zero_sans_tests(lesson):
    ex = Exercise.objects.create(
        lesson=lesson, instructions='x', starter_code='', solution='', tests=[],
    )
    assert ex.total_points == 0


def test_quiz_totaux_forme_enveloppee(quiz):
    """Régression `Quiz.total_points` : sur `{'questions': [...]}` la somme
    itérait les clés du dictionnaire et levait `AttributeError`."""
    assert quiz.total_points == 2
    assert quiz.question_count == 1


def test_quiz_totaux_forme_liste_directe(lesson_quiz):
    """L'autre forme historique (`[...]`) doit fonctionner aussi."""
    q = Quiz.objects.create(
        lesson=lesson_quiz,
        questions=[{'text': 'Q', 'points': 5}, {'text': 'Q2', 'points': 3}],
    )
    assert q.total_points == 8
    assert q.question_count == 2


def test_le_serialiseur_de_quiz_rend_une_liste(learner, quiz):
    """Le front fait `Array.isArray(quiz.questions)` : l'API doit donc renvoyer
    une **liste**, jamais le dictionnaire enveloppant brut."""
    response = client_for(learner).get(f'/api/courses/quizzes/{quiz.id}/')
    assert response.status_code == 200
    assert isinstance(response.json()['questions'], list)
    assert len(response.json()['questions']) == 1


def test_chapter_lesson_count(chapter, lesson, lesson_quiz):
    assert chapter.lesson_count == 2


# ---------------------------------------------------------------------------
# 2. Masquage du contenu sensible — exercices
# ---------------------------------------------------------------------------

def test_l_apprenant_ne_recoit_ni_solution_ni_tests(learner, exercise):
    response = client_for(learner).get(f'/api/courses/exercises/{exercise.id}/')

    assert response.status_code == 200
    data = response.json()
    assert 'solution' not in data
    assert 'tests' not in data
    # Le total de points reste exposé (baliser l'effort), mais pas le détail.
    assert data['total_points'] == 15


def test_le_formateur_voit_la_solution_et_les_tests(trainer, exercise):
    response = client_for(trainer).get(f'/api/courses/exercises/{exercise.id}/')

    assert response.status_code == 200
    data = response.json()
    assert data['solution'] == '<h1>Bonjour</h1>'
    assert 'tests' in data


def test_l_exercice_exige_une_authentification(exercise):
    assert APIClient().get(
        f'/api/courses/exercises/{exercise.id}/'
    ).status_code == 401


# ---------------------------------------------------------------------------
# 3. Masquage du contenu sensible — quiz
# ---------------------------------------------------------------------------

def test_l_apprenant_ne_voit_pas_les_bonnes_reponses(learner, quiz):
    response = client_for(learner).get(f'/api/courses/quizzes/{quiz.id}/')

    assert response.status_code == 200
    question = response.json()['questions'][0]
    assert 'correct_answer' not in question
    assert 'explanation' not in question
    # Le texte et les options, eux, sont bien là : on peut répondre.
    assert question['text'] == 'Que signifie HTML ?'
    assert question['options'] == ['a', 'b', 'c']


def test_le_formateur_voit_les_bonnes_reponses(trainer, quiz):
    response = client_for(trainer).get(f'/api/courses/quizzes/{quiz.id}/')

    question = response.json()['questions'][0]
    assert question['correct_answer'] == 0
    assert question['explanation'] == 'HyperText Markup Language'


# ---------------------------------------------------------------------------
# 4. Seul le contenu publié est servi
# ---------------------------------------------------------------------------

def test_un_chapitre_non_publie_est_absent_de_la_liste(learner):
    Chapter.objects.create(
        title='Brouillon', slug='brouillon', description='…',
        order_index=5, estimated_duration=30, is_published=False,
    )
    response = client_for(learner).get('/api/courses/chapters/')

    slugs = [c['slug'] for c in response.json()['results']]
    assert 'brouillon' not in slugs


def test_un_chapitre_non_publie_renvoie_404(learner):
    Chapter.objects.create(
        title='Brouillon', slug='brouillon', description='…',
        order_index=5, estimated_duration=30, is_published=False,
    )
    response = client_for(learner).get('/api/courses/chapters/brouillon/')
    assert response.status_code == 404


def test_un_exercice_de_lecon_non_publiee_est_inaccessible(learner, chapter):
    lesson = Lesson.objects.create(
        chapter=chapter, title='Cachée', slug='cachee',
        lesson_type='EXERCISE', order_index=9, is_published=False,
    )
    ex = Exercise.objects.create(
        lesson=lesson, instructions='x', starter_code='', solution='', tests=[],
    )
    response = client_for(learner).get(f'/api/courses/exercises/{ex.id}/')
    assert response.status_code == 404


def test_un_projet_non_publie_est_absent_de_la_liste(learner, chapter):
    Project.objects.create(
        chapter=chapter, title='Projet caché', slug='cache',
        description='…', requirements='…', is_published=False,
    )
    response = client_for(learner).get('/api/courses/projects/')
    slugs = [p['slug'] for p in response.json()['results']]
    assert 'cache' not in slugs


# ---------------------------------------------------------------------------
# 5. La liste des chapitres expose l'accessibilité
# ---------------------------------------------------------------------------

def test_la_liste_des_chapitres_indique_l_accessibilite(learner, chapter):
    response = client_for(learner).get('/api/courses/chapters/')

    assert response.status_code == 200
    first = response.json()['results'][0]
    assert 'is_accessible' in first
    # Premier chapitre + apprenant autonome ⇒ ouvert d'emblée.
    assert first['is_accessible'] is True

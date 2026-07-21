"""
Tests de la notation des quiz et du suivi du temps.

Deux mécanismes qui ont en commun d'alimenter les points et les badges : s'ils
sont manipulables depuis le client, toute la gamification perd son sens.
"""
import pytest

from apps.courses.models import Lesson, Quiz
from apps.progression.models import UserProgress
from apps.progression.views import MAX_TIME_INCREMENT_SECONDS, _grade_quiz

pytestmark = pytest.mark.django_db


QUESTIONS = [
    {'id': 1, 'question': '2+2 ?', 'options': ['3', '4'], 'correct_answer': '4',
     'explanation': 'Quatre.'},
    {'id': 2, 'question': 'Couleurs primaires ?', 'options': ['rouge', 'bleu', 'vert'],
     'correct_answer': ['rouge', 'bleu'], 'explanation': 'Deux réponses.'},
]


@pytest.fixture
def quiz_lesson(parcours):
    """Une leçon de type quiz, dans le premier chapitre (toujours ouvert)."""
    lesson = Lesson.objects.create(
        chapter=parcours[0], title='Quiz 1', slug='quiz-1', order_index=9,
        lesson_type='QUIZ', points=20, is_published=True,
    )
    quiz = Quiz.objects.create(
        lesson=lesson, questions=QUESTIONS, passing_score=70,
    )
    return lesson, quiz


# ---------------------------------------------------------------------------
# Notation : le barème ne vient jamais du client
# ---------------------------------------------------------------------------

def test_toutes_les_reponses_justes_donnent_100(quiz_lesson):
    _, quiz = quiz_lesson

    score, passed, details = _grade_quiz(quiz, {'1': '4', '2': ['rouge', 'bleu']})

    assert score == 100
    assert passed is True
    assert all(d['is_correct'] for d in details)


def test_une_reponse_sur_deux_donne_50_et_echoue(quiz_lesson):
    _, quiz = quiz_lesson

    score, passed, _ = _grade_quiz(quiz, {'1': '4', '2': ['rouge']})

    assert score == 50
    assert passed is False  # seuil à 70


def test_lordre_des_reponses_multiples_est_indifferent(quiz_lesson):
    """Cocher « bleu » puis « rouge » vaut « rouge » puis « bleu » : l'ordre
    d'affichage des options peut être aléatoire."""
    _, quiz = quiz_lesson

    score, _, _ = _grade_quiz(quiz, {'1': '4', '2': ['bleu', 'rouge']})

    assert score == 100


def test_une_reponse_partielle_a_choix_multiple_est_fausse(quiz_lesson):
    """Cocher une seule des deux bonnes cases n'est pas « à moitié juste »."""
    _, quiz = quiz_lesson

    _, _, details = _grade_quiz(quiz, {'2': ['rouge']})

    assert details[1]['is_correct'] is False


def test_une_reponse_en_trop_est_fausse(quiz_lesson):
    _, quiz = quiz_lesson

    _, _, details = _grade_quiz(quiz, {'2': ['rouge', 'bleu', 'vert']})

    assert details[1]['is_correct'] is False


def test_labsence_de_reponse_ne_fait_pas_planter(quiz_lesson):
    """Un quiz soumis vide doit donner zéro, pas une erreur serveur."""
    _, quiz = quiz_lesson

    score, passed, details = _grade_quiz(quiz, {})

    assert score == 0
    assert passed is False
    assert len(details) == 2


def test_un_quiz_sans_question_ne_fait_pas_de_division_par_zero(parcours):
    lesson = Lesson.objects.create(
        chapter=parcours[0], title='Vide', slug='quiz-vide', order_index=8,
        lesson_type='QUIZ', points=0, is_published=True,
    )
    quiz = Quiz.objects.create(lesson=lesson, questions=[], passing_score=70)

    assert _grade_quiz(quiz, {}) == (0, False, [])


def test_les_cles_numeriques_et_textuelles_sont_acceptees(quiz_lesson):
    """Le JSON transmis par le client a des clés chaînes ; un test Python
    passe des entiers. Les deux doivent marcher."""
    _, quiz = quiz_lesson

    par_texte, _, _ = _grade_quiz(quiz, {'1': '4'})
    par_entier, _, _ = _grade_quiz(quiz, {1: '4'})

    assert par_texte == par_entier == 50


# ---------------------------------------------------------------------------
# Soumission via l'API
# ---------------------------------------------------------------------------

def test_soumettre_un_quiz_enregistre_le_score(client_for, learner, quiz_lesson):
    lesson, _ = quiz_lesson

    response = client_for(learner).post('/api/progression/progress/submit_quiz/', {
        'lesson_id': str(lesson.id),
        'answers': {'1': '4', '2': ['rouge', 'bleu']},
    }, format='json')

    assert response.status_code == 200
    assert response.data['score'] == 100

    progress = UserProgress.objects.get(user=learner, lesson=lesson)
    assert progress.score == 100
    assert progress.status == UserProgress.ProgressStatus.COMPLETED


def test_le_client_ne_peut_pas_imposer_son_score(client_for, learner, quiz_lesson):
    """Le score est recalculé côté serveur : l'envoyer ne sert à rien.

    Sans cette garantie, il suffirait d'un appel forgé pour obtenir tous les
    points et les badges qui en dépendent.
    """
    lesson, _ = quiz_lesson

    response = client_for(learner).post('/api/progression/progress/submit_quiz/', {
        'lesson_id': str(lesson.id),
        'answers': {'1': 'mauvaise réponse'},
        'score': 100,
        'is_passed': True,
    }, format='json')

    assert response.data['score'] == 0
    assert UserProgress.objects.get(user=learner, lesson=lesson).score == 0


# ---------------------------------------------------------------------------
# Suivi du temps
# ---------------------------------------------------------------------------

def test_le_temps_sajoute_au_lieu_de_remplacer(client_for, learner, parcours):
    """Deux onglets ouverts sur la même leçon doivent s'additionner. Poser une
    valeur absolue ferait perdre le temps de l'un des deux."""
    lesson = parcours[0].lessons.first()
    url = '/api/progression/progress/track_time/'
    charge = {'lesson_id': str(lesson.id), 'seconds': 30}

    client_for(learner).post(url, charge, format='json')
    client_for(learner).post(url, charge, format='json')

    assert UserProgress.objects.get(user=learner, lesson=lesson).time_spent == 60


def test_un_increment_demesure_est_plafonne(client_for, learner, parcours):
    """Ce compteur alimente les badges de temps : il doit rester crédible.

    Le client émet toutes les 30 s ; une valeur bien supérieure ne peut être
    qu'une dérive d'horloge ou une falsification.
    """
    lesson = parcours[0].lessons.first()

    client_for(learner).post('/api/progression/progress/track_time/', {
        'lesson_id': str(lesson.id), 'seconds': 99999,
    }, format='json')

    progress = UserProgress.objects.get(user=learner, lesson=lesson)
    assert progress.time_spent == MAX_TIME_INCREMENT_SECONDS


@pytest.mark.parametrize('seconds', [0, -60, 'beaucoup', None])
def test_un_increment_invalide_est_refuse(client_for, learner, parcours, seconds):
    lesson = parcours[0].lessons.first()

    response = client_for(learner).post('/api/progression/progress/track_time/', {
        'lesson_id': str(lesson.id), 'seconds': seconds,
    }, format='json')

    assert response.status_code == 400
    assert not UserProgress.objects.filter(user=learner, lesson=lesson).exists()


def test_le_temps_ne_peut_pas_etre_pose_par_un_patch(client_for, learner, parcours):
    """`time_spent` a été retiré de `UserProgressUpdateSerializer` : sinon un
    PATCH permettait de poser un total arbitraire, contournant le plafond."""
    lesson = parcours[0].lessons.first()
    progress = UserProgress.objects.create(user=learner, lesson=lesson, time_spent=10)

    client_for(learner).patch(
        f'/api/progression/progress/{progress.id}/',
        {'time_spent': 99999}, format='json',
    )

    progress.refresh_from_db()
    assert progress.time_spent == 10


def test_ouvrir_une_lecon_cree_sa_progression(client_for, learner, parcours):
    """Effet de bord voulu : lire une leçon de théorie compte comme activité,
    ce qui entretient la série de jours."""
    lesson = parcours[0].lessons.first()

    client_for(learner).post('/api/progression/progress/track_time/', {
        'lesson_id': str(lesson.id), 'seconds': 30,
    }, format='json')

    progress = UserProgress.objects.get(user=learner, lesson=lesson)
    assert progress.status == UserProgress.ProgressStatus.IN_PROGRESS

"""
Vue d'ensemble du tableau de bord.

⚠️ Le chiffre affiché ne mesurait pas ce qu'il annonçait. Le client calculait
`terminées / (terminées + en cours)` sur les seules leçons **déjà touchées** :
une première leçon terminée donnait **100 % de progression globale**, et
ouvrir une leçon *faisait baisser* le pourcentage. Le dénominateur réel — le
nombre de leçons publiées — n'existait nulle part côté client.

Les tests ci-dessous fixent donc d'abord le dénominateur, puis les deux pièges
qui l'accompagnent : le périmètre de publication et la moyenne des scores.
"""
import pytest
from django.db import connection
from django.test.utils import CaptureQueriesContext
from rest_framework.test import APIClient

from apps.accounts.models import User
from apps.courses.models import Chapter, Lesson
from apps.progression.models import UserProgress

pytestmark = pytest.mark.django_db

URL = '/api/progression/progress/overview/'

TEST_PASSWORD = 'fixture-pwd-not-a-real-secret'


@pytest.fixture
def apprenant():
    return User.objects.create_user(email='eleve@example.com', password=TEST_PASSWORD)


@pytest.fixture
def client(apprenant):
    api = APIClient()
    api.force_authenticate(user=apprenant)
    return api


def make_chapter(slug, order_index, lessons=3, published=True):
    chapitre = Chapter.objects.create(
        title=slug.upper(), slug=slug, order_index=order_index,
        estimated_duration=60, is_published=published,
    )
    for position in range(1, lessons + 1):
        Lesson.objects.create(
            chapter=chapitre, title=f'Leçon {position}',
            slug=f'{slug}-{position}', lesson_type='THEORY',
            order_index=position, content='…', points=10, is_published=True,
        )
    return chapitre


def terminer(apprenant, lesson, score=None):
    return UserProgress.objects.create(
        user=apprenant, lesson=lesson, score=score,
        status=UserProgress.ProgressStatus.COMPLETED,
    )


# ---------------------------------------------------------------------------
# Le dénominateur
# ---------------------------------------------------------------------------

def test_le_pourcentage_se_compte_sur_tout_le_programme(client, apprenant):
    chapitre = make_chapter('html', 1, lessons=10)
    terminer(apprenant, chapitre.lessons.first())

    payload = client.get(URL).json()['lessons']

    # L'ancien calcul (« terminées / touchées ») aurait dit 100 %.
    assert payload == {
        'total': 10, 'completed': 1, 'in_progress': 0, 'percent': 10
    }


def test_ouvrir_une_lecon_ne_fait_pas_baisser_la_progression(client, apprenant):
    """Le symptôme le plus visible de l'ancien calcul.

    Une leçon en cours entrait au dénominateur sans entrer au numérateur : la
    barre reculait au moment précis où l'apprenant se remettait au travail.
    """
    chapitre = make_chapter('html', 1, lessons=4)
    lecons = list(chapitre.lessons.order_by('order_index'))
    terminer(apprenant, lecons[0])

    avant = client.get(URL).json()['lessons']['percent']

    UserProgress.objects.create(
        user=apprenant, lesson=lecons[1],
        status=UserProgress.ProgressStatus.IN_PROGRESS,
    )
    apres = client.get(URL).json()['lessons']

    assert apres['percent'] == avant == 25
    assert apres['in_progress'] == 1


def test_un_parcours_vierge_vaut_zero_et_non_une_division_par_zero(client):
    assert client.get(URL).json()['lessons'] == {
        'total': 0, 'completed': 0, 'in_progress': 0, 'percent': 0
    }


# ---------------------------------------------------------------------------
# Le périmètre : exactement celui de `next_lesson`
# ---------------------------------------------------------------------------

def test_le_contenu_non_publie_est_hors_du_compte(client):
    make_chapter('html', 1, lessons=2)
    make_chapter('brouillon', 2, lessons=5, published=False)
    Lesson.objects.filter(slug='html-2').update(is_published=False)

    payload = client.get(URL).json()

    # Une seule leçon publiée dans un chapitre publié.
    assert payload['lessons']['total'] == 1
    assert [c['slug'] for c in payload['chapters']] == ['html']


def test_le_meme_perimetre_que_le_bloc_continuer_l_apprentissage(client, apprenant):
    """Les deux blocs se contrediraient sinon, sur le même écran.

    `next_lesson` filtre sur `is_published` de la leçon **et** de son chapitre ;
    `Chapter.lesson_count`, lui, compte tout. Utiliser ce dernier ferait dire au
    total « 7 leçons » quand le parcours n'en propose que 2.
    """
    make_chapter('html', 1, lessons=2)
    Lesson.objects.create(
        chapter=Chapter.objects.get(slug='html'), title='Cachée',
        slug='html-cachee', lesson_type='THEORY', order_index=99,
        content='…', points=10, is_published=False,
    )

    total = client.get(URL).json()['lessons']['total']
    suivante = client.get('/api/progression/progress/next_lesson/').json()

    assert total == 2 == suivante['chapter_progress']['total']


# ---------------------------------------------------------------------------
# Le détail par chapitre
# ---------------------------------------------------------------------------

def test_chaque_chapitre_porte_son_propre_avancement(client, apprenant):
    html = make_chapter('html', 1, lessons=4)
    make_chapter('css', 2, lessons=2)
    for lecon in html.lessons.order_by('order_index')[:3]:
        terminer(apprenant, lecon)

    chapitres = client.get(URL).json()['chapters']

    assert [c['slug'] for c in chapitres] == ['html', 'css']
    assert (chapitres[0]['completed'], chapitres[0]['percent']) == (3, 75)
    assert (chapitres[1]['completed'], chapitres[1]['percent']) == (0, 0)


def test_les_chapitres_verrouilles_restent_listes(client):
    """Même règle que le sommaire : on montre la suite, on ne l'ouvre pas.

    Masquer les chapitres verrouillés priverait l'apprenant de la vue
    d'ensemble qui lui donne envie d'avancer.
    """
    make_chapter('html', 1, lessons=2)
    make_chapter('css', 2, lessons=2)

    chapitres = client.get(URL).json()['chapters']

    assert len(chapitres) == 2
    assert chapitres[0]['is_accessible'] is True   # rythme libre : le 1 s'ouvre
    assert chapitres[1]['is_accessible'] is False


# ---------------------------------------------------------------------------
# La moyenne des scores
# ---------------------------------------------------------------------------

def test_la_moyenne_ignore_les_lecons_sans_note(client, apprenant):
    """Une leçon de théorie n'a rien à noter — son `score` est nul.

    Le tableau de bord les comptait comme des zéros : deux quiz parfaits et
    huit leçons lues affichaient « 20 % de score moyen », ce qu'un apprenant
    lit comme un échec.
    """
    chapitre = make_chapter('html', 1, lessons=4)
    lecons = list(chapitre.lessons.order_by('order_index'))
    terminer(apprenant, lecons[0], score=100)
    terminer(apprenant, lecons[1], score=80)
    terminer(apprenant, lecons[2])  # théorie : aucune note

    payload = client.get(URL).json()

    assert payload['average_score'] == 90
    assert payload['graded_count'] == 2


def test_sans_aucune_note_la_moyenne_est_nulle_pas_zero(client):
    """`None` et `0` ne veulent pas dire la même chose à l'écran."""
    make_chapter('html', 1, lessons=2)

    payload = client.get(URL).json()

    assert payload['average_score'] is None
    assert payload['graded_count'] == 0


# ---------------------------------------------------------------------------
# Cloisonnement et coût
# ---------------------------------------------------------------------------

def test_la_progression_d_un_autre_compte_n_est_pas_comptee(client, apprenant):
    chapitre = make_chapter('html', 1, lessons=4)
    autre = User.objects.create_user(email='autre@example.com', password=TEST_PASSWORD)
    for lecon in chapitre.lessons.all():
        terminer(autre, lecon)

    assert client.get(URL).json()['lessons']['completed'] == 0


def test_la_vue_d_ensemble_exige_une_session():
    assert APIClient().get(URL).status_code == 401


def test_le_cout_ne_depend_pas_du_volume(client, apprenant):
    """Égalité stricte entre deux volumes, plutôt qu'un plafond chiffré.

    Un plafond « assez grand » laisserait passer un N+1 modéré. On compte donc
    deux fois, à dix fois plus de leçons et de lignes de progression.

    On ne fige volontairement **aucun nombre absolu** : la vue s'appuie sur
    `accessible_chapter_ids`, qui matérialise au passage les accès dus au
    rythme libre — un coût partagé avec tout le reste de l'application, et qui
    n'a pas à être verrouillé ici. Ce qui doit rester plat, c'est ce que cette
    vue ajoute.
    """
    chapitre = make_chapter('html', 1, lessons=3)

    client.get(URL)  # première passe : matérialise les accès du rythme libre

    with CaptureQueriesContext(connection) as petit_volume:
        client.get(URL)

    for position in range(4, 34):
        lecon = Lesson.objects.create(
            chapter=chapitre, title=f'Leçon {position}',
            slug=f'html-{position}', lesson_type='THEORY',
            order_index=position, content='…', points=10, is_published=True,
        )
        terminer(apprenant, lecon, score=70)

    with CaptureQueriesContext(connection) as gros_volume:
        client.get(URL)

    assert len(gros_volume) == len(petit_volume)

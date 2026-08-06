"""
« Continuer l'apprentissage » : quelle leçon proposer.

⚠️ Deux défauts corrigés, constatés sur la base de développement.

1. **La leçon la plus récemment entamée gagnait sur l'ordre du programme.** Un
   compte ayant ouvert une leçon du dernier chapitre — ce que fait tout auteur
   ou formateur qui relit son contenu — se voyait proposer « Mettre son site en
   ligne » avec un chapitre 1 intact.
2. **Le verrou de chapitre n'était pas consulté** : le bouton « Commencer »
   pouvait mener droit à un 403.
"""
import pytest
from rest_framework.test import APIClient

from apps.accounts.models import User
from apps.cohorts.models import Cohort
from apps.courses.models import Chapter, Lesson
from apps.progression.models import ChapterAccess, UserProgress
from apps.progression.services import unlock_chapter_for

pytestmark = pytest.mark.django_db

URL = '/api/progression/progress/next_lesson/'

TEST_PASSWORD = 'fixture-pwd-not-a-real-secret'


@pytest.fixture
def apprenant():
    return User.objects.create_user(email='eleve@example.com', password=TEST_PASSWORD)


@pytest.fixture
def client(apprenant):
    api = APIClient()
    api.force_authenticate(user=apprenant)
    return api


@pytest.fixture
def parcours():
    """Quatre chapitres de deux leçons, comme le vrai programme."""
    chapitres = []
    for index, slug in enumerate(['html', 'css', 'js', 'vitrine'], start=1):
        chapitre = Chapter.objects.create(
            title=slug.upper(), slug=slug, order_index=index,
            estimated_duration=60, is_published=True,
        )
        for position in (1, 2):
            Lesson.objects.create(
                chapter=chapitre, title=f'{slug} {position}',
                slug=f'{slug}-{position}', lesson_type='THEORY',
                order_index=position, content='…', points=10, is_published=True,
            )
        chapitres.append(chapitre)
    return chapitres


def entamer(apprenant, slug):
    return UserProgress.objects.create(
        user=apprenant, lesson=Lesson.objects.get(slug=slug),
        status=UserProgress.ProgressStatus.IN_PROGRESS,
    )


def terminer(apprenant, slug):
    return UserProgress.objects.create(
        user=apprenant, lesson=Lesson.objects.get(slug=slug),
        status=UserProgress.ProgressStatus.COMPLETED,
    )


# ---------------------------------------------------------------------------
# L'ordre du parcours fait autorité
# ---------------------------------------------------------------------------

def test_un_compte_neuf_demarre_par_la_premiere_lecon(client, parcours):
    payload = client.get(URL).json()

    assert payload['lesson']['slug'] == 'html-1'
    assert payload['chapter']['slug'] == 'html'
    assert payload['is_resuming'] is False


def test_une_lecon_entamee_plus_loin_ne_double_pas_le_debut(client, apprenant, parcours):
    """Le défaut d'origine, dans sa forme exacte.

    Le dernier chapitre a été ouvert (un auteur qui relit son contenu), le
    premier est intact : c'est par le premier qu'il faut reprendre.
    """
    for chapitre in parcours[1:]:
        unlock_chapter_for(apprenant, chapitre)
    entamer(apprenant, 'vitrine-2')

    payload = client.get(URL).json()

    assert payload['lesson']['slug'] == 'html-1'


def test_on_reprend_la_premiere_lecon_inachevee(client, apprenant, parcours):
    terminer(apprenant, 'html-1')
    entamer(apprenant, 'html-2')

    payload = client.get(URL).json()

    assert payload['lesson']['slug'] == 'html-2'
    assert payload['is_resuming'] is True


def test_un_trou_dans_le_parcours_se_comble_avant_la_suite(client, apprenant, parcours):
    """Terminer plus loin ne fait pas disparaître ce qui a été sauté."""
    unlock_chapter_for(apprenant, parcours[1])
    terminer(apprenant, 'html-2')
    entamer(apprenant, 'css-1')

    assert client.get(URL).json()['lesson']['slug'] == 'html-1'


# ---------------------------------------------------------------------------
# Le verrou de chapitre
# ---------------------------------------------------------------------------

def test_jamais_une_lecon_de_chapitre_verrouille(client, apprenant, parcours):
    """Sinon « Commencer » mène droit à un 403."""
    terminer(apprenant, 'html-1')
    terminer(apprenant, 'html-2')

    payload = client.get(URL).json()

    # Au rythme libre, terminer le chapitre 1 ouvre le 2 : c'est donc `css-1`.
    assert payload['lesson']['slug'] == 'css-1'
    assert ChapterAccess.objects.filter(
        user=apprenant, chapter=parcours[1], is_unlocked=True
    ).exists()


def test_le_rythme_libre_ouvre_le_premier_chapitre_a_un_compte_neuf(client, apprenant, parcours):
    """Le tableau de bord d'un compte neuf doit proposer quelque chose.

    L'accès est matérialisé par `ensure_self_paced_access`, appelé au travers
    de `accessible_chapter_ids` : sans lui, la vue proposait une leçon que
    l'apprenant n'avait pas encore le droit d'ouvrir.
    """
    assert not ChapterAccess.objects.filter(user=apprenant).exists()

    assert client.get(URL).json()['lesson']['slug'] == 'html-1'
    assert ChapterAccess.objects.filter(
        user=apprenant, chapter=parcours[0], is_unlocked=True
    ).exists()


def test_en_classe_sans_chapitre_ouvert_on_le_dit(client, apprenant, parcours):
    """Un apprenant dont le formateur n'a rien ouvert n'a rien à commencer.

    `locked` le distingue d'un contenu absent : le message affiché n'est pas
    le même, et « aucune leçon disponible » serait faux.
    """
    formateur = User.objects.create_user(
        email='prof@example.com', password=TEST_PASSWORD, role=User.Role.TRAINER,
    )
    classe = Cohort.objects.create(name='Promo', trainer=formateur)
    apprenant.profile.cohort = classe
    apprenant.profile.save(update_fields=['cohort'])

    payload = client.get(URL).json()

    assert payload['lesson'] is None
    assert payload['locked'] is True
    assert payload['all_completed'] is False


def test_tout_ce_qui_est_ouvert_est_fini_mais_le_parcours_continue(client, apprenant, parcours):
    """« Parcours terminé » serait faux : trois chapitres restent à voir."""
    formateur = User.objects.create_user(
        email='prof@example.com', password=TEST_PASSWORD, role=User.Role.TRAINER,
    )
    classe = Cohort.objects.create(name='Promo', trainer=formateur)
    apprenant.profile.cohort = classe
    apprenant.profile.save(update_fields=['cohort'])
    unlock_chapter_for(apprenant, parcours[0])

    terminer(apprenant, 'html-1')
    terminer(apprenant, 'html-2')

    payload = client.get(URL).json()

    assert payload['lesson'] is None
    assert payload['all_completed'] is False
    assert payload['locked'] is True


def test_parcours_reellement_termine(client, apprenant, parcours):
    for chapitre in parcours:
        unlock_chapter_for(apprenant, chapitre)
    for lecon in Lesson.objects.all():
        UserProgress.objects.create(
            user=apprenant, lesson=lecon,
            status=UserProgress.ProgressStatus.COMPLETED,
        )

    payload = client.get(URL).json()

    assert payload['all_completed'] is True
    assert payload['locked'] is False


def test_sans_contenu_publie_ce_n_est_ni_termine_ni_verrouille(client):
    payload = client.get(URL).json()

    assert payload == {'lesson': None, 'all_completed': False, 'locked': False}


# ---------------------------------------------------------------------------
# Formateurs et administrateurs
# ---------------------------------------------------------------------------

def test_un_formateur_voit_aussi_le_debut_du_parcours(parcours):
    """Il n'a pas de `ChapterAccess`, mais tout lui est ouvert.

    C'est précisément le compte qui déclenchait le défaut : il relit une leçon
    du dernier chapitre, et son tableau de bord l'y renvoyait indéfiniment.
    """
    formateur = User.objects.create_user(
        email='prof@example.com', password=TEST_PASSWORD, role=User.Role.TRAINER,
    )
    UserProgress.objects.create(
        user=formateur, lesson=Lesson.objects.get(slug='vitrine-1'),
        status=UserProgress.ProgressStatus.IN_PROGRESS,
    )

    api = APIClient()
    api.force_authenticate(user=formateur)

    assert api.get(URL).json()['lesson']['slug'] == 'html-1'

"""
Tests du classement.

Le classement est la **seule page où un apprenant voit les autres**. Les
invariants vérifiés ici sont donc d'abord des invariants de discrétion — rien
d'identifiant ne doit sortir de l'API — puis des invariants d'exactitude du
rang. Chacun a été validé par sabotage : retirer le filtre correspondant fait
rougir exactement le test attendu.
"""
import json

import pytest
from django.utils import timezone
from rest_framework.test import APIClient

from apps.accounts.models import Profile, User
from apps.cohorts.models import Cohort
from apps.gamification.leaderboard import build_leaderboard, display_name
from apps.gamification.models import Badge, UserBadge

pytestmark = pytest.mark.django_db

TEST_PASSWORD = 'fixture-pwd-not-a-real-secret'

URL = '/api/gamification/leaderboard/'


def make_learner(email, points=0, first_name='Eve', last_name='Martin',
                 role=User.Role.LEARNER, **profil):
    """Crée un apprenant et pose son solde directement.

    On écrit `total_points` sans passer par `award_points` : ce module ne
    calcule aucun point, il ordonne des soldes. Passer par le grand livre
    n'ajouterait ici qu'un décor.
    """
    user = User.objects.create_user(
        email=email, password=TEST_PASSWORD,
        first_name=first_name, last_name=last_name, role=role,
    )
    Profile.objects.filter(user=user).update(total_points=points, **profil)
    user.refresh_from_db()
    return user


@pytest.fixture
def me():
    return make_learner('moi@example.com', points=100, first_name='Lory',
                        last_name='Carvajol')


@pytest.fixture
def api(me):
    client = APIClient()
    client.force_authenticate(user=me)
    return client


# ---------------------------------------------------------------------------
# Discrétion : ce qui ne doit jamais sortir
# ---------------------------------------------------------------------------

def test_aucun_email_ne_sort_du_classement(api, me):
    make_learner('camarade@example.com', points=500)

    response = api.get(URL)
    brut = json.dumps(response.json())

    assert response.status_code == 200
    assert 'camarade@example.com' not in brut
    assert 'moi@example.com' not in brut
    assert '@' not in brut


def test_le_nom_de_famille_est_reduit_a_son_initiale(api):
    make_learner('camarade@example.com', points=500,
                 first_name='Camille', last_name='Durand')

    entries = api.get(URL).json()['entries']
    noms = [entry['display_name'] for entry in entries]

    assert 'Camille D.' in noms
    assert 'Camille Durand' not in noms


def test_meme_son_propre_nom_est_reduit(api):
    """Une seule règle d'affichage, sans exception pour soi.

    Faire une exception donnerait un nom complet dans la réponse — donc dans
    une réponse que rien n'empêche de partager — pour un gain nul : le client
    identifie sa propre ligne par `is_me`.
    """
    ma_ligne = next(e for e in api.get(URL).json()['entries'] if e['is_me'])
    assert ma_ligne['display_name'] == 'Lory C.'


def test_un_compte_sans_identite_est_simplement_apprenant():
    anonyme = User.objects.create_user(
        email='vide@example.com', password=TEST_PASSWORD,
    )
    assert display_name(anonyme) == 'Apprenant'


# ---------------------------------------------------------------------------
# Qui figure au classement
# ---------------------------------------------------------------------------

def test_les_comptes_anonymises_desactives_et_non_apprenants_sont_exclus(api, me):
    make_learner('anonymise@example.com', points=900,
                 anonymized_at=timezone.now())

    desactive = make_learner('desactive@example.com', points=800)
    User.objects.filter(pk=desactive.pk).update(is_active=False)

    make_learner('formateur@example.com', points=700, role=User.Role.TRAINER)

    payload = api.get(URL).json()

    assert [e['points'] for e in payload['entries']] == [100]
    assert payload['total_participants'] == 1


def test_le_retrait_volontaire_est_respecte(api):
    make_learner('discret@example.com', points=900, show_in_leaderboard=False)

    payload = api.get(URL).json()

    assert payload['total_participants'] == 1
    assert 900 not in [e['points'] for e in payload['entries']]


def test_un_compte_retire_ne_voit_plus_son_propre_rang(me):
    """Sinon le retrait serait cosmétique : on garderait le bénéfice du
    classement (savoir où l'on se situe) tout en refusant d'y figurer."""
    Profile.objects.filter(user=me).update(show_in_leaderboard=False)
    me.refresh_from_db()

    payload = build_leaderboard(me)

    assert payload['participating'] is False
    assert payload['me'] is None


def test_sans_le_moindre_point_on_n_est_pas_classe():
    debutant = make_learner('debutant@example.com', points=0)

    payload = build_leaderboard(debutant)

    assert payload['participating'] is False
    assert payload['total_participants'] == 0


# ---------------------------------------------------------------------------
# Exactitude du rang
# ---------------------------------------------------------------------------

def test_les_ex_aequo_partagent_leur_rang(api):
    make_learner('a@example.com', points=500)
    make_learner('b@example.com', points=500)
    make_learner('c@example.com', points=300)

    rangs = [(e['rank'], e['points']) for e in api.get(URL).json()['entries']]

    assert rangs == [(1, 500), (1, 500), (3, 300), (4, 100)]


def test_mon_rang_est_renvoye_meme_hors_du_tableau(me):
    """C'est le vingt-et-unième qui a le plus besoin de savoir où il en est."""
    for index in range(5):
        make_learner(f'devant{index}@example.com', points=1000 + index)

    payload = build_leaderboard(me, limit=2)

    assert len(payload['entries']) == 2
    assert payload['me']['rank'] == 6
    assert payload['me']['points'] == 100


def test_le_rang_personnel_suit_la_regle_des_ex_aequo(me):
    make_learner('a@example.com', points=500)
    make_learner('b@example.com', points=500)

    # Deux apprenants strictement devant : le rang est 3, pas 2.
    assert build_leaderboard(me)['me']['rank'] == 3


def test_le_nombre_de_badges_accompagne_chaque_ligne(api, me):
    badge = Badge.objects.create(
        code='premier-pas', name='Premier pas', description='…',
        rule_type=Badge.RuleType.LESSONS_COMPLETED, criteria={'count': 1},
    )
    UserBadge.objects.create(user=me, badge=badge)

    ma_ligne = next(e for e in api.get(URL).json()['entries'] if e['is_me'])
    assert ma_ligne['badges_count'] == 1


# ---------------------------------------------------------------------------
# Portées
# ---------------------------------------------------------------------------

def test_la_portee_classe_ne_montre_que_ses_camarades(me):
    formateur = User.objects.create_user(
        email='prof@example.com', password=TEST_PASSWORD,
        role=User.Role.TRAINER,
    )
    classe = Cohort.objects.create(name='Promo 2026', trainer=formateur)

    camarade = make_learner('camarade@example.com', points=400)
    Profile.objects.filter(user__in=[me, camarade]).update(cohort=classe)
    make_learner('etranger@example.com', points=900)

    payload = build_leaderboard(me, scope='cohort')

    assert payload['available'] is True
    assert payload['total_participants'] == 2
    assert 900 not in [e['points'] for e in payload['entries']]


def test_sans_classe_la_portee_classe_explique_au_lieu_de_rendre_un_vide(me):
    payload = build_leaderboard(me, scope='cohort')

    assert payload['available'] is False
    assert payload['reason']
    assert payload['entries'] == []


def test_une_portee_inconnue_retombe_sur_le_classement_global(me):
    assert build_leaderboard(me, scope='n-importe-quoi')['scope'] == 'global'


def test_la_longueur_demandee_est_plafonnee(api):
    for index in range(3):
        make_learner(f'x{index}@example.com', points=200 + index)

    # Un `limit` absurde ne doit ni faire échouer la requête ni servir de
    # levier pour une réponse démesurée.
    assert len(api.get(URL, {'limit': 99999}).json()['entries']) == 4
    assert len(api.get(URL, {'limit': 'abc'}).json()['entries']) == 4
    assert len(api.get(URL, {'limit': 2}).json()['entries']) == 2


def test_le_classement_exige_une_session():
    assert APIClient().get(URL).status_code == 401


# ---------------------------------------------------------------------------
# Coût
# ---------------------------------------------------------------------------

def test_le_cout_ne_depend_pas_du_nombre_d_apprenants(me, django_assert_num_queries):
    """Comparaison à deux volumes plutôt que plafond chiffré.

    Un plafond « assez grand » laisserait passer un N+1 modéré ; l'égalité
    stricte entre deux volumes ne laisse rien passer. C'est la page que toute
    une promo ouvre en même temps.
    """
    for index in range(3):
        make_learner(f'p{index}@example.com', points=100 + index)

    # Instance rechargée avant chaque mesure : sans cela, le profil resterait
    # en cache du premier appel au second, et les deux comptes différeraient
    # d'une requête pour une raison étrangère au volume.
    frais = User.objects.get(pk=me.pk)
    with django_assert_num_queries(5):
        build_leaderboard(frais)

    for index in range(20):
        make_learner(f'q{index}@example.com', points=200 + index)

    frais = User.objects.get(pk=me.pk)
    with django_assert_num_queries(5):
        build_leaderboard(frais)

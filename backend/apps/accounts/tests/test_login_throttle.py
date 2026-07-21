"""
Tests de la limitation des échecs de connexion.

Avant ce garde-fou, la seule limite sur `/api/auth/login/` était le plafond
anonyme global de 100 requêtes par heure : de quoi essayer cent mots de passe
sur un compte, chaque heure, sans être inquiété.

Les tests forcent les réglages de production : `development.py` vide
`DEFAULT_THROTTLE_RATES`, donc rien ne serait limité par défaut.
"""
import pytest
from django.core.cache import cache
from django.test import override_settings
from rest_framework.test import APIClient

from apps.accounts.models import User

pytestmark = pytest.mark.django_db

TEST_PASSWORD = 'fixture-pwd-not-a-real-secret'
MAUVAIS = 'ce-nest-pas-le-bon-mot-de-passe'

#: Réglages de production reconstitués : sans cela, `development.py` désactive
#: toute limitation et les tests passeraient sans rien vérifier.
AVEC_THROTTLE = override_settings(REST_FRAMEWORK={
    'DEFAULT_THROTTLE_RATES': {'login': '3/hour'},
})


@pytest.fixture(autouse=True)
def cache_propre():
    """Le compteur vit dans le cache : deux tests le partageraient sinon."""
    cache.clear()
    yield
    cache.clear()


@pytest.fixture
def eleve():
    return User.objects.create_user(
        email='eve@example.com', password=TEST_PASSWORD, first_name='Eve',
    )


def tenter(email, mot_de_passe):
    return APIClient().post(
        '/api/auth/login/', {'email': email, 'password': mot_de_passe}, format='json',
    )


# ---------------------------------------------------------------------------
# La limite mord
# ---------------------------------------------------------------------------

@AVEC_THROTTLE
def test_les_echecs_repetes_finissent_bloques(eleve):
    """Le cas qu'on veut arrêter : essayer des mots de passe en série."""
    for _ in range(3):
        assert tenter('eve@example.com', MAUVAIS).status_code == 401

    assert tenter('eve@example.com', MAUVAIS).status_code == 429


@AVEC_THROTTLE
def test_changer_la_casse_ne_remet_pas_le_compteur_a_zero(eleve):
    """`User.save()` normalise les emails : `Eve@` et `eve@` sont le même
    compte. Sans normalisation de la clé, varier la casse offrirait un quota
    neuf à chaque fois."""
    for _ in range(3):
        tenter('eve@example.com', MAUVAIS)

    assert tenter('EVE@Example.COM', MAUVAIS).status_code == 429


@AVEC_THROTTLE
def test_un_compte_inexistant_est_limite_aussi(eleve):
    """Sinon l'énumération de comptes redevient gratuite : un attaquant
    distinguerait les emails connus des autres à la vitesse de réponse."""
    for _ in range(3):
        tenter('inconnu@example.com', MAUVAIS)

    assert tenter('inconnu@example.com', MAUVAIS).status_code == 429


# ---------------------------------------------------------------------------
# La limite ne mord pas les innocents
# ---------------------------------------------------------------------------

@AVEC_THROTTLE
def test_une_classe_entiere_derriere_la_meme_ip_nest_pas_bloquee(eleve):
    """**Le piège de cette application.** Trente élèves se connectent depuis le
    NAT de leur établissement, donc depuis une seule adresse IP. Un compteur
    par IP les mettrait tous dehors à neuf heures du matin.

    On compte par compte visé : les échecs des uns n'affectent pas les autres.
    """
    camarades = [
        User.objects.create_user(email=f'eleve{i}@example.com', password=TEST_PASSWORD)
        for i in range(4)
    ]

    # Un élève se trompe assez pour être bloqué, lui.
    for _ in range(4):
        tenter('eve@example.com', MAUVAIS)
    assert tenter('eve@example.com', TEST_PASSWORD).status_code == 429

    # Ses camarades, sur la même IP, entrent normalement.
    for camarade in camarades:
        assert tenter(camarade.email, TEST_PASSWORD).status_code == 200


@AVEC_THROTTLE
def test_une_connexion_reussie_efface_lardoise(eleve):
    """Trois fautes de frappe puis la bonne saisie ne doivent pas laisser
    l'apprenant à un essai du blocage."""
    for _ in range(2):
        tenter('eve@example.com', MAUVAIS)

    assert tenter('eve@example.com', TEST_PASSWORD).status_code == 200

    # Le quota est de nouveau entier.
    for _ in range(3):
        assert tenter('eve@example.com', MAUVAIS).status_code == 401


@AVEC_THROTTLE
def test_les_reussites_ne_consomment_pas_de_quota(eleve):
    """Quelqu'un qui connaît son mot de passe ne doit jamais être bloqué —
    sinon brûler le quota d'un camarade suffirait à l'empêcher d'entrer."""
    for _ in range(10):
        assert tenter('eve@example.com', TEST_PASSWORD).status_code == 200


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

@override_settings(REST_FRAMEWORK={'DEFAULT_THROTTLE_RATES': {}})
def test_la_connexion_fonctionne_sans_reglage_de_debit(eleve):
    """⚠️ `development.py` vide `DEFAULT_THROTTLE_RATES`.

    Le throttle étant déclaré sur la vue, il est instancié même là ; sans une
    tolérance explicite à l'absence de réglage, `SimpleRateThrottle` lèverait
    `ImproperlyConfigured` et **la connexion serait cassée en développement**.

    L'absence de réglage est posée explicitement plutôt que laissée à
    l'ambiant : `SimpleRateThrottle.THROTTLE_RATES` est un attribut de classe
    que `override_settings` modifie **sans le restaurer**. Un test non décoré
    hérite donc du débit posé par le test précédent.
    """
    for _ in range(12):
        assert tenter('eve@example.com', MAUVAIS).status_code == 401

    assert tenter('eve@example.com', TEST_PASSWORD).status_code == 200


@AVEC_THROTTLE
def test_une_requete_sans_email_ne_fait_pas_planter():
    """Pas de clé calculable : on laisse le serializer répondre 400."""
    assert APIClient().post(
        '/api/auth/login/', {'password': MAUVAIS}, format='json',
    ).status_code == 400

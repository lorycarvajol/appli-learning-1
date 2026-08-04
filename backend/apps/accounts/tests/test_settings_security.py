"""
Garde-fous de configuration.

Ces tests ne valident pas du code applicatif mais des réglages dont la
défaillance est silencieuse : l'application démarre, sert des requêtes, et
n'est plus sûre. Ils tournent dans l'environnement courant, quel qu'il soit.
"""
import pytest
from django.conf import settings


def test_les_jwt_sont_signes_avec_la_cle_courante():
    """`SIMPLE_JWT` copie SECRET_KEY à l'import de base.py.

    Un environnement qui redéfinit SECRET_KEY ensuite (c'est ce que fait
    production.py) doit impérativement réassigner `SIGNING_KEY`, sinon les
    jetons restent signés avec l'ancienne clé — celle du dépôt.
    """
    assert settings.SIMPLE_JWT['SIGNING_KEY'] == settings.SECRET_KEY


@pytest.mark.skipif(settings.DEBUG, reason="Contrôle réservé à la production")
def test_la_cle_de_developpement_nest_pas_utilisee_hors_debug():
    from config.settings.base import INSECURE_DEV_SECRET_KEY

    assert settings.SECRET_KEY != INSECURE_DEV_SECRET_KEY
    assert len(settings.SECRET_KEY) >= 50


def test_la_cle_de_repli_reste_reconnaissable():
    """Le garde-fou de production.py compare à cette constante : si quelqu'un
    change la valeur de repli sans elle, le garde-fou cesse de mordre."""
    from config.settings.base import INSECURE_DEV_SECRET_KEY

    assert INSECURE_DEV_SECRET_KEY.startswith('django-insecure-')


# ---------------------------------------------------------------------------
# Limitation de débit
# ---------------------------------------------------------------------------
#
# `development.py` **vide entièrement** `DEFAULT_THROTTLE_CLASSES` et
# `DEFAULT_THROTTLE_RATES` — c'est voulu, un plafond gêne le développement.
# Le risque est qu'on l'oublie : une production dont les débits seraient vides
# démarre, sert des requêtes, et laisse essayer cent mots de passe par heure
# sur un compte sans que rien ne le signale.

#: Débits sans lesquels une protection décrite dans CLAUDE.md n'existe plus.
DEBITS_ATTENDUS = ('anon', 'user', 'login', 'password_reset', 'invite')


def _reglages_de_base_intacts():
    """Charge `base.py` dans un espace de noms neuf.

    ⚠️ On ne peut **pas** écrire `from config.settings.base import
    REST_FRAMEWORK` : `development.py` fait `from .base import *` puis
    `REST_FRAMEWORK['DEFAULT_THROTTLE_RATES'] = {}`, ce qui mute le
    dictionnaire **en place** — c'est le même objet en mémoire. L'import
    rendrait donc la version déjà vidée, et le test passerait au vert sur une
    base.py devenue vide.

    C'est le même piège d'aliasing que celui documenté pour `SIMPLE_JWT`, qui
    copie `SECRET_KEY` à l'import : un réglage composé n'est pas un réglage
    déclaré.
    """
    import importlib.util
    from pathlib import Path

    chemin = Path(__file__).resolve().parents[3] / 'config' / 'settings' / 'base.py'
    spec = importlib.util.spec_from_file_location('_base_intacte', chemin)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_les_debits_sont_declares_dans_les_reglages_de_base():
    """La déclaration vit dans `base.py` et doit y rester complète."""
    REST_FRAMEWORK = _reglages_de_base_intacts().REST_FRAMEWORK

    rates = REST_FRAMEWORK['DEFAULT_THROTTLE_RATES']
    manquants = [nom for nom in DEBITS_ATTENDUS if not rates.get(nom)]
    assert not manquants, (
        f"Débits absents de base.py : {manquants}. Chacun correspond à une "
        f"protection documentée (connexion, mot de passe oublié, invitations)."
    )
    assert REST_FRAMEWORK['DEFAULT_THROTTLE_CLASSES'], (
        "Sans classe de throttle, les débits déclarés ne s'appliquent à rien."
    )


@pytest.mark.skipif(settings.DEBUG, reason="Contrôle réservé à la production")
def test_le_throttling_est_actif_hors_developpement():
    """En production, les débits doivent avoir survécu à la composition.

    `production.py` hérite de `base.py` sans les vider — mais rien ne
    l'imposait jusqu'ici.
    """
    rates = settings.REST_FRAMEWORK['DEFAULT_THROTTLE_RATES']
    assert settings.REST_FRAMEWORK['DEFAULT_THROTTLE_CLASSES']
    for nom in DEBITS_ATTENDUS:
        assert rates.get(nom), f"Débit « {nom} » absent en production."

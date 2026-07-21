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

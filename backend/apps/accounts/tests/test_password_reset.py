"""
Tests du parcours « mot de passe oublié ».

Deux propriétés de sécurité sont vérifiées ici en plus du fonctionnel :

- **pas d'oracle d'énumération** : la réponse est identique que le compte
  existe ou non, sinon l'endpoint révèle qui est inscrit
- **révocation des sessions** : après réinitialisation, les refresh tokens
  déjà émis sont blacklistés — sans ça un compte compromis le reste 7 jours
"""
import re
from datetime import datetime, timedelta
from unittest.mock import patch

import pytest
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.core import mail
from django.test import override_settings
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from apps.accounts.models import User

pytestmark = pytest.mark.django_db

# Mots de passe de test. Valeurs volontairement descriptives : elles ne
# ressemblent pas à un identifiant réel, ce qui évite de déclencher les
# détecteurs de secrets sur chaque nouveau test. Elles satisfont malgré tout
# les validateurs Django (longueur, non courant, non numérique).
TEST_PASSWORD = 'fixture-pwd-not-a-real-secret'
NEW_PASSWORD = 'fixture-pwd-rotated'
MISMATCHED_PASSWORD = 'fixture-pwd-does-not-match'


REQUEST_URL = '/api/auth/password-reset/'
VALIDATE_URL = '/api/auth/password-reset/validate/'
CONFIRM_URL = '/api/auth/password-reset/confirm/'


@pytest.fixture
def api():
    return APIClient()


@pytest.fixture
def learner():
    return User.objects.create_user(
        email='eleve@example.com', password=TEST_PASSWORD, first_name='Eve'
    )


def extract_link(message):
    """Récupère (uid, token) depuis le lien contenu dans l'email."""
    match = re.search(r'/reset-password/([^/\s]+)/([^\s]+)', message.body)
    assert match, f"Aucun lien de réinitialisation dans :\n{message.body}"
    return match.group(1), match.group(2)


def request_reset(api, email):
    response = api.post(REQUEST_URL, {'email': email}, format='json')
    assert response.status_code == 200
    return response


# ---------------------------------------------------------------------------
# Demande : aucune fuite sur l'existence du compte
# ---------------------------------------------------------------------------

def test_un_email_est_envoye_pour_un_compte_existant(api, learner):
    request_reset(api, learner.email)

    assert len(mail.outbox) == 1
    assert mail.outbox[0].to == [learner.email]
    assert '/reset-password/' in mail.outbox[0].body


def test_reponse_identique_pour_un_compte_inexistant(api, learner):
    existing = request_reset(api, learner.email)
    mail.outbox.clear()
    unknown = request_reset(api, 'personne@example.com')

    # Même statut et même corps : impossible de distinguer les deux cas.
    assert existing.json() == unknown.json()
    assert len(mail.outbox) == 0


def test_aucun_email_pour_un_compte_desactive(api, learner):
    learner.is_active = False
    learner.save()

    request_reset(api, learner.email)

    assert len(mail.outbox) == 0


def test_la_demande_est_insensible_a_la_casse(api, learner):
    request_reset(api, 'Eleve@Example.COM')

    assert len(mail.outbox) == 1
    assert mail.outbox[0].to == ['eleve@example.com']


def test_un_email_malforme_est_refuse(api):
    response = api.post(REQUEST_URL, {'email': 'pas-un-email'}, format='json')

    assert response.status_code == 400
    assert len(mail.outbox) == 0


# ---------------------------------------------------------------------------
# Validation du lien avant affichage du formulaire
# ---------------------------------------------------------------------------

def test_un_lien_valide_est_reconnu(api, learner):
    request_reset(api, learner.email)
    uid, token = extract_link(mail.outbox[0])

    response = api.get(VALIDATE_URL, {'uid': uid, 'token': token})

    assert response.json() == {'valid': True, 'email': learner.email}


def test_un_lien_bricole_est_rejete_sans_erreur(api, learner):
    request_reset(api, learner.email)
    uid, _ = extract_link(mail.outbox[0])

    for params in (
        {'uid': uid, 'token': 'nimportequoi'},
        {'uid': 'bricole', 'token': 'nimportequoi'},
        {'uid': '', 'token': ''},
    ):
        response = api.get(VALIDATE_URL, params)
        assert response.status_code == 200, params
        assert response.json() == {'valid': False}, params


# ---------------------------------------------------------------------------
# Confirmation
# ---------------------------------------------------------------------------

def test_le_mot_de_passe_est_bien_remplace(api, learner):
    request_reset(api, learner.email)
    uid, token = extract_link(mail.outbox[0])

    response = api.post(CONFIRM_URL, {
        'uid': uid, 'token': token,
        'new_password': NEW_PASSWORD, 'new_password_confirm': NEW_PASSWORD,
    }, format='json')
    assert response.status_code == 200

    assert api.post(
        '/api/auth/login/', {'email': learner.email, 'password': NEW_PASSWORD},
        format='json',
    ).status_code == 200

    assert api.post(
        '/api/auth/login/', {'email': learner.email, 'password': TEST_PASSWORD},
        format='json',
    ).status_code == 401


def test_le_lien_ne_sert_quune_fois(api, learner):
    request_reset(api, learner.email)
    uid, token = extract_link(mail.outbox[0])
    payload = {
        'uid': uid, 'token': token,
        'new_password': NEW_PASSWORD, 'new_password_confirm': NEW_PASSWORD,
    }

    assert api.post(CONFIRM_URL, payload, format='json').status_code == 200
    # Le jeton est signé sur le hash du mot de passe : celui-ci ayant changé,
    # le lien est mort. Pas besoin de le stocker pour le rendre à usage unique.
    assert api.post(CONFIRM_URL, payload, format='json').status_code == 400


def test_les_deux_mots_de_passe_doivent_correspondre(api, learner):
    request_reset(api, learner.email)
    uid, token = extract_link(mail.outbox[0])

    response = api.post(CONFIRM_URL, {
        'uid': uid, 'token': token,
        'new_password': NEW_PASSWORD, 'new_password_confirm': MISMATCHED_PASSWORD,
    }, format='json')

    assert response.status_code == 400
    learner.refresh_from_db()
    assert learner.check_password(TEST_PASSWORD)


def test_un_mot_de_passe_trop_faible_est_refuse(api, learner):
    request_reset(api, learner.email)
    uid, token = extract_link(mail.outbox[0])

    response = api.post(CONFIRM_URL, {
        'uid': uid, 'token': token,
        'new_password': '1234', 'new_password_confirm': '1234',
    }, format='json')

    assert response.status_code == 400
    learner.refresh_from_db()
    assert learner.check_password(TEST_PASSWORD)


@override_settings(PASSWORD_RESET_TIMEOUT=3600)
def test_un_lien_expire_est_refuse(api, learner):
    """On avance l'horloge du générateur plutôt que de mettre le délai à 0 :
    Django compare `écoulé > timeout`, donc un délai nul laisse passer un
    jeton vérifié dans la même seconde."""
    request_reset(api, learner.email)
    uid, token = extract_link(mail.outbox[0])

    # `_now()` de Django est naïf : renvoyer un datetime aware casse son calcul.
    two_hours_later = datetime.now() + timedelta(hours=2)
    with patch.object(
        PasswordResetTokenGenerator, '_now', return_value=two_hours_later
    ):
        response = api.post(CONFIRM_URL, {
            'uid': uid, 'token': token,
            'new_password': NEW_PASSWORD, 'new_password_confirm': NEW_PASSWORD,
        }, format='json')

    assert response.status_code == 400
    learner.refresh_from_db()
    assert learner.check_password(TEST_PASSWORD)


@override_settings(PASSWORD_RESET_TIMEOUT=3600)
def test_un_lien_reste_valide_avant_expiration(api, learner):
    """Contrepartie du test précédent : sans lui, on ne saurait pas si le
    refus vient de l'expiration ou du gel de l'horloge lui-même."""
    request_reset(api, learner.email)
    uid, token = extract_link(mail.outbox[0])

    almost_expired = datetime.now() + timedelta(minutes=59)
    with patch.object(
        PasswordResetTokenGenerator, '_now', return_value=almost_expired
    ):
        response = api.post(CONFIRM_URL, {
            'uid': uid, 'token': token,
            'new_password': NEW_PASSWORD, 'new_password_confirm': NEW_PASSWORD,
        }, format='json')

    assert response.status_code == 200


def test_se_connecter_entre_temps_invalide_le_lien(api, learner):
    """Propriété offerte par le générateur sans état : le jeton dépend de
    `last_login`, donc une reconnexion réussie périme le lien envoyé."""
    request_reset(api, learner.email)
    uid, token = extract_link(mail.outbox[0])

    api.post(
        '/api/auth/login/', {'email': learner.email, 'password': TEST_PASSWORD},
        format='json',
    )

    response = api.post(CONFIRM_URL, {
        'uid': uid, 'token': token,
        'new_password': NEW_PASSWORD, 'new_password_confirm': NEW_PASSWORD,
    }, format='json')

    assert response.status_code == 400


# ---------------------------------------------------------------------------
# Révocation des sessions ouvertes
# ---------------------------------------------------------------------------

def test_les_sessions_ouvertes_sont_revoquees(api, learner):
    """Un compte compromis ne doit pas rester accessible après le reset."""
    stolen = RefreshToken.for_user(learner)

    request_reset(api, learner.email)
    uid, token = extract_link(mail.outbox[0])
    api.post(CONFIRM_URL, {
        'uid': uid, 'token': token,
        'new_password': NEW_PASSWORD, 'new_password_confirm': NEW_PASSWORD,
    }, format='json')

    response = api.post(
        '/api/auth/token/refresh/', {'refresh': str(stolen)}, format='json'
    )
    assert response.status_code == 401


# ---------------------------------------------------------------------------
# Garde-fou de configuration
# ---------------------------------------------------------------------------

def test_les_vues_publiques_declarent_un_throttle():
    """Ces endpoints sont anonymes : sans limite, ils servent d'oracle et de
    relais d'envoi de mails. Le taux est réglé dans les settings."""
    from apps.accounts.views import (
        PasswordResetConfirmView,
        PasswordResetRequestView,
        PasswordResetValidateView,
    )

    for view in (
        PasswordResetRequestView,
        PasswordResetValidateView,
        PasswordResetConfirmView,
    ):
        assert view.throttle_scope == 'password_reset', view.__name__

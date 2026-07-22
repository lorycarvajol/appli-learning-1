"""
Tests des fonctionnalités RGPD côté apprenant.

Trois garanties sont verrouillées ici :

1. **Consentement obligatoire** : impossible de créer un compte sans accepter
   la politique de confidentialité et les CGU ; l'acceptation est horodatée.
2. **Portabilité** : chacun peut exporter ses propres données, personne celles
   d'un tiers.
3. **Effacement en self-service** : l'apprenant supprime son compte lui-même,
   avec son mot de passe, l'opération est tracée et irréversible.
"""
import pytest
from rest_framework.test import APIClient

from apps.accounts.models import User
from apps.administration.models import AuditLog

pytestmark = pytest.mark.django_db

TEST_PASSWORD = 'fixture-pwd-not-a-real-secret'


@pytest.fixture
def learner():
    return User.objects.create_user(
        email='eleve@example.com', password=TEST_PASSWORD, first_name='Eve'
    )


def _register_payload(**overrides):
    payload = {
        'email': 'nouveau@example.com',
        'password': TEST_PASSWORD,
        'password_confirm': TEST_PASSWORD,
        'first_name': 'Nouveau',
        'last_name': 'Venu',
        'accept_terms': True,
    }
    payload.update(overrides)
    return payload


# ---------------------------------------------------------------------------
# 1. Consentement à l'inscription
# ---------------------------------------------------------------------------

def test_l_inscription_exige_le_consentement():
    """Sans case cochée, pas de compte : la case n'est pas décorative."""
    response = APIClient().post(
        '/api/auth/register/', _register_payload(accept_terms=False), format='json'
    )
    assert response.status_code == 400
    assert 'accept_terms' in response.json()
    assert not User.objects.filter(email='nouveau@example.com').exists()


def test_l_inscription_refuse_un_consentement_absent():
    payload = _register_payload()
    payload.pop('accept_terms')
    response = APIClient().post('/api/auth/register/', payload, format='json')
    assert response.status_code == 400
    assert 'accept_terms' in response.json()


def test_le_consentement_est_horodate():
    response = APIClient().post(
        '/api/auth/register/', _register_payload(), format='json'
    )
    assert response.status_code == 201

    user = User.objects.get(email='nouveau@example.com')
    assert user.profile.terms_accepted_at is not None


# ---------------------------------------------------------------------------
# 2. Export des données (portabilité)
# ---------------------------------------------------------------------------

def test_l_export_exige_une_authentification():
    assert APIClient().get('/api/auth/export/').status_code == 401


def test_l_export_contient_les_donnees_du_compte(learner):
    client = APIClient()
    client.force_authenticate(user=learner)

    response = client.get('/api/auth/export/')

    assert response.status_code == 200
    data = response.json()
    assert data['compte']['email'] == 'eleve@example.com'
    # Structure attendue (portabilité) : les sections sont toujours présentes.
    for key in ('profil', 'progression', 'points', 'badges', 'activite'):
        assert key in data


def test_l_export_ne_concerne_que_le_compte_courant(learner):
    """Chacun exporte ses données, jamais celles d'un autre : pas de paramètre
    permettant de viser un tiers."""
    autre = User.objects.create_user(
        email='autre@example.com', password=TEST_PASSWORD
    )
    client = APIClient()
    client.force_authenticate(user=learner)

    response = client.get(f'/api/auth/export/?user_id={autre.id}')

    assert response.status_code == 200
    assert response.json()['compte']['email'] == 'eleve@example.com'


# ---------------------------------------------------------------------------
# 3. Suppression de compte en self-service (droit à l'effacement)
# ---------------------------------------------------------------------------

def test_la_suppression_exige_le_bon_mot_de_passe(learner):
    client = APIClient()
    client.force_authenticate(user=learner)

    response = client.post(
        '/api/auth/delete-account/', {'password': 'mauvais'}, format='json'
    )

    assert response.status_code == 400
    learner.refresh_from_db()
    assert learner.email == 'eleve@example.com'  # intact
    assert learner.is_active is True


def test_la_suppression_anonymise_le_compte(learner):
    client = APIClient()
    client.force_authenticate(user=learner)

    response = client.post(
        '/api/auth/delete-account/', {'password': TEST_PASSWORD}, format='json'
    )

    assert response.status_code == 200
    learner.refresh_from_db()
    assert learner.email.endswith('@anonymized.invalid')
    assert learner.first_name == ''
    assert learner.is_active is False
    assert learner.profile.anonymized_at is not None


def test_la_suppression_est_tracee_dans_le_journal(learner):
    client = APIClient()
    client.force_authenticate(user=learner)

    client.post('/api/auth/delete-account/', {'password': TEST_PASSWORD}, format='json')

    entry = AuditLog.objects.filter(action=AuditLog.Action.ACCOUNT_DELETED).first()
    assert entry is not None
    # Le libellé fige l'identité *avant* effacement : « eleve@example.com »,
    # pas l'adresse anonymisée. C'est tout l'intérêt de la trace.
    assert entry.target_label == 'eleve@example.com'


def test_le_dernier_admin_ne_peut_pas_se_supprimer():
    """Garde-fou : un admin isolé rendrait la plateforme impilotable."""
    admin = User.objects.create_user(
        email='admin@example.com', password=TEST_PASSWORD, role=User.Role.ADMIN
    )
    client = APIClient()
    client.force_authenticate(user=admin)

    response = client.post(
        '/api/auth/delete-account/', {'password': TEST_PASSWORD}, format='json'
    )

    assert response.status_code == 400
    admin.refresh_from_db()
    assert admin.is_active is True
    assert admin.profile.anonymized_at is None

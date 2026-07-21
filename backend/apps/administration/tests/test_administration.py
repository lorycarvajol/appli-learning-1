"""
Tests de l'espace administration.

L'essentiel porte sur les garde-fous : une action d'administration mal bornée
peut rendre la plateforme impilotable ou détruire des données irrécupérables.
"""
import pytest
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from apps.accounts.models import User
from apps.cohorts.models import Cohort
from apps.progression.models import UserProgress

pytestmark = pytest.mark.django_db

# Mots de passe de test. Valeurs volontairement descriptives : elles ne
# ressemblent pas à un identifiant réel, ce qui évite de déclencher les
# détecteurs de secrets sur chaque nouveau test. Elles satisfont malgré tout
# les validateurs Django (longueur, non courant, non numérique).
TEST_PASSWORD = 'fixture-pwd-not-a-real-secret'


def client_for(user):
    client = APIClient()
    client.force_authenticate(user=user)
    return client


@pytest.fixture
def admin():
    return User.objects.create_user(
        email='admin@example.com', password=TEST_PASSWORD, role=User.Role.ADMIN,
    )


@pytest.fixture
def other_admin():
    return User.objects.create_user(
        email='admin2@example.com', password=TEST_PASSWORD, role=User.Role.ADMIN,
    )


@pytest.fixture
def trainer():
    return User.objects.create_user(
        email='formateur@example.com', password=TEST_PASSWORD,
        first_name='Jean', role=User.Role.TRAINER,
    )


@pytest.fixture
def learner():
    return User.objects.create_user(
        email='eleve@example.com', password=TEST_PASSWORD, first_name='Eve',
    )


# ---------------------------------------------------------------------------
# Réconciliation role / is_staff
# ---------------------------------------------------------------------------

def test_un_admin_obtient_lacces_a_ladmin_django(learner):
    """Régression : rien ne synchronisait le rôle et `is_staff`, on pouvait
    créer un administrateur incapable d'ouvrir /admin/."""
    assert learner.is_staff is False

    learner.role = User.Role.ADMIN
    learner.save()

    assert learner.is_staff is True


def test_retrograder_un_admin_lui_retire_lacces(admin, other_admin):
    admin.role = User.Role.TRAINER
    admin.save()

    assert admin.is_staff is False


def test_un_superutilisateur_garde_toujours_lacces():
    """Filet de sécurité : ne jamais s'enfermer dehors."""
    root = User.objects.create_superuser(email='root@example.com', password=TEST_PASSWORD)
    root.role = User.Role.LEARNER
    root.save()

    assert root.is_staff is True


def test_un_formateur_ne_peut_pas_forcer_is_staff(trainer):
    """Le rôle fait autorité : cocher la case ne suffit pas."""
    trainer.is_staff = True
    trainer.save()

    trainer.refresh_from_db()
    assert trainer.is_staff is False


# ---------------------------------------------------------------------------
# Cloisonnement de l'espace
# ---------------------------------------------------------------------------

@pytest.mark.parametrize('path', [
    '/api/administration/overview/',
    '/api/administration/trainers/',
    '/api/administration/users/',
])
def test_lespace_admin_est_ferme_aux_formateurs(trainer, path):
    assert client_for(trainer).get(path).status_code == 403


def test_lespace_admin_est_ferme_aux_apprenants(learner):
    assert client_for(learner).get('/api/administration/overview/').status_code == 403


# ---------------------------------------------------------------------------
# Pilotage
# ---------------------------------------------------------------------------

def test_le_pilotage_compte_les_apprenants_sans_classe(admin, trainer, learner):
    cohort = Cohort.objects.create(name='Promo', trainer=trainer)
    assigned = User.objects.create_user(email='rattache@example.com', password=TEST_PASSWORD)
    assigned.profile.cohort = cohort
    assigned.profile.save()

    data = client_for(admin).get('/api/administration/overview/').json()

    assert data['users']['learners'] == 2
    assert data['users']['unassigned_learners'] == 1  # `learner`, sans classe
    assert data['cohorts']['total'] == 1


def test_le_pilotage_signale_les_classes_sans_formateur(admin):
    Cohort.objects.create(name='Orpheline', trainer=None)

    data = client_for(admin).get('/api/administration/overview/').json()

    assert data['cohorts']['without_trainer'] == 1


def test_la_liste_des_formateurs_donne_leurs_effectifs(admin, trainer, learner):
    cohort = Cohort.objects.create(name='Promo', trainer=trainer)
    learner.profile.cohort = cohort
    learner.profile.save()

    data = client_for(admin).get('/api/administration/trainers/').json()

    assert len(data) == 1
    assert data[0]['learner_count'] == 1
    assert data[0]['cohorts'][0]['name'] == 'Promo'


def test_on_peut_filtrer_les_apprenants_sans_classe(admin, trainer, learner):
    cohort = Cohort.objects.create(name='Promo', trainer=trainer)
    assigned = User.objects.create_user(email='rattache@example.com', password=TEST_PASSWORD)
    assigned.profile.cohort = cohort
    assigned.profile.save()

    data = client_for(admin).get(
        '/api/administration/users/?unassigned=true'
    ).json()

    assert [u['email'] for u in data['results']] == [learner.email]


# ---------------------------------------------------------------------------
# Rattachement
# ---------------------------------------------------------------------------

def test_un_admin_rattache_un_apprenant_orphelin(admin, trainer, learner):
    cohort = Cohort.objects.create(name='Promo', trainer=trainer)

    response = client_for(admin).post(
        f'/api/administration/users/{learner.id}/assign_cohort/',
        {'cohort_id': str(cohort.id)}, format='json',
    )

    assert response.status_code == 200
    learner.profile.refresh_from_db()
    assert learner.profile.cohort == cohort


def test_un_formateur_ne_se_rattache_pas_a_une_classe(admin, trainer):
    cohort = Cohort.objects.create(name='Promo', trainer=trainer)

    response = client_for(admin).post(
        f'/api/administration/users/{trainer.id}/assign_cohort/',
        {'cohort_id': str(cohort.id)}, format='json',
    )

    assert response.status_code == 400


# ---------------------------------------------------------------------------
# Cycle de vie : garde-fous
# ---------------------------------------------------------------------------

def test_on_ne_peut_pas_supprimer_le_dernier_administrateur(admin):
    """Sinon la plateforme devient impilotable en un clic."""
    response = client_for(admin).post(
        f'/api/administration/users/{admin.id}/set_role/',
        {'role': 'LEARNER'}, format='json',
    )

    assert response.status_code == 400
    admin.refresh_from_db()
    assert admin.role == User.Role.ADMIN


def test_on_ne_peut_pas_modifier_son_propre_role(admin, other_admin):
    response = client_for(admin).post(
        f'/api/administration/users/{admin.id}/set_role/',
        {'role': 'LEARNER'}, format='json',
    )

    assert response.status_code == 400


def test_un_admin_peut_en_retrograder_un_autre(admin, other_admin):
    response = client_for(admin).post(
        f'/api/administration/users/{other_admin.id}/set_role/',
        {'role': 'TRAINER'}, format='json',
    )

    assert response.status_code == 200
    other_admin.refresh_from_db()
    assert other_admin.role == User.Role.TRAINER
    assert other_admin.is_staff is False


def test_desactiver_un_compte_revoque_ses_sessions(admin, learner):
    stolen = RefreshToken.for_user(learner)

    client_for(admin).post(
        f'/api/administration/users/{learner.id}/set_active/',
        {'is_active': False}, format='json',
    )

    learner.refresh_from_db()
    assert learner.is_active is False
    assert APIClient().post(
        '/api/auth/token/refresh/', {'refresh': str(stolen)}, format='json'
    ).status_code == 401


def test_la_desactivation_est_reversible(admin, learner):
    api = client_for(admin)
    api.post(f'/api/administration/users/{learner.id}/set_active/',
             {'is_active': False}, format='json')
    api.post(f'/api/administration/users/{learner.id}/set_active/',
             {'is_active': True}, format='json')

    learner.refresh_from_db()
    assert learner.is_active is True
    assert learner.email == 'eleve@example.com'


# ---------------------------------------------------------------------------
# Anonymisation (RGPD)
# ---------------------------------------------------------------------------

def test_lanonymisation_efface_lidentite_et_garde_la_progression(
    admin, learner, trainer
):
    """Le droit à l'effacement porte sur les données personnelles, pas sur les
    agrégats : effacer en cascade fausserait les statistiques des classes."""
    from apps.courses.models import Chapter, Lesson

    chapter = Chapter.objects.create(
        title='HTML', slug='html', description='…',
        estimated_duration=60, is_published=True,
    )
    lesson = Lesson.objects.create(
        chapter=chapter, title='Balises', slug='balises',
        lesson_type='THEORY', points=10, is_published=True,
    )
    UserProgress.objects.create(
        user=learner, lesson=lesson,
        status=UserProgress.ProgressStatus.COMPLETED,
    )

    response = client_for(admin).post(
        f'/api/administration/users/{learner.id}/anonymize/', {}, format='json'
    )
    assert response.status_code == 200

    learner.refresh_from_db()
    assert learner.email.endswith('@anonymized.invalid')
    assert learner.first_name == ''
    assert learner.is_active is False
    assert learner.has_usable_password() is False
    assert learner.profile.anonymized_at is not None

    # La progression survit, détachée de toute identité.
    assert UserProgress.objects.filter(user=learner).count() == 1


def test_on_ne_peut_pas_anonymiser_deux_fois(admin, learner):
    api = client_for(admin)
    api.post(f'/api/administration/users/{learner.id}/anonymize/', {}, format='json')

    second = api.post(
        f'/api/administration/users/{learner.id}/anonymize/', {}, format='json'
    )

    assert second.status_code == 400


def test_on_ne_peut_pas_sanonymiser_soi_meme(admin, other_admin):
    response = client_for(admin).post(
        f'/api/administration/users/{admin.id}/anonymize/', {}, format='json'
    )

    assert response.status_code == 400
    admin.refresh_from_db()
    assert admin.email == 'admin@example.com'


def test_lanonymisation_detache_de_la_classe(admin, trainer, learner):
    cohort = Cohort.objects.create(name='Promo', trainer=trainer)
    learner.profile.cohort = cohort
    learner.profile.save()

    client_for(admin).post(
        f'/api/administration/users/{learner.id}/anonymize/', {}, format='json'
    )

    learner.profile.refresh_from_db()
    assert learner.profile.cohort is None

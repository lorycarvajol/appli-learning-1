"""
Tests du journal d'audit et des vues de pilotage.

Le journal est la contrepartie du « tout pouvoir » de l'administrateur : ce
sont ces tests qui empêchent qu'une action lourde redevienne silencieuse.
"""
import pytest
from django.db import connection
from django.test.utils import CaptureQueriesContext
from django.utils import timezone
from rest_framework.test import APIClient

from apps.accounts.models import User
from apps.administration.models import AuditLog
from apps.cohorts.models import Cohort
from apps.courses.models import Chapter, Lesson
from apps.progression.models import ActivityLog, UserProgress

pytestmark = pytest.mark.django_db

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
# Chaque action lourde laisse une trace
# ---------------------------------------------------------------------------

def test_changer_un_role_est_journalise(admin, learner):
    client_for(admin).post(
        f'/api/administration/users/{learner.id}/set_role/',
        {'role': User.Role.TRAINER}, format='json',
    )

    entry = AuditLog.objects.get(action=AuditLog.Action.SET_ROLE)
    assert entry.actor == admin
    assert entry.target_label == 'eleve@example.com'
    assert entry.changes == {'before': User.Role.LEARNER, 'after': User.Role.TRAINER}


def test_desactiver_un_compte_est_journalise(admin, learner):
    client_for(admin).post(
        f'/api/administration/users/{learner.id}/set_active/',
        {'is_active': False}, format='json',
    )

    entry = AuditLog.objects.get(action=AuditLog.Action.SET_ACTIVE)
    assert entry.changes == {'before': True, 'after': False}


def test_rattacher_a_une_classe_est_journalise(admin, trainer, learner):
    cohort = Cohort.objects.create(name='Promo 2026', trainer=trainer)

    client_for(admin).post(
        f'/api/administration/users/{learner.id}/assign_cohort/',
        {'cohort_id': str(cohort.id)}, format='json',
    )

    entry = AuditLog.objects.get(action=AuditLog.Action.ASSIGN_COHORT)
    assert entry.changes == {'before': '', 'after': 'Promo 2026'}


def test_une_action_refusee_ne_laisse_aucune_trace(admin):
    """Le journal consigne ce qui a eu lieu, pas ce qui a été tenté.

    Sans cette garantie, un refus métier gonflerait le journal d'entrées
    décrivant des changements qui n'ont jamais eu lieu.
    """
    response = client_for(admin).post(
        f'/api/administration/users/{admin.id}/set_role/',
        {'role': User.Role.LEARNER}, format='json',
    )

    assert response.status_code == 400
    assert not AuditLog.objects.exists()


# ---------------------------------------------------------------------------
# Le point critique : la trace survit à l'anonymisation
# ---------------------------------------------------------------------------

def test_lanonymisation_fige_lidentite_dorigine(admin, learner):
    """Sans libellé figé, le journal dirait « un compte anonyme a été anonymisé ».

    C'est précisément la trace exigée par le RGPD : pouvoir démontrer quelle
    demande d'effacement a été honorée, et par qui.
    """
    client_for(admin).post(
        f'/api/administration/users/{learner.id}/anonymize/', {}, format='json',
    )

    learner.refresh_from_db()
    assert learner.email.endswith('@anonymized.invalid')

    entry = AuditLog.objects.get(action=AuditLog.Action.ANONYMIZE)
    assert entry.target_label == 'eleve@example.com'
    assert entry.target_id == learner.id


def test_la_trace_survit_a_la_suppression_de_son_auteur(admin, other_admin, learner):
    """Un journal qui s'efface avec son auteur ne prouve rien."""
    client_for(admin).post(
        f'/api/administration/users/{learner.id}/set_active/',
        {'is_active': False}, format='json',
    )

    admin.delete()

    entry = AuditLog.objects.get(action=AuditLog.Action.SET_ACTIVE)
    assert entry.actor is None
    assert entry.actor_label == 'admin@example.com'


# ---------------------------------------------------------------------------
# Le journal est en lecture seule, y compris pour un admin
# ---------------------------------------------------------------------------

def test_le_journal_est_lisible_par_un_admin(admin, learner):
    client_for(admin).post(
        f'/api/administration/users/{learner.id}/set_active/',
        {'is_active': False}, format='json',
    )

    response = client_for(admin).get('/api/administration/audit/')

    assert response.status_code == 200
    results = response.data.get('results', response.data)
    assert results[0]['action'] == AuditLog.Action.SET_ACTIVE
    assert results[0]['actor_label'] == 'admin@example.com'


def test_le_journal_nest_ni_ecrivable_ni_supprimable(admin, learner):
    """Un journal réécrivable par ceux qu'il surveille n'est pas un journal."""
    client_for(admin).post(
        f'/api/administration/users/{learner.id}/set_active/',
        {'is_active': False}, format='json',
    )
    entry = AuditLog.objects.get()
    client = client_for(admin)

    assert client.post('/api/administration/audit/', {}, format='json').status_code == 405
    assert client.delete(f'/api/administration/audit/{entry.id}/').status_code == 405
    assert client.patch(
        f'/api/administration/audit/{entry.id}/', {'action': 'SET_ROLE'}, format='json'
    ).status_code == 405


@pytest.mark.parametrize('role', [User.Role.TRAINER, User.Role.LEARNER])
def test_le_journal_est_ferme_aux_non_admins(role):
    user = User.objects.create_user(
        email=f'{role.lower()}@example.com', password=TEST_PASSWORD, role=role,
    )
    assert client_for(user).get('/api/administration/audit/').status_code == 403


# ---------------------------------------------------------------------------
# Affectation de formateur
# ---------------------------------------------------------------------------

def test_un_admin_designe_un_autre_formateur_a_la_creation(admin, trainer):
    """Avant, l'admin devenait formateur de chaque classe qu'il créait."""
    response = client_for(admin).post(
        '/api/cohorts/cohorts/',
        {'name': 'Promo A', 'trainer_id': str(trainer.id)}, format='json',
    )

    assert response.status_code == 201
    assert Cohort.objects.get().trainer == trainer
    assert AuditLog.objects.filter(action=AuditLog.Action.CREATE_COHORT).exists()


def test_un_formateur_ne_peut_pas_creer_une_classe_pour_un_autre(trainer):
    """Le champ est ignoré, pas honoré : sinon le cloisonnement saute."""
    autre = User.objects.create_user(
        email='autre@example.com', password=TEST_PASSWORD, role=User.Role.TRAINER,
    )

    response = client_for(trainer).post(
        '/api/cohorts/cohorts/',
        {'name': 'Promo B', 'trainer_id': str(autre.id)}, format='json',
    )

    assert response.status_code == 201
    assert Cohort.objects.get().trainer == trainer


def test_un_admin_reaffecte_une_classe_orpheline(admin, trainer):
    cohort = Cohort.objects.create(name='Orpheline')

    response = client_for(admin).post(
        f'/api/cohorts/cohorts/{cohort.id}/set_trainer/',
        {'trainer_id': str(trainer.id)}, format='json',
    )

    assert response.status_code == 200
    cohort.refresh_from_db()
    assert cohort.trainer == trainer

    entry = AuditLog.objects.get(action=AuditLog.Action.ASSIGN_TRAINER)
    assert entry.changes == {'before': '', 'after': 'formateur@example.com'}


def test_on_ne_confie_pas_une_classe_a_un_apprenant(admin, learner):
    """Sinon il hériterait, via `visible_learners`, de la vue sur ses camarades."""
    cohort = Cohort.objects.create(name='Promo C')

    response = client_for(admin).post(
        f'/api/cohorts/cohorts/{cohort.id}/set_trainer/',
        {'trainer_id': str(learner.id)}, format='json',
    )

    assert response.status_code == 400
    cohort.refresh_from_db()
    assert cohort.trainer is None


def test_emettre_une_invitation_est_journalise_sans_le_jeton(admin, trainer):
    """Le journal se lit à plusieurs : le jeton n'y figure jamais.

    Une invitation crée des comptes — et pour un rôle TRAINER, un encadrant.
    L'émission doit donc laisser une trace, mais recopier le jeton dans une
    table consultable reviendrait à le rediffuser.
    """
    cohort = Cohort.objects.create(name='Promo E', trainer=trainer)

    response = client_for(admin).post(
        '/api/cohorts/invites/', {'cohort': str(cohort.id)}, format='json',
    )
    assert response.status_code == 201

    entry = AuditLog.objects.get(action=AuditLog.Action.INVITE_CREATED)
    assert entry.target_label == 'Promo E'
    assert response.data['token'] not in str(entry.changes)


def test_revoquer_une_invitation_est_journalise(admin, trainer):
    cohort = Cohort.objects.create(name='Promo F', trainer=trainer)
    created = client_for(admin).post(
        '/api/cohorts/invites/', {'cohort': str(cohort.id)}, format='json',
    )

    client_for(admin).delete(f'/api/cohorts/invites/{created.data["id"]}/')

    assert AuditLog.objects.filter(action=AuditLog.Action.INVITE_REVOKED).exists()


def test_un_formateur_ne_reaffecte_pas_une_classe(trainer):
    """Réservé à l'admin : sinon le cloisonnement de `get_queryset` saute."""
    cohort = Cohort.objects.create(name='Promo D', trainer=trainer)

    response = client_for(trainer).post(
        f'/api/cohorts/cohorts/{cohort.id}/set_trainer/',
        {'trainer_id': str(trainer.id)}, format='json',
    )

    assert response.status_code == 403


# ---------------------------------------------------------------------------
# L'admin Django ne doit plus offrir de porte dérobée
# ---------------------------------------------------------------------------

def _admin_for(model):
    from django.contrib import admin as django_admin

    return django_admin.site._registry[model]


def test_ladmin_django_ne_peut_plus_changer_un_role(admin):
    """Le seul chemin vers un rôle doit être `services.set_role`.

    Sinon un changement effectué depuis `/admin/` échappait au journal
    d'audit, à la règle du « dernier administrateur actif » et à la
    révocation des sessions.
    """
    readonly = _admin_for(User).get_readonly_fields(
        type('R', (), {'user': admin, 'method': 'GET'})(), admin
    )

    for field in ('role', 'is_active', 'is_staff', 'is_superuser'):
        assert field in readonly


def test_ladmin_django_ne_supprime_pas_un_compte(admin):
    """Supprimer détruirait la progression en cascade.

    La voie RGPD est l'anonymisation : elle vide l'identité et conserve les
    agrégats, pour ne pas fausser rétroactivement les stats des classes.
    """
    assert _admin_for(User).has_delete_permission(None) is False


@pytest.mark.parametrize('model_path,champ', [
    ('apps.gamification.models.PointTransaction', 'grand livre de points'),
    ('apps.gamification.models.UserBadge', 'badges obtenus'),
    ('apps.progression.models.UserProgress', 'progression'),
    ('apps.progression.models.ActivityLog', "journal d'activité"),
    ('apps.accounts.models.Profile', 'profil et solde'),
])
def test_les_donnees_derivees_sont_en_lecture_seule(model_path, champ):
    """Elles portent des invariants qu'une saisie manuelle ferait décrocher.

    `Profile.total_points` doit toujours égaler la somme des
    `PointTransaction` : un ajustement à la main casse cette égalité sans
    laisser de trace.
    """
    from django.utils.module_loading import import_string

    model_admin = _admin_for(import_string(model_path))
    assert model_admin.has_change_permission(None) is False, champ
    assert model_admin.has_add_permission(None) is False, champ
    assert model_admin.has_delete_permission(None) is False, champ


def test_le_journal_daudit_nest_pas_expose_dans_ladmin_django():
    """Il n'y est pas enregistré du tout : rien ne doit pouvoir le réécrire."""
    from django.contrib import admin as django_admin

    assert AuditLog not in django_admin.site._registry


def test_le_contenu_pedagogique_reste_pleinement_editable():
    """C'est la raison d'être de l'admin Django — ne pas le brider par excès.

    On interroge avec un superutilisateur : les `ModelAdmin` par défaut
    consultent les permissions Django, contrairement à `ReadOnlyAdmin` qui
    refuse quoi qu'il arrive.
    """
    from apps.courses.models import Chapter, Exercise, Lesson, Project, Quiz
    from apps.gamification.models import Badge

    superuser = User.objects.create_superuser(
        email='root@example.com', password=TEST_PASSWORD,
    )
    request = type('R', (), {'user': superuser, 'method': 'GET'})()

    for model in (Chapter, Lesson, Exercise, Quiz, Project, Badge):
        model_admin = _admin_for(model)
        assert model_admin.has_change_permission(request) is True, model.__name__
        assert model_admin.has_add_permission(request) is True, model.__name__


# ---------------------------------------------------------------------------
# Pilotage : tendance, décrochage, et coût en requêtes
# ---------------------------------------------------------------------------

def test_le_pilotage_expose_une_tendance_sur_30_jours(admin, learner):
    ActivityLog.objects.create(
        user=learner, activity_type=ActivityLog.ActivityType.LESSON_STARTED,
    )

    response = client_for(admin).get('/api/administration/overview/')
    trend = response.data['activity']['trend']

    # Les jours creux doivent être présents : une courbe à trous se lit comme
    # une courbe qui remonte.
    assert len(trend) == 30
    assert trend[-1]['date'] == timezone.localdate().isoformat()
    assert trend[-1]['count'] == 1
    assert trend[0]['count'] == 0


def test_le_pilotage_distingue_decroches_et_jamais_demarres(admin, learner):
    jamais = User.objects.create_user(
        email='jamais@example.com', password=TEST_PASSWORD,
    )
    activity = ActivityLog.objects.create(
        user=learner, activity_type=ActivityLog.ActivityType.LESSON_STARTED,
    )
    # `created_at` est en auto_now_add : on force la date après coup.
    ActivityLog.objects.filter(pk=activity.pk).update(
        created_at=timezone.now() - timezone.timedelta(days=30)
    )

    response = client_for(admin).get('/api/administration/overview/')

    assert response.data['activity']['stalled_learners'] == 1
    assert response.data['activity']['never_started_learners'] == 1
    assert jamais.role == User.Role.LEARNER


def _query_count(user, url):
    """Nombre de requêtes SQL émises par un appel."""
    with CaptureQueriesContext(connection) as captured:
        response = client_for(user).get(url)
        assert response.status_code == 200, response.data
    return len(captured), response


def _published_lesson():
    chapter = Chapter.objects.create(
        title='C1', slug='c1', estimated_duration=60, is_published=True,
    )
    return Lesson.objects.create(
        chapter=chapter, title='L1', slug='l1', lesson_type='THEORY',
        points=10, is_published=True,
    )


def test_le_pilotage_ne_grossit_pas_avec_le_nombre_de_classes(admin, trainer):
    """Verrouille la correction du N+1 du pilotage.

    On compare deux volumes plutôt que de fixer un plafond chiffré : un
    plafond se contente d'être « assez grand » et laisserait repasser un N+1
    modéré. Ce qui compte est que le coût soit **constant**.
    """
    _published_lesson()
    for index in range(3):
        Cohort.objects.create(name=f'Petite {index}', trainer=trainer)
    baseline, _ = _query_count(admin, '/api/administration/overview/')

    for index in range(20):
        Cohort.objects.create(name=f'Grande {index}', trainer=trainer)
    scaled, response = _query_count(admin, '/api/administration/overview/')

    assert len(response.data['per_cohort']) == 23
    assert scaled == baseline


def test_le_resume_des_apprenants_ne_grossit_pas_avec_leffectif(admin, trainer):
    """Cette vue faisait quatre requêtes **par apprenant**.

    Pour un formateur c'était supportable ; pour un admin, `visible_learners`
    renvoie toute la plateforme — elle dégénérait donc là où elle sert le plus.
    """
    lesson = _published_lesson()

    def enrole(prefix, count):
        for index in range(count):
            student = User.objects.create_user(
                email=f'{prefix}{index}@example.com', password=TEST_PASSWORD,
            )
            UserProgress.objects.create(
                user=student, lesson=lesson,
                status=UserProgress.ProgressStatus.IN_PROGRESS,
            )

    url = '/api/progression/trainer-dashboard/learners_summary/'
    enrole('petit', 3)
    baseline, _ = _query_count(admin, url)

    enrole('grand', 20)
    scaled, response = _query_count(admin, url)

    assert len(response.data) == 23
    assert scaled == baseline

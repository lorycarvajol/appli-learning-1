"""
Tests des classes, invitations et verrouillage des chapitres.

Trois familles de propriétés :

1. **Cloisonnement** : un formateur ne voit et ne pilote que ses classes.
2. **Invitations** : le rôle et la classe viennent du jeton, jamais du client.
3. **Accès aux chapitres** : le verrou existe vraiment, et ne se referme jamais.
"""
from datetime import timedelta

import pytest
from django.utils import timezone
from rest_framework.test import APIClient

from apps.accounts.models import User
from apps.cohorts.models import Cohort, CohortInvite
from apps.courses.models import Chapter, Lesson
from apps.progression.models import ChapterAccess, UserProgress
from apps.progression.services import ensure_self_paced_access

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
def trainer():
    return User.objects.create_user(
        email='formateur@example.com', password=TEST_PASSWORD,
        first_name='Formateur', role=User.Role.TRAINER,
    )


@pytest.fixture
def other_trainer():
    return User.objects.create_user(
        email='autre@example.com', password=TEST_PASSWORD, role=User.Role.TRAINER,
    )


@pytest.fixture
def admin():
    return User.objects.create_user(
        email='admin@example.com', password=TEST_PASSWORD, role=User.Role.ADMIN,
    )


@pytest.fixture
def cohort(trainer):
    return Cohort.objects.create(name='Promo Dev 2026', trainer=trainer)


@pytest.fixture
def learner(cohort):
    user = User.objects.create_user(
        email='eleve@example.com', password=TEST_PASSWORD, first_name='Eve',
    )
    user.profile.cohort = cohort
    user.profile.save()
    return user


@pytest.fixture
def solo_learner():
    """Apprenant inscrit en autonomie, sans classe."""
    return User.objects.create_user(email='solo@example.com', password=TEST_PASSWORD)


@pytest.fixture
def invite(cohort, trainer):
    return CohortInvite.objects.create(cohort=cohort, created_by=trainer)


@pytest.fixture
def chapters():
    """Deux chapitres publiés, d'une leçon chacun."""
    made = []
    for i in range(2):
        chapter = Chapter.objects.create(
            title=f'Chapitre {i + 1}', slug=f'chapitre-{i + 1}', description='…',
            estimated_duration=60, is_published=True, order_index=i,
        )
        Lesson.objects.create(
            chapter=chapter, title=f'Leçon {i + 1}', slug=f'lecon-{i + 1}',
            lesson_type='THEORY', points=10, is_published=True, order_index=0,
        )
        made.append(chapter)
    return made


# ---------------------------------------------------------------------------
# Cloisonnement formateur
# ---------------------------------------------------------------------------

def test_un_formateur_ne_voit_que_ses_classes(trainer, other_trainer):
    Cohort.objects.create(name='La mienne', trainer=trainer)
    Cohort.objects.create(name="Celle d'un autre", trainer=other_trainer)

    data = client_for(trainer).get('/api/cohorts/cohorts/').json()
    names = [c['name'] for c in data['results']]

    assert names == ['La mienne']


def test_un_admin_voit_toutes_les_classes(admin, trainer, other_trainer):
    Cohort.objects.create(name='A', trainer=trainer)
    Cohort.objects.create(name='B', trainer=other_trainer)

    data = client_for(admin).get('/api/cohorts/cohorts/').json()

    assert data['count'] == 2


def test_la_classe_creee_appartient_a_son_createur(trainer, other_trainer):
    """Le formateur vient de la requête : impossible d'en désigner un autre."""
    response = client_for(trainer).post(
        '/api/cohorts/cohorts/',
        {'name': 'Ma promo', 'trainer': str(other_trainer.id)},
        format='json',
    )

    assert response.status_code == 201
    assert Cohort.objects.get(name='Ma promo').trainer == trainer


def test_un_apprenant_ne_peut_pas_lister_les_classes(learner):
    assert client_for(learner).get('/api/cohorts/cohorts/').status_code == 403


def test_un_formateur_ne_voit_que_les_apprenants_de_ses_classes(
    trainer, other_trainer, learner
):
    """Régression : `learners_summary` renvoyait toute la plateforme."""
    autre_classe = Cohort.objects.create(name='Ailleurs', trainer=other_trainer)
    etranger = User.objects.create_user(email='etranger@example.com', password=TEST_PASSWORD)
    etranger.profile.cohort = autre_classe
    etranger.profile.save()

    data = client_for(trainer).get(
        '/api/progression/trainer-dashboard/learners_summary/'
    ).json()
    emails = [row['user']['email'] for row in data]

    assert emails == [learner.email]


def test_un_formateur_ne_peut_pas_debloquer_pour_un_etranger(
    trainer, other_trainer, chapters
):
    autre_classe = Cohort.objects.create(name='Ailleurs', trainer=other_trainer)
    etranger = User.objects.create_user(email='etranger@example.com', password=TEST_PASSWORD)
    etranger.profile.cohort = autre_classe
    etranger.profile.save()

    response = client_for(trainer).post(
        '/api/progression/chapter-access/unlock_chapter/',
        {'user_id': str(etranger.id), 'chapter_id': str(chapters[0].id)},
        format='json',
    )

    assert response.status_code == 403
    assert not ChapterAccess.objects.filter(user=etranger, is_unlocked=True).exists()


def test_le_detail_dun_apprenant_etranger_est_introuvable(trainer, other_trainer):
    autre_classe = Cohort.objects.create(name='Ailleurs', trainer=other_trainer)
    etranger = User.objects.create_user(email='etranger@example.com', password=TEST_PASSWORD)
    etranger.profile.cohort = autre_classe
    etranger.profile.save()

    response = client_for(trainer).get(
        f'/api/progression/trainer-dashboard/{etranger.id}/learner_detail/'
    )

    assert response.status_code == 404


def test_deblocage_groupe_pour_toute_la_classe(trainer, cohort, learner, chapters):
    autre = User.objects.create_user(email='eleve2@example.com', password=TEST_PASSWORD)
    autre.profile.cohort = cohort
    autre.profile.save()

    response = client_for(trainer).post(
        f'/api/cohorts/cohorts/{cohort.id}/unlock_chapter/',
        {'chapter_id': str(chapters[1].id)},
        format='json',
    )

    assert response.status_code == 200
    assert response.json()['members'] == 2
    for member in (learner, autre):
        assert ChapterAccess.objects.filter(
            user=member, chapter=chapters[1], is_unlocked=True
        ).exists()


# ---------------------------------------------------------------------------
# Invitations
# ---------------------------------------------------------------------------

def test_le_lien_public_ne_revele_que_le_minimum(invite, cohort):
    data = APIClient().get(f'/api/cohorts/join/{invite.token}/').json()

    assert data == {
        'valid': True,
        'role': 'LEARNER',
        'cohort_name': cohort.name,
        'trainer_name': 'Formateur',
    }
    # Ni compteurs d'usage, ni membres, ni identité de l'émetteur.
    assert 'uses_count' not in data
    assert 'members' not in data


@pytest.mark.parametrize('mutate', [
    lambda i: setattr(i, 'is_revoked', True),
    lambda i: setattr(i, 'expires_at', timezone.now() - timedelta(days=1)),
    lambda i: (setattr(i, 'max_uses', 1), setattr(i, 'uses_count', 1)),
])
def test_les_liens_inutilisables_sont_indistinguables(invite, mutate):
    """Révoqué, expiré ou épuisé donnent tous la même réponse qu'un jeton
    inexistant : sinon on confirme qu'un lien a existé."""
    mutate(invite)
    invite.save()

    assert APIClient().get(f'/api/cohorts/join/{invite.token}/').json() == {'valid': False}
    assert APIClient().get('/api/cohorts/join/nimportequoi/').json() == {'valid': False}


def test_accepter_une_invitation_cree_le_compte_et_rattache(invite, cohort):
    response = APIClient().post(
        f'/api/cohorts/join/{invite.token}/register/',
        {
            'email': 'nouveau@example.com', 'password': TEST_PASSWORD,
            'password_confirm': TEST_PASSWORD, 'first_name': 'Nouveau',
            'accept_terms': True,
        },
        format='json',
    )

    assert response.status_code == 201
    assert 'access' in response.json()['tokens']

    user = User.objects.get(email='nouveau@example.com')
    assert user.role == User.Role.LEARNER
    assert user.profile.cohort == cohort
    invite.refresh_from_db()
    assert invite.uses_count == 1


def test_le_role_ne_peut_pas_etre_force_par_le_formulaire(invite):
    """Le rôle vient du jeton. Le glisser dans le corps ne doit rien changer."""
    APIClient().post(
        f'/api/cohorts/join/{invite.token}/register/',
        {
            'email': 'malin@example.com', 'password': TEST_PASSWORD,
            'password_confirm': TEST_PASSWORD, 'role': 'ADMIN', 'is_staff': True,
            'accept_terms': True,
        },
        format='json',
    )

    user = User.objects.get(email='malin@example.com')
    assert user.role == User.Role.LEARNER
    assert user.is_staff is False


def test_la_classe_ne_peut_pas_etre_forcee_par_le_formulaire(invite, cohort, trainer):
    autre = Cohort.objects.create(name='Classe convoitée', trainer=trainer)

    APIClient().post(
        f'/api/cohorts/join/{invite.token}/register/',
        {
            'email': 'malin@example.com', 'password': TEST_PASSWORD,
            'password_confirm': TEST_PASSWORD, 'cohort': str(autre.id),
            'accept_terms': True,
        },
        format='json',
    )

    assert User.objects.get(email='malin@example.com').profile.cohort == cohort


def test_un_compte_existant_rejoint_sans_se_recreer(invite, cohort, solo_learner):
    """Cas de l'apprenant inscrit en autonomie qui reçoit un lien plus tard."""
    response = client_for(solo_learner).post(
        f'/api/cohorts/join/{invite.token}/attach/', {}, format='json'
    )

    assert response.status_code == 200
    solo_learner.profile.refresh_from_db()
    assert solo_learner.profile.cohort == cohort


def test_une_adresse_deja_inscrite_est_orientee_vers_la_connexion(invite, learner):
    response = APIClient().post(
        f'/api/cohorts/join/{invite.token}/register/',
        {
            'email': learner.email, 'password': TEST_PASSWORD,
            'password_confirm': TEST_PASSWORD, 'accept_terms': True,
        },
        format='json',
    )

    assert response.status_code == 400
    assert 'Connectez-vous' in response.json()['email'][0]


def test_le_nombre_dusages_est_respecte(invite, solo_learner):
    invite.max_uses = 1
    invite.save()

    client_for(solo_learner).post(f'/api/cohorts/join/{invite.token}/attach/', {}, format='json')

    response = APIClient().post(
        f'/api/cohorts/join/{invite.token}/register/',
        {'email': 'trop-tard@example.com', 'password': TEST_PASSWORD,
         'password_confirm': TEST_PASSWORD, 'accept_terms': True},
        format='json',
    )

    assert response.status_code == 400
    assert not User.objects.filter(email='trop-tard@example.com').exists()


def test_un_formateur_ne_peut_pas_en_recruter_un_autre(trainer):
    """Sinon le rôle formateur s'auto-réplique et perd tout sens."""
    response = client_for(trainer).post(
        '/api/cohorts/invites/', {'role': 'TRAINER'}, format='json'
    )

    assert response.status_code == 403


def test_un_admin_peut_inviter_un_formateur(admin):
    response = client_for(admin).post(
        '/api/cohorts/invites/', {'role': 'TRAINER'}, format='json'
    )
    assert response.status_code == 201

    token = response.json()['token']
    APIClient().post(
        f'/api/cohorts/join/{token}/register/',
        {'email': 'futur@example.com', 'password': TEST_PASSWORD,
         'password_confirm': TEST_PASSWORD, 'accept_terms': True},
        format='json',
    )

    assert User.objects.get(email='futur@example.com').role == User.Role.TRAINER


def test_un_formateur_ne_peut_pas_inviter_dans_la_classe_dun_autre(
    trainer, other_trainer
):
    autre_classe = Cohort.objects.create(name='Ailleurs', trainer=other_trainer)

    response = client_for(trainer).post(
        '/api/cohorts/invites/', {'cohort': str(autre_classe.id)}, format='json'
    )

    assert response.status_code == 403


def test_supprimer_une_invitation_la_revoque_sans_leffacer(trainer, invite):
    client_for(trainer).delete(f'/api/cohorts/invites/{invite.id}/')

    invite.refresh_from_db()
    assert invite.is_revoked is True
    assert CohortInvite.objects.filter(pk=invite.pk).exists()


# ---------------------------------------------------------------------------
# Verrouillage des chapitres
# ---------------------------------------------------------------------------

def test_un_chapitre_non_debloque_bloque_ses_lecons(learner, chapters):
    """Régression : ChapterAccess n'était consulté par aucune vue apprenant."""
    response = client_for(learner).get(f'/api/courses/lessons/{chapters[1].lessons.first().slug}/')

    assert response.status_code == 403


def test_un_chapitre_debloque_ouvre_ses_lecons(learner, chapters, trainer):
    ChapterAccess.objects.create(user=learner, chapter=chapters[1], is_unlocked=True)

    response = client_for(learner).get(f'/api/courses/lessons/{chapters[1].lessons.first().slug}/')

    assert response.status_code == 200


def test_les_chapitres_verrouilles_restent_listes(learner, chapters):
    """Masquer la suite priverait l'apprenant de la vue d'ensemble."""
    data = client_for(learner).get('/api/courses/chapters/').json()
    results = {c['slug']: c['is_accessible'] for c in data['results']}

    assert set(results) == {'chapitre-1', 'chapitre-2'}
    assert results['chapitre-2'] is False


def test_le_formateur_accede_a_tout(trainer, chapters):
    response = client_for(trainer).get(f'/api/courses/lessons/{chapters[1].lessons.first().slug}/')

    assert response.status_code == 200


# ---------------------------------------------------------------------------
# Rythme libre (apprenant sans classe)
# ---------------------------------------------------------------------------

def test_le_premier_chapitre_est_ouvert_a_un_autonome(solo_learner, chapters):
    ensure_self_paced_access(solo_learner)

    assert ChapterAccess.objects.filter(
        user=solo_learner, chapter=chapters[0], is_unlocked=True
    ).exists()
    assert not ChapterAccess.objects.filter(
        user=solo_learner, chapter=chapters[1], is_unlocked=True
    ).exists()


def test_terminer_un_chapitre_ouvre_le_suivant(solo_learner, chapters):
    UserProgress.objects.create(
        user=solo_learner, lesson=chapters[0].lessons.first(),
        status=UserProgress.ProgressStatus.COMPLETED,
    )

    ensure_self_paced_access(solo_learner)

    assert ChapterAccess.objects.filter(
        user=solo_learner, chapter=chapters[1], is_unlocked=True
    ).exists()


def test_un_apprenant_en_classe_ne_beneficie_pas_du_rythme_libre(learner, chapters):
    """En classe, c'est le formateur qui donne le tempo."""
    ensure_self_paced_access(learner)

    assert not ChapterAccess.objects.filter(user=learner, is_unlocked=True).exists()


def test_rejoindre_une_classe_ne_retire_aucun_acces(solo_learner, chapters, invite):
    """« On ne reverrouille jamais » — sinon rejoindre une classe punirait
    l'apprenant qui avait déjà avancé seul."""
    ensure_self_paced_access(solo_learner)
    acquired = set(
        ChapterAccess.objects.filter(user=solo_learner, is_unlocked=True)
        .values_list('chapter_id', flat=True)
    )
    assert acquired

    client_for(solo_learner).post(f'/api/cohorts/join/{invite.token}/attach/', {}, format='json')

    still = set(
        ChapterAccess.objects.filter(user=solo_learner, is_unlocked=True)
        .values_list('chapter_id', flat=True)
    )
    assert still == acquired

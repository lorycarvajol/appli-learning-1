"""
Tests des comptes utilisateurs.

Trois régressions sont verrouillées ici, chacune ayant causé une panne ou une
perte de données silencieuse :

1. `User.Role` manquait → le déblocage de chapitre renvoyait HTTP 500
2. un signal réécrivait le profil depuis la mémoire → points perdus
3. les emails n'étaient normalisés que sur le domaine → comptes en double
"""
import pytest
from django.db import IntegrityError, transaction
from rest_framework.test import APIClient

from apps.accounts.models import Profile, User
from apps.cohorts.models import Cohort
from apps.courses.models import Chapter
from apps.gamification.models import PointTransaction
from apps.gamification.services import award_points

pytestmark = pytest.mark.django_db


@pytest.fixture
def learner():
    return User.objects.create_user(
        email='eleve@example.com', password='Motdepasse!2026', first_name='Eve'
    )


@pytest.fixture
def trainer():
    return User.objects.create_user(
        email='formateur@example.com', password='Motdepasse!2026',
        role=User.Role.TRAINER,
    )


# ---------------------------------------------------------------------------
# 1. Rôles
# ---------------------------------------------------------------------------

def test_les_roles_sont_exposes_comme_choices():
    """`User.Role` doit exister : du code applicatif s'y réfère."""
    assert User.Role.LEARNER == 'LEARNER'
    assert User.Role.TRAINER == 'TRAINER'
    assert User.Role.ADMIN == 'ADMIN'
    assert User.ROLE_CHOICES == User.Role.choices


def test_un_nouvel_utilisateur_est_apprenant_par_defaut(learner):
    assert learner.role == User.Role.LEARNER


def test_le_deblocage_de_chapitre_fonctionne(trainer, learner):
    """Régression : cette route renvoyait HTTP 500 (User.Role inexistant)."""
    chapter = Chapter.objects.create(
        title='HTML', slug='html', description='…',
        estimated_duration=60, is_published=True,
    )
    # Depuis l'introduction des classes, un formateur ne peut débloquer que
    # pour ses propres apprenants (cf. apps/cohorts/tests).
    cohort = Cohort.objects.create(name='Promo', trainer=trainer)
    learner.profile.cohort = cohort
    learner.profile.save()

    client = APIClient()
    client.force_authenticate(user=trainer)

    response = client.post(
        '/api/progression/chapter-access/unlock_chapter/',
        {'user_id': str(learner.id), 'chapter_id': str(chapter.id)},
        format='json',
    )

    assert response.status_code == 200
    assert response.json()['is_unlocked'] is True


def test_un_apprenant_ne_peut_pas_debloquer_de_chapitre(learner):
    chapter = Chapter.objects.create(
        title='HTML', slug='html', description='…',
        estimated_duration=60, is_published=True,
    )
    client = APIClient()
    client.force_authenticate(user=learner)

    response = client.post(
        '/api/progression/chapter-access/unlock_chapter/',
        {'user_id': str(learner.id), 'chapter_id': str(chapter.id)},
        format='json',
    )

    assert response.status_code == 403


def test_un_apprenant_ne_peut_pas_se_promouvoir(learner):
    """Le rôle est en lecture seule : pas d'auto-promotion via PATCH /me/."""
    client = APIClient()
    client.force_authenticate(user=learner)

    response = client.patch('/api/auth/me/', {'role': 'ADMIN'}, format='json')

    assert response.status_code == 200
    learner.refresh_from_db()
    assert learner.role == User.Role.LEARNER


# ---------------------------------------------------------------------------
# 2. Le profil n'est plus écrasé par une sauvegarde du User
# ---------------------------------------------------------------------------

def test_sauver_le_user_nefface_pas_les_points_du_profil(learner):
    """Régression : un signal réécrivait le profil chargé en mémoire.

    Le scénario réel : `request.user.profile` est lu en début de requête,
    des points sont crédités par ailleurs, puis un `user.save()` (mise à jour
    de last_login, changement de mot de passe...) réécrivait l'ancien solde.
    """
    stale_profile = learner.profile          # profil chargé en mémoire
    assert stale_profile.total_points == 0

    award_points(learner, 150, PointTransaction.Reason.MANUAL, source_key='test:x')

    learner.first_name = 'Eve'
    learner.save()                            # ne doit toucher qu'au User

    assert Profile.objects.get(user=learner).total_points == 150


def test_le_profil_est_cree_une_seule_fois(learner):
    learner.save()
    learner.save()
    assert Profile.objects.filter(user=learner).count() == 1


# ---------------------------------------------------------------------------
# 3. Emails : une seule casse possible
# ---------------------------------------------------------------------------

def test_lemail_est_normalise_en_minuscules():
    user = User.objects.create_user(
        email='  Prenom.Nom@Ecole.FR  ', password='Motdepasse!2026'
    )
    assert user.email == 'prenom.nom@ecole.fr'


def test_deux_casses_du_meme_email_sont_le_meme_compte():
    """Régression : `normalize_email` ne minuscule que le domaine."""
    User.objects.create_user(email='Loryc@example.com', password='Motdepasse!2026')

    with pytest.raises(IntegrityError):
        with transaction.atomic():
            User.objects.create_user(
                email='loryc@example.com', password='Motdepasse!2026'
            )


def test_la_contrainte_resiste_a_une_ecriture_hors_modele():
    """`update()` court-circuite `save()` : la base doit tenir seule."""
    User.objects.create_user(email='a@example.com', password='Motdepasse!2026')
    other = User.objects.create_user(email='b@example.com', password='Motdepasse!2026')

    with pytest.raises(IntegrityError):
        with transaction.atomic():
            User.objects.filter(pk=other.pk).update(email='A@example.com')


def test_connexion_insensible_a_la_casse(learner):
    """L'apprenant doit pouvoir taper son email comme il l'écrit d'habitude."""
    client = APIClient()

    response = client.post(
        '/api/auth/login/',
        {'email': 'Eleve@Example.com', 'password': 'Motdepasse!2026'},
        format='json',
    )

    assert response.status_code == 200
    assert 'access' in response.json()


def test_inscription_puis_connexion_avec_une_autre_casse():
    client = APIClient()

    register = client.post(
        '/api/auth/register/',
        {
            'email': 'Nouvel.Eleve@Ecole.FR',
            'password': 'Motdepasse!2026',
            'password_confirm': 'Motdepasse!2026',
            'first_name': 'Nouvel',
            'last_name': 'Eleve',
        },
        format='json',
    )
    assert register.status_code == 201
    assert register.json()['user']['email'] == 'nouvel.eleve@ecole.fr'

    login = client.post(
        '/api/auth/login/',
        {'email': 'nouvel.eleve@ecole.fr', 'password': 'Motdepasse!2026'},
        format='json',
    )
    assert login.status_code == 200

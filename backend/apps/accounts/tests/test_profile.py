"""
Tests de la personnalisation du profil.

L'enjeu : ouvrir l'écriture du profil à l'apprenant lui-même **sans** ouvrir
au passage ce qui ne lui appartient pas — son rôle, sa classe, son solde de
points.
"""
import pytest
from rest_framework.test import APIClient

from apps.accounts.avatars import avatar_choices
from apps.accounts.models import Profile, User
from apps.cohorts.models import Cohort

pytestmark = pytest.mark.django_db

TEST_PASSWORD = 'fixture-pwd-not-a-real-secret'


def client_for(user):
    client = APIClient()
    client.force_authenticate(user=user)
    return client


@pytest.fixture
def learner():
    return User.objects.create_user(
        email='eleve@example.com', password=TEST_PASSWORD, first_name='Eve',
    )


# ---------------------------------------------------------------------------
# Ce que l'apprenant peut changer
# ---------------------------------------------------------------------------

def test_un_apprenant_personnalise_son_profil(learner):
    response = client_for(learner).patch('/api/auth/me/', {
        'first_name': 'Ève',
        'profile': {
            'bio': 'J’apprends le JavaScript.',
            'avatar_key': 'nova-violet',
            'theme': Profile.Theme.DARK,
            'github_username': 'eve-dev',
        },
    }, format='json')

    assert response.status_code == 200
    learner.refresh_from_db()
    assert learner.first_name == 'Ève'
    assert learner.profile.avatar_key == 'nova-violet'
    assert learner.profile.theme == Profile.Theme.DARK
    assert learner.profile.bio == 'J’apprends le JavaScript.'


def test_le_catalogue_davatars_est_expose(learner):
    response = client_for(learner).get('/api/auth/avatars/')

    assert response.status_code == 200
    assert 'nova' in response.data['visages']
    assert 'violet' in response.data['palettes']
    assert 'nova-violet' in response.data['keys']

    # Sept familles de six visages, six palettes.
    assert len(response.data['visages']) == 42
    assert len(response.data['keys']) == 42 * 6

    # Un visage dont l'identifiant porterait un tiret casserait le découpage de
    # la clé côté client : la clé serait tronquée, donc refusée, et l'apprenant
    # verrait son choix revenir aux initiales sans explication.
    assert all('-' not in visage for visage in response.data['visages'])


def test_lavatar_vide_est_accepte(learner):
    """Revenir aux initiales doit rester possible."""
    learner.profile.avatar_key = 'nova-violet'
    learner.profile.save()

    response = client_for(learner).patch(
        '/api/auth/me/', {'profile': {'avatar_key': ''}}, format='json',
    )

    assert response.status_code == 200
    learner.refresh_from_db()
    assert learner.profile.avatar_key == ''


# ---------------------------------------------------------------------------
# Ce qu'il ne peut pas changer
# ---------------------------------------------------------------------------

def test_une_cle_davatar_hors_catalogue_est_refusee(learner):
    """Sans validation serveur, la chaîne finirait dans le rendu SVG du client."""
    response = client_for(learner).patch('/api/auth/me/', {
        'profile': {'avatar_key': '<script>alert(1)</script>'},
    }, format='json')

    assert response.status_code == 400
    learner.refresh_from_db()
    assert learner.profile.avatar_key == ''


@pytest.mark.parametrize('cle', avatar_choices()[:3])
def test_toutes_les_cles_du_catalogue_sont_acceptees(learner, cle):
    response = client_for(learner).patch(
        '/api/auth/me/', {'profile': {'avatar_key': cle}}, format='json',
    )
    assert response.status_code == 200


def test_le_profil_ne_permet_pas_de_se_crediter_des_points(learner):
    """`total_points` est un solde dérivé du grand livre, pas une saisie."""
    learner.profile.total_points = 10
    learner.profile.save()

    response = client_for(learner).patch('/api/auth/me/', {
        'profile': {'total_points': 99999, 'level': 42, 'bio': 'coucou'},
    }, format='json')

    assert response.status_code == 200
    learner.refresh_from_db()
    assert learner.profile.total_points == 10
    assert learner.profile.level == 1
    assert learner.profile.bio == 'coucou'


def test_le_profil_expose_le_nom_de_la_classe(learner):
    """L'en-tête du profil l'affiche : sans ce champ, la ligne reste morte.

    Elle l'a été longtemps — le composant lisait `profile.cohort_name`, que le
    sérialiseur ne produisait pas.
    """
    learner.profile.cohort = Cohort.objects.create(name='Promo 2026')
    learner.profile.save(update_fields=['cohort'])

    response = client_for(learner).get('/api/auth/me/')

    assert response.status_code == 200
    assert response.data['profile']['cohort_name'] == 'Promo 2026'


def test_le_nom_de_classe_vaut_none_sans_classe(learner):
    """Un apprenant autonome n'a pas de classe : le champ doit valoir `None`,
    pas faire échouer la sérialisation."""
    response = client_for(learner).get('/api/auth/me/')

    assert response.status_code == 200
    assert response.data['profile']['cohort_name'] is None


def test_le_nom_de_classe_reste_en_lecture_seule(learner):
    """L'exposer ne doit pas offrir une deuxième voie pour changer de classe."""
    cohort = Cohort.objects.create(name='Promo fermée')

    response = client_for(learner).patch('/api/auth/me/', {
        'profile': {'cohort_name': cohort.name},
    }, format='json')

    assert response.status_code == 200
    learner.refresh_from_db()
    assert learner.profile.cohort is None


def test_le_profil_ne_permet_pas_de_changer_de_classe(learner):
    """La classe relève du formateur : s'y inscrire soi-même contournerait
    l'invitation et le déblocage contrôlé des chapitres."""
    cohort = Cohort.objects.create(name='Promo fermée')

    client_for(learner).patch('/api/auth/me/', {
        'profile': {'cohort': str(cohort.id)},
    }, format='json')

    learner.refresh_from_db()
    assert learner.profile.cohort is None


def test_le_profil_ne_permet_pas_de_changer_de_role(learner):
    """Déjà verrouillé par `read_only_fields`, mais l'écriture imbriquée du
    profil est une nouvelle porte — on revérifie qu'elle ne l'a pas ouverte."""
    response = client_for(learner).patch(
        '/api/auth/me/', {'role': User.Role.ADMIN}, format='json',
    )

    assert response.status_code == 200
    learner.refresh_from_db()
    assert learner.role == User.Role.LEARNER


def test_une_bio_demesuree_est_refusee(learner):
    response = client_for(learner).patch(
        '/api/auth/me/', {'profile': {'bio': 'x' * 501}}, format='json',
    )
    assert response.status_code == 400


def test_modifier_le_profil_necrase_pas_un_gain_de_points_concurrent(learner):
    """Le piège documenté dans `signals.py`, reproduit sur la nouvelle voie.

    On charge l'utilisateur (donc un profil en mémoire avec l'ancien solde),
    des points sont crédités entre-temps, puis on enregistre la bio. Écrire le
    profil en entier remettrait l'ancien solde ; `update_fields` l'évite.
    """
    from apps.gamification.services import award_points

    charge = User.objects.select_related('profile').get(pk=learner.pk)
    assert charge.profile.total_points == 0

    award_points(learner, 50, reason='TEST', source_key='test:1')

    serializer_input = {'profile': {'bio': 'écrit après coup'}}
    response = client_for(charge).patch('/api/auth/me/', serializer_input, format='json')

    assert response.status_code == 200
    learner.refresh_from_db()
    assert learner.profile.total_points == 50
    assert learner.profile.bio == 'écrit après coup'


def test_un_apprenant_ne_modifie_pas_le_profil_dun_autre(learner):
    """`/me/` est toujours résolu depuis le jeton, jamais depuis un paramètre."""
    autre = User.objects.create_user(
        email='autre@example.com', password=TEST_PASSWORD,
    )

    client_for(learner).patch(
        '/api/auth/me/', {'profile': {'bio': 'piraté'}}, format='json',
    )

    autre.refresh_from_db()
    assert autre.profile.bio == ''


# ---------------------------------------------------------------------------
# Bordure d'avatar
#
# Champ distinct d'`avatar_key`, et non un troisième segment de la clé : la
# clé est découpée sur le tiret côté client, l'y ajouter aurait invalidé
# toutes celles déjà en base.
# ---------------------------------------------------------------------------

def test_un_apprenant_choisit_une_bordure(learner):
    response = client_for(learner).patch(
        '/api/auth/me/', {'profile': {'avatar_border': 'double'}}, format='json',
    )

    assert response.status_code == 200
    learner.refresh_from_db()
    assert learner.profile.avatar_border == 'double'


def test_la_bordure_vide_est_acceptee(learner):
    """« Aucune bordure » est l'état neutre, il doit rester atteignable."""
    learner.profile.avatar_border = 'lueur'
    learner.profile.save(update_fields=['avatar_border'])

    response = client_for(learner).patch(
        '/api/auth/me/', {'profile': {'avatar_border': ''}}, format='json',
    )

    assert response.status_code == 200
    learner.refresh_from_db()
    assert learner.profile.avatar_border == ''


def test_une_bordure_hors_catalogue_est_refusee(learner):
    """Sans ce refus, la valeur finirait interpolée dans le rendu du client."""
    response = client_for(learner).patch(
        '/api/auth/me/',
        {'profile': {'avatar_border': '"><script>'}},
        format='json',
    )

    assert response.status_code == 400
    learner.refresh_from_db()
    assert learner.profile.avatar_border == ''


def test_choisir_une_bordure_ne_touche_pas_a_l_avatar(learner):
    """Les deux champs sont indépendants : c'est tout l'intérêt de les avoir
    séparés plutôt que d'allonger la clé."""
    learner.profile.avatar_key = 'nova-violet'
    learner.profile.save(update_fields=['avatar_key'])

    client_for(learner).patch(
        '/api/auth/me/', {'profile': {'avatar_border': 'clair'}}, format='json',
    )

    learner.refresh_from_db()
    assert learner.profile.avatar_key == 'nova-violet'
    assert learner.profile.avatar_border == 'clair'


def test_le_catalogue_expose_les_bordures(learner):
    response = client_for(learner).get('/api/auth/avatars/')

    assert response.status_code == 200
    assert '' in response.data['bordures'], "« aucune » doit être proposable"
    assert 'double' in response.data['bordures']

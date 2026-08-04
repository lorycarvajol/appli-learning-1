"""
Comptes de démonstration et comptes de test.

`create_demo_users` crée un formateur dont le mot de passe (`trainer123`) est
écrit dans le dépôt et documenté dans plusieurs fichiers. Rien n'empêchait de
lancer cette commande sur une instance réelle : il suffisait de recopier la
ligne d'amorçage de `frontend/e2e/README.md` sur le serveur pour ouvrir à
quiconque lit GitHub un compte formateur — et un formateur voit la progression
de ses apprenants, débloque des chapitres, consulte sa classe.

Le garde-fou porte sur `settings.ENVIRONMENT`, pas sur `settings.DEBUG` : le
lanceur de tests force `DEBUG = False`, ce qui aurait rendu le comportement
intestable, alors qu'`ENVIRONMENT` est la variable qui sélectionne réellement
les réglages de production.
"""
import pytest
from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import override_settings

from apps.accounts.models import User
from apps.accounts.management.commands.create_demo_users import DEMO_EMAILS
from apps.accounts.management.commands.purge_test_accounts import find_test_accounts

pytestmark = pytest.mark.django_db


# ---------------------------------------------------------------------------
# Le garde-fou de production
# ---------------------------------------------------------------------------

@override_settings(ENVIRONMENT='production')
def test_create_demo_users_refuse_de_tourner_en_production():
    with pytest.raises(CommandError) as erreur:
        call_command('create_demo_users', verbosity=0)

    # Le message doit orienter vers la bonne commande, pas seulement refuser.
    assert 'createsuperuser' in str(erreur.value)
    assert not User.objects.filter(email__in=DEMO_EMAILS).exists()


@override_settings(ENVIRONMENT='development')
def test_create_demo_users_fonctionne_en_developpement():
    """Le garde-fou ne doit pas gêner l'usage légitime."""
    call_command('create_demo_users', verbosity=0)

    assert User.objects.filter(email__in=DEMO_EMAILS).count() == len(DEMO_EMAILS)
    formateur = User.objects.get(email='trainer@test.com')
    assert formateur.role == 'TRAINER'
    assert formateur.check_password('trainer123')


@override_settings(ENVIRONMENT='development')
def test_create_demo_users_est_rejouable():
    call_command('create_demo_users', verbosity=0)
    call_command('create_demo_users', verbosity=0)
    assert User.objects.filter(email__in=DEMO_EMAILS).count() == len(DEMO_EMAILS)


# ---------------------------------------------------------------------------
# Le nettoyage
# ---------------------------------------------------------------------------

@pytest.fixture
def base_encombree():
    """Une base mêlant comptes de test et comptes réels."""
    for email in DEMO_EMAILS:
        User.objects.create_user(email=email, password='x')
    for i in range(3):
        User.objects.create_user(email=f'e2e-178472279{i}-abc{i}xy@example.com', password='x')
    vrai = User.objects.create_user(email='eleve.reel@lycee.fr', password='x')
    return vrai


def test_le_recensement_distingue_les_comptes_de_test_des_vrais(base_encombree):
    demo, e2e, douteux = find_test_accounts()

    assert {u.email for u in demo} == set(DEMO_EMAILS)
    assert len(e2e) == 3
    assert not douteux
    assert base_encombree.email not in {u.email for u in demo + e2e}


def test_une_adresse_e2e_au_format_inattendu_est_signalee_et_conservee():
    """Ni supprimée en silence, ni ignorée en silence.

    Écarter une adresse que le motif ne reconnaît pas serait le pire des deux
    mondes : elle resterait en base sans que personne ne le sache.
    """
    User.objects.create_user(email='e2e-ancien-format@example.com', password='x')

    demo, e2e, douteux = find_test_accounts()
    assert not demo and not e2e
    assert [u.email for u in douteux] == ['e2e-ancien-format@example.com']

    call_command('purge_test_accounts', '--apply', verbosity=0)
    assert User.objects.filter(email='e2e-ancien-format@example.com').exists()


def test_sans_apply_la_commande_ne_supprime_rien(base_encombree):
    """Le recensement doit rester sûr : c'est le mode par défaut."""
    avant = User.objects.count()
    call_command('purge_test_accounts', verbosity=0)
    assert User.objects.count() == avant


def test_avec_apply_seuls_les_comptes_de_test_disparaissent(base_encombree):
    call_command('purge_test_accounts', '--apply', verbosity=0)

    assert not User.objects.filter(email__in=DEMO_EMAILS).exists()
    assert not User.objects.filter(email__startswith='e2e-').exists()
    assert User.objects.filter(email=base_encombree.email).exists()


def test_un_administrateur_a_adresse_de_test_n_est_jamais_supprime():
    """Filet anti-enfermement.

    `trainer@test.com` a été promu ADMIN à la main sur la base de
    développement. Si un tel compte était le seul administrateur d'une
    instance, le supprimer la rendrait impilotable — même logique que le
    garde-fou « dernier administrateur actif » du cycle de vie des comptes.
    """
    admin = User.objects.create_user(email='trainer@test.com', password='x')
    admin.role = 'ADMIN'
    admin.save()

    call_command('purge_test_accounts', '--apply', verbosity=0)

    assert User.objects.filter(email='trainer@test.com').exists()

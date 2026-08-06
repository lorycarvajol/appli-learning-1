"""
Tests des commandes de chargement de contenu.

Le contenu pédagogique ne vit pas en base : il vit dans les commandes
`apps/courses/management/commands/load_*`. La base n'en est qu'une projection.
Ces commandes sont donc *destructives par conception* — elles suppriment avant
de recréer — et c'est exactement là qu'un incident s'est produit.

Le 2026-07-22, `load_demo_content` faisait `Chapter.objects.all().delete()`.
Il n'emportait pas seulement ses trois chapitres de démonstration mais **tout**
le contenu, y compris les chapitres bien plus riches produits par les
`load_section_*`. Comme l'amorçage de la suite Playwright recommandait cette
commande, lancer les tests bout-en-bout suffisait à vider les cours.

L'invariant verrouillé ici est donc : **une commande de chargement ne supprime
que les chapitres qu'elle crée elle-même.**
"""
import pytest
from django.core.management import call_command

from apps.courses.models import Chapter, Lesson
from apps.courses.management.commands.load_demo_content import DEMO_CHAPTER_SLUGS

pytestmark = pytest.mark.django_db


@pytest.fixture
def chapitre_etranger():
    """Un chapitre qu'aucune commande de démonstration ne crée.

    Représente ici les chapitres des `load_section_*` — c'est la catégorie qui
    a réellement été détruite.
    """
    chapter = Chapter.objects.create(
        title='Réaliser un site vitrine',
        slug='site-vitrine',
        description='Chapitre riche, produit par load_section_4.',
        order_index=4,
        estimated_duration=600,
        is_published=True,
    )
    Lesson.objects.create(
        chapter=chapter,
        title='Choisir son poste de travail',
        slug='site-vitrine-poste',
        lesson_type='THEORY',
        order_index=1,
        content='# Un contenu long et coûteux à reproduire',
        is_published=True,
    )
    return chapter


def test_load_demo_content_ne_supprime_pas_les_chapitres_des_autres(chapitre_etranger):
    """Le cœur de la régression du 2026-07-22.

    Avant correction, ce chapitre disparaissait — avec ses leçons, et par
    cascade avec la progression des apprenants qui l'avaient entamé.
    """
    call_command('load_demo_content', '--force', verbosity=0)

    chapitre_etranger.refresh_from_db()
    assert Chapter.objects.filter(slug='site-vitrine').exists()
    assert chapitre_etranger.lessons.count() == 1


def test_load_demo_content_est_rejouable_sans_doublon():
    """Deux passages laissent un seul exemplaire de chaque chapitre de démo.

    C'est la contrepartie de la suppression bornée : si un slug créé plus bas
    manquait à `DEMO_CHAPTER_SLUGS`, la relance laisserait un doublon derrière
    elle (ou échouerait sur la contrainte d'unicité du slug).
    """
    call_command('load_demo_content', '--force', verbosity=0)
    premiers = set(Chapter.objects.values_list('slug', flat=True))

    call_command('load_demo_content', '--force', verbosity=0)

    assert set(Chapter.objects.values_list('slug', flat=True)) == premiers
    for slug in DEMO_CHAPTER_SLUGS:
        assert Chapter.objects.filter(slug=slug).count() == 1


def test_les_slugs_declares_couvrent_les_chapitres_reellement_crees():
    """`DEMO_CHAPTER_SLUGS` doit rester le miroir exact de ce que la commande crée.

    Sans ce test, ajouter un chapitre à la commande sans l'ajouter à la liste
    passerait inaperçu jusqu'à la première relance.
    """
    call_command('load_demo_content', '--force', verbosity=0)

    assert set(Chapter.objects.values_list('slug', flat=True)) == set(DEMO_CHAPTER_SLUGS)


def test_load_section_1_html_ne_touche_quau_chapitre_html(chapitre_etranger):
    """Le loader de section est celui qui amorce les tests E2E : il doit être sûr.

    Il fournit aussi le chapitre attendu par `navigation.spec.js` — même slug,
    même titre, premier du parcours — d'où le fait qu'il remplace
    `load_demo_content` dans la procédure d'amorçage.
    """
    call_command('load_section_1_html', '--force', verbosity=0)

    assert Chapter.objects.filter(slug='site-vitrine').exists()

    html = Chapter.objects.get(slug='introduction-html')
    assert html.title == 'Introduction au HTML'
    assert html.order_index == 1
    assert html.lessons.filter(slug='quest-ce-que-le-html').exists()

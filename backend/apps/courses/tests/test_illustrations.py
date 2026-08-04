"""
Cohérence des illustrations de cours.

Le 2026-08-04, le cours ne montrait **aucune** illustration : 31 PNG dormaient
dans `media/courses/` sans qu'une seule leçon les cite. Les figures étaient
posées par des scripts qui modifiaient la base *après coup* ; recharger un
chapitre effaçait leur travail sans rien signaler.

Les règles vivent désormais dans `content/illustrations.py` et sont appliquées
par le chargeur du chapitre. Ces tests verrouillent les trois façons dont cette
mécanique peut se désaccorder en silence :

- une règle cite un fichier qui n'existe pas → figure cassée dans la leçon ;
- un fichier n'est cité par aucune règle → poids mort, et signe qu'une figure
  a été dessinée puis oubliée (c'était le cas de `viewport.avif`) ;
- une ancre ne correspond plus au texte source → la figure disparaît.

Les deux premiers ne touchent pas la base : ils lisent le disque et le registre.
"""
from pathlib import Path

import pytest
from django.conf import settings

from apps.courses.content import illustrations
from apps.courses.models import Chapter, Lesson

MEDIA_COURSES = Path(settings.MEDIA_ROOT) / 'courses'


def _disk_images():
    """Chemins d'illustrations présents sur le disque, au format des règles."""
    return {
        '/media/' + p.relative_to(settings.MEDIA_ROOT).as_posix()
        for p in MEDIA_COURSES.rglob('*')
        if p.is_file()
    }


def test_toute_image_citee_existe_sur_le_disque():
    """Une règle qui pointe dans le vide donne une image cassée en production.

    Rien d'autre ne l'attraperait : le chargement réussit, la leçon s'affiche,
    seul le visuel manque.
    """
    manquantes = illustrations.referenced_images() - _disk_images()
    assert not manquantes, (
        f"Ces illustrations sont citées par content/illustrations.py mais "
        f"absentes de media/courses/ : {sorted(manquantes)}"
    )


def test_aucune_illustration_orpheline():
    """Un fichier que personne ne cite est une figure oubliée, pas un fichier en trop.

    C'est ce test qui aurait signalé les 31 PNG inutilisés — et `viewport.avif`,
    resté sur le disque après avoir été remplacé par sa version PNG.
    """
    orphelines = _disk_images() - illustrations.referenced_images()
    assert not orphelines, (
        f"Ces fichiers de media/courses/ ne sont cités par aucune règle : "
        f"{sorted(orphelines)}. Les rattacher dans content/illustrations.py, "
        f"ou les supprimer."
    )


def test_une_regle_sans_ancre_leve_une_erreur():
    """La panne doit être bruyante.

    Les anciens scripts faisaient `content.replace()` sans vérifier : un texte
    source modifié faisait échouer l'insertion **en silence**, et la leçon
    partait en base amputée de sa figure.
    """
    regle = illustrations.after(
        'une ancre qui ne figure nulle part', '/media/courses/x/y/z.png', 'légende'
    )
    with pytest.raises(illustrations.IllustrationError):
        regle.apply_to('un contenu de leçon quelconque', 'lecon-test')


def test_une_regle_deja_appliquee_ne_duplique_pas_la_figure():
    """Idempotence : c'est ce qui permet de recharger un chapitre sans crainte."""
    image = '/media/courses/x/y/z.png'
    regle = illustrations.after('ANCRE', image, 'légende')

    contenu, applique = regle.apply_to('avant ANCRE après', 'lecon-test')
    assert applique
    assert contenu.count(image) == 1

    # Deuxième passage : l'ancre est toujours là, mais la figure aussi.
    reapplique, change = regle.apply_to(contenu, 'lecon-test')
    assert not change
    assert reapplique == contenu
    assert reapplique.count(image) == 1


@pytest.mark.django_db
def test_le_chargement_dun_chapitre_pose_ses_illustrations():
    """Le test de bout en bout : une commande, un chapitre complet et illustré.

    Il couvre la régression d'origine — le contenu arrivait en base sans ses
    figures, et il fallait penser à lancer un second script pour les poser.
    """
    from django.core.management import call_command

    call_command('load_section_1_html', '--force', verbosity=0)

    chapitre = Chapter.objects.get(slug='introduction-html')
    contenu = '\n'.join(chapitre.lessons.values_list('content', flat=True))

    assert '/media/courses/html/section1/html-css-js-comparison.png' in contenu
    assert 'Illustration à voir' not in contenu, (
        "Un marqueur « Illustration à voir » a survécu au chargement : "
        "la figure correspondante n'a pas été posée."
    )


@pytest.mark.django_db
def test_recharger_un_chapitre_ne_change_pas_son_contenu():
    """Deux chargements successifs doivent donner exactement le même contenu.

    Sans cette garantie, la ré-application des règles empilerait les figures à
    chaque passage — le défaut classique d'un enrichissement par substitution.
    """
    from django.core.management import call_command

    call_command('load_section_1_html', '--force', verbosity=0)
    premier = dict(
        Lesson.objects.filter(chapter__slug='introduction-html')
        .values_list('slug', 'content')
    )

    call_command('load_section_1_html', '--force', verbosity=0)
    second = dict(
        Lesson.objects.filter(chapter__slug='introduction-html')
        .values_list('slug', 'content')
    )

    assert premier == second

"""
Assemblage d'un chapitre : contenu de base, compléments, illustrations.

Avant ce module, construire un chapitre complet demandait de lancer jusqu'à
six scripts, dans un ordre précis que rien n'écrivait nulle part — et dont
l'oubli produisait un chapitre amputé sans le moindre message. Le chapitre 1
demandait par exemple `load_section_1_html`, puis `expand_section_1_html.py`,
puis `add_html_quiz.py`, puis `fix_html_quiz_option_order.py`, puis deux
scripts d'images. La contrainte la plus surprenante : `expand_section_1_html`
échouait si `add_html_quiz` n'était pas passé avant.

Désormais **une commande construit un chapitre entier**. `finish()` est le
point de passage commun : il joue les compléments dans l'ordre déclaré par la
commande, rattache les illustrations, puis affiche le récapitulatif.
"""
import contextlib
import io

from .illustrations import attach_to_chapter


def _replay(command, text):
    """Réémet vers la sortie de la commande ce que les étapes ont `print()`.

    Les modules de `content/` viennent de scripts autonomes et écrivent avec
    `print()`. Les réécrire tous pour prendre un flux en paramètre toucherait
    des centaines de lignes de contenu pédagogique pour un gain nul : on capte
    la sortie ici, une fois.
    """
    for line in text.rstrip().splitlines():
        command.stdout.write(f'  {line}')


def run_steps(command, steps, verbosity=1):
    """Exécute les `build()` complémentaires d'un chapitre, dans l'ordre."""
    for step in steps:
        buffer = io.StringIO()
        with contextlib.redirect_stdout(buffer):
            step()
        if verbosity:
            _replay(command, buffer.getvalue())


def finish(command, chapter, steps=(), verbosity=1):
    """Complète un chapitre puis affiche son récapitulatif.

    À appeler à la fin de chaque `load_section_*`, une fois le contenu de base
    créé. Rattacher les illustrations **ici** est ce qui rend un rechargement
    sûr : le chapitre ressort toujours complet, jamais dépouillé de ses figures.
    """
    from apps.courses.models import Exercise, Lesson, Quiz

    run_steps(command, steps, verbosity=verbosity)

    chapter.refresh_from_db()
    illustrated = attach_to_chapter(chapter, stdout=command.stdout if verbosity else None)

    lessons = Lesson.objects.filter(chapter=chapter)
    if verbosity:
        command.stdout.write(command.style.SUCCESS(f'\n✅ {chapter.title}'))
        command.stdout.write(f'📖 Leçons : {lessons.count()}')
        command.stdout.write(f'💻 Exercices : {Exercise.objects.filter(lesson__chapter=chapter).count()}')
        command.stdout.write(f'📝 Quiz : {Quiz.objects.filter(lesson__chapter=chapter).count()}')
        command.stdout.write(f'🖼️  Leçons illustrées : {illustrated}')
        command.stdout.write(f'🏆 Points : {sum(l.points for l in lessons)}')
    return chapter

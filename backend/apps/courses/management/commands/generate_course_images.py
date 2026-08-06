"""
Régénère les illustrations pédagogiques des cours.

Usage:
    python manage.py generate_course_images            # les 3 chapitres
    python manage.py generate_course_images --section 2

⚠️ **Cette commande ne fait pas partie de l'amorçage.** Les PNG sont versionnés
dans `backend/media/courses/` : un clone du dépôt affiche les illustrations sans
rien exécuter. Elle sert à *retoucher* une figure — on la relance alors et on
commite le PNG modifié.

Elle exige Pillow et les polices DejaVu, installés par le Dockerfile du backend.
La production n'en a pas besoin.

Remplace cinq scripts de la racine de `backend/` (`generate_html_images.py`,
`generate_css_images.py`, `generate_js_images.py`, et leurs variantes
`*_lessons2_*`) qui dupliquaient chacun la palette et les primitives de dessin.
"""
from django.core.management.base import BaseCommand, CommandError

from apps.courses.content.images import section1_html, section2_css, section3_javascript

SECTIONS = (
    (1, section1_html, 'HTML'),
    (2, section2_css, 'CSS'),
    (3, section3_javascript, 'JavaScript'),
)


class Command(BaseCommand):
    help = 'Régénère les illustrations PNG des chapitres HTML, CSS et JavaScript'

    def add_arguments(self, parser):
        parser.add_argument(
            '--section', type=int, action='append', dest='sections',
            help='Ne régénérer que cette section (répétable). Par défaut : toutes.',
        )

    def handle(self, *args, **options):
        verbosity = options.get('verbosity', 1)

        wanted = options.get('sections')
        if wanted:
            unknown = set(wanted) - {n for n, _, _ in SECTIONS}
            if unknown:
                raise CommandError(f'Section(s) inconnue(s) : {sorted(unknown)}.')
            selected = [s for s in SECTIONS if s[0] in set(wanted)]
        else:
            selected = list(SECTIONS)

        try:
            total = 0
            for number, module, label in selected:
                if verbosity:
                    self.stdout.write(self.style.MIGRATE_HEADING(
                        f'\n━━━ Section {number} — {label} ━━━'
                    ))
                total += module.build()
        except OSError as exc:
            # Police introuvable : le message brut de Pillow n'aide pas.
            raise CommandError(
                f'Rendu impossible ({exc}).\n'
                f'Les polices DejaVu et Pillow sont-elles installées dans '
                f'l\'image ? Voir backend/Dockerfile.'
            ) from exc

        if verbosity:
            self.stdout.write(self.style.SUCCESS(f'\n✨ {total} illustrations régénérées.'))

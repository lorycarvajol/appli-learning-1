"""
Charge la totalité du parcours, dans l'ordre.

Usage:
    python manage.py load_course_content            # tout le parcours
    python manage.py load_course_content --section 3
    python manage.py load_course_content --list

C'est le point d'entrée à privilégier pour amorcer un environnement : il évite
d'avoir à connaître la liste des sections et leur ordre. Chaque section reste
lançable seule quand on ne retouche qu'un chapitre.

Toutes les sections sont **idempotentes** — les rejouer ne duplique rien. Elles
passent `--force` à leurs commandes respectives, qui suppriment et recréent
*leur propre chapitre*, jamais les autres (cf. l'incident documenté dans
`load_demo_content`).
"""
from django.core.management import call_command
from django.core.management.base import BaseCommand, CommandError

# Ordre canonique du parcours. Ajouter une section ici la rend automatiquement
# disponible pour `--section` et incluse dans le chargement complet.
SECTIONS = (
    (1, 'load_section_1_html', 'Introduction au HTML'),
    (2, 'load_section_2_css', 'Introduction au CSS'),
    (3, 'load_section_3_javascript', 'Introduction à JavaScript'),
    (4, 'load_section_4_site_vitrine', 'Créer et mettre en ligne un site vitrine'),
)


class Command(BaseCommand):
    help = 'Charge tout le contenu du parcours (chapitres, leçons, exercices, quiz, illustrations)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--section', type=int, action='append', dest='sections',
            help='Ne charger que cette section (répétable). Par défaut : toutes.',
        )
        parser.add_argument(
            '--list', action='store_true',
            help='Affiche les sections disponibles sans rien charger.',
        )

    def handle(self, *args, **options):
        verbosity = options.get('verbosity', 1)

        if options.get('list'):
            for number, command, title in SECTIONS:
                self.stdout.write(f'  {number}. {title}  ({command})')
            return

        wanted = options.get('sections')
        if wanted:
            unknown = set(wanted) - {number for number, _, _ in SECTIONS}
            if unknown:
                raise CommandError(
                    f'Section(s) inconnue(s) : {sorted(unknown)}. '
                    f'Voir `manage.py load_course_content --list`.'
                )
            selected = [s for s in SECTIONS if s[0] in set(wanted)]
        else:
            selected = list(SECTIONS)

        for number, command, title in selected:
            if verbosity:
                self.stdout.write(self.style.MIGRATE_HEADING(
                    f'\n━━━ Section {number} — {title} ━━━'
                ))
            call_command(command, force=True, verbosity=verbosity)

        if verbosity:
            self.stdout.write(self.style.SUCCESS(
                f'\n✨ {len(selected)} section(s) chargée(s).'
            ))

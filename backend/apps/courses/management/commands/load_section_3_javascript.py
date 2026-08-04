"""
Charge la section 3 : Introduction à JavaScript.

Usage: python manage.py load_section_3_javascript [--force]

⚠️ Ce chapitre existait depuis longtemps sous forme de script à la racine
(`backend/load_section_3_javascript.py`, 48 Ko, 17 leçons) qui n'a jamais été
promu en commande. Conséquence : personne ne le lançait, et le parcours servait
à sa place les deux leçons squelettiques de `load_demo_content`
(`javascript-debutants`). Le contenu était écrit, mais invisible.

Le chapitre de démonstration est donc supprimé ici : les deux ne peuvent pas
cohabiter, ils occupent la même place dans le parcours.
"""
from django.core.management.base import BaseCommand

from apps.courses.content import pipeline, section3_javascript, section3_javascript_quiz
from apps.courses.models import Chapter

CHAPTER_SLUG = 'introduction-javascript'

# Le chapitre JavaScript de `load_demo_content`, que celui-ci remplace.
DEMO_SLUG = 'javascript-debutants'


class Command(BaseCommand):
    help = 'Charge la section 3 : Introduction à JavaScript (chapitre complet)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Supprime le chapitre JavaScript existant avant de le recréer',
        )

    def handle(self, *args, **options):
        verbosity = options.get('verbosity', 1)
        if verbosity:
            self.stdout.write(self.style.SUCCESS('Chargement de la section 3 : JavaScript…'))

        if options.get('force'):
            Chapter.objects.filter(slug=CHAPTER_SLUG).delete()
            if verbosity:
                self.stdout.write(self.style.WARNING('Chapitre JavaScript existant supprimé.'))

        # Le chapitre de démonstration ferait doublon dans le sommaire.
        removed, _ = Chapter.objects.filter(slug=DEMO_SLUG).delete()
        if removed and verbosity:
            self.stdout.write(self.style.WARNING(
                f'Chapitre de démonstration « {DEMO_SLUG} » retiré (remplacé par celui-ci).'
            ))

        pipeline.run_steps(self, [section3_javascript.build], verbosity=verbosity)

        chapter = Chapter.objects.get(slug=CHAPTER_SLUG)
        pipeline.finish(
            self, chapter,
            steps=[section3_javascript_quiz.build],
            verbosity=verbosity,
        )

"""
Rattrapage des accès aux chapitres.

À lancer **une fois** après la mise en service du verrouillage. Jusqu'ici
`ChapterAccess` n'était consulté par aucune vue apprenant : tout le monde
voyait tout. Activer le verrou sans rattrapage enfermerait les apprenants
existants hors des chapitres qu'ils suivent déjà.

Deux passes, toutes deux idempotentes :

1. **Débloquer ce qui a été touché** : tout chapitre où l'apprenant a une
   progression, quelle qu'elle soit. On n'enlève jamais un accès de fait.
2. **Appliquer le rythme libre** aux apprenants sans classe, pour qu'ils
   repartent avec au moins le premier chapitre ouvert.

Relançable sans risque.
"""
from django.core.management.base import BaseCommand

from apps.accounts.models import User
from apps.courses.models import Chapter
from apps.progression.models import UserProgress
from apps.progression.services import ensure_self_paced_access, unlock_chapter_for


class Command(BaseCommand):
    help = "Ouvre les chapitres déjà entamés et applique le rythme libre."

    def add_arguments(self, parser):
        parser.add_argument('--email', help="Ne traiter qu'un apprenant.")
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help="Affiche ce qui serait fait sans rien écrire.",
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        learners = User.objects.filter(role=User.Role.LEARNER).select_related('profile')
        if options.get('email'):
            learners = learners.filter(email=options['email'])

        total_opened = 0
        total_self_paced = 0

        for learner in learners:
            touched_chapter_ids = set(
                UserProgress.objects.filter(user=learner)
                .values_list('lesson__chapter_id', flat=True)
            )
            chapters = Chapter.objects.filter(id__in=touched_chapter_ids)

            opened = []
            for chapter in chapters:
                if dry_run:
                    opened.append(chapter.title)
                    continue
                _, newly = unlock_chapter_for(learner, chapter)
                if newly:
                    opened.append(chapter.title)

            self_paced = []
            if not dry_run:
                self_paced = [c.title for c in ensure_self_paced_access(learner)]

            total_opened += len(opened)
            total_self_paced += len(self_paced)

            if opened or self_paced:
                cohort = getattr(learner.profile, 'cohort', None)
                label = cohort.name if cohort else 'autonome'
                details = ', '.join(opened + self_paced)
                self.stdout.write(f"  {learner.email} ({label}) → {details}")

        prefix = '[simulation] ' if dry_run else ''
        self.stdout.write(self.style.SUCCESS(
            f"{prefix}{total_opened} chapitre(s) déjà entamé(s) ouvert(s), "
            f"{total_self_paced} ouvert(s) au rythme libre."
        ))

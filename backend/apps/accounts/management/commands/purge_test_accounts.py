"""
Recense — et retire sur demande — les comptes de test d'une base.

Usage :
    python manage.py purge_test_accounts            # recense, ne touche à rien
    python manage.py purge_test_accounts --apply    # supprime

Deux familles se sont accumulées et n'ont rien à faire sur une instance
réelle :

- les **comptes de démonstration** (`create_demo_users`), dont les mots de
  passe sont écrits dans le dépôt ;
- les **comptes jetables des tests bout-en-bout** (`e2e-<horodatage>-<alea>@example.com`),
  créés à chaque exécution de la suite Playwright et jamais nettoyés — la base
  de développement en comptait plus de soixante.

⚠️ **Suppression, et non anonymisation.** C'est l'inverse du choix fait pour un
apprenant réel (cf. « RGPD : anonymisation, pas suppression en cascade ») : là,
l'anonymisation préserve des statistiques de classe qui ont un sens. Ici, les
comptes ne désignent personne et leur progression est du bruit — la conserver
sous forme anonymisée fausserait les taux de complétion au lieu de les
préserver.

Par prudence, la commande **refuse de toucher à un compte administrateur** et
n'agit qu'avec `--apply`.
"""
import re

from django.core.management.base import BaseCommand
from django.db.models import Q

from apps.accounts.models import User

from .create_demo_users import DEMO_EMAILS

#: Adresses jetables produites par `e2e/helpers.uniqueEmail`.
E2E_PATTERN = re.compile(r'^e2e-\d+-[a-z0-9]+@example\.com$', re.IGNORECASE)


def find_test_accounts():
    """Rend (comptes_de_demo, comptes_e2e, douteux), administrateurs exclus.

    `douteux` recueille les adresses qui commencent par `e2e-` sans respecter
    le format attendu. Les écarter en silence serait le pire des deux mondes :
    ni supprimées, ni signalées. Elles sont donc rapportées et laissées en
    place, à trancher à la main.
    """
    candidats = User.objects.filter(
        Q(email__in=DEMO_EMAILS) | Q(email__startswith='e2e-')
    ).exclude(role='ADMIN')

    demo, e2e, douteux = [], [], []
    for user in candidats:
        if user.email in DEMO_EMAILS:
            demo.append(user)
        elif E2E_PATTERN.match(user.email):
            e2e.append(user)
        else:
            douteux.append(user)
    return demo, e2e, douteux


class Command(BaseCommand):
    help = "Recense (et supprime avec --apply) les comptes de démonstration et de test E2E"

    def add_arguments(self, parser):
        parser.add_argument(
            '--apply',
            action='store_true',
            help='Supprime réellement. Sans ce drapeau, la commande se contente de recenser.',
        )

    def handle(self, *args, **options):
        demo, e2e, douteux = find_test_accounts()
        total = len(demo) + len(e2e)

        for user in douteux:
            self.stdout.write(self.style.WARNING(
                f'⚠️  {user.email} ressemble à un compte de test sans en avoir '
                f'le format : laissé en place, à vérifier.'
            ))

        if not total:
            self.stdout.write(self.style.SUCCESS('Aucun compte de test trouvé.'))
            return

        self.stdout.write(f'Comptes de démonstration : {len(demo)}')
        for user in demo:
            self.stdout.write(f'  - {user.email} ({user.role})')

        self.stdout.write(f'Comptes de test E2E : {len(e2e)}')
        for user in e2e[:5]:
            self.stdout.write(f'  - {user.email}')
        if len(e2e) > 5:
            self.stdout.write(f'  … et {len(e2e) - 5} autres')

        # Un administrateur portant une adresse de test est signalé, jamais
        # supprimé : ce peut être le seul compte de pilotage de l'instance.
        admins = User.objects.filter(
            Q(email__in=DEMO_EMAILS) | Q(email__startswith='e2e-'), role='ADMIN'
        )
        for user in admins:
            self.stdout.write(self.style.WARNING(
                f'⚠️  {user.email} est ADMINISTRATEUR : non supprimé. '
                f'À renommer ou à retirer à la main après avoir promu un remplaçant.'
            ))

        if not options['apply']:
            self.stdout.write(self.style.WARNING(
                f'\n{total} compte(s) concerné(s). Relancer avec --apply pour supprimer.'
            ))
            return

        supprimes, _ = User.objects.filter(
            id__in=[u.id for u in demo + e2e]
        ).delete()
        self.stdout.write(self.style.SUCCESS(
            f'\n✅ {total} compte(s) supprimé(s) ({supprimes} lignes au total, cascades comprises).'
        ))

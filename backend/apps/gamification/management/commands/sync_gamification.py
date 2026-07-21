"""
Réconcilie l'état gamifié de tous les apprenants.

À lancer une fois après la mise en place du grand livre de points, puis à
volonté : l'opération est idempotente.

Deux étapes par utilisateur :

1. **Report du solde historique.** Les points accordés avant l'introduction du
   grand livre n'ont pas de transaction correspondante. On crée une écriture
   ``LEGACY`` unique (clé ``legacy:balance``) pour la différence, afin que le
   solde reste vrai *et* reconstructible. Comme la clé est unique par
   utilisateur, relancer la commande ne recrée pas l'écriture.
2. **Évaluation des badges** sur l'état actuel, sans toucher à la série de
   jours (on ne veut pas qu'une commande d'administration fasse croire à une
   activité de l'apprenant).
"""
from django.core.management.base import BaseCommand
from django.db.models import Sum

from apps.accounts.models import User
from apps.gamification.models import PointTransaction
from apps.gamification.services import sync_user_gamification


class Command(BaseCommand):
    help = "Reporte les soldes historiques et réévalue les badges de tous les apprenants."

    def add_arguments(self, parser):
        parser.add_argument(
            '--email',
            help="Ne traiter qu'un utilisateur (par email).",
        )

    def handle(self, *args, **options):
        users = User.objects.select_related('profile')
        if options.get('email'):
            users = users.filter(email=options['email'])

        total_new_badges = 0

        for user in users:
            profile = getattr(user, 'profile', None)
            if profile is None:
                continue

            ledger_total = PointTransaction.objects.filter(user=user).aggregate(
                total=Sum('amount')
            )['total'] or 0

            gap = profile.total_points - ledger_total
            if gap > 0:
                # Écriture directe : le solde du profil reflète *déjà* ces
                # points, on n'ajoute donc que la ligne manquante au grand
                # livre. La contrainte d'unicité (user, source_key) empêche
                # tout doublon si la commande est relancée.
                PointTransaction.objects.get_or_create(
                    user=user,
                    source_key='legacy:balance',
                    defaults={
                        'amount': gap,
                        'reason': PointTransaction.Reason.LEGACY,
                        'metadata': {'note': 'Solde antérieur au grand livre'},
                    },
                )

            new_badges = sync_user_gamification(user, touch=False)
            total_new_badges += len(new_badges)

            if new_badges:
                names = ', '.join(b.badge.name for b in new_badges)
                self.stdout.write(f"  {user.email} → {names}")

        self.stdout.write(self.style.SUCCESS(
            f"Réconciliation terminée : {total_new_badges} badge(s) attribué(s)."
        ))

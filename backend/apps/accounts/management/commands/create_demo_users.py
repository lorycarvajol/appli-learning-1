"""
Crée les comptes de démonstration du développement.

Usage : python manage.py create_demo_users

⚠️ **Ces comptes ont des mots de passe écrits dans ce dépôt.** Ils n'existent
que pour tester l'application localement, et la commande **refuse de s'exécuter
en production** (voir `_refuse_en_production`). Créer le premier administrateur
d'une instance réelle se fait avec `createsuperuser`, jamais ici.

Le contrôle porte sur `settings.ENVIRONMENT` et non sur `settings.DEBUG` : le
lanceur de tests de Django force `DEBUG = False`, ce qui rendrait la commande
intestable, alors qu'`ENVIRONMENT` est précisément la variable qui sélectionne
les réglages de production (`config/settings/__init__.py`).
"""
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from apps.accounts.models import User

# Mot de passe volontairement trivial : ces comptes ne doivent jamais quitter
# un poste de développement.
TRAINER_PASSWORD = 'trainer123'
LEARNER_PASSWORD = 'learner123'

TRAINER = ('trainer@test.com', 'Jean', 'Formateur')

LEARNERS = [
    ('alice@test.com', 'Alice', 'Dupont'),
    ('bob@test.com', 'Bob', 'Martin'),
    ('charlie@test.com', 'Charlie', 'Bernard'),
]

#: Adresses créées ici — sert aussi à `purge_test_accounts`.
DEMO_EMAILS = [TRAINER[0]] + [email for email, _, _ in LEARNERS]


def _refuse_en_production():
    """Empêche la création de comptes à mot de passe public sur une instance réelle.

    Sans ce garde-fou, il suffisait de recopier la ligne d'amorçage documentée
    dans `frontend/e2e/README.md` sur le serveur pour ouvrir à tout le monde un
    compte formateur dont le mot de passe est lisible sur GitHub — et un
    formateur voit la progression de ses apprenants.
    """
    if getattr(settings, 'ENVIRONMENT', 'development') == 'production':
        raise CommandError(
            "create_demo_users est réservé au développement : ces comptes ont "
            "des mots de passe publiés dans le dépôt.\n"
            "Pour créer le premier administrateur d'une instance réelle :\n"
            "  python manage.py createsuperuser"
        )


class Command(BaseCommand):
    help = "Crée les comptes de démonstration (développement uniquement)"

    def handle(self, *args, **options):
        _refuse_en_production()

        self.stdout.write(self.style.WARNING(
            '⚠️  Comptes de démonstration à mot de passe public — '
            'développement uniquement.'
        ))

        email, first_name, last_name = TRAINER
        trainer, created = User.objects.get_or_create(
            email=email,
            defaults={
                'first_name': first_name,
                'last_name': last_name,
                'role': 'TRAINER',
                'is_active': True,
            },
        )
        if created:
            trainer.set_password(TRAINER_PASSWORD)
            trainer.save()
            self.stdout.write(f'✅ Formateur créé : {trainer.email}')
        else:
            self.stdout.write(f'ℹ️  Formateur déjà présent : {trainer.email}')

        for email, first_name, last_name in LEARNERS:
            learner, created = User.objects.get_or_create(
                email=email,
                defaults={
                    'first_name': first_name,
                    'last_name': last_name,
                    'role': 'LEARNER',
                    'is_active': True,
                },
            )
            if created:
                learner.set_password(LEARNER_PASSWORD)
                learner.save()
                self.stdout.write(f'✅ Apprenant créé : {learner.email}')
            else:
                self.stdout.write(f'ℹ️  Apprenant déjà présent : {learner.email}')

        self.stdout.write(self.style.SUCCESS('\n✅ Comptes de démonstration prêts.'))
        self.stdout.write(f'  Formateur : {TRAINER[0]} / {TRAINER_PASSWORD}')
        for email, _, _ in LEARNERS:
            self.stdout.write(f'  Apprenant : {email} / {LEARNER_PASSWORD}')

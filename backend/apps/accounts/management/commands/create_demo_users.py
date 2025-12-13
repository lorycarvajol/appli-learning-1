"""
Management command to create demo users for testing.
Usage: python manage.py create_demo_users
"""
from django.core.management.base import BaseCommand
from apps.accounts.models import User


class Command(BaseCommand):
    help = 'Create demo users (trainer and learners) for testing'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Creating demo users...'))

        # Create a trainer
        trainer, created = User.objects.get_or_create(
            email='trainer@test.com',
            defaults={
                'first_name': 'Jean',
                'last_name': 'Formateur',
                'role': 'TRAINER',
                'is_active': True
            }
        )
        if created:
            trainer.set_password('trainer123')
            trainer.save()
            self.stdout.write(f'✅ Created trainer: {trainer.email} (password: trainer123)')
        else:
            self.stdout.write(f'ℹ️  Trainer already exists: {trainer.email}')

        # Create learners
        learners_data = [
            ('alice@test.com', 'Alice', 'Dupont'),
            ('bob@test.com', 'Bob', 'Martin'),
            ('charlie@test.com', 'Charlie', 'Bernard'),
        ]

        for email, first_name, last_name in learners_data:
            learner, created = User.objects.get_or_create(
                email=email,
                defaults={
                    'first_name': first_name,
                    'last_name': last_name,
                    'role': 'LEARNER',
                    'is_active': True
                }
            )
            if created:
                learner.set_password('learner123')
                learner.save()
                self.stdout.write(f'✅ Created learner: {learner.email} (password: learner123)')
            else:
                self.stdout.write(f'ℹ️  Learner already exists: {learner.email}')

        self.stdout.write(self.style.SUCCESS('\n✅ Demo users created successfully!'))
        self.stdout.write('\nYou can now log in with:')
        self.stdout.write('  Trainer: trainer@test.com / trainer123')
        self.stdout.write('  Learners: alice@test.com / learner123')
        self.stdout.write('           bob@test.com / learner123')
        self.stdout.write('           charlie@test.com / learner123')

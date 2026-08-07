"""
Catalogue initial des badges.

Deux familles :

- **Objectifs visibles** (``is_secret=False``) : annoncés avec une barre de
  progression. Ils balisent le parcours et restent atteignables.
- **Objectifs secrets** (``is_secret=True``) : seule une énigme est visible ;
  le nom et la description ne sont révélés qu'à l'obtention. L'API ne les
  divulgue jamais avant.

La commande est idempotente : elle met à jour les badges existants (repérés
par ``code``) sans jamais toucher aux badges déjà obtenus par les apprenants.
"""
from django.core.management.base import BaseCommand

from apps.gamification.models import Badge

R = Badge.RuleType
T = Badge.Tier
C = Badge.Category

# ---------------------------------------------------------------------------
# Objectifs visibles — la piste balisée
# ---------------------------------------------------------------------------
VISIBLE = [
    {
        'code': 'premier-pas', 'name': 'Premier pas', 'icon': '🌱',
        'description': 'Vous avez terminé votre toute première leçon. Le voyage commence !',
        'category': C.PROGRESSION, 'tier': T.BRONZE,
        'rule_type': R.LESSONS_COMPLETED, 'criteria': {'count': 1},
        'points_reward': 10,
    },
    {
        'code': 'en-route', 'name': 'En route', 'icon': '🚀',
        'description': '5 leçons terminées. Vous avez pris le rythme.',
        'category': C.PROGRESSION, 'tier': T.BRONZE,
        'rule_type': R.LESSONS_COMPLETED, 'criteria': {'count': 5},
        'points_reward': 20,
    },
    {
        'code': 'bien-lance', 'name': 'Bien lancé', 'icon': '🧗',
        'description': '15 leçons terminées. La régularité paie.',
        'category': C.PROGRESSION, 'tier': T.SILVER,
        'rule_type': R.LESSONS_COMPLETED, 'criteria': {'count': 15},
        'points_reward': 40,
    },
    {
        'code': 'marathonien', 'name': 'Marathonien', 'icon': '🏔️',
        'description': '30 leçons terminées. Peu de monde arrive jusqu\'ici.',
        'category': C.PROGRESSION, 'tier': T.GOLD,
        'rule_type': R.LESSONS_COMPLETED, 'criteria': {'count': 30},
        'points_reward': 80,
    },
    {
        'code': 'chapitre-boucle', 'name': 'Chapitre bouclé', 'icon': '📗',
        'description': 'Un chapitre entier terminé, de la première à la dernière leçon.',
        'category': C.PROGRESSION, 'tier': T.SILVER,
        'rule_type': R.CHAPTERS_COMPLETED, 'criteria': {'count': 1},
        'points_reward': 30,
    },
    {
        'code': 'trois-chapitres', 'name': 'Bibliothécaire', 'icon': '📚',
        'description': 'Trois chapitres complets à votre actif.',
        'category': C.PROGRESSION, 'tier': T.GOLD,
        'rule_type': R.CHAPTERS_COMPLETED, 'criteria': {'count': 3},
        'points_reward': 75,
    },
    {
        'code': 'codeur-debutant', 'name': 'Les mains dans le code', 'icon': '⌨️',
        'description': 'Votre premier exercice de code validé par les tests.',
        'category': C.MASTERY, 'tier': T.BRONZE,
        'rule_type': R.EXERCISES_PASSED, 'criteria': {'count': 1},
        'points_reward': 15,
    },
    {
        'code': 'codeur-confirme', 'name': 'Artisan du code', 'icon': '🛠️',
        'description': '10 exercices de code réussis. Le clavier vous obéit.',
        'category': C.MASTERY, 'tier': T.SILVER,
        'rule_type': R.EXERCISES_PASSED, 'criteria': {'count': 10},
        'points_reward': 50,
    },
    {
        'code': 'quiz-reussi', 'name': 'Bonne réponse', 'icon': '✅',
        'description': 'Un premier quiz réussi.',
        'category': C.MASTERY, 'tier': T.BRONZE,
        'rule_type': R.QUIZZES_PASSED, 'criteria': {'count': 1},
        'points_reward': 15,
    },
    {
        'code': 'sans-faute', 'name': 'Sans faute', 'icon': '💯',
        'description': 'Un quiz terminé avec 100 % de bonnes réponses.',
        'category': C.MASTERY, 'tier': T.SILVER,
        'rule_type': R.PERFECT_QUIZZES, 'criteria': {'count': 1},
        'points_reward': 30,
    },
    {
        'code': 'serie-3', 'name': 'Trois jours de suite', 'icon': '🔥',
        'description': 'Trois jours consécutifs d\'apprentissage.',
        'category': C.REGULARITY, 'tier': T.BRONZE,
        'rule_type': R.STREAK_DAYS, 'criteria': {'days': 3},
        'points_reward': 20,
    },
    {
        'code': 'serie-7', 'name': 'Semaine parfaite', 'icon': '🗓️',
        'description': 'Sept jours consécutifs. La régularité est votre super-pouvoir.',
        'category': C.REGULARITY, 'tier': T.GOLD,
        'rule_type': R.STREAK_DAYS, 'criteria': {'days': 7},
        'points_reward': 60,
    },
    {
        'code': 'cap-100', 'name': 'Cap des 100 points', 'icon': '🎯',
        'description': '100 points cumulés.',
        'category': C.PROGRESSION, 'tier': T.BRONZE,
        'rule_type': R.POINTS_TOTAL, 'criteria': {'points': 100},
        'points_reward': 0,
    },
    {
        'code': 'cap-500', 'name': 'Cap des 500 points', 'icon': '🏆',
        'description': '500 points cumulés. Niveau confirmé.',
        'category': C.PROGRESSION, 'tier': T.GOLD,
        'rule_type': R.POINTS_TOTAL, 'criteria': {'points': 500},
        'points_reward': 0,
    },
    {
        'code': 'deux-heures', 'name': 'Deux heures au compteur', 'icon': '⏱️',
        'description': '120 minutes d\'apprentissage cumulées.',
        'category': C.REGULARITY, 'tier': T.SILVER,
        'rule_type': R.TIME_SPENT, 'criteria': {'minutes': 120},
        'points_reward': 25,
    },
    {
        'code': 'dix-heures', 'name': 'Dix heures au compteur', 'icon': '⏳',
        'description': '600 minutes d\'apprentissage cumulées. Le temps y est.',
        'category': C.REGULARITY, 'tier': T.GOLD,
        'rule_type': R.TIME_SPENT, 'criteria': {'minutes': 600},
        'points_reward': 60,
    },

    # -----------------------------------------------------------------------
    # Un badge par chapitre du parcours.
    #
    # `CHAPTER_MASTERED` existait dans le modèle **et** dans le registre de
    # règles depuis l'origine, sans qu'aucun badge ne s'en serve : la règle
    # était écrite, testable, et morte. Ces quatre badges lui donnent son
    # emploi, et ils disent quelque chose que `chapitre-boucle` (un chapitre,
    # n'importe lequel) et `trois-chapitres` (trois, n'importe lesquels) ne
    # disent pas — **lequel** on a terminé.
    #
    # ⚠️ Le `chapter_slug` doit exister en base, sinon le badge reste
    # éternellement à 0 sans que rien ne le signale. Les quatre slugs sont
    # ceux que posent les commandes `load_section_*` ; les renommer casserait
    # ces badges en silence. Un test les verrouille.
    # -----------------------------------------------------------------------
    {
        'code': 'maitre-html', 'name': 'Charpentier', 'icon': '🧱',
        'description': 'Le chapitre HTML terminé de bout en bout. La structure n\'a plus de secret.',
        'category': C.MASTERY, 'tier': T.SILVER,
        'rule_type': R.CHAPTER_MASTERED,
        'criteria': {'chapter_slug': 'introduction-html'},
        'points_reward': 40,
    },
    {
        'code': 'maitre-css', 'name': 'Coloriste', 'icon': '🎨',
        'description': 'Le chapitre CSS terminé de bout en bout. Vos pages ont un style.',
        'category': C.MASTERY, 'tier': T.SILVER,
        'rule_type': R.CHAPTER_MASTERED,
        'criteria': {'chapter_slug': 'introduction-css'},
        'points_reward': 40,
    },
    {
        'code': 'maitre-javascript', 'name': 'Mécanicien', 'icon': '⚙️',
        'description': 'Le chapitre JavaScript terminé de bout en bout. Vos pages réagissent.',
        'category': C.MASTERY, 'tier': T.GOLD,
        'rule_type': R.CHAPTER_MASTERED,
        'criteria': {'chapter_slug': 'introduction-javascript'},
        'points_reward': 50,
    },
    {
        'code': 'maitre-site-vitrine', 'name': 'En ligne', 'icon': '🌐',
        'description': 'Le chapitre du site vitrine terminé. Votre site existe pour de vrai.',
        'category': C.MASTERY, 'tier': T.GOLD,
        'rule_type': R.CHAPTER_MASTERED,
        'criteria': {'chapter_slug': 'site-vitrine'},
        'points_reward': 50,
    },
]

# ---------------------------------------------------------------------------
# Objectifs secrets — la surprise
# Le champ « hint » est la seule chose que l'apprenant voit avant l'obtention.
# ---------------------------------------------------------------------------
SECRET = [
    {
        'code': 'oiseau-de-nuit', 'name': 'Oiseau de nuit', 'icon': '🦉',
        'description': 'Cinq sessions entre 22 h et 5 h du matin. Le code n\'attend pas le jour.',
        'hint': "Certains apprennent quand les autres dorment…",
        'category': C.EXPLORATION, 'tier': T.SILVER,
        'rule_type': R.NIGHT_OWL, 'criteria': {'count': 5},
        'points_reward': 35,
    },
    {
        'code': 'leve-tot', 'name': 'Lève-tôt', 'icon': '🌅',
        'description': 'Cinq sessions entre 5 h et 8 h du matin. Le monde vous appartient.',
        'hint': "Le premier café a peut-être quelque chose à voir avec ça…",
        'category': C.EXPLORATION, 'tier': T.SILVER,
        'rule_type': R.EARLY_BIRD, 'criteria': {'count': 5},
        'points_reward': 35,
    },
    {
        'code': 'weekend-studieux', 'name': 'Week-end studieux', 'icon': '🏖️',
        'description': 'Cinq activités un samedi ou un dimanche. Repos ? Plus tard.',
        'hint': "Deux jours par semaine sont plus calmes que les autres…",
        'category': C.EXPLORATION, 'tier': T.BRONZE,
        'rule_type': R.WEEKEND_LEARNER, 'criteria': {'count': 5},
        'points_reward': 25,
    },
    {
        'code': 'du-premier-coup', 'name': 'Du premier coup', 'icon': '🎯',
        'description': 'Trois quiz réussis dès la première tentative. Impressionnant.',
        'hint': "Et si vous n'aviez besoin que d'un seul essai ?",
        'category': C.MASTERY, 'tier': T.GOLD,
        'rule_type': R.FIRST_TRY_QUIZZES, 'criteria': {'count': 3},
        'points_reward': 50,
    },
    {
        'code': 'perseverant', 'name': 'Increvable', 'icon': '🧱',
        'description': 'Une réussite obtenue après cinq tentatives. Abandonner n\'est pas une option.',
        'hint': "Échouer, recommencer, échouer encore… puis réussir.",
        'category': C.EXPLORATION, 'tier': T.GOLD,
        'rule_type': R.PERSEVERANCE, 'criteria': {'attempts': 5},
        'points_reward': 45,
    },
    {
        'code': 'eclair', 'name': 'Éclair', 'icon': '⚡',
        'description': 'Trois leçons bouclées en moins de cinq minutes chacune.',
        'hint': "La vitesse aussi peut être une forme de maîtrise…",
        'category': C.EXPLORATION, 'tier': T.SILVER,
        'rule_type': R.FAST_LESSONS, 'criteria': {'count': 3, 'max_minutes': 5},
        'points_reward': 30,
    },
    {
        'code': 'sans-faute-x3', 'name': 'Perfectionniste', 'icon': '💎',
        'description': 'Trois quiz à 100 %. Aucune approximation.',
        'hint': "Une fois, c'est de la chance. Trois fois…",
        'category': C.MASTERY, 'tier': T.LEGENDARY,
        'rule_type': R.PERFECT_QUIZZES, 'criteria': {'count': 3},
        'points_reward': 70,
    },
    {
        'code': 'serie-14', 'name': 'Inarrêtable', 'icon': '🌟',
        'description': 'Quatorze jours consécutifs. Vous en avez fait une habitude.',
        'hint': "Une semaine, c'est bien. Mais après ?",
        'category': C.REGULARITY, 'tier': T.LEGENDARY,
        'rule_type': R.STREAK_DAYS, 'criteria': {'days': 14},
        'points_reward': 120,
    },
    {
        'code': 'serie-30', 'name': 'Un mois sans faillir', 'icon': '🛡️',
        'description': 'Trente jours consécutifs. Ce n\'est plus une série, c\'est une routine.',
        'hint': "Quatorze jours n'étaient que l'échauffement…",
        'category': C.REGULARITY, 'tier': T.LEGENDARY,
        'rule_type': R.STREAK_DAYS, 'criteria': {'days': 30},
        'points_reward': 150,
    },
    {
        'code': 'premier-coup-x5', 'name': 'Sans filet', 'icon': '🃏',
        'description': 'Les cinq quiz du parcours réussis dès la première tentative. '
                       'Aucun ne vous a résisté.',
        'hint': "Trois du premier coup, c'était déjà rare. Et tous ?",
        'category': C.MASTERY, 'tier': T.LEGENDARY,
        'rule_type': R.FIRST_TRY_QUIZZES, 'criteria': {'count': 5},
        'points_reward': 90,
    },
]


class Command(BaseCommand):
    help = "Crée ou met à jour le catalogue de badges (idempotent)."

    def handle(self, *args, **options):
        created_count = 0
        updated_count = 0

        for index, entry in enumerate(VISIBLE + SECRET):
            spec = dict(entry)  # ne pas muter le catalogue en mémoire
            code = spec.pop('code')
            spec['is_secret'] = 'hint' in spec
            spec['order_index'] = index * 10
            spec['is_active'] = True

            _, created = Badge.objects.update_or_create(code=code, defaults=spec)
            if created:
                created_count += 1
                self.stdout.write(f"  + {spec['icon']} {spec['name']}")
            else:
                updated_count += 1

        self.stdout.write(self.style.SUCCESS(
            f"Catalogue à jour : {created_count} créé(s), {updated_count} mis à jour, "
            f"{len(SECRET)} objectif(s) secret(s)."
        ))

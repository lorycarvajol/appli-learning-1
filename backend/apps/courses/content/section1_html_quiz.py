"""
Quiz final du chapitre 1 : 20 questions sur les fondamentaux du HTML.

Appelé par la commande `load_section_1_html`, jamais seul : le quiz se
raccroche à un chapitre que la commande vient de construire.

⚠️ **Les positions des bonnes réponses sont mélangées ici, à la construction.**
Les questions sont rédigées avec la bonne réponse en tête, ce qui est commode à
écrire mais donne un quiz devinable : dans la version d'origine, 16 des 20
bonnes réponses étaient en position 1. Le mélange utilise une graine fixe
(`random.Random(42)`) pour rester reproductible d'un chargement à l'autre, et
`verify_unchanged` garantit que seule la *position* change — jamais le texte des
options ni celui de la bonne réponse.

Cette correction vivait dans un script séparé (`fix_html_quiz_option_order.py`)
qu'il fallait penser à lancer *après* celui-ci. Un quiz chargé sans lui restait
biaisé sans que rien ne le signale.
"""
import copy
import random

from apps.courses.models import Chapter, Lesson, Quiz


def reorder_question(question, rng):
    """Permute les options d'une question et réaligne la bonne réponse."""
    options = question['options']
    permutation = list(range(len(options)))
    rng.shuffle(permutation)

    # position_map[ancien_index] = nouvel_index
    position_map = {old: new for new, old in enumerate(permutation)}

    old_correct = question['correct_answer']
    if isinstance(old_correct, list):
        new_correct = sorted(position_map[i] for i in old_correct)
    else:
        new_correct = position_map[old_correct]

    question['options'] = [options[i] for i in permutation]
    question['correct_answer'] = new_correct
    return question


def _correct_texts(question):
    correct = question['correct_answer']
    if isinstance(correct, list):
        return {question['options'][i] for i in correct}
    return {question['options'][correct]}


def verify_unchanged(original, reordered):
    """Le texte des bonnes réponses doit être intact — seule la place change."""
    for orig, fixed in zip(original, reordered):
        assert _correct_texts(orig) == _correct_texts(fixed), (
            f"La bonne réponse de la question {orig['id']} a changé de contenu."
        )
        assert set(orig['options']) == set(fixed['options']), (
            f"Les options de la question {orig['id']} ont changé."
        )


def build():
    """Construit ou met à jour le quiz du chapitre HTML. Idempotent."""
    chapter = Chapter.objects.get(slug='introduction-html')
    print(f"Chapitre trouvé: {chapter.title}")

    # 20 questions pédagogiques sur HTML, rédigées bonne réponse en tête ;
    # l'ordre est mélangé plus bas, avant enregistrement.
    quiz_questions = [
        {
            "id": 1,
            "question": "Que signifie HTML ?",
            "options": [
                "HyperText Machine Language",
                "HighText Machine Language",
                "HighText Markup Language",
                "HyperText Markup Language"
            ],
            "correct_answer": 3,
            "type": "single",
            "explanation": "HTML signifie HyperText Markup Language. C'est le langage de balisage standard pour créer des pages web.",
        },
        {
            "id": 2,
            "question": "Quelle est la structure de base d'un document HTML5 ?",
            "options": [
                "<html>, <body>, <content>",
                "<!DOCTYPE>, <page>, <content>",
                "<!DOCTYPE html>, <html>, <head>, <body>",
                "<html>, <header>, <content>, <footer>"
            ],
            "correct_answer": 2,
            "type": "single",
            "explanation": "Un document HTML5 commence par <!DOCTYPE html>, suivi des balises <html>, <head> et <body>.",
        },
        {
            "id": 3,
            "question": "À quoi sert la balise <head> ?",
            "options": [
                "Contenir les métadonnées et informations de la page",
                "Définir le pied de page",
                "Créer l'en-tête de la page",
                "Afficher le contenu visible de la page"
            ],
            "correct_answer": 0,
            "type": "single",
            "explanation": "La balise <head> contient les métadonnées, le titre, les liens vers les CSS et autres informations qui ne sont pas affichées directement.",
        },
        {
            "id": 4,
            "question": "Quelles balises sont utilisées pour créer des titres en HTML ? (plusieurs réponses possibles)",
            "options": [
                "<title>",
                "<header>",
                "<h1> à <h6>",
                "<heading>"
            ],
            "correct_answer": [
                2
            ],
            "type": "multiple",
            "explanation": "Les balises <h1> à <h6> sont utilisées pour les titres, h1 étant le plus important et h6 le moins important.",
        },
        {
            "id": 5,
            "question": "Comment créer un lien hypertexte en HTML ?",
            "options": [
                "<link url='url'>Texte</link>",
                "<href='url'>Texte</href>",
                "<hyperlink>Texte</hyperlink>",
                "<a href='url'>Texte</a>"
            ],
            "correct_answer": 3,
            "type": "single",
            "explanation": "La balise <a> avec l'attribut href est utilisée pour créer des liens hypertextes.",
        },
        {
            "id": 6,
            "question": "Quelle balise permet d'insérer une image ?",
            "options": [
                "<image>",
                "<photo>",
                "<picture>",
                "<img>"
            ],
            "correct_answer": 3,
            "type": "single",
            "explanation": "La balise <img> avec l'attribut src est utilisée pour insérer des images. C'est une balise auto-fermante.",
        },
        {
            "id": 7,
            "question": "Quels attributs sont obligatoires pour la balise <img> ? (plusieurs réponses)",
            "options": [
                "width (largeur)",
                "alt (texte alternatif)",
                "src (source de l'image)",
                "height (hauteur)"
            ],
            "correct_answer": [
                1,
                2
            ],
            "type": "multiple",
            "explanation": "Les attributs src (source) et alt (texte alternatif) sont obligatoires pour l'accessibilité et le SEO.",
        },
        {
            "id": 8,
            "question": "Comment créer une liste non ordonnée ?",
            "options": [
                "<ol> avec des <li>",
                "<ulist> avec des <li>",
                "<ul> avec des <li>",
                "<list> avec des <item>"
            ],
            "correct_answer": 2,
            "type": "single",
            "explanation": "Une liste non ordonnée utilise <ul> (unordered list) avec des éléments <li> (list item).",
        },
        {
            "id": 9,
            "question": "Quelle est la différence entre <div> et <span> ?",
            "options": [
                "<div> est en bloc, <span> est en ligne",
                "Aucune différence",
                "<div> est en ligne, <span> est en bloc",
                "<div> est pour le texte, <span> pour les images"
            ],
            "correct_answer": 0,
            "type": "single",
            "explanation": "<div> est un élément de bloc qui prend toute la largeur disponible, tandis que <span> est un élément en ligne qui ne prend que l'espace nécessaire.",
        },
        {
            "id": 10,
            "question": "À quoi sert l'attribut 'class' ?",
            "options": [
                "Définir le type de l'élément",
                "Nommer l'élément de manière unique",
                "Appliquer des styles CSS et sélectionner avec JavaScript",
                "Créer une nouvelle classe en JavaScript"
            ],
            "correct_answer": 2,
            "type": "single",
            "explanation": "L'attribut 'class' permet d'appliquer des styles CSS et de sélectionner des éléments avec JavaScript. Plusieurs éléments peuvent avoir la même classe.",
        },
        {
            "id": 11,
            "question": "Quelle balise est sémantique pour représenter un article ?",
            "options": [
                "<div>",
                "<section>",
                "<content>",
                "<article>"
            ],
            "correct_answer": 3,
            "type": "single",
            "explanation": "La balise <article> est sémantique et représente un contenu indépendant et autonome, comme un article de blog.",
        },
        {
            "id": 12,
            "question": "Quelles balises HTML5 sont sémantiques ? (plusieurs réponses)",
            "options": [
                "<div>",
                "<footer>",
                "<nav>",
                "<header>"
            ],
            "correct_answer": [
                1,
                2,
                3
            ],
            "type": "multiple",
            "explanation": "<header>, <nav> et <footer> sont des balises sémantiques HTML5. <div> est une balise générique non sémantique.",
        },
        {
            "id": 13,
            "question": "Comment créer un formulaire en HTML ?",
            "options": [
                "<webform>",
                "<input> avec type='form'",
                "<form> avec action et method",
                "<formular>"
            ],
            "correct_answer": 2,
            "type": "single",
            "explanation": "La balise <form> avec les attributs action (URL de destination) et method (GET ou POST) est utilisée pour créer des formulaires.",
        },
        {
            "id": 14,
            "question": "Quel type d'input permet de saisir un email ?",
            "options": [
                "type='e-mail'",
                "type='address'",
                "type='mail'",
                "type='email'"
            ],
            "correct_answer": 3,
            "type": "single",
            "explanation": "L'attribut type='email' valide automatiquement que l'entrée est une adresse email valide.",
        },
        {
            "id": 15,
            "question": "À quoi sert la balise <meta charset='UTF-8'> ?",
            "options": [
                "Définir l'encodage des caractères",
                "Définir le style de la page",
                "Définir le titre de la page",
                "Créer des métadonnées"
            ],
            "correct_answer": 0,
            "type": "single",
            "explanation": "Cette balise définit l'encodage UTF-8 pour supporter tous les caractères internationaux correctement.",
        },
        {
            "id": 16,
            "question": "Quelle balise crée un tableau ?",
            "options": [
                "<tbl>",
                "<table>",
                "<grid>",
                "<tab>"
            ],
            "correct_answer": 1,
            "type": "single",
            "explanation": "La balise <table> crée un tableau, avec <tr> pour les lignes et <td> pour les cellules.",
        },
        {
            "id": 17,
            "question": "Quels éléments composent un tableau ? (plusieurs réponses)",
            "options": [
                "<td> (cellule)",
                "<tc> (colonne)",
                "<th> (en-tête)",
                "<tr> (ligne)"
            ],
            "correct_answer": [
                0,
                2,
                3
            ],
            "type": "multiple",
            "explanation": "Un tableau utilise <tr> pour les lignes, <td> pour les cellules de données et <th> pour les cellules d'en-tête.",
        },
        {
            "id": 18,
            "question": "Comment créer un commentaire en HTML ?",
            "options": [
                "// commentaire",
                "# commentaire",
                "<!-- commentaire -->",
                "/* commentaire */"
            ],
            "correct_answer": 2,
            "type": "single",
            "explanation": "Les commentaires HTML utilisent la syntaxe <!-- commentaire -->. Ils ne sont pas affichés dans le navigateur.",
        },
        {
            "id": 19,
            "question": "Quelle balise permet d'intégrer une vidéo en HTML5 ?",
            "options": [
                "<embed>",
                "<media>",
                "<movie>",
                "<video>"
            ],
            "correct_answer": 3,
            "type": "single",
            "explanation": "La balise <video> permet d'intégrer des vidéos nativement en HTML5, avec des attributs comme controls, autoplay, etc.",
        },
        {
            "id": 20,
            "question": "Pourquoi est-il important d'utiliser des balises sémantiques ?",
            "options": [
                "Améliorer l'accessibilité et le SEO",
                "Rendre le code plus rapide",
                "Économiser de l'espace disque",
                "Colorier automatiquement le texte"
            ],
            "correct_answer": 0,
            "type": "single",
            "explanation": "Les balises sémantiques améliorent l'accessibilité pour les lecteurs d'écran et le référencement (SEO) en donnant du sens au contenu.",
        },
    ]

    # Mélange des positions (graine fixe = résultat reproductible), puis
    # contrôle que seule la position a bougé. Voir l'en-tête du module.
    _original = copy.deepcopy(quiz_questions)
    _rng = random.Random(42)
    quiz_questions = [reorder_question(copy.deepcopy(q), _rng) for q in quiz_questions]
    verify_unchanged(_original, quiz_questions)

    # Créer une leçon de type QUIZ
    lesson, lesson_created = Lesson.objects.update_or_create(
        slug='quiz-html-fondamentaux',
        defaults={
            'chapter': chapter,
            'title': 'Quiz : Les Fondamentaux du HTML',
            'lesson_type': 'QUIZ',
            'order_index': 5,  # À la fin du chapitre (après les 2 exercices)
            'estimated_duration': 20,
            'points': 100,
            'is_published': True,
        }
    )

    if lesson_created:
        print(f"✅ Leçon créée: {lesson.title}")
    else:
        print(f"✅ Leçon mise à jour: {lesson.title}")

    # Créer ou mettre à jour le quiz associé
    quiz, quiz_created = Quiz.objects.update_or_create(
        lesson=lesson,
        defaults={
            'instructions': "Testez vos connaissances sur les bases du HTML ! Ce quiz couvre les concepts essentiels que vous devez maîtriser. Prenez votre temps et lisez bien chaque question.",
            'questions': quiz_questions,
            'passing_score': 70,
            'time_limit': 20,  # 20 minutes
            'randomize_questions': False,
            'randomize_options': True,
            'max_attempts': 0,  # Illimité
        }
    )

    if quiz_created:
        print(f"✅ Quiz créé pour: {lesson.title}")
    else:
        print(f"✅ Quiz mis à jour pour: {lesson.title}")

    print(f"\n🎯 Quiz disponible avec {quiz.question_count} questions")
    print(f"📊 Score minimum pour réussir: {quiz.passing_score}%")
    print(f"⏱️ Temps limite: {quiz.time_limit} minutes")

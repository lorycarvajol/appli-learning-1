"""
Script pour ajouter un quiz HTML avec 20 questions pédagogiques
Exécuter avec: docker-compose exec backend python manage.py shell < add_html_quiz.py
"""

import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
django.setup()

from apps.courses.models import Chapter, Lesson, Quiz

# Trouver le chapitre "Introduction HTML"
try:
    chapter = Chapter.objects.get(slug='introduction-html')
    print(f"Chapitre trouvé: {chapter.title}")
except Chapter.DoesNotExist:
    print("Chapitre 'introduction-html' non trouvé!")
    exit(1)

# 20 questions pédagogiques sur HTML
quiz_questions = [
        {
            "id": 1,
            "question": "Que signifie HTML ?",
            "options": [
                "HyperText Markup Language",
                "HighText Machine Language",
                "HyperText Machine Language",
                "HighText Markup Language"
            ],
            "correct_answer": 0,
            "type": "single",
            "explanation": "HTML signifie HyperText Markup Language. C'est le langage de balisage standard pour créer des pages web."
        },
        {
            "id": 2,
            "question": "Quelle est la structure de base d'un document HTML5 ?",
            "options": [
                "<!DOCTYPE html>, <html>, <head>, <body>",
                "<html>, <header>, <content>, <footer>",
                "<!DOCTYPE>, <page>, <content>",
                "<html>, <body>, <content>"
            ],
            "correct_answer": 0,
            "type": "single",
            "explanation": "Un document HTML5 commence par <!DOCTYPE html>, suivi des balises <html>, <head> et <body>."
        },
        {
            "id": 3,
            "question": "À quoi sert la balise <head> ?",
            "options": [
                "Afficher le contenu visible de la page",
                "Contenir les métadonnées et informations de la page",
                "Créer l'en-tête de la page",
                "Définir le pied de page"
            ],
            "correct_answer": 1,
            "type": "single",
            "explanation": "La balise <head> contient les métadonnées, le titre, les liens vers les CSS et autres informations qui ne sont pas affichées directement."
        },
        {
            "id": 4,
            "question": "Quelles balises sont utilisées pour créer des titres en HTML ? (plusieurs réponses possibles)",
            "options": [
                "<h1> à <h6>",
                "<title>",
                "<header>",
                "<heading>"
            ],
            "correct_answer": [0],
            "type": "multiple",
            "explanation": "Les balises <h1> à <h6> sont utilisées pour les titres, h1 étant le plus important et h6 le moins important."
        },
        {
            "id": 5,
            "question": "Comment créer un lien hypertexte en HTML ?",
            "options": [
                "<a href='url'>Texte</a>",
                "<link url='url'>Texte</link>",
                "<href='url'>Texte</href>",
                "<hyperlink>Texte</hyperlink>"
            ],
            "correct_answer": 0,
            "type": "single",
            "explanation": "La balise <a> avec l'attribut href est utilisée pour créer des liens hypertextes."
        },
        {
            "id": 6,
            "question": "Quelle balise permet d'insérer une image ?",
            "options": [
                "<img>",
                "<image>",
                "<picture>",
                "<photo>"
            ],
            "correct_answer": 0,
            "type": "single",
            "explanation": "La balise <img> avec l'attribut src est utilisée pour insérer des images. C'est une balise auto-fermante."
        },
        {
            "id": 7,
            "question": "Quels attributs sont obligatoires pour la balise <img> ? (plusieurs réponses)",
            "options": [
                "src (source de l'image)",
                "alt (texte alternatif)",
                "width (largeur)",
                "height (hauteur)"
            ],
            "correct_answer": [0, 1],
            "type": "multiple",
            "explanation": "Les attributs src (source) et alt (texte alternatif) sont obligatoires pour l'accessibilité et le SEO."
        },
        {
            "id": 8,
            "question": "Comment créer une liste non ordonnée ?",
            "options": [
                "<ul> avec des <li>",
                "<ol> avec des <li>",
                "<list> avec des <item>",
                "<ulist> avec des <li>"
            ],
            "correct_answer": 0,
            "type": "single",
            "explanation": "Une liste non ordonnée utilise <ul> (unordered list) avec des éléments <li> (list item)."
        },
        {
            "id": 9,
            "question": "Quelle est la différence entre <div> et <span> ?",
            "options": [
                "<div> est en bloc, <span> est en ligne",
                "<div> est en ligne, <span> est en bloc",
                "Aucune différence",
                "<div> est pour le texte, <span> pour les images"
            ],
            "correct_answer": 0,
            "type": "single",
            "explanation": "<div> est un élément de bloc qui prend toute la largeur disponible, tandis que <span> est un élément en ligne qui ne prend que l'espace nécessaire."
        },
        {
            "id": 10,
            "question": "À quoi sert l'attribut 'class' ?",
            "options": [
                "Appliquer des styles CSS et sélectionner avec JavaScript",
                "Créer une nouvelle classe en JavaScript",
                "Définir le type de l'élément",
                "Nommer l'élément de manière unique"
            ],
            "correct_answer": 0,
            "type": "single",
            "explanation": "L'attribut 'class' permet d'appliquer des styles CSS et de sélectionner des éléments avec JavaScript. Plusieurs éléments peuvent avoir la même classe."
        },
        {
            "id": 11,
            "question": "Quelle balise est sémantique pour représenter un article ?",
            "options": [
                "<article>",
                "<section>",
                "<div>",
                "<content>"
            ],
            "correct_answer": 0,
            "type": "single",
            "explanation": "La balise <article> est sémantique et représente un contenu indépendant et autonome, comme un article de blog."
        },
        {
            "id": 12,
            "question": "Quelles balises HTML5 sont sémantiques ? (plusieurs réponses)",
            "options": [
                "<header>",
                "<nav>",
                "<footer>",
                "<div>"
            ],
            "correct_answer": [0, 1, 2],
            "type": "multiple",
            "explanation": "<header>, <nav> et <footer> sont des balises sémantiques HTML5. <div> est une balise générique non sémantique."
        },
        {
            "id": 13,
            "question": "Comment créer un formulaire en HTML ?",
            "options": [
                "<form> avec action et method",
                "<input> avec type='form'",
                "<formular>",
                "<webform>"
            ],
            "correct_answer": 0,
            "type": "single",
            "explanation": "La balise <form> avec les attributs action (URL de destination) et method (GET ou POST) est utilisée pour créer des formulaires."
        },
        {
            "id": 14,
            "question": "Quel type d'input permet de saisir un email ?",
            "options": [
                "type='email'",
                "type='mail'",
                "type='e-mail'",
                "type='address'"
            ],
            "correct_answer": 0,
            "type": "single",
            "explanation": "L'attribut type='email' valide automatiquement que l'entrée est une adresse email valide."
        },
        {
            "id": 15,
            "question": "À quoi sert la balise <meta charset='UTF-8'> ?",
            "options": [
                "Définir l'encodage des caractères",
                "Définir le style de la page",
                "Créer des métadonnées",
                "Définir le titre de la page"
            ],
            "correct_answer": 0,
            "type": "single",
            "explanation": "Cette balise définit l'encodage UTF-8 pour supporter tous les caractères internationaux correctement."
        },
        {
            "id": 16,
            "question": "Quelle balise crée un tableau ?",
            "options": [
                "<table>",
                "<tab>",
                "<grid>",
                "<tbl>"
            ],
            "correct_answer": 0,
            "type": "single",
            "explanation": "La balise <table> crée un tableau, avec <tr> pour les lignes et <td> pour les cellules."
        },
        {
            "id": 17,
            "question": "Quels éléments composent un tableau ? (plusieurs réponses)",
            "options": [
                "<tr> (ligne)",
                "<td> (cellule)",
                "<th> (en-tête)",
                "<tc> (colonne)"
            ],
            "correct_answer": [0, 1, 2],
            "type": "multiple",
            "explanation": "Un tableau utilise <tr> pour les lignes, <td> pour les cellules de données et <th> pour les cellules d'en-tête."
        },
        {
            "id": 18,
            "question": "Comment créer un commentaire en HTML ?",
            "options": [
                "<!-- commentaire -->",
                "// commentaire",
                "/* commentaire */",
                "# commentaire"
            ],
            "correct_answer": 0,
            "type": "single",
            "explanation": "Les commentaires HTML utilisent la syntaxe <!-- commentaire -->. Ils ne sont pas affichés dans le navigateur."
        },
        {
            "id": 19,
            "question": "Quelle balise permet d'intégrer une vidéo en HTML5 ?",
            "options": [
                "<video>",
                "<movie>",
                "<media>",
                "<embed>"
            ],
            "correct_answer": 0,
            "type": "single",
            "explanation": "La balise <video> permet d'intégrer des vidéos nativement en HTML5, avec des attributs comme controls, autoplay, etc."
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
            "explanation": "Les balises sémantiques améliorent l'accessibilité pour les lecteurs d'écran et le référencement (SEO) en donnant du sens au contenu."
        }
]

# Créer une leçon de type QUIZ
lesson, lesson_created = Lesson.objects.update_or_create(
    slug='quiz-html-fondamentaux',
    defaults={
        'chapter': chapter,
        'title': 'Quiz : Les Fondamentaux du HTML',
        'lesson_type': 'QUIZ',
        'order_index': 10,  # À la fin du chapitre
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
        'randomize_options': False,
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
print(f"🔗 Slug de la leçon: {lesson.slug}")

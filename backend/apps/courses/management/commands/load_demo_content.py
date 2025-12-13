"""
Management command to load demo course content.
Usage: python manage.py load_demo_content
"""
from django.core.management.base import BaseCommand
from django.utils.text import slugify
from apps.courses.models import Chapter, Lesson, Exercise, Quiz


class Command(BaseCommand):
    help = 'Load demo course content (chapters, lessons, exercises, quizzes)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force delete existing content without confirmation',
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Loading demo course content...'))

        # Clear existing content if needed
        force = options.get('force', False)
        if force or self.confirm_action('This will DELETE all existing course content. Continue?'):
            Chapter.objects.all().delete()
            self.stdout.write(self.style.WARNING('Existing content deleted.'))

        # Chapter 1: Introduction au HTML
        chapter1 = Chapter.objects.create(
            title="Introduction au HTML",
            slug="introduction-html",
            description="Apprenez les bases du HTML : structure, balises et sémantique.",
            order_index=1,
            estimated_duration=180,  # 3 heures
            is_published=True
        )
        self.stdout.write(f'Created chapter: {chapter1.title}')

        # Lessons for Chapter 1
        lesson1_1 = Lesson.objects.create(
            chapter=chapter1,
            title="Qu'est-ce que le HTML ?",
            slug="quest-ce-que-le-html",
            lesson_type='THEORY',
            order_index=1,
            content="""# Qu'est-ce que le HTML ?

HTML (HyperText Markup Language) est le langage de balisage standard pour créer des pages web.

## Concepts clés

- **Balises** : Les éléments de base du HTML (ex: `<p>`, `<h1>`, `<div>`)
- **Structure** : Chaque page HTML a une structure de base
- **Sémantique** : Utiliser les bonnes balises pour le bon contenu

## Exemple de structure HTML

```html
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <title>Ma première page</title>
</head>
<body>
    <h1>Bonjour le monde !</h1>
    <p>Ceci est mon premier paragraphe.</p>
</body>
</html>
```

## Points importants

1. Toujours déclarer le DOCTYPE
2. Utiliser l'attribut `lang` pour la langue
3. Définir le charset en UTF-8
""",
            video_url="https://www.youtube.com/watch?v=example",
            estimated_duration=30,
            points=10,
            is_published=True
        )
        self.stdout.write(f'  - Created lesson: {lesson1_1.title}')

        lesson1_2 = Lesson.objects.create(
            chapter=chapter1,
            title="Structure d'une page HTML",
            slug="structure-page-html",
            lesson_type='THEORY',
            order_index=2,
            content="""# Structure d'une page HTML

Une page HTML est composée de deux parties principales : `<head>` et `<body>`.

## La balise <head>

Contient les métadonnées de la page :
- Titre de la page (`<title>`)
- Encodage des caractères (`<meta charset>`)
- Liens vers les fichiers CSS
- Meta descriptions pour le SEO

## La balise <body>

Contient tout le contenu visible de la page :
- Titres (`<h1>` à `<h6>`)
- Paragraphes (`<p>`)
- Images (`<img>`)
- Liens (`<a>`)
- Et bien plus encore !
""",
            estimated_duration=25,
            points=10,
            is_published=True
        )
        self.stdout.write(f'  - Created lesson: {lesson1_2.title}')

        lesson1_3 = Lesson.objects.create(
            chapter=chapter1,
            title="Exercice : Ma première page",
            slug="exercice-premiere-page",
            lesson_type='EXERCISE',
            order_index=3,
            content="",
            estimated_duration=45,
            points=50,
            is_published=True
        )
        self.stdout.write(f'  - Created lesson: {lesson1_3.title}')

        Exercise.objects.create(
            lesson=lesson1_3,
            instructions="""# Créez votre première page HTML

Complétez le code ci-dessous pour créer une page HTML valide avec :

1. Une structure HTML complète (DOCTYPE, html, head, body)
2. Un titre de page "Ma première page web"
3. Un titre h1 avec votre nom
4. Un paragraphe de présentation

**Conseil :** N'oubliez pas de fermer toutes les balises !
""",
            starter_code="""<!DOCTYPE html>
<html lang="fr">
<head>
    <!-- Ajoutez le charset UTF-8 ici -->
    <!-- Ajoutez le titre de la page ici -->
</head>
<body>
    <!-- Ajoutez votre code ici -->

</body>
</html>
""",
            solution="""<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <title>Ma première page web</title>
</head>
<body>
    <h1>Jean Dupont</h1>
    <p>Bonjour, je suis Jean et j'apprends le développement web !</p>
</body>
</html>
""",
            tests={
                "tests": [
                    {
                        "name": "DOCTYPE présent",
                        "code": "assert '<!DOCTYPE html>' in solution",
                        "points": 10
                    },
                    {
                        "name": "Charset UTF-8 défini",
                        "code": "assert 'charset=\"UTF-8\"' in solution or \"charset='UTF-8'\" in solution",
                        "points": 10
                    },
                    {
                        "name": "Titre de page présent",
                        "code": "assert '<title>' in solution and '</title>' in solution",
                        "points": 10
                    },
                    {
                        "name": "Titre h1 présent",
                        "code": "assert '<h1>' in solution and '</h1>' in solution",
                        "points": 10
                    },
                    {
                        "name": "Paragraphe présent",
                        "code": "assert '<p>' in solution and '</p>' in solution",
                        "points": 10
                    }
                ]
            },
            difficulty='EASY',
            max_attempts=5,
            time_limit=600,
            hints=[
                "N'oubliez pas la balise <meta charset=\"UTF-8\">",
                "Le titre de la page va dans la balise <title>",
                "Les titres principaux utilisent la balise <h1>"
            ]
        )
        self.stdout.write(f'    - Created exercise for: {lesson1_3.title}')

        lesson1_4 = Lesson.objects.create(
            chapter=chapter1,
            title="Quiz : Connaissances HTML de base",
            slug="quiz-html-base",
            lesson_type='QUIZ',
            order_index=4,
            content="",
            estimated_duration=20,
            points=30,
            is_published=True
        )
        self.stdout.write(f'  - Created lesson: {lesson1_4.title}')

        Quiz.objects.create(
            lesson=lesson1_4,
            instructions="Répondez aux questions suivantes pour valider vos connaissances en HTML de base.",
            questions={
                "questions": [
                    {
                        "id": 1,
                        "question": "Que signifie HTML ?",
                        "type": "multiple_choice",
                        "options": [
                            {"id": "a", "text": "HyperText Markup Language"},
                            {"id": "b", "text": "High Tech Modern Language"},
                            {"id": "c", "text": "Home Tool Markup Language"},
                            {"id": "d", "text": "Hyperlinks and Text Markup Language"}
                        ],
                        "correct_answer": "a",
                        "points": 10
                    },
                    {
                        "id": 2,
                        "question": "Quelle balise définit le titre principal d'une page ?",
                        "type": "multiple_choice",
                        "options": [
                            {"id": "a", "text": "<title>"},
                            {"id": "b", "text": "<h1>"},
                            {"id": "c", "text": "<header>"},
                            {"id": "d", "text": "<head>"}
                        ],
                        "correct_answer": "b",
                        "points": 10
                    },
                    {
                        "id": 3,
                        "question": "Où place-t-on les métadonnées d'une page HTML ?",
                        "type": "multiple_choice",
                        "options": [
                            {"id": "a", "text": "Dans la balise <body>"},
                            {"id": "b", "text": "Dans la balise <head>"},
                            {"id": "c", "text": "Dans la balise <meta>"},
                            {"id": "d", "text": "Dans la balise <title>"}
                        ],
                        "correct_answer": "b",
                        "points": 10
                    }
                ]
            },
            passing_score=70,
            time_limit=600,
            max_attempts=3,
            randomize_questions=False,
            randomize_options=True
        )
        self.stdout.write(f'    - Created quiz for: {lesson1_4.title}')

        # Chapter 2: CSS Fondamentaux
        chapter2 = Chapter.objects.create(
            title="CSS Fondamentaux",
            slug="css-fondamentaux",
            description="Découvrez comment styliser vos pages web avec CSS : sélecteurs, propriétés et mise en page.",
            order_index=2,
            estimated_duration=240,  # 4 heures
            is_published=True
        )
        self.stdout.write(f'Created chapter: {chapter2.title}')

        lesson2_1 = Lesson.objects.create(
            chapter=chapter2,
            title="Introduction au CSS",
            slug="introduction-css",
            lesson_type='THEORY',
            order_index=1,
            content="""# Introduction au CSS

CSS (Cascading Style Sheets) permet de styliser vos pages HTML.

## Trois façons d'ajouter du CSS

1. **Inline CSS** : Directement dans les balises HTML
```html
<p style="color: red;">Texte rouge</p>
```

2. **Internal CSS** : Dans la balise `<style>` du `<head>`
```html
<style>
    p { color: red; }
</style>
```

3. **External CSS** : Dans un fichier `.css` séparé (recommandé)
```html
<link rel="stylesheet" href="style.css">
```

## Syntaxe de base

```css
selecteur {
    propriete: valeur;
    autre-propriete: autre-valeur;
}
```

## Exemple

```css
h1 {
    color: blue;
    font-size: 32px;
    text-align: center;
}
```
""",
            estimated_duration=30,
            points=10,
            is_published=True
        )
        self.stdout.write(f'  - Created lesson: {lesson2_1.title}')

        lesson2_2 = Lesson.objects.create(
            chapter=chapter2,
            title="Exercice : Styliser une page",
            slug="exercice-styliser-page",
            lesson_type='EXERCISE',
            order_index=2,
            content="",
            estimated_duration=60,
            points=50,
            is_published=True
        )
        self.stdout.write(f'  - Created lesson: {lesson2_2.title}')

        Exercise.objects.create(
            lesson=lesson2_2,
            instructions="""# Ajoutez du style à votre page

Complétez le CSS pour obtenir le résultat suivant :

1. Titre h1 en bleu (`#0066cc`) et centré
2. Paragraphes avec une taille de police de 16px
3. Corps de page avec une couleur de fond gris clair (`#f5f5f5`)

**Astuce :** Utilisez les propriétés `color`, `text-align`, `font-size` et `background-color`.
""",
            starter_code="""/* Ajoutez votre CSS ici */

body {
    /* Couleur de fond */
}

h1 {
    /* Couleur et alignement */
}

p {
    /* Taille de police */
}
""",
            solution="""body {
    background-color: #f5f5f5;
}

h1 {
    color: #0066cc;
    text-align: center;
}

p {
    font-size: 16px;
}
""",
            tests={
                "tests": [
                    {
                        "name": "Couleur de fond du body",
                        "code": "assert '#f5f5f5' in solution or 'rgb(245, 245, 245)' in solution",
                        "points": 15
                    },
                    {
                        "name": "Couleur du h1",
                        "code": "assert '#0066cc' in solution or 'rgb(0, 102, 204)' in solution",
                        "points": 15
                    },
                    {
                        "name": "Alignement du h1",
                        "code": "assert 'text-align' in solution and 'center' in solution",
                        "points": 10
                    },
                    {
                        "name": "Taille de police du paragraphe",
                        "code": "assert 'font-size' in solution and '16px' in solution",
                        "points": 10
                    }
                ]
            },
            difficulty='EASY',
            max_attempts=5,
            time_limit=900,
            hints=[
                "Utilisez background-color pour la couleur de fond",
                "N'oubliez pas le # devant les codes couleur hexadécimaux",
                "La propriété text-align: center permet de centrer le texte"
            ]
        )
        self.stdout.write(f'    - Created exercise for: {lesson2_2.title}')

        # Chapter 3: JavaScript Débutant
        chapter3 = Chapter.objects.create(
            title="JavaScript pour Débutants",
            slug="javascript-debutants",
            description="Apprenez les bases de la programmation avec JavaScript : variables, fonctions et manipulation du DOM.",
            order_index=3,
            estimated_duration=300,  # 5 heures
            is_published=True
        )
        self.stdout.write(f'Created chapter: {chapter3.title}')

        lesson3_1 = Lesson.objects.create(
            chapter=chapter3,
            title="Variables et types de données",
            slug="variables-types-donnees",
            lesson_type='THEORY',
            order_index=1,
            content="""# Variables et Types de Données en JavaScript

## Déclarer des variables

Il existe trois façons de déclarer des variables en JavaScript :

```javascript
var ancienneMethode = "à éviter";
let variableModifiable = "recommandé";
const variableConstante = "recommandé pour les valeurs fixes";
```

## Types de données de base

1. **String** (chaîne de caractères)
```javascript
let nom = "Alice";
let message = 'Bonjour';
```

2. **Number** (nombre)
```javascript
let age = 25;
let prix = 19.99;
```

3. **Boolean** (booléen)
```javascript
let estConnecte = true;
let estAdmin = false;
```

4. **Array** (tableau)
```javascript
let fruits = ["pomme", "banane", "orange"];
```

5. **Object** (objet)
```javascript
let personne = {
    nom: "Alice",
    age: 25,
    ville: "Paris"
};
```

## Bonne pratique

Utilisez `const` par défaut, et `let` uniquement si vous devez réassigner la variable.
""",
            estimated_duration=40,
            points=10,
            is_published=True
        )
        self.stdout.write(f'  - Created lesson: {lesson3_1.title}')

        lesson3_2 = Lesson.objects.create(
            chapter=chapter3,
            title="Exercice : Manipulation de variables",
            slug="exercice-variables",
            lesson_type='EXERCISE',
            order_index=2,
            content="",
            estimated_duration=45,
            points=50,
            is_published=True
        )
        self.stdout.write(f'  - Created lesson: {lesson3_2.title}')

        Exercise.objects.create(
            lesson=lesson3_2,
            instructions="""# Créez et manipulez des variables

Complétez le code pour :

1. Créer une variable `prenom` avec votre prénom
2. Créer une variable `age` avec votre âge
3. Créer une variable `message` qui combine prénom et âge
4. La fonction doit retourner le message

**Format attendu :** "Je m'appelle [prenom] et j'ai [age] ans."
""",
            starter_code="""function presentation() {
    // Déclarez vos variables ici
    const prenom = "";
    const age = 0;
    const message = "";

    return message;
}

// Test (ne modifiez pas)
console.log(presentation());
""",
            solution="""function presentation() {
    const prenom = "Alice";
    const age = 25;
    const message = `Je m'appelle ${prenom} et j'ai ${age} ans.`;

    return message;
}

// Test (ne modifiez pas)
console.log(presentation());
""",
            tests={
                "tests": [
                    {
                        "name": "La fonction existe",
                        "code": "assert 'function presentation' in solution",
                        "points": 10
                    },
                    {
                        "name": "Variable prenom déclarée",
                        "code": "assert 'prenom' in solution",
                        "points": 10
                    },
                    {
                        "name": "Variable age déclarée",
                        "code": "assert 'age' in solution",
                        "points": 10
                    },
                    {
                        "name": "Variable message déclarée",
                        "code": "assert 'message' in solution",
                        "points": 10
                    },
                    {
                        "name": "Fonction retourne le message",
                        "code": "assert 'return message' in solution",
                        "points": 10
                    }
                ]
            },
            difficulty='EASY',
            max_attempts=5,
            time_limit=600,
            hints=[
                "Utilisez const pour déclarer vos variables",
                "Vous pouvez utiliser les template strings avec `${variable}`",
                "N'oubliez pas le return pour retourner le message"
            ]
        )
        self.stdout.write(f'    - Created exercise for: {lesson3_2.title}')

        self.stdout.write(self.style.SUCCESS('\n✅ Demo content loaded successfully!'))
        self.stdout.write(f'Created {Chapter.objects.count()} chapters')
        self.stdout.write(f'Created {Lesson.objects.count()} lessons')
        self.stdout.write(f'Created {Exercise.objects.count()} exercises')
        self.stdout.write(f'Created {Quiz.objects.count()} quizzes')

    def confirm_action(self, message):
        """Ask for user confirmation."""
        response = input(f'\n{message} (yes/no): ')
        return response.lower() in ['yes', 'y']

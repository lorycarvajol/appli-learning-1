"""
Management command to load Section 2: Introduction to CSS
Usage: python manage.py load_section_2_css --force
"""
from django.core.management.base import BaseCommand

from apps.courses.content import pipeline, section2_css_extra
from apps.courses.models import Chapter, Lesson, Exercise, Quiz


class Command(BaseCommand):
    help = 'Load Section 2: Introduction to CSS (complete and detailed)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force delete existing CSS chapter',
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Loading Section 2: Introduction to CSS...'))

        force = options.get('force', False)

        if force:
            Chapter.objects.filter(slug='introduction-css').delete()
            self.stdout.write(self.style.WARNING('Existing CSS chapter deleted.'))

        # ==========================================
        # CHAPTER: Introduction au CSS
        # ==========================================
        chapter = Chapter.objects.create(
            title="Introduction au CSS",
            slug="introduction-css",
            description="""Apprenez à styliser vos pages web avec CSS, le langage qui donne vie au HTML.
            Ce chapitre couvre la syntaxe CSS, les sélecteurs, le modèle de boîte (box model) et les
            bonnes pratiques pour créer des mises en page propres et maintenables.""",
            order_index=2,
            estimated_duration=70,
            is_published=True
        )
        self.stdout.write(f'✅ Created chapter: {chapter.title}')

        # ==========================================
        # LESSON 2.1: Qu'est-ce que le CSS ?
        # ==========================================
        lesson_2_1 = Lesson.objects.create(
            chapter=chapter,
            title="Qu'est-ce que le CSS ?",
            slug="quest-ce-que-le-css",
            lesson_type='THEORY',
            order_index=1,
            content="""# Qu'est-ce que le CSS ?

## 🎯 Objectifs de cette leçon

À la fin de cette leçon, vous serez capable de :
- ✅ Définir ce qu'est le CSS et son rôle dans le web
- ✅ Comprendre la syntaxe de base d'une règle CSS
- ✅ Connaître les 3 façons d'appliquer du CSS à une page HTML
- ✅ Choisir la bonne méthode selon le contexte

---

## 📖 Définition du CSS

**CSS** signifie **Cascading Style Sheets** (Feuilles de Style en Cascade).

### Décortiquons cette définition :

**Cascading (en cascade)** 🌊
- Les règles s'appliquent selon un ordre de priorité
- Plusieurs règles peuvent s'appliquer au même élément
- Le navigateur "cascade" les styles du plus général au plus spécifique

**Style Sheets (feuilles de style)** 🎨
- Un ensemble de règles qui décrivent l'apparence
- Séparées du contenu HTML
- Réutilisables sur plusieurs pages

---

## 🌍 Le rôle du CSS dans le Web

Le CSS est la **décoration** de toute page web. Il contrôle :

✅ **Les couleurs** : texte, fond, bordures
✅ **La typographie** : police, taille, graisse, interlignage
✅ **La mise en page** : positionnement, alignement, espacements
✅ **Les animations** : transitions, transformations
✅ **Le responsive** : adaptation à toutes les tailles d'écran

> 💡 **Rappel de l'analogie** : Si HTML est le squelette de la maison, CSS est la peinture, les meubles et la décoration intérieure.

---

## ✍️ Syntaxe de base d'une règle CSS

```css
sélecteur {
    propriété: valeur;
    propriété: valeur;
}
```

### Exemple concret :

```css
h1 {
    color: blue;
    font-size: 32px;
    text-align: center;
}
```

**Décomposition :**
- `h1` → le **sélecteur** (quel élément styliser)
- `{ }` → le **bloc de déclarations**
- `color: blue;` → une **déclaration** (propriété + valeur)
- `;` → sépare chaque déclaration

> ⚠️ **Règle importante** : Chaque déclaration se termine par un point-virgule `;`. L'oublier sur la dernière ligne fonctionne, mais c'est une mauvaise pratique.

---

## 🔗 Les 3 façons d'appliquer du CSS

### 1️⃣ CSS en ligne (inline)

```html
<h1 style="color: blue; font-size: 32px;">Titre</h1>
```

✅ Rapide pour tester
❌ Mélange contenu et présentation
❌ Impossible à réutiliser
❌ Priorité très élevée (difficile à surcharger)

> 🚫 **À éviter** en production, sauf cas très spécifiques (styles générés dynamiquement en JavaScript).

### 2️⃣ CSS interne (internal)

```html
<head>
    <style>
        h1 {
            color: blue;
            font-size: 32px;
        }
    </style>
</head>
```

✅ Pratique pour une page unique
❌ Non réutilisable sur d'autres pages
❌ Alourdit le fichier HTML

> 💡 **Utile pour** : prototypage rapide, démonstrations, emails HTML.

### 3️⃣ CSS externe (external) — **La méthode recommandée** ⭐

**Fichier `style.css` :**
```css
h1 {
    color: blue;
    font-size: 32px;
}
```

**Fichier `index.html` :**
```html
<head>
    <link rel="stylesheet" href="style.css">
</head>
```

✅ **Séparation des préoccupations** (contenu vs présentation)
✅ **Réutilisable** sur toutes les pages du site
✅ **Mise en cache** par le navigateur (meilleures performances)
✅ **Maintenance facilitée** (un seul fichier à modifier)

> 🎓 **Bonne pratique** : Toujours privilégier le CSS externe dans un projet réel.

---

## 📝 Les commentaires en CSS

```css
/* Ceci est un commentaire */
h1 {
    color: blue; /* Couleur du titre principal */
}
```

✅ Syntaxe `/* ... */` (pas de `//` comme en JavaScript)
✅ Utile pour documenter ou désactiver temporairement du code

---

## 🎓 Points clés à retenir

✅ CSS = Cascading Style Sheets
✅ Une règle CSS = sélecteur + déclarations entre accolades
✅ Chaque déclaration se termine par un point-virgule
✅ 3 méthodes : inline, interne, externe
✅ Le CSS externe est la méthode recommandée en production
✅ Les commentaires CSS utilisent `/* ... */`

---

## 🚀 À vous de jouer !

Dans la prochaine leçon, nous allons explorer les **sélecteurs CSS** et le **modèle de boîte (box model)**, deux notions essentielles pour maîtriser la mise en page.

> 💬 **Question de réflexion** : Pourquoi la séparation entre HTML (structure) et CSS (présentation) est-elle considérée comme une bonne pratique ?
""",
            video_url="",
            estimated_duration=15,
            points=10,
            is_published=True
        )
        self.stdout.write(f'  ✅ Leçon 2.1: {lesson_2_1.title}')

        # ==========================================
        # LESSON 2.2: Sélecteurs et Box Model
        # ==========================================
        lesson_2_2 = Lesson.objects.create(
            chapter=chapter,
            title="Sélecteurs et Box Model",
            slug="selecteurs-et-box-model",
            lesson_type='THEORY',
            order_index=2,
            content="""# Sélecteurs CSS et Box Model

## 🎯 Objectifs de cette leçon

À la fin de cette leçon, vous serez capable de :
- ✅ Utiliser les principaux sélecteurs CSS
- ✅ Comprendre et manipuler le modèle de boîte (box model)
- ✅ Différencier `margin`, `border`, `padding` et `content`
- ✅ Appliquer `box-sizing` correctement

---

## 🎯 Les sélecteurs CSS

Les sélecteurs déterminent **quels éléments HTML** seront stylisés.

### 1️⃣ Sélecteur d'élément (type)

```css
p {
    color: black;
}
```
Cible **tous** les `<p>` de la page.

### 2️⃣ Sélecteur de classe

```html
<p class="alerte">Attention !</p>
```

```css
.alerte {
    color: red;
}
```
✅ Réutilisable sur plusieurs éléments
✅ Le point `.` précède le nom de la classe

### 3️⃣ Sélecteur d'ID

```html
<p id="titre-principal">Bienvenue</p>
```

```css
#titre-principal {
    font-size: 28px;
}
```
⚠️ Un ID doit être **unique** dans la page
⚠️ Priorité (spécificité) plus forte qu'une classe

### 4️⃣ Sélecteurs combinés

```css
/* Descendant : tous les <a> à l'intérieur de <nav> */
nav a {
    text-decoration: none;
}

/* Enfant direct : les <li> enfants directs de <ul> */
ul > li {
    list-style: none;
}

/* Plusieurs sélecteurs pour une même règle */
h1, h2, h3 {
    font-family: Arial, sans-serif;
}
```

### 5️⃣ Pseudo-classes

```css
a:hover {
    color: orange;
}

button:disabled {
    opacity: 0.5;
}
```

---

## 📐 Le Box Model (modèle de boîte)

En CSS, **chaque élément HTML est une boîte rectangulaire** composée de 4 couches :

```
┌─────────────────────────────────────┐
│              margin                  │
│   ┌───────────────────────────────┐ │
│   │           border               │ │
│   │   ┌───────────────────────┐   │ │
│   │   │       padding          │   │ │
│   │   │   ┌───────────────┐   │   │ │
│   │   │   │    content     │   │   │ │
│   │   │   └───────────────┘   │   │ │
│   │   └───────────────────────┘   │ │
│   └───────────────────────────────┘ │
└─────────────────────────────────────┘
```

### 1️⃣ Content (contenu)

Le texte ou les éléments à l'intérieur de la boîte.

```css
.box {
    width: 200px;
    height: 100px;
}
```

### 2️⃣ Padding (espacement intérieur)

L'espace entre le contenu et la bordure.

```css
.box {
    padding: 20px;              /* 4 côtés */
    padding: 10px 20px;         /* haut/bas gauche/droite */
    padding: 10px 20px 15px 5px; /* haut droite bas gauche */
    padding-top: 10px;          /* un seul côté */
}
```

### 3️⃣ Border (bordure)

```css
.box {
    border: 2px solid black;    /* épaisseur style couleur */
    border-radius: 8px;         /* coins arrondis */
}
```

### 4️⃣ Margin (espacement extérieur)

L'espace entre la boîte et les éléments voisins.

```css
.box {
    margin: 20px;
    margin: 0 auto; /* centrer horizontalement un bloc */
}
```

> 💡 **Astuce classique** : `margin: 0 auto;` sur un élément avec une `width` définie le centre horizontalement.

---

## 🧮 Calcul de la taille totale

Par défaut (`box-sizing: content-box`), la largeur totale d'une boîte est :

```
Largeur totale = width + padding (gauche+droite) + border (gauche+droite) + margin (gauche+droite)
```

**Exemple :**
```css
.box {
    width: 200px;
    padding: 20px;
    border: 5px solid black;
}
```
Largeur visible (hors margin) = 200 + (20×2) + (5×2) = **250px**

> ⚠️ **Piège fréquent** : Beaucoup de débutants pensent que `width: 200px` donne une boîte de 200px de large affichée. En réalité, padding et border s'ajoutent !

---

## 🔧 `box-sizing: border-box` — La solution moderne

```css
* {
    box-sizing: border-box;
}
```

Avec `border-box`, `width` inclut le padding et la bordure :

```
Largeur totale = width (padding et border sont inclus dedans)
```

**Reprenons l'exemple :**
```css
.box {
    box-sizing: border-box;
    width: 200px;
    padding: 20px;
    border: 5px solid black;
}
```
Largeur visible = **200px** (padding et border sont absorbés dans les 200px)

> 🎓 **Bonne pratique universelle** : Appliquer `box-sizing: border-box` à tous les éléments via `*` en début de feuille de style. Cela simplifie énormément les calculs de mise en page.

```css
* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}
```

---

## 🎓 Points clés à retenir

✅ Sélecteurs : élément, `.classe`, `#id`, combinaisons, pseudo-classes
✅ Une classe est réutilisable, un ID est unique
✅ Box model = content + padding + border + margin
✅ `box-sizing: border-box` simplifie le calcul des tailles
✅ `margin: 0 auto;` centre un bloc horizontalement

---

## 🚀 Prochaine étape

Maintenant que vous connaissez les sélecteurs et le box model, passons à la pratique avec vos **premiers exercices CSS** ! 💪
""",
            video_url="",
            estimated_duration=20,
            points=10,
            is_published=True
        )
        self.stdout.write(f'  ✅ Leçon 2.2: {lesson_2_2.title}')

        # ==========================================
        # EXERCISE 2.1: Styliser sa première page
        # ==========================================
        lesson_2_3 = Lesson.objects.create(
            chapter=chapter,
            title="Exercice : Styliser sa première page",
            slug="exercice-styliser-premiere-page",
            lesson_type='EXERCISE',
            order_index=3,
            content="",
            estimated_duration=15,
            points=25,
            is_published=True
        )
        self.stdout.write(f'  ✅ Leçon 2.3: {lesson_2_3.title}')

        Exercise.objects.create(
            lesson=lesson_2_3,
            instructions="""# 🎯 Exercice : Styliser sa première page

## Objectif

Écrire une feuille de style CSS qui applique des règles de base à des sélecteurs d'élément, de classe et d'ID.

---

## 📋 Instructions détaillées

Écrivez du CSS qui respecte les règles suivantes :

### 1. Sélecteur d'élément ✅

- [ ] Tous les `<h1>` doivent avoir `color: blue;`

### 2. Sélecteur de classe ✅

- [ ] La classe `.alerte` doit avoir `color: red;`

### 3. Sélecteur d'ID ✅

- [ ] L'élément avec `#titre-principal` doit avoir `font-size: 28px;`

### 4. Police globale ✅

- [ ] Le sélecteur `body` doit définir `font-family: Arial, sans-serif;`

---

## 💡 Conseils

- Respectez la syntaxe `sélecteur { propriété: valeur; }`
- N'oubliez pas les points-virgules
- Un sélecteur de classe commence par un point `.`
- Un sélecteur d'ID commence par un dièse `#`

---

## ✅ Critères de validation

Votre code sera testé automatiquement sur :

1. ✅ Règle pour `h1` avec `color: blue`
2. ✅ Règle pour `.alerte` avec `color: red`
3. ✅ Règle pour `#titre-principal` avec `font-size: 28px`
4. ✅ Règle pour `body` avec `font-family`

---

## 🚀 Prêt ? C'est parti !

Écrivez votre code CSS dans l'éditeur ci-dessous et cliquez sur "Valider" pour tester ! 💪
""",
            starter_code="""/* Stylisez le titre h1 */


/* Stylisez la classe .alerte */


/* Stylisez l'ID #titre-principal */


/* Définissez la police globale du body */

""",
            solution="""h1 {
    color: blue;
}

.alerte {
    color: red;
}

#titre-principal {
    font-size: 28px;
}

body {
    font-family: Arial, sans-serif;
}
""",
            tests={
                "tests": [
                    {
                        "name": "Règle h1 avec color: blue",
                        "code": "import re\nassert re.search(r'h1\\s*\\{[^}]*color\\s*:\\s*blue', solution)",
                        "points": 5,
                        "error_message": "Ajoutez une règle 'h1 { color: blue; }'"
                    },
                    {
                        "name": "Classe .alerte avec color: red",
                        "code": "import re\nassert re.search(r'\\.alerte\\s*\\{[^}]*color\\s*:\\s*red', solution)",
                        "points": 5,
                        "error_message": "Ajoutez une règle '.alerte { color: red; }'"
                    },
                    {
                        "name": "ID #titre-principal avec font-size: 28px",
                        "code": "import re\nassert re.search(r'#titre-principal\\s*\\{[^}]*font-size\\s*:\\s*28px', solution)",
                        "points": 5,
                        "error_message": "Ajoutez une règle '#titre-principal { font-size: 28px; }'"
                    },
                    {
                        "name": "body avec font-family",
                        "code": "import re\nassert re.search(r'body\\s*\\{[^}]*font-family\\s*:', solution)",
                        "points": 5,
                        "error_message": "Ajoutez une règle 'body { font-family: ...; }'"
                    }
                ]
            },
            difficulty='EASY',
            max_attempts=5,
            time_limit=900,
            hints=[
                "💡 Astuce 1 : Chaque règle suit le format 'sélecteur { propriété: valeur; }'",
                "💡 Astuce 2 : La classe commence par un point, l'ID par un dièse",
                "💡 Astuce 3 : Vérifiez que chaque déclaration se termine par un point-virgule"
            ]
        )
        self.stdout.write(f'    ✅ Exercice créé pour : {lesson_2_3.title}')

        # ==========================================
        # EXERCISE 2.2: Mise en page avec Box Model
        # ==========================================
        lesson_2_4 = Lesson.objects.create(
            chapter=chapter,
            title="Exercice : Mise en page avec Box Model",
            slug="exercice-box-model",
            lesson_type='EXERCISE',
            order_index=4,
            content="",
            estimated_duration=15,
            points=25,
            is_published=True
        )
        self.stdout.write(f'  ✅ Leçon 2.4: {lesson_2_4.title}')

        Exercise.objects.create(
            lesson=lesson_2_4,
            instructions="""# 🎯 Exercice : Mise en page avec le Box Model

## Objectif

Mettre en pratique le modèle de boîte (box model) en stylisant une carte (`.card`) avec padding, border, margin et box-sizing.

---

## 📋 Instructions détaillées

Complétez la règle CSS pour la classe `.card` avec les propriétés suivantes :

### 1. Dimensions et box-sizing ✅

- [ ] `width: 300px;`
- [ ] `box-sizing: border-box;`

### 2. Espacements ✅

- [ ] `padding: 20px;`
- [ ] `margin: 0 auto;` (pour centrer horizontalement)

### 3. Bordure ✅

- [ ] `border: 1px solid black;`
- [ ] `border-radius: 8px;` (coins arrondis)

---

## 💡 Conseils

- `margin: 0 auto;` centre un bloc horizontalement lorsqu'il a une largeur définie
- `box-sizing: border-box;` évite les surprises de calcul de taille
- Pensez à utiliser un raccourci pour `border` : `épaisseur style couleur`

---

## ✅ Critères de validation

Votre code sera testé automatiquement sur :

1. ✅ `.card` a `width: 300px`
2. ✅ `.card` a `box-sizing: border-box`
3. ✅ `.card` a `padding: 20px`
4. ✅ `.card` a `margin: 0 auto`
5. ✅ `.card` a une bordure (`border`)
6. ✅ `.card` a `border-radius`

---

## 🚀 À vous de jouer !
""",
            starter_code=""".card {
    /* Ajoutez width et box-sizing */

    /* Ajoutez padding et margin */

    /* Ajoutez border et border-radius */

}
""",
            solution=""".card {
    width: 300px;
    box-sizing: border-box;
    padding: 20px;
    margin: 0 auto;
    border: 1px solid black;
    border-radius: 8px;
}
""",
            tests={
                "tests": [
                    {
                        "name": ".card a width: 300px",
                        "code": "import re\nassert re.search(r'\\.card\\s*\\{[^}]*width\\s*:\\s*300px', solution)",
                        "points": 4,
                        "error_message": "Ajoutez 'width: 300px;' dans .card"
                    },
                    {
                        "name": ".card a box-sizing: border-box",
                        "code": "import re\nassert re.search(r'\\.card\\s*\\{[^}]*box-sizing\\s*:\\s*border-box', solution)",
                        "points": 4,
                        "error_message": "Ajoutez 'box-sizing: border-box;' dans .card"
                    },
                    {
                        "name": ".card a padding: 20px",
                        "code": "import re\nassert re.search(r'\\.card\\s*\\{[^}]*padding\\s*:\\s*20px', solution)",
                        "points": 4,
                        "error_message": "Ajoutez 'padding: 20px;' dans .card"
                    },
                    {
                        "name": ".card a margin: 0 auto",
                        "code": "import re\nassert re.search(r'\\.card\\s*\\{[^}]*margin\\s*:\\s*0\\s+auto', solution)",
                        "points": 4,
                        "error_message": "Ajoutez 'margin: 0 auto;' dans .card pour centrer le bloc"
                    },
                    {
                        "name": ".card a une bordure",
                        "code": "import re\nassert re.search(r'\\.card\\s*\\{[^}]*border\\s*:', solution)",
                        "points": 4,
                        "error_message": "Ajoutez une propriété 'border:' dans .card"
                    },
                    {
                        "name": ".card a border-radius",
                        "code": "import re\nassert re.search(r'\\.card\\s*\\{[^}]*border-radius\\s*:', solution)",
                        "points": 5,
                        "error_message": "Ajoutez 'border-radius:' dans .card pour arrondir les coins"
                    }
                ]
            },
            difficulty='MEDIUM',
            max_attempts=5,
            time_limit=900,
            hints=[
                "💡 Astuce 1 : Toutes les propriétés doivent être à l'intérieur du même bloc .card { ... }",
                "💡 Astuce 2 : 'border: 1px solid black;' combine épaisseur, style et couleur en une ligne",
                "💡 Astuce 3 : 'margin: 0 auto;' signifie 0 en haut/bas et 'auto' en gauche/droite"
            ]
        )
        self.stdout.write(f'    ✅ Exercice créé pour : {lesson_2_4.title}')

        # ==========================================
        # QUIZ 2: Validation Sélecteurs et Box Model
        # ==========================================
        lesson_2_5 = Lesson.objects.create(
            chapter=chapter,
            title="Quiz : Sélecteurs et Box Model",
            slug="quiz-selecteurs-box-model",
            lesson_type='QUIZ',
            order_index=5,
            content="",
            estimated_duration=10,
            points=20,
            is_published=True
        )
        self.stdout.write(f'  ✅ Leçon 2.5: {lesson_2_5.title}')

        Quiz.objects.create(
            lesson=lesson_2_5,
            instructions="""# 📝 Quiz : Validez vos connaissances sur le CSS

Testez votre compréhension des sélecteurs CSS et du box model.

**Durée** : 10 minutes
**Score minimal** : 70%
**Tentatives** : 3 maximum

Bonne chance ! 🍀
""",
            questions={
                "questions": [
                    {
                        "id": 1,
                        "question": "Que signifie l'acronyme CSS ?",
                        "type": "multiple_choice",
                        "options": [
                            {"id": "a", "text": "Cascading Style Sheets"},
                            {"id": "b", "text": "Computer Style System"},
                            {"id": "c", "text": "Creative Style Syntax"},
                            {"id": "d", "text": "Colorful Style Sheets"}
                        ],
                        "correct_answer": "a",
                        "points": 2,
                        "explanation": "CSS signifie Cascading Style Sheets, les feuilles de style en cascade."
                    },
                    {
                        "id": 2,
                        "question": "Quel symbole précède un sélecteur de classe en CSS ?",
                        "type": "multiple_choice",
                        "options": [
                            {"id": "a", "text": "# (dièse)"},
                            {"id": "b", "text": ". (point)"},
                            {"id": "c", "text": "@ (arobase)"},
                            {"id": "d", "text": "% (pourcentage)"}
                        ],
                        "correct_answer": "b",
                        "points": 2,
                        "explanation": "Un point précède les sélecteurs de classe, un dièse précède les sélecteurs d'ID."
                    },
                    {
                        "id": 3,
                        "question": "Quelle est la méthode recommandée pour appliquer du CSS en production ?",
                        "type": "multiple_choice",
                        "options": [
                            {"id": "a", "text": "CSS en ligne (attribut style)"},
                            {"id": "b", "text": "CSS interne (balise <style>)"},
                            {"id": "c", "text": "CSS externe (fichier .css lié)"},
                            {"id": "d", "text": "Toutes se valent"}
                        ],
                        "correct_answer": "c",
                        "points": 3,
                        "explanation": "Le CSS externe permet la réutilisation, la mise en cache et sépare contenu et présentation."
                    },
                    {
                        "id": 4,
                        "question": "Dans le box model, quel est l'ordre des couches de l'intérieur vers l'extérieur ?",
                        "type": "multiple_choice",
                        "options": [
                            {"id": "a", "text": "content, border, padding, margin"},
                            {"id": "b", "text": "content, padding, border, margin"},
                            {"id": "c", "text": "margin, padding, border, content"},
                            {"id": "d", "text": "padding, content, margin, border"}
                        ],
                        "correct_answer": "b",
                        "points": 3,
                        "explanation": "L'ordre est : content (contenu) → padding (espace intérieur) → border (bordure) → margin (espace extérieur)."
                    },
                    {
                        "id": 5,
                        "question": "Que fait la propriété 'box-sizing: border-box' ?",
                        "type": "multiple_choice",
                        "options": [
                            {"id": "a", "text": "Elle ajoute une bordure automatiquement"},
                            {"id": "b", "text": "Elle inclut padding et border dans la largeur définie (width)"},
                            {"id": "c", "text": "Elle supprime le padding"},
                            {"id": "d", "text": "Elle centre l'élément"}
                        ],
                        "correct_answer": "b",
                        "points": 3,
                        "explanation": "Avec border-box, la largeur (width) inclut le padding et la bordure, simplifiant les calculs."
                    },
                    {
                        "id": 6,
                        "question": "Comment centrer horizontalement un bloc avec une largeur définie ?",
                        "type": "multiple_choice",
                        "options": [
                            {"id": "a", "text": "margin: auto 0;"},
                            {"id": "b", "text": "padding: 0 auto;"},
                            {"id": "c", "text": "margin: 0 auto;"},
                            {"id": "d", "text": "text-align: center;"}
                        ],
                        "correct_answer": "c",
                        "points": 3,
                        "explanation": "margin: 0 auto; répartit l'espace horizontal restant également des deux côtés, centrant le bloc."
                    },
                    {
                        "id": 7,
                        "question": "Quel sélecteur cible tous les <li> qui sont enfants directs d'un <ul> ?",
                        "type": "multiple_choice",
                        "options": [
                            {"id": "a", "text": "ul li"},
                            {"id": "b", "text": "ul > li"},
                            {"id": "c", "text": "ul + li"},
                            {"id": "d", "text": "ul ~ li"}
                        ],
                        "correct_answer": "b",
                        "points": 3,
                        "explanation": "Le combinateur > sélectionne uniquement les enfants directs, contrairement à l'espace qui cible tous les descendants."
                    },
                    {
                        "id": 8,
                        "question": "Entre une classe et un ID, lequel doit être unique dans la page ?",
                        "type": "multiple_choice",
                        "options": [
                            {"id": "a", "text": "La classe"},
                            {"id": "b", "text": "L'ID"},
                            {"id": "c", "text": "Les deux"},
                            {"id": "d", "text": "Aucun des deux"}
                        ],
                        "correct_answer": "b",
                        "points": 2,
                        "explanation": "Un ID doit être unique dans la page, tandis qu'une classe peut être réutilisée sur plusieurs éléments."
                    }
                ]
            },
            passing_score=70,
            time_limit=600,
            max_attempts=3,
            randomize_questions=False,
            randomize_options=True
        )
        self.stdout.write(f'    ✅ Quiz créé pour : {lesson_2_5.title}')

        # ==========================================
        # Compléments et illustrations
        # ==========================================
        # `section2_css_extra` ajoute 12 leçons, réordonne le chapitre et
        # reconstruit le quiz au format enrichi.
        pipeline.finish(
            self, chapter,
            steps=[section2_css_extra.build],
            verbosity=options.get('verbosity', 1),
        )

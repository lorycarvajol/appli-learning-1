"""
Management command to load Section 1: Introduction to HTML
Usage: python manage.py load_section_1_html --force
"""
from django.core.management.base import BaseCommand

from apps.courses.content import pipeline, section1_html_extra, section1_html_quiz
from apps.courses.models import Chapter, Lesson, Exercise, Quiz


class Command(BaseCommand):
    help = 'Load Section 1: Introduction to HTML (complete and detailed)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force delete existing HTML chapter',
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Loading Section 1: Introduction to HTML...'))

        force = options.get('force', False)

        # Delete existing HTML chapter if --force
        if force:
            Chapter.objects.filter(slug='introduction-html').delete()
            self.stdout.write(self.style.WARNING('Existing HTML chapter deleted.'))

        # ==========================================
        # CHAPTER: Introduction au HTML
        # ==========================================
        chapter = Chapter.objects.create(
            title="Introduction au HTML",
            slug="introduction-html",
            description="""Maîtrisez les fondamentaux du HTML, le langage de balisage qui structure toutes les pages web.
            Ce chapitre couvre l'histoire du HTML, sa syntaxe de base, et les bonnes pratiques pour créer des pages web
            valides, sémantiques et accessibles.""",
            order_index=1,
            estimated_duration=60,  # 60 minutes
            is_published=True
        )
        self.stdout.write(f'✅ Created chapter: {chapter.title}')

        # ==========================================
        # LESSON 1.1: Qu'est-ce que le HTML ?
        # ==========================================
        lesson_1_1 = Lesson.objects.create(
            chapter=chapter,
            title="Qu'est-ce que le HTML ?",
            slug="quest-ce-que-le-html",
            lesson_type='THEORY',
            order_index=1,
            content="""# Qu'est-ce que le HTML ?

## 🎯 Objectifs de cette leçon

À la fin de cette leçon, vous serez capable de :
- ✅ Définir ce qu'est le HTML et son rôle dans le web
- ✅ Comprendre la place du HTML dans l'écosystème web
- ✅ Différencier HTML, CSS et JavaScript
- ✅ Connaître l'évolution du HTML jusqu'à HTML5

---

## 📖 Définition du HTML

**HTML** signifie **HyperText Markup Language** (Langage de Balisage HyperTexte).

### Décortiquons cette définition :

**HyperTexte** 🔗
- Texte enrichi avec des liens (hyperliens)
- Permet de naviguer entre les pages
- Crée une toile de documents interconnectés (le "Web")

**Markup** 🏷️
- Système de balisage pour structurer le contenu
- Utilise des balises `<comme ceci>`
- Indique au navigateur comment afficher le contenu

**Language** 💬
- Un langage formel avec une syntaxe précise
- Compris par tous les navigateurs web
- Standard universel du web

---

## 🌍 Le rôle du HTML dans le Web

Le HTML est le **squelette** de toute page web. Il définit :

✅ **La structure** : titres, paragraphes, sections, listes
✅ **Le contenu** : texte, images, vidéos, liens
✅ **La sémantique** : signification des éléments (navigation, article, etc.)
✅ **L'accessibilité** : informations pour les lecteurs d'écran

> 💡 **Analogie** : Si une page web était une maison, le HTML serait la structure (murs, sol, plafond), le CSS serait la décoration (peinture, meubles), et JavaScript serait l'électricité (interactivité).

---

## 🎨 HTML, CSS et JavaScript : La Trinité du Web

Le développement web moderne repose sur **trois technologies complémentaires** :

### 1️⃣ HTML (Structure)
```html
<h1>Bienvenue sur mon site</h1>
<p>Ceci est un paragraphe.</p>
```
**Rôle** : Définir le contenu et sa structure
**Analogie** : Les fondations et murs d'une maison

### 2️⃣ CSS (Présentation)
```css
h1 {
    color: blue;
    font-size: 32px;
}
```
**Rôle** : Styliser l'apparence visuelle
**Analogie** : La décoration et l'aménagement

### 3️⃣ JavaScript (Comportement)
```javascript
document.querySelector('h1').addEventListener('click', () => {
    alert('Titre cliqué !');
});
```
**Rôle** : Ajouter de l'interactivité
**Analogie** : L'électricité et la domotique

> 📊 **Illustration à voir** : Schéma "HTML vs CSS vs JavaScript"

---

## 📈 L'évolution du HTML

Le HTML a connu plusieurs versions depuis sa création :

### 🕰️ Histoire rapide

| Année | Version | Nouveautés principales |
|-------|---------|------------------------|
| **1991** | HTML 1.0 | Première version par Tim Berners-Lee |
| **1995** | HTML 2.0 | Formulaires, tableaux |
| **1997** | HTML 3.2 | Scripts, feuilles de style |
| **1999** | HTML 4.01 | Séparation contenu/présentation |
| **2000** | XHTML 1.0 | HTML conforme XML (plus strict) |
| **2014** | **HTML5** | Vidéo native, canvas, APIs, sémantique |
| **Aujourd'hui** | HTML Living Standard | Évolution continue |

### 🚀 HTML5 : La révolution moderne

HTML5 (2014) a apporté des innovations majeures :

✨ **Balises sémantiques** : `<header>`, `<nav>`, `<article>`, `<footer>`
🎬 **Médias natifs** : `<video>`, `<audio>` sans plugins
🎨 **Graphiques** : `<canvas>`, `<svg>` pour dessiner
📱 **APIs modernes** : géolocalisation, stockage local, drag & drop
♿ **Accessibilité** : Meilleur support ARIA

---

## 🔍 HTML vs XHTML : Quelle différence ?

### HTML (Syntaxe permissive)
```html
<p>Paragraphe pas fermé
<img src="photo.jpg">
<BR>
```
✅ Tolère certaines erreurs
✅ Pas besoin de fermer toutes les balises
✅ Plus rapide à écrire

### XHTML (Syntaxe stricte)
```xhtml
<p>Paragraphe correctement fermé</p>
<img src="photo.jpg" />
<br />
```
✅ Conforme XML
✅ Toutes les balises doivent être fermées
✅ Syntaxe plus rigoureuse

> 💡 **Aujourd'hui** : On utilise HTML5 avec de bonnes pratiques (fermer les balises, indenter, etc.) sans la rigueur excessive de XHTML.

---

## 🌐 Comment fonctionne le HTML ?

### Le cycle de vie d'une page web :

1. **Vous écrivez** du code HTML dans un fichier `.html`
2. **Vous ouvrez** ce fichier dans un navigateur
3. **Le navigateur lit** (parse) le code HTML
4. **Le navigateur construit** le DOM (Document Object Model)
5. **Le navigateur affiche** la page à l'écran

> 📊 **Illustration à voir** : Schéma "Architecture Client-Serveur"

```
Développeur → Écrit HTML → Serveur → Envoie HTML → Navigateur → Affiche
```

---

## ✅ Exemple minimal de HTML

Voici la structure la plus simple d'une page HTML valide :

```html
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <title>Ma première page</title>
</head>
<body>
    <h1>Bonjour le monde !</h1>
    <p>Ceci est ma première page web en HTML.</p>
</body>
</html>
```

**Décomposition :**
- `<!DOCTYPE html>` → Déclare la version HTML5
- `<html>` → Racine du document
- `<head>` → Métadonnées (non visibles)
- `<body>` → Contenu visible
- `<h1>` → Titre principal
- `<p>` → Paragraphe

---

## 🎓 Points clés à retenir

✅ HTML = HyperText Markup Language
✅ HTML structure le contenu, CSS le stylise, JS le rend interactif
✅ HTML5 est la version moderne (2014-aujourd'hui)
✅ Tout document HTML commence par `<!DOCTYPE html>`
✅ Le HTML est universel et compris par tous les navigateurs

---

## 🚀 À vous de jouer !

Dans la prochaine leçon, nous allons décortiquer en détail la **structure de base d'une page HTML** et comprendre chaque élément essentiel.

> 💬 **Question de réflexion** : Pourquoi est-il important de bien structurer son HTML, même si CSS peut changer l'apparence visuelle ?
""",
            video_url="",  # Optionnel : URL YouTube explicative
            estimated_duration=15,
            points=10,
            is_published=True
        )
        self.stdout.write(f'  ✅ Leçon 1.1: {lesson_1_1.title}')

        # ==========================================
        # LESSON 1.2: Structure de base d'une page HTML
        # ==========================================
        lesson_1_2 = Lesson.objects.create(
            chapter=chapter,
            title="Structure de base d'une page HTML",
            slug="structure-base-page-html",
            lesson_type='THEORY',
            order_index=2,
            content="""# Structure de base d'une page HTML

## 🎯 Objectifs de cette leçon

À la fin de cette leçon, vous serez capable de :
- ✅ Comprendre chaque élément de la structure HTML
- ✅ Écrire une page HTML valide
- ✅ Utiliser les métadonnées essentielles
- ✅ Configurer correctement le charset et le viewport

---

## 🏗️ Anatomie complète d'une page HTML

Voici une page HTML5 complète et bien structurée :

```html
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="description" content="Description de ma page pour les moteurs de recherche">
    <meta name="author" content="Votre Nom">
    <title>Titre de la page - Mon Site</title>
    <link rel="stylesheet" href="style.css">
    <link rel="icon" href="favicon.ico">
</head>
<body>
    <h1>Contenu principal</h1>
    <p>Votre contenu ici...</p>
</body>
</html>
```

> 📊 **Illustration à voir** : Diagramme "Anatomie d'une page HTML"

---

## 1️⃣ La déclaration DOCTYPE

```html
<!DOCTYPE html>
```

### À quoi ça sert ?

✅ **Indique la version HTML** : HTML5 dans ce cas
✅ **Active le mode standard** du navigateur
✅ **Évite le "quirks mode"** (mode de compatibilité avec anciennes versions)

### Règles importantes :

⚠️ **Toujours en première ligne** du fichier
⚠️ **Insensible à la casse** : `<!doctype html>` fonctionne aussi
⚠️ **Obligatoire** pour un HTML valide

> 💡 **Histoire** : Avant HTML5, le DOCTYPE était très long. HTML5 l'a simplifié à `<!DOCTYPE html>`.

**Ancien DOCTYPE (HTML 4.01) :**
```html
<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN" "http://www.w3.org/TR/html4/loose.dtd">
```

**HTML5 (simple) :**
```html
<!DOCTYPE html>
```

---

## 2️⃣ La balise racine `<html>`

```html
<html lang="fr">
    <!-- Tout le contenu ici -->
</html>
```

### Attribut `lang` : Pourquoi est-il crucial ?

✅ **Accessibilité** : Les lecteurs d'écran savent quelle langue utiliser
✅ **SEO** : Les moteurs de recherche comprennent la langue du contenu
✅ **Traduction automatique** : Aide les navigateurs à proposer une traduction
✅ **Sélection de police** : Le navigateur choisit les bonnes polices

### Valeurs courantes :

| Code | Langue |
|------|--------|
| `fr` | Français |
| `en` | Anglais |
| `es` | Espagnol |
| `de` | Allemand |
| `it` | Italien |
| `pt` | Portugais |

### Multilangue :

```html
<html lang="fr">
<body>
    <p>Texte en français</p>
    <p lang="en">Text in English</p>
    <p lang="es">Texto en español</p>
</body>
</html>
```

---

## 3️⃣ La section `<head>` : Les métadonnées

La balise `<head>` contient des **informations sur la page**, mais **pas de contenu visible**.

### 📋 Métadonnées essentielles

#### A. Charset (encodage des caractères)

```html
<meta charset="UTF-8">
```

✅ **UTF-8** : Supporte tous les caractères (émojis, accents, alphabets non-latins)
✅ **Toujours en premier** dans le `<head>`
✅ **Évite les caractères bizarres** (é → Ã©)

> ⚠️ **Sans UTF-8** : "Hôtel" s'affiche "HÃ´tel"

#### B. Viewport (responsive design)

```html
<meta name="viewport" content="width=device-width, initial-scale=1.0">
```

✅ **Essentiel pour mobile** : Adapte la page à la taille de l'écran
✅ **width=device-width** : Largeur = largeur de l'appareil
✅ **initial-scale=1.0** : Zoom initial à 100%

**Sans viewport sur mobile :**
```
📱 [Page de bureau rétrécie] ← Illisible
```

**Avec viewport sur mobile :**
```
📱 [Page adaptée à l'écran] ← Parfait !
```

#### C. Description (SEO)

```html
<meta name="description" content="Apprenez le HTML facilement avec des exemples pratiques et des exercices interactifs.">
```

✅ **Affiché dans Google** sous le titre
✅ **Maximum 155-160 caractères**
✅ **Influence le taux de clic**

**Rendu dans Google :**
```
Mon Site - Apprendre le HTML
https://monsite.com
Apprenez le HTML facilement avec des exemples pratiques...
```

#### D. Autres métadonnées utiles

```html
<!-- Auteur -->
<meta name="author" content="Jean Dupont">

<!-- Mots-clés (moins important aujourd'hui) -->
<meta name="keywords" content="HTML, tutoriel, débutant, web">

<!-- Robots (indexation) -->
<meta name="robots" content="index, follow">

<!-- Open Graph (réseaux sociaux) -->
<meta property="og:title" content="Apprendre le HTML">
<meta property="og:description" content="Le meilleur tutoriel HTML">
<meta property="og:image" content="https://monsite.com/preview.jpg">

<!-- Twitter Card -->
<meta name="twitter:card" content="summary_large_image">
```

---

### 📄 Titre de la page

```html
<title>Apprendre le HTML - Chapitre 1 | Mon Site</title>
```

✅ **Affiché dans l'onglet** du navigateur
✅ **Titre dans les résultats Google**
✅ **Important pour le SEO**
✅ **50-60 caractères max** pour Google

**Structure recommandée :**
```
Page - Section | Nom du site
```

**Exemples :**
```html
<title>Accueil | MonSite.fr</title>
<title>Contact - Nous joindre | MonSite.fr</title>
<title>HTML Débutant - Chapitre 1 | FormationWeb</title>
```

---

### 🔗 Liens vers ressources externes

#### Feuille de style CSS

```html
<link rel="stylesheet" href="style.css">
<link rel="stylesheet" href="https://cdn.example.com/style.css">
```

#### Favicon (icône dans l'onglet)

```html
<link rel="icon" href="favicon.ico" type="image/x-icon">
<link rel="icon" href="favicon.png" type="image/png">
```

#### Polices web

```html
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Roboto&display=swap" rel="stylesheet">
```

---

## 4️⃣ La section `<body>` : Le contenu visible

Tout ce qui apparaît dans la fenêtre du navigateur va dans `<body>` :

```html
<body>
    <header>
        <h1>Mon Site Web</h1>
        <nav>
            <a href="/">Accueil</a>
            <a href="/about">À propos</a>
        </nav>
    </header>

    <main>
        <article>
            <h2>Article principal</h2>
            <p>Contenu de l'article...</p>
        </article>
    </main>

    <footer>
        <p>&copy; 2024 Mon Site</p>
    </footer>
</body>
```

---

## 📐 Indentation et lisibilité

### ✅ Bon code (indenté)

```html
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <title>Ma Page</title>
</head>
<body>
    <h1>Titre</h1>
    <p>Paragraphe</p>
</body>
</html>
```

### ❌ Mauvais code (non indenté)

```html
<!DOCTYPE html>
<html lang="fr">
<head>
<meta charset="UTF-8">
<title>Ma Page</title>
</head>
<body>
<h1>Titre</h1>
<p>Paragraphe</p>
</body>
</html>
```

> 💡 **Règle d'or** : Chaque niveau d'imbrication = une indentation (2 ou 4 espaces)

---

## ✅ Template complet de démarrage

Voici un template HTML5 complet que vous pouvez réutiliser :

```html
<!DOCTYPE html>
<html lang="fr">
<head>
    <!-- Encodage et compatibilité -->
    <meta charset="UTF-8">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">

    <!-- SEO -->
    <meta name="description" content="Description de la page (max 160 caractères)">
    <meta name="keywords" content="mot-clé1, mot-clé2, mot-clé3">
    <meta name="author" content="Votre Nom">

    <!-- Titre -->
    <title>Titre de la page | Nom du site</title>

    <!-- Favicon -->
    <link rel="icon" href="favicon.ico">

    <!-- Feuilles de style -->
    <link rel="stylesheet" href="css/style.css">
</head>
<body>

    <!-- Votre contenu ici -->

</body>
</html>
```

---

## 🎓 Points clés à retenir

✅ `<!DOCTYPE html>` → Toujours en première ligne
✅ `<html lang="fr">` → Définir la langue
✅ `<meta charset="UTF-8">` → Supporte tous les caractères
✅ `<meta name="viewport">` → Essentiel pour mobile
✅ `<title>` → Important pour SEO et UX
✅ `<head>` → Métadonnées (invisible)
✅ `<body>` → Contenu visible
✅ Indentation → Lisibilité du code

---

## 🚀 Prochaine étape

Maintenant que vous connaissez la structure, passons à la pratique avec votre **premier exercice** ! 💪
""",
            video_url="",
            estimated_duration=20,
            points=10,
            is_published=True
        )
        self.stdout.write(f'  ✅ Leçon 1.2: {lesson_1_2.title}')

        # ==========================================
        # EXERCISE 1.1: Créer sa première page HTML
        # ==========================================
        lesson_1_3 = Lesson.objects.create(
            chapter=chapter,
            title="Exercice : Ma première page HTML",
            slug="exercice-premiere-page-html",
            lesson_type='EXERCISE',
            order_index=3,
            content="",
            estimated_duration=15,
            points=25,
            is_published=True
        )
        self.stdout.write(f'  ✅ Leçon 1.3: {lesson_1_3.title}')

        Exercise.objects.create(
            lesson=lesson_1_3,
            instructions="""# 🎯 Exercice : Ma première page HTML

## Objectif

Créer une page HTML5 complète et valide avec tous les éléments essentiels que nous venons d'apprendre.

---

## 📋 Instructions détaillées

Créez une page HTML qui présente **votre profil personnel** avec les éléments suivants :

### 1. Structure de base ✅

- [ ] DOCTYPE HTML5
- [ ] Balise `<html>` avec attribut `lang="fr"`
- [ ] Section `<head>` complète
- [ ] Section `<body>` avec contenu

### 2. Métadonnées dans `<head>` ✅

- [ ] Meta charset UTF-8
- [ ] Meta viewport pour responsive
- [ ] Meta description (décrivez votre profil en max 160 caractères)
- [ ] Meta author (votre nom)
- [ ] Titre de page : "Profil de [Votre Nom] | Portfolio"

### 3. Contenu dans `<body>` ✅

- [ ] Un titre h1 avec votre nom
- [ ] Un paragraphe de présentation (minimum 2 phrases)
- [ ] Un deuxième paragraphe sur vos passions ou objectifs

---

## 💡 Conseils

- Utilisez le template de la leçon précédente comme point de départ
- Respectez l'indentation (2 ou 4 espaces par niveau)
- Fermez toutes les balises
- Pensez à l'accessibilité (lang, meta viewport)

---

## ✅ Critères de validation

Votre code sera testé automatiquement sur :

1. ✅ Présence du DOCTYPE HTML5
2. ✅ Attribut `lang="fr"` sur la balise html
3. ✅ Meta charset UTF-8 présent
4. ✅ Meta viewport présent
5. ✅ Balise `<title>` avec contenu
6. ✅ Balise `<h1>` présente dans le body
7. ✅ Au moins 2 balises `<p>` (paragraphes)
8. ✅ Code correctement indenté

---

## 🎁 Exemple de résultat attendu

```
[Page web affichée]
┌─────────────────────────────────┐
│ Profil de Jean Dupont | Portfolio │ ← Titre de l'onglet
├─────────────────────────────────┤
│                                 │
│  Jean Dupont                    │ ← h1
│                                 │
│  Bonjour ! Je suis développeur  │
│  web passionné par...           │ ← Paragraphe 1
│                                 │
│  J'aime créer des sites...      │ ← Paragraphe 2
│                                 │
└─────────────────────────────────┘
```

---

## 🚀 Prêt ? C'est parti !

Écrivez votre code dans l'éditeur ci-dessous et cliquez sur "Valider" pour tester ! 💪
""",
            starter_code="""<!DOCTYPE html>
<html lang="fr">
<head>
    <!-- Ajoutez vos métadonnées ici -->

</head>
<body>
    <!-- Ajoutez votre contenu ici -->

</body>
</html>
""",
            solution="""<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="description" content="Portfolio personnel de Jean Dupont, développeur web passionné">
    <meta name="author" content="Jean Dupont">
    <title>Profil de Jean Dupont | Portfolio</title>
</head>
<body>
    <h1>Jean Dupont</h1>
    <p>Bonjour ! Je suis développeur web passionné par la création de sites internet modernes et accessibles.</p>
    <p>J'aime apprendre de nouvelles technologies et partager mes connaissances avec la communauté.</p>
</body>
</html>
""",
            tests={
                "tests": [
                    {
                        "name": "DOCTYPE HTML5 présent",
                        "code": "assert '<!DOCTYPE html>' in solution or '<!doctype html>' in solution",
                        "points": 3,
                        "error_message": "N'oubliez pas d'ajouter <!DOCTYPE html> en première ligne"
                    },
                    {
                        "name": "Attribut lang='fr' sur <html>",
                        "code": "assert 'lang=\"fr\"' in solution or \"lang='fr'\" in solution",
                        "points": 3,
                        "error_message": "Ajoutez l'attribut lang='fr' à la balise <html>"
                    },
                    {
                        "name": "Meta charset UTF-8",
                        "code": "assert 'charset=\"UTF-8\"' in solution or \"charset='UTF-8'\" in solution",
                        "points": 3,
                        "error_message": "Ajoutez <meta charset='UTF-8'> dans le <head>"
                    },
                    {
                        "name": "Meta viewport présent",
                        "code": "assert 'name=\"viewport\"' in solution or \"name='viewport'\" in solution",
                        "points": 3,
                        "error_message": "Ajoutez la balise <meta name='viewport'> pour le responsive"
                    },
                    {
                        "name": "Meta description présent",
                        "code": "assert 'name=\"description\"' in solution or \"name='description'\" in solution",
                        "points": 2,
                        "error_message": "Ajoutez une meta description pour le SEO"
                    },
                    {
                        "name": "Meta author présent",
                        "code": "assert 'name=\"author\"' in solution or \"name='author'\" in solution",
                        "points": 2,
                        "error_message": "Ajoutez une meta author avec votre nom"
                    },
                    {
                        "name": "Balise <title> avec contenu",
                        "code": "assert '<title>' in solution and '</title>' in solution and solution.find('<title>') < solution.find('</title>')",
                        "points": 3,
                        "error_message": "Ajoutez un titre à votre page avec la balise <title>"
                    },
                    {
                        "name": "Balise <h1> présente",
                        "code": "assert '<h1>' in solution and '</h1>' in solution",
                        "points": 3,
                        "error_message": "Ajoutez un titre principal avec <h1>"
                    },
                    {
                        "name": "Au moins 2 paragraphes <p>",
                        "code": "assert solution.count('<p>') >= 2 and solution.count('</p>') >= 2",
                        "points": 3,
                        "error_message": "Ajoutez au moins 2 paragraphes avec la balise <p>"
                    }
                ]
            },
            difficulty='EASY',
            max_attempts=5,
            time_limit=900,  # 15 minutes
            hints=[
                "💡 Astuce 1 : Commencez par la structure de base vue dans la leçon (<!DOCTYPE html>, <html>, <head>, <body>)",
                "💡 Astuce 2 : Les métadonnées vont dans <head>, le contenu visible va dans <body>",
                "💡 Astuce 3 : Pour la meta viewport, copiez exactement : <meta name='viewport' content='width=device-width, initial-scale=1.0'>"
            ]
        )
        self.stdout.write(f'    ✅ Exercice créé pour : {lesson_1_3.title}')

        # ==========================================
        # EXERCISE 1.2: Structure complète avec SEO
        # ==========================================
        lesson_1_4 = Lesson.objects.create(
            chapter=chapter,
            title="Exercice : Page optimisée SEO",
            slug="exercice-page-seo",
            lesson_type='EXERCISE',
            order_index=4,
            content="",
            estimated_duration=10,
            points=15,
            is_published=True
        )
        self.stdout.write(f'  ✅ Leçon 1.4: {lesson_1_4.title}')

        Exercise.objects.create(
            lesson=lesson_1_4,
            instructions="""# 🎯 Exercice : Page optimisée pour le SEO

## Objectif

Enrichir votre page HTML avec des métadonnées avancées pour améliorer le référencement (SEO) et le partage sur les réseaux sociaux.

---

## 📋 Instructions

Reprenez votre page HTML précédente et ajoutez les éléments suivants :

### 1. Métadonnées SEO ✅

- [ ] Meta keywords (5 mots-clés pertinents)
- [ ] Favicon (lien vers favicon.ico)
- [ ] Lien vers feuille de style externe (style.css)

### 2. Open Graph (réseaux sociaux) ✅

Ajoutez les balises Open Graph pour un beau rendu sur Facebook, LinkedIn, etc. :

- [ ] og:title (titre pour les réseaux sociaux)
- [ ] og:description (description pour les réseaux sociaux)
- [ ] og:image (URL d'une image preview)
- [ ] og:url (URL de la page)

---

## 💡 Exemple de balises Open Graph

```html
<meta property="og:title" content="Profil de Jean Dupont">
<meta property="og:description" content="Développeur web passionné">
<meta property="og:image" content="https://monsite.com/photo.jpg">
<meta property="og:url" content="https://monsite.com">
```

---

## ✅ Critères de validation

1. ✅ Meta keywords présent avec au moins 3 mots-clés
2. ✅ Lien vers favicon.ico
3. ✅ Lien vers feuille de style CSS
4. ✅ Au moins 3 balises Open Graph (og:title, og:description, og:image)
5. ✅ Code bien structuré et indenté

---

## 🎁 Résultat attendu

Quand quelqu'un partage votre page sur Facebook ou LinkedIn, une belle carte s'affiche avec :
- Votre titre
- Votre description
- Votre image

📊 **Illustration** : Voir exemple de rendu Open Graph

---

## 🚀 À vous de jouer !
""",
            starter_code="""<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="description" content="Portfolio personnel">
    <meta name="author" content="Votre Nom">

    <!-- Ajoutez les métadonnées SEO et Open Graph ici -->

    <title>Profil | Portfolio</title>
</head>
<body>
    <h1>Mon Profil</h1>
    <p>Contenu de présentation.</p>
</body>
</html>
""",
            solution="""<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="description" content="Portfolio personnel de Jean Dupont, développeur web">
    <meta name="author" content="Jean Dupont">
    <meta name="keywords" content="développeur web, HTML, CSS, JavaScript, portfolio, frontend">

    <!-- Open Graph -->
    <meta property="og:title" content="Profil de Jean Dupont | Développeur Web">
    <meta property="og:description" content="Portfolio et projets de Jean Dupont, développeur web passionné">
    <meta property="og:image" content="https://monsite.com/images/preview.jpg">
    <meta property="og:url" content="https://monsite.com">

    <title>Profil de Jean Dupont | Portfolio</title>

    <!-- Ressources -->
    <link rel="icon" href="favicon.ico">
    <link rel="stylesheet" href="style.css">
</head>
<body>
    <h1>Jean Dupont</h1>
    <p>Développeur web passionné par la création de sites modernes et accessibles.</p>
</body>
</html>
""",
            tests={
                "tests": [
                    {
                        "name": "Meta keywords présent",
                        "code": "assert 'name=\"keywords\"' in solution or \"name='keywords'\" in solution",
                        "points": 3,
                        "error_message": "Ajoutez une balise meta keywords"
                    },
                    {
                        "name": "Lien vers favicon",
                        "code": "assert 'favicon' in solution.lower() and 'rel=\"icon\"' in solution or \"rel='icon'\" in solution",
                        "points": 3,
                        "error_message": "Ajoutez un lien vers le favicon"
                    },
                    {
                        "name": "Lien vers feuille de style",
                        "code": "assert 'stylesheet' in solution and '.css' in solution",
                        "points": 3,
                        "error_message": "Ajoutez un lien vers une feuille de style CSS"
                    },
                    {
                        "name": "Open Graph title",
                        "code": "assert 'og:title' in solution",
                        "points": 2,
                        "error_message": "Ajoutez la balise Open Graph og:title"
                    },
                    {
                        "name": "Open Graph description",
                        "code": "assert 'og:description' in solution",
                        "points": 2,
                        "error_message": "Ajoutez la balise Open Graph og:description"
                    },
                    {
                        "name": "Open Graph image",
                        "code": "assert 'og:image' in solution",
                        "points": 2,
                        "error_message": "Ajoutez la balise Open Graph og:image"
                    }
                ]
            },
            difficulty='EASY',
            max_attempts=5,
            time_limit=600,  # 10 minutes
            hints=[
                "💡 Les balises Open Graph utilisent property= au lieu de name=",
                "💡 Le favicon est un fichier .ico placé à la racine du site",
                "💡 Pour les keywords, séparez les mots par des virgules"
            ]
        )
        self.stdout.write(f'    ✅ Exercice créé pour : {lesson_1_4.title}')

        # ==========================================
        # QUIZ 1: Validation Structure HTML
        # ==========================================
        lesson_1_5 = Lesson.objects.create(
            chapter=chapter,
            title="Quiz : Structure HTML",
            slug="quiz-structure-html",
            lesson_type='QUIZ',
            order_index=5,
            content="",
            estimated_duration=10,
            points=20,
            is_published=True
        )
        self.stdout.write(f'  ✅ Leçon 1.5: {lesson_1_5.title}')

        Quiz.objects.create(
            lesson=lesson_1_5,
            instructions="""# 📝 Quiz : Validez vos connaissances sur la structure HTML

Testez votre compréhension de la structure HTML de base.

**Durée** : 10 minutes
**Score minimal** : 70%
**Tentatives** : 3 maximum

Bonne chance ! 🍀
""",
            questions={
                "questions": [
                    {
                        "id": 1,
                        "question": "Que signifie l'acronyme HTML ?",
                        "type": "multiple_choice",
                        "options": [
                            {"id": "a", "text": "HyperText Markup Language"},
                            {"id": "b", "text": "High Tech Modern Language"},
                            {"id": "c", "text": "Home Tool Markup Language"},
                            {"id": "d", "text": "Hyperlinks and Text Markup Language"}
                        ],
                        "correct_answer": "a",
                        "points": 2,
                        "explanation": "HTML signifie HyperText Markup Language, le langage de balisage pour structurer les pages web."
                    },
                    {
                        "id": 2,
                        "question": "Quelle balise contient les métadonnées de la page (charset, viewport, title) ?",
                        "type": "multiple_choice",
                        "options": [
                            {"id": "a", "text": "<body>"},
                            {"id": "b", "text": "<head>"},
                            {"id": "c", "text": "<meta>"},
                            {"id": "d", "text": "<html>"}
                        ],
                        "correct_answer": "b",
                        "points": 2,
                        "explanation": "La balise <head> contient toutes les métadonnées (informations sur la page, non visibles)."
                    },
                    {
                        "id": 3,
                        "question": "Quel DOCTYPE utiliser pour une page HTML5 ?",
                        "type": "multiple_choice",
                        "options": [
                            {"id": "a", "text": "<!DOCTYPE HTML5>"},
                            {"id": "b", "text": "<!DOCTYPE html>"},
                            {"id": "c", "text": "<html version='5'>"},
                            {"id": "d", "text": "<!HTML5>"}
                        ],
                        "correct_answer": "b",
                        "points": 3,
                        "explanation": "HTML5 a simplifié le DOCTYPE à <!DOCTYPE html>, toujours en première ligne."
                    },
                    {
                        "id": 4,
                        "question": "Pourquoi utiliser l'attribut lang='fr' sur la balise <html> ?",
                        "type": "multiple_choice",
                        "options": [
                            {"id": "a", "text": "Pour traduire automatiquement la page"},
                            {"id": "b", "text": "Pour aider les lecteurs d'écran et le SEO"},
                            {"id": "c", "text": "Pour changer la police de caractères"},
                            {"id": "d", "text": "C'est obligatoire sinon la page ne s'affiche pas"}
                        ],
                        "correct_answer": "b",
                        "points": 3,
                        "explanation": "L'attribut lang aide les lecteurs d'écran, les moteurs de recherche, et améliore l'accessibilité."
                    },
                    {
                        "id": 5,
                        "question": "Quelle balise définit le titre affiché dans l'onglet du navigateur ?",
                        "type": "multiple_choice",
                        "options": [
                            {"id": "a", "text": "<h1>"},
                            {"id": "b", "text": "<title>"},
                            {"id": "c", "text": "<header>"},
                            {"id": "d", "text": "<name>"}
                        ],
                        "correct_answer": "b",
                        "points": 2,
                        "explanation": "La balise <title> dans le <head> définit le titre de l'onglet et des résultats Google."
                    },
                    {
                        "id": 6,
                        "question": "Quel encodage de caractères est recommandé pour supporter les émojis et accents ?",
                        "type": "multiple_choice",
                        "options": [
                            {"id": "a", "text": "ASCII"},
                            {"id": "b", "text": "ISO-8859-1"},
                            {"id": "c", "text": "UTF-8"},
                            {"id": "d", "text": "Windows-1252"}
                        ],
                        "correct_answer": "c",
                        "points": 3,
                        "explanation": "UTF-8 est l'encodage universel qui supporte tous les caractères (émojis, alphabets, accents)."
                    },
                    {
                        "id": 7,
                        "question": "Quelle balise meta est essentielle pour le responsive design sur mobile ?",
                        "type": "multiple_choice",
                        "options": [
                            {"id": "a", "text": "<meta name='mobile'>"},
                            {"id": "b", "text": "<meta name='responsive'>"},
                            {"id": "c", "text": "<meta name='viewport'>"},
                            {"id": "d", "text": "<meta name='device'>"}
                        ],
                        "correct_answer": "c",
                        "points": 3,
                        "explanation": "La meta viewport adapte la page à la largeur de l'écran sur mobile."
                    },
                    {
                        "id": 8,
                        "question": "Dans le trio HTML/CSS/JavaScript, quel est le rôle du HTML ?",
                        "type": "multiple_choice",
                        "options": [
                            {"id": "a", "text": "La structure et le contenu"},
                            {"id": "b", "text": "La présentation et le style"},
                            {"id": "c", "text": "Le comportement et l'interactivité"},
                            {"id": "d", "text": "La base de données"}
                        ],
                        "correct_answer": "a",
                        "points": 2,
                        "explanation": "HTML = Structure, CSS = Présentation, JavaScript = Comportement."
                    }
                ]
            },
            passing_score=70,
            time_limit=600,  # 10 minutes
            max_attempts=3,
            randomize_questions=False,
            randomize_options=True
        )
        self.stdout.write(f'    ✅ Quiz créé pour : {lesson_1_5.title}')

        # ==========================================
        # Compléments et illustrations
        # ==========================================
        # ⚠️ L'ordre compte : `section1_html_quiz` doit passer **avant**
        # `section1_html_extra`, qui réordonne les leçons du chapitre et attend
        # que le quiz final existe déjà. C'est la contrainte qui faisait échouer
        # l'ancien `expand_section_1_html.py` quand on le lançait en premier.
        pipeline.finish(
            self, chapter,
            steps=[section1_html_quiz.build, section1_html_extra.build],
            verbosity=options.get('verbosity', 1),
        )

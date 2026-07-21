"""
Étoffe le chapitre 1 (Introduction au HTML) avec 6 nouvelles leçons
théoriques (une par famille de balises) suivies chacune d'un petit exercice
de mise en pratique immédiate, pensées pour un public débutant.

Réordonne les leçons existantes (2 gros exercices + quiz) à la fin du
chapitre pour qu'elles arrivent après avoir vu tout le vocabulaire testé
par le quiz.

Usage: python manage.py shell < expand_section_1_html.py
   ou: docker-compose exec backend python expand_section_1_html.py
"""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
django.setup()

from apps.courses.models import Chapter, Lesson, Exercise


def upsert_theory(chapter, slug, title, order_index, content, duration, points):
    lesson, created = Lesson.objects.update_or_create(
        slug=slug,
        defaults={
            'chapter': chapter,
            'title': title,
            'lesson_type': 'THEORY',
            'order_index': order_index,
            'content': content,
            'video_url': '',
            'estimated_duration': duration,
            'points': points,
            'is_published': True,
        }
    )
    print(f"  {'✅ créée' if created else '♻️  mise à jour'} : {lesson.title}")
    return lesson


def upsert_mini_exercise(chapter, slug, title, order_index, instructions,
                          starter_code, solution, tests, hints, duration=10, points=10):
    lesson, created = Lesson.objects.update_or_create(
        slug=slug,
        defaults={
            'chapter': chapter,
            'title': title,
            'lesson_type': 'EXERCISE',
            'order_index': order_index,
            'content': '',
            'estimated_duration': duration,
            'points': points,
            'is_published': True,
        }
    )
    Exercise.objects.update_or_create(
        lesson=lesson,
        defaults={
            'instructions': instructions,
            'starter_code': starter_code,
            'solution': solution,
            'tests': {'tests': tests},
            'difficulty': 'EASY',
            'max_attempts': 0,
            'time_limit': 600,
            'hints': hints,
        }
    )
    print(f"  {'✅ créée' if created else '♻️  mise à jour'} : {lesson.title}")
    return lesson


chapter = Chapter.objects.get(slug='introduction-html')
print(f"Chapitre : {chapter.title}\n")

# ==========================================================================
# 1. LE TEXTE : TITRES, PARAGRAPHES ET MISE EN FORME
# ==========================================================================

upsert_theory(
    chapter, 'html-texte-titres-paragraphes', 'Le texte : titres, paragraphes et mise en forme', 3,
    """# Le texte : titres, paragraphes et mise en forme

## 🎯 Objectifs de cette leçon

À la fin de cette leçon, vous serez capable de :
- ✅ Structurer un texte avec les titres `<h1>` à `<h6>`
- ✅ Créer des paragraphes avec `<p>`
- ✅ Mettre en valeur du texte important avec `<strong>` et `<em>`
- ✅ Comprendre pourquoi l'ordre des titres compte

---

## 👶 Pourquoi commencer par le texte ?

La quasi-totalité d'une page web, c'est du texte : un titre, une explication, une liste, un bouton...
Avant de construire des mises en page complexes, il faut savoir structurer du texte simple. C'est la
brique de base de tout le reste.

> 💡 **Analogie** : Écrire en HTML, c'est comme rédiger un document Word en indiquant à chaque phrase
> son rôle ("ceci est un titre", "ceci est un paragraphe") plutôt que juste sa taille de police.

---

## 1️⃣ Les titres : `<h1>` à `<h6>`

```html
<h1>Titre principal de la page</h1>
<h2>Un grand titre de section</h2>
<h3>Un sous-titre</h3>
<h4>Un sous-sous-titre</h4>
<h5>Encore plus petit</h5>
<h6>Le plus petit niveau</h6>
```

### Règles importantes

⚠️ **Un seul `<h1>` par page**, en général : c'est LE titre principal (comme le titre d'un livre).
⚠️ **Respectez l'ordre hiérarchique** : `<h1>` → `<h2>` → `<h3>`, sans sauter de niveau juste pour la taille.
✅ Les niveaux servent à **structurer le sens**, pas à choisir une taille de police (ça, c'est le rôle de CSS).

> 🚫 **Mauvaise pratique** : utiliser `<h3>` juste parce qu'un `<h1>` est "trop gros" visuellement.
> La bonne solution est d'utiliser `<h1>` puis de le restyliser en CSS plus tard.

### Pourquoi c'est important ?

- 🦯 **Accessibilité** : les lecteurs d'écran permettent de naviguer de titre en titre. Une hiérarchie
  cassée rend la page confuse pour les personnes malvoyantes.
- 🔍 **SEO** : Google utilise les titres pour comprendre la structure et l'importance du contenu.

---

## 2️⃣ Les paragraphes : `<p>`

```html
<p>Ceci est un premier paragraphe. Il peut contenir plusieurs phrases.</p>
<p>Ceci est un deuxième paragraphe, bien séparé du premier.</p>
```

✅ Chaque `<p>` crée automatiquement un espace avant/après (géré par le navigateur par défaut).
✅ Un paragraphe peut contenir plusieurs phrases, mais pas d'autres balises de bloc (`<h1>`, `<div>`...).

---

## 3️⃣ Sauts de ligne et séparateurs

### `<br>` : retour à la ligne

```html
<p>
  123 rue de la Paix<br>
  75000 Paris<br>
  France
</p>
```

⚠️ `<br>` sert à des sauts de ligne **ponctuels** (adresse, poème). Ne l'utilisez pas pour espacer des
paragraphes : c'est le rôle de `<p>` !

### `<hr>` : séparateur horizontal

```html
<p>Section 1</p>
<hr>
<p>Section 2</p>
```

Trace une ligne horizontale pour marquer un changement de sujet.

---

## 4️⃣ Mettre du texte en valeur : `<strong>` et `<em>`

```html
<p>Ce produit est <strong>en rupture de stock</strong>.</p>
<p>C'est <em>vraiment</em> important de tester son code.</p>
```

| Balise | Rendu visuel | Sens |
|--------|--------------|------|
| `<strong>` | **Gras** | Importance forte (le lecteur d'écran insiste dessus) |
| `<em>` | *Italique* | Emphase, insistance |
| `<b>` | **Gras** | Gras "décoratif", sans signification particulière |
| `<i>` | *Italique* | Italique "décoratif", sans signification particulière |

> 💡 **Bonne pratique** : privilégiez `<strong>`/`<em>` (sémantiques) à `<b>`/`<i>` (purement visuels).
> Le rendu est identique, mais `<strong>` et `<em>` donnent du sens à votre contenu — un lecteur
> d'écran les annonce différemment, ce qui aide l'accessibilité.

---

## ✅ Exemple complet

```html
<h1>Mon carnet de voyage</h1>

<h2>Jour 1 : Arrivée</h2>
<p>Nous sommes arrivés à <strong>Lisbonne</strong> après un vol de 2h30.</p>
<p>Le temps était <em>magnifique</em>, parfait pour se promener.</p>

<hr>

<h2>Jour 2 : Exploration</h2>
<p>
  Adresse de l'hôtel :<br>
  Rua Augusta 100<br>
  Lisbonne, Portugal
</p>
```

---

## 🎓 Points clés à retenir

✅ `<h1>` à `<h6>` structurent le texte par ordre d'importance, sans saut de niveau
✅ `<p>` pour chaque paragraphe de texte
✅ `<br>` pour un saut de ligne ponctuel, pas pour espacer des blocs
✅ `<strong>` et `<em>` sont sémantiques, à préférer à `<b>` et `<i>`

---

## 🚀 À vous de jouer !

Passez à l'exercice pour mettre tout de suite ces balises en pratique sur un petit texte.
""",
    12, 10,
)

upsert_mini_exercise(
    chapter, 'exercice-texte-titres-paragraphes', 'Exercice rapide : titres et paragraphes', 4,
    """# 🎯 Exercice rapide : titres et paragraphes

## Objectif

Rédiger une courte présentation personnelle en utilisant titres, paragraphes et mise en forme.

---

## 📋 Instructions

Complétez le code avec :

- [ ] Un titre principal `<h1>` avec votre prénom (ou un prénom inventé)
- [ ] Un sous-titre `<h2>` "À propos de moi"
- [ ] Au moins **2 paragraphes** `<p>` de présentation
- [ ] Au moins un mot important en `<strong>`
- [ ] Au moins un mot en emphase avec `<em>`

---

## ✅ Critères de validation

1. ✅ Un `<h1>` présent
2. ✅ Un `<h2>` présent
3. ✅ Au moins 2 `<p>`
4. ✅ Au moins un `<strong>`
5. ✅ Au moins un `<em>`

---

## 🚀 C'est parti !
""",
    """<!-- Ajoutez votre h1 ici -->

<!-- Ajoutez votre h2 "À propos de moi" ici -->

<!-- Ajoutez au moins 2 paragraphes, avec un mot en <strong> et un mot en <em> -->
""",
    """<h1>Alex</h1>

<h2>À propos de moi</h2>

<p>Je m'appelle Alex et je suis <strong>passionné</strong> de développement web depuis peu.</p>
<p>J'apprends le HTML et c'est <em>vraiment</em> plus simple que je ne le pensais !</p>
""",
    [
        {"name": "Titre h1 présent", "code": "assert '<h1>' in solution and '</h1>' in solution", "points": 2, "error_message": "Ajoutez un titre principal avec <h1>"},
        {"name": "Sous-titre h2 présent", "code": "assert '<h2>' in solution and '</h2>' in solution", "points": 2, "error_message": "Ajoutez un sous-titre avec <h2>"},
        {"name": "Au moins 2 paragraphes", "code": "assert solution.count('<p>') >= 2", "points": 3, "error_message": "Ajoutez au moins 2 paragraphes avec <p>"},
        {"name": "Un mot en <strong>", "code": "assert '<strong>' in solution and '</strong>' in solution", "points": 2, "error_message": "Mettez un mot important en valeur avec <strong>"},
        {"name": "Un mot en <em>", "code": "assert '<em>' in solution and '</em>' in solution", "points": 1, "error_message": "Ajoutez une emphase avec <em>"},
    ],
    [
        "💡 Astuce 1 : <h1>Votre prénom</h1> pour commencer",
        "💡 Astuce 2 : N'oubliez pas les balises fermantes </p>, </strong>, </em>",
    ],
)

# ==========================================================================
# 2. LES LISTES
# ==========================================================================

upsert_theory(
    chapter, 'html-les-listes', 'Les listes', 5,
    """# Les listes

## 🎯 Objectifs de cette leçon

À la fin de cette leçon, vous serez capable de :
- ✅ Créer une liste à puces avec `<ul>`
- ✅ Créer une liste numérotée avec `<ol>`
- ✅ Choisir la bonne liste selon le contexte
- ✅ Imbriquer des listes les unes dans les autres

---

## 🛒 Pourquoi des listes ?

Dès que vous énumérez plusieurs éléments (ingrédients d'une recette, étapes d'un tutoriel, liens de
menu...), une liste est plus adaptée qu'une suite de paragraphes.

> 💡 **Analogie** : Une liste de courses griffonnée sur un post-it, c'est une `<ul>` (l'ordre n'a pas
> d'importance). Une recette de cuisine avec des étapes à suivre dans l'ordre, c'est une `<ol>`.

---

## 1️⃣ Liste non ordonnée : `<ul>`

```html
<ul>
    <li>Pommes</li>
    <li>Lait</li>
    <li>Pain</li>
</ul>
```

**Rendu :**
```
• Pommes
• Lait
• Pain
```

✅ `<ul>` = *Unordered List* (liste non ordonnée)
✅ Chaque élément est un `<li>` (*List Item*)
✅ L'ordre des éléments n'a pas d'importance

---

## 2️⃣ Liste ordonnée : `<ol>`

```html
<ol>
    <li>Préchauffer le four à 180°C</li>
    <li>Mélanger la farine et le sucre</li>
    <li>Enfourner 25 minutes</li>
</ol>
```

**Rendu :**
```
1. Préchauffer le four à 180°C
2. Mélanger la farine et le sucre
3. Enfourner 25 minutes
```

✅ `<ol>` = *Ordered List* (liste ordonnée)
✅ Le navigateur numérote automatiquement — si vous ajoutez un élément au milieu, la numérotation
  se met à jour toute seule !

---

## 3️⃣ Imbriquer des listes

Une liste peut contenir une autre liste, pour représenter une hiérarchie :

```html
<ul>
    <li>Frontend
        <ul>
            <li>HTML</li>
            <li>CSS</li>
            <li>JavaScript</li>
        </ul>
    </li>
    <li>Backend
        <ul>
            <li>Django</li>
            <li>PostgreSQL</li>
        </ul>
    </li>
</ul>
```

> ⚠️ **Piège fréquent** : la liste imbriquée doit être placée **à l'intérieur** du `<li>` parent,
> avant sa balise fermante `</li>`.

---

## 🆚 `<ul>` vs `<ol>` : comment choisir ?

| Situation | Bonne balise |
|-----------|--------------|
| Liste de courses | `<ul>` (l'ordre importe peu) |
| Étapes d'une recette | `<ol>` (l'ordre est essentiel) |
| Liens de navigation | `<ul>` |
| Classement d'un podium | `<ol>` |
| Ingrédients | `<ul>` |

---

## 🎓 Points clés à retenir

✅ `<ul>` pour une liste sans ordre, `<ol>` pour une liste où l'ordre compte
✅ Chaque élément d'une liste est un `<li>`
✅ Les listes peuvent s'imbriquer pour représenter une hiérarchie
✅ Le navigateur gère automatiquement la numérotation des `<ol>`

---

## 🚀 À vous de jouer !
""",
    10, 10,
)

upsert_mini_exercise(
    chapter, 'exercice-les-listes', 'Exercice rapide : les listes', 6,
    """# 🎯 Exercice rapide : les listes

## Objectif

Créer une liste non ordonnée et une liste ordonnée.

---

## 📋 Instructions

- [ ] Une liste `<ul>` avec **au moins 3** ingrédients (ou objets de votre choix)
- [ ] Une liste `<ol>` avec **au moins 3** étapes d'une recette ou d'un tutoriel

---

## ✅ Critères de validation

1. ✅ Une balise `<ul>` présente
2. ✅ Au moins 3 `<li>` à l'intérieur de la liste (au total)
3. ✅ Une balise `<ol>` présente
4. ✅ Au moins 6 `<li>` au total (3 pour chaque liste)

---

## 🚀 C'est parti !
""",
    """<h2>Ingrédients</h2>
<!-- Ajoutez votre <ul> avec au moins 3 <li> -->

<h2>Étapes</h2>
<!-- Ajoutez votre <ol> avec au moins 3 <li> -->
""",
    """<h2>Ingrédients</h2>
<ul>
    <li>Farine</li>
    <li>Sucre</li>
    <li>Œufs</li>
</ul>

<h2>Étapes</h2>
<ol>
    <li>Mélanger les ingrédients secs</li>
    <li>Ajouter les œufs</li>
    <li>Enfourner 20 minutes</li>
</ol>
""",
    [
        {"name": "Liste <ul> présente", "code": "assert '<ul>' in solution and '</ul>' in solution", "points": 3, "error_message": "Ajoutez une liste non ordonnée avec <ul>"},
        {"name": "Liste <ol> présente", "code": "assert '<ol>' in solution and '</ol>' in solution", "points": 3, "error_message": "Ajoutez une liste ordonnée avec <ol>"},
        {"name": "Au moins 6 éléments <li> au total", "code": "assert solution.count('<li>') >= 6", "points": 4, "error_message": "Ajoutez au moins 3 <li> dans chaque liste (6 au total)"},
    ],
    [
        "💡 Astuce 1 : chaque élément d'une liste s'écrit <li>texte</li>",
        "💡 Astuce 2 : n'oubliez pas de refermer </ul> et </ol>",
    ],
)

# ==========================================================================
# 3. LES LIENS ET LES IMAGES
# ==========================================================================

upsert_theory(
    chapter, 'html-liens-et-images', 'Les liens et les images', 7,
    """# Les liens et les images

## 🎯 Objectifs de cette leçon

À la fin de cette leçon, vous serez capable de :
- ✅ Créer un lien hypertexte avec `<a>`
- ✅ Ouvrir un lien dans un nouvel onglet en toute sécurité
- ✅ Insérer une image avec `<img>`
- ✅ Comprendre pourquoi l'attribut `alt` est indispensable

---

## 🔗 Les liens : `<a>`

Le "Hyper" de HyperText vient de là : la capacité à relier des documents entre eux.

```html
<a href="https://www.wikipedia.org">Visiter Wikipédia</a>
```

- `<a>` = *anchor* (ancre)
- `href` = *Hypertext REFerence*, l'URL de destination

### Liens internes vs externes

```html
<!-- Lien externe : URL complète -->
<a href="https://www.mozilla.org">Site de Mozilla</a>

<!-- Lien interne : chemin relatif vers une autre page du même site -->
<a href="a-propos.html">À propos</a>

<!-- Lien vers une adresse email -->
<a href="mailto:contact@monsite.com">Nous contacter</a>
```

### Ouvrir un lien dans un nouvel onglet

```html
<a href="https://exemple.com" target="_blank" rel="noopener noreferrer">
    Ouvrir dans un nouvel onglet
</a>
```

⚠️ `target="_blank"` ouvre un nouvel onglet, mais **pensez toujours à ajouter `rel="noopener noreferrer"`** :
sans ça, la nouvelle page peut avoir accès à votre page d'origine (faille de sécurité connue).

---

## 🖼️ Les images : `<img>`

```html
<img src="chat.jpg" alt="Un chat noir dormant sur un coussin">
```

- `src` = *source*, le chemin vers le fichier image
- `alt` = texte alternatif, affiché si l'image ne charge pas

### ⚠️ `<img>` est une balise auto-fermante

Contrairement à `<p>` ou `<a>`, `<img>` n'a **pas de balise fermante** : elle ne contient rien, elle
se suffit à elle-même.

```html
<!-- ✅ Correct -->
<img src="photo.jpg" alt="Description">

<!-- ❌ Incorrect : pas de </img> -->
<img src="photo.jpg" alt="Description"></img>
```

### Pourquoi `alt` n'est jamais optionnel

✅ **Accessibilité** : un lecteur d'écran lit le texte `alt` à voix haute pour les personnes malvoyantes.
✅ **SEO** : Google "lit" `alt` pour comprendre le contenu de l'image (il ne "voit" pas l'image elle-même).
✅ **Résilience** : si l'image ne charge pas (lien cassé, connexion lente), le texte `alt` s'affiche à la place.

> 🚫 `alt=""` (vide) est acceptable **uniquement** pour une image purement décorative, jamais pour une
> image porteuse d'information.

### Dimensionner une image

```html
<img src="logo.png" alt="Logo de l'entreprise" width="200" height="100">
```

💡 Préciser `width`/`height` évite que la page "saute" pendant le chargement de l'image.

---

## 🔗🖼️ Combiner lien et image

Une image peut elle-même être cliquable, en la plaçant à l'intérieur d'un `<a>` :

```html
<a href="https://monsite.com">
    <img src="logo.png" alt="Retour à l'accueil">
</a>
```

---

## 🎓 Points clés à retenir

✅ `<a href="...">texte</a>` pour un lien
✅ `target="_blank"` + `rel="noopener noreferrer"` pour ouvrir un lien en sécurité dans un nouvel onglet
✅ `<img src="..." alt="...">` est une balise auto-fermante, sans `</img>`
✅ `alt` est **toujours** nécessaire pour l'accessibilité et le SEO

---

## 🚀 À vous de jouer !
""",
    12, 10,
)

upsert_mini_exercise(
    chapter, 'exercice-liens-et-images', 'Exercice rapide : liens et images', 8,
    """# 🎯 Exercice rapide : liens et images

## Objectif

Créer un lien vers un site externe et insérer une image avec son texte alternatif.

---

## 📋 Instructions

- [ ] Un lien `<a>` avec un attribut `href` pointant vers une URL de votre choix
- [ ] Ce lien doit s'ouvrir dans un nouvel onglet (`target="_blank"`)
- [ ] Une image `<img>` avec un attribut `src` et un attribut `alt` non vide

---

## ✅ Critères de validation

1. ✅ Un `<a>` avec un attribut `href`
2. ✅ L'attribut `target="_blank"` présent
3. ✅ Une balise `<img>` avec `src`
4. ✅ Un attribut `alt` non vide sur l'image

---

## 🚀 C'est parti !
""",
    """<!-- Ajoutez votre lien ici -->

<!-- Ajoutez votre image ici -->
""",
    """<a href="https://www.wikipedia.org" target="_blank" rel="noopener noreferrer">Visiter Wikipédia</a>

<img src="paysage.jpg" alt="Un paysage de montagne au coucher du soleil">
""",
    [
        {"name": "Lien avec href présent", "code": "assert '<a ' in solution and 'href=' in solution", "points": 3, "error_message": "Ajoutez un lien avec <a href=\"...\">"},
        {"name": "Lien ouvert en nouvel onglet", "code": "assert 'target=\"_blank\"' in solution or \"target='_blank'\" in solution", "points": 2, "error_message": "Ajoutez target=\"_blank\" à votre lien"},
        {"name": "Image avec src présent", "code": "assert '<img' in solution and 'src=' in solution", "points": 3, "error_message": "Ajoutez une image avec <img src=\"...\">"},
        {"name": "Attribut alt non vide", "code": "import re\nm = re.search(r'alt=\"([^\"]*)\"', solution) or re.search(r\"alt='([^']*)'\", solution)\nassert m and len(m.group(1).strip()) > 0", "points": 2, "error_message": "Ajoutez un attribut alt non vide décrivant l'image"},
    ],
    [
        "💡 Astuce 1 : <a href=\"https://...\" target=\"_blank\" rel=\"noopener noreferrer\">texte</a>",
        "💡 Astuce 2 : <img> n'a pas de balise fermante",
    ],
)

# ==========================================================================
# 4. DIV, SPAN ET SÉMANTIQUE HTML5
# ==========================================================================

upsert_theory(
    chapter, 'html-div-span-semantique', 'Structurer sa page : div, span et sémantique HTML5', 9,
    """# Structurer sa page : div, span et sémantique HTML5

## 🎯 Objectifs de cette leçon

À la fin de cette leçon, vous serez capable de :
- ✅ Différencier `<div>` (bloc) et `<span>` (en ligne)
- ✅ Utiliser les balises sémantiques HTML5 : `<header>`, `<nav>`, `<main>`, `<article>`, `<section>`, `<footer>`
- ✅ Comprendre pourquoi la sémantique améliore l'accessibilité et le SEO

---

## 📦 `<div>` : le conteneur générique

```html
<div>
    <h2>Titre</h2>
    <p>Contenu du bloc.</p>
</div>
```

- `<div>` = *division*, un bloc générique sans signification propre
- Il prend **toute la largeur disponible** et commence sur une nouvelle ligne
- Sert à **regrouper** des éléments pour les styliser ou les organiser ensemble

## ✏️ `<span>` : le conteneur en ligne

```html
<p>Le prix est de <span class="prix">49,99 €</span> aujourd'hui.</p>
```

- `<span>` ne prend que l'espace nécessaire, **au milieu du texte**, sans saut de ligne
- Sert à cibler un petit bout de texte pour le styliser (ex : une couleur particulière)

| | `<div>` | `<span>` |
|---|---------|----------|
| Type | Bloc | En ligne |
| Saut de ligne | Oui | Non |
| Usage typique | Regrouper une section entière | Cibler quelques mots dans une phrase |

---

## 🏗️ Le problème du "div-soup"

Avant HTML5, les développeurs empilaient des `<div>` partout :

```html
<!-- ❌ Avant HTML5 : aucune balise ne dit "à quoi ça sert" -->
<div id="header">...</div>
<div id="nav">...</div>
<div id="main">...</div>
<div id="footer">...</div>
```

Le problème : ni le navigateur, ni un lecteur d'écran, ni Google ne peuvent deviner le rôle de
chaque `<div>` — seul le nom donné en `id` (qui n'a aucune valeur officielle) laisse un indice.

---

## ✨ HTML5 : les balises sémantiques

HTML5 a introduit des balises qui **portent un sens** :

```html
<body>
    <header>
        <h1>Mon Site</h1>
        <nav>
            <a href="/">Accueil</a>
            <a href="/blog">Blog</a>
        </nav>
    </header>

    <main>
        <article>
            <h2>Titre de l'article</h2>
            <p>Contenu de l'article...</p>
        </article>

        <aside>
            <p>Contenu complémentaire (pub, liens liés...)</p>
        </aside>
    </main>

    <footer>
        <p>&copy; 2026 Mon Site</p>
    </footer>
</body>
```

| Balise | Rôle |
|--------|------|
| `<header>` | En-tête de page ou de section (logo, titre, navigation) |
| `<nav>` | Bloc de liens de navigation |
| `<main>` | Contenu principal de la page (un seul par page) |
| `<article>` | Contenu autonome et réutilisable (article de blog, produit...) |
| `<section>` | Regroupement thématique de contenu |
| `<aside>` | Contenu complémentaire, pas essentiel (barre latérale) |
| `<footer>` | Pied de page ou de section |

> 💡 **Astuce simple** : si vous pouvez nommer clairement le rôle d'un bloc ("c'est l'en-tête",
> "c'est un article"), il existe probablement une balise sémantique pour lui. Si c'est juste un
> "conteneur technique" sans rôle précis, `<div>` reste parfaitement légitime.

---

## 🆚 `<section>` vs `<article>` : le piège classique

- `<article>` : doit avoir du sens **tout seul**, même sorti de son contexte (un post de blog partageable).
- `<section>` : un regroupement thématique **dans** une page (ex : la section "Avis clients").

```html
<article>
    <h2>Comment apprendre le HTML</h2>
    <section>
        <h3>Étape 1 : les bases</h3>
        <p>...</p>
    </section>
    <section>
        <h3>Étape 2 : s'entraîner</h3>
        <p>...</p>
    </section>
</article>
```

---

## 🎓 Points clés à retenir

✅ `<div>` = bloc générique, `<span>` = ligne générique — aucun sens propre
✅ HTML5 apporte des balises sémantiques : `<header>`, `<nav>`, `<main>`, `<article>`, `<section>`, `<aside>`, `<footer>`
✅ La sémantique aide l'accessibilité, le SEO et la lisibilité du code
✅ `<div>`/`<span>` restent utiles quand aucune balise sémantique ne convient

---

## 🚀 À vous de jouer !
""",
    12, 10,
)

upsert_mini_exercise(
    chapter, 'exercice-div-span-semantique', 'Exercice rapide : sémantique HTML5', 10,
    """# 🎯 Exercice rapide : sémantique HTML5

## Objectif

Construire le squelette sémantique d'une page avec en-tête, navigation, contenu principal et pied de page.

---

## 📋 Instructions

- [ ] Un `<header>` contenant un `<h1>` et une `<nav>`
- [ ] La `<nav>` doit contenir au moins 2 liens `<a>`
- [ ] Un `<main>` contenant au moins un `<p>`
- [ ] Un `<footer>` avec un texte de copyright

---

## ✅ Critères de validation

1. ✅ `<header>` présent
2. ✅ `<nav>` présent, imbriquée dans le header
3. ✅ Au moins 2 liens `<a>` dans la navigation
4. ✅ `<main>` présent
5. ✅ `<footer>` présent

---

## 🚀 C'est parti !
""",
    """<!-- Construisez ici le squelette : header (h1 + nav), main, footer -->
""",
    """<header>
    <h1>Mon Site</h1>
    <nav>
        <a href="/">Accueil</a>
        <a href="/contact">Contact</a>
    </nav>
</header>

<main>
    <p>Bienvenue sur mon site personnel !</p>
</main>

<footer>
    <p>&copy; 2026 Mon Site</p>
</footer>
""",
    [
        {"name": "<header> présent", "code": "assert '<header>' in solution and '</header>' in solution", "points": 2, "error_message": "Ajoutez une balise <header>"},
        {"name": "<nav> imbriquée dans le header", "code": "import re\nm = re.search(r'<header>(.*?)</header>', solution, re.S)\nassert m and '<nav>' in m.group(1)", "points": 2, "error_message": "Placez une balise <nav> à l'intérieur de <header>"},
        {"name": "Au moins 2 liens dans la nav", "code": "import re\nm = re.search(r'<nav>(.*?)</nav>', solution, re.S)\nassert m and m.group(1).count('<a ') >= 2", "points": 3, "error_message": "Ajoutez au moins 2 liens <a> dans votre <nav>"},
        {"name": "<main> présent", "code": "assert '<main>' in solution and '</main>' in solution", "points": 2, "error_message": "Ajoutez une balise <main>"},
        {"name": "<footer> présent", "code": "assert '<footer>' in solution and '</footer>' in solution", "points": 1, "error_message": "Ajoutez une balise <footer>"},
    ],
    [
        "💡 Astuce 1 : la structure ressemble à header > (h1 + nav), puis main, puis footer",
        "💡 Astuce 2 : chaque lien de navigation s'écrit <a href=\"...\">texte</a>",
    ],
)

# ==========================================================================
# 5. LES TABLEAUX
# ==========================================================================

upsert_theory(
    chapter, 'html-les-tableaux', 'Les tableaux', 11,
    """# Les tableaux

## 🎯 Objectifs de cette leçon

À la fin de cette leçon, vous serez capable de :
- ✅ Créer un tableau avec `<table>`, `<tr>`, `<td>` et `<th>`
- ✅ Ajouter une ligne d'en-tête
- ✅ Savoir quand utiliser (et ne pas utiliser) un tableau

---

## 📊 À quoi servent les tableaux ?

Les tableaux HTML servent à afficher des **données tabulaires** : un emploi du temps, un tarif, des
résultats sportifs... Toute donnée qui a naturellement une forme de grille (lignes × colonnes).

> 🚫 **Piège historique** : dans les années 2000, les tableaux étaient utilisés pour *mettre en page*
> des sites entiers (menus, colonnes...). C'est aujourd'hui une mauvaise pratique : la mise en page
> est le rôle de CSS. Un tableau HTML doit contenir de vraies données, pas juste organiser visuellement
> la page.

---

## 1️⃣ La structure de base

```html
<table>
    <tr>
        <th>Nom</th>
        <th>Âge</th>
    </tr>
    <tr>
        <td>Alice</td>
        <td>28</td>
    </tr>
    <tr>
        <td>Bob</td>
        <td>34</td>
    </tr>
</table>
```

**Rendu :**
```
┌───────┬─────┐
│ Nom   │ Âge │  ← ligne d'en-tête (<th>)
├───────┼─────┤
│ Alice │ 28  │
│ Bob   │ 34  │
└───────┴─────┘
```

| Balise | Rôle |
|--------|------|
| `<table>` | Le tableau entier |
| `<tr>` | *table row* — une ligne |
| `<th>` | *table header* — une cellule d'en-tête (gras, centré par défaut) |
| `<td>` | *table data* — une cellule de donnée normale |

---

## 2️⃣ Organiser un tableau plus grand : `<thead>` et `<tbody>`

```html
<table>
    <thead>
        <tr>
            <th>Produit</th>
            <th>Prix</th>
        </tr>
    </thead>
    <tbody>
        <tr>
            <td>Clavier</td>
            <td>29,99 €</td>
        </tr>
        <tr>
            <td>Souris</td>
            <td>14,99 €</td>
        </tr>
    </tbody>
</table>
```

✅ `<thead>` regroupe la/les ligne(s) d'en-tête
✅ `<tbody>` regroupe le corps du tableau
✅ Optionnel pour un petit tableau, mais recommandé dès que le tableau grandit (plus lisible, et
  utile pour le style CSS futur)

---

## 3️⃣ Fusionner des cellules (aperçu)

```html
<table>
    <tr>
        <th colspan="2">Informations</th>
    </tr>
    <tr>
        <td>Nom</td>
        <td>Dupont</td>
    </tr>
</table>
```

- `colspan="2"` : la cellule s'étend sur 2 colonnes
- `rowspan="2"` : la cellule s'étend sur 2 lignes (fonctionne pareil, verticalement)

---

## 🎓 Points clés à retenir

✅ `<table>` > `<tr>` (ligne) > `<th>`/`<td>` (cellules)
✅ `<th>` pour les en-têtes, `<td>` pour les données
✅ `<thead>`/`<tbody>` structurent les tableaux plus grands
✅ Un tableau sert à afficher des données, jamais à mettre en page une page entière

---

## 🚀 À vous de jouer !
""",
    10, 10,
)

upsert_mini_exercise(
    chapter, 'exercice-les-tableaux', 'Exercice rapide : un tableau', 12,
    """# 🎯 Exercice rapide : un tableau

## Objectif

Créer un tableau simple avec une ligne d'en-tête et deux lignes de données.

---

## 📋 Instructions

Créez un tableau présentant 2 produits et leur prix :

- [ ] Une ligne d'en-tête avec 2 `<th>` ("Produit" et "Prix")
- [ ] Deux lignes de données, chacune avec 2 `<td>`

---

## ✅ Critères de validation

1. ✅ `<table>` présent
2. ✅ Au moins 3 `<tr>` (1 en-tête + 2 données)
3. ✅ Au moins 2 `<th>`
4. ✅ Au moins 4 `<td>`

---

## 🚀 C'est parti !
""",
    """<!-- Construisez votre tableau ici -->
""",
    """<table>
    <tr>
        <th>Produit</th>
        <th>Prix</th>
    </tr>
    <tr>
        <td>Clavier</td>
        <td>29,99 €</td>
    </tr>
    <tr>
        <td>Souris</td>
        <td>14,99 €</td>
    </tr>
</table>
""",
    [
        {"name": "<table> présent", "code": "assert '<table>' in solution and '</table>' in solution", "points": 2, "error_message": "Ajoutez une balise <table>"},
        {"name": "Au moins 3 lignes <tr>", "code": "assert solution.count('<tr>') >= 3", "points": 3, "error_message": "Ajoutez au moins 3 lignes <tr> (1 en-tête + 2 données)"},
        {"name": "Au moins 2 <th>", "code": "assert solution.count('<th>') >= 2", "points": 2, "error_message": "Ajoutez au moins 2 cellules d'en-tête <th>"},
        {"name": "Au moins 4 <td>", "code": "assert solution.count('<td>') >= 4", "points": 3, "error_message": "Ajoutez au moins 4 cellules de données <td>"},
    ],
    [
        "💡 Astuce 1 : la première <tr> contient les <th>, les suivantes contiennent des <td>",
        "💡 Astuce 2 : chaque ligne <tr> doit avoir le même nombre de cellules",
    ],
)

# ==========================================================================
# 6. LES FORMULAIRES
# ==========================================================================

upsert_theory(
    chapter, 'html-les-formulaires', 'Les formulaires', 13,
    """# Les formulaires

## 🎯 Objectifs de cette leçon

À la fin de cette leçon, vous serez capable de :
- ✅ Créer un formulaire avec `<form>`
- ✅ Utiliser les principaux types de champs `<input>`
- ✅ Associer correctement un `<label>` à son champ
- ✅ Ajouter un bouton de validation

---

## 📝 À quoi sert un formulaire ?

Un formulaire permet de **récolter des informations** auprès de l'utilisateur : se connecter,
s'inscrire, envoyer un message, rechercher un produit... C'est l'un des éléments les plus utilisés
du web.

---

## 1️⃣ La balise `<form>`

```html
<form action="/envoyer" method="POST">
    <!-- les champs vont ici -->
</form>
```

- `action` : l'URL qui va recevoir les données du formulaire
- `method` : `GET` (données visibles dans l'URL, pour une recherche) ou `POST` (données invisibles,
  pour des informations sensibles comme un mot de passe)

---

## 2️⃣ Les champs `<input>`

```html
<input type="text" name="pseudo" placeholder="Votre pseudo">
<input type="email" name="email" placeholder="vous@exemple.com">
<input type="password" name="mdp">
<input type="number" name="age" min="0" max="120">
<input type="checkbox" name="newsletter">
<input type="radio" name="genre" value="homme"> Homme
<input type="radio" name="genre" value="femme"> Femme
```

| `type` | Usage |
|--------|-------|
| `text` | Texte libre sur une ligne |
| `email` | Email (le navigateur vérifie automatiquement le format) |
| `password` | Mot de passe (caractères masqués) |
| `number` | Nombre, avec `min`/`max` optionnels |
| `checkbox` | Case à cocher (choix indépendants) |
| `radio` | Bouton radio (un seul choix parmi plusieurs, même `name`) |

> 💡 Le `type="email"` déclenche une **validation automatique** par le navigateur, sans une ligne
> de JavaScript !

---

## 3️⃣ `<label>` : le champ le plus oublié (et le plus important)

```html
<label for="pseudo">Votre pseudo :</label>
<input type="text" id="pseudo" name="pseudo">
```

⚠️ **`for` du label doit correspondre exactement à `id` du champ.**

### Pourquoi c'est essentiel

✅ **Accessibilité** : un lecteur d'écran annonce le label quand le champ reçoit le focus.
✅ **Confort** : cliquer sur le texte du label active/sélectionne le champ (essayez avec une case à cocher !).

> 🚫 Un formulaire sans `<label>` associé est un des problèmes d'accessibilité les plus fréquents sur
> le web — pourtant très simple à corriger.

---

## 4️⃣ Le bouton de soumission

```html
<button type="submit">Envoyer</button>
<!-- ou, équivalent : -->
<input type="submit" value="Envoyer">
```

`type="submit"` déclenche l'envoi du formulaire vers l'URL définie dans `action`.

---

## ✅ Exemple complet

```html
<form action="/inscription" method="POST">
    <label for="email">Email :</label>
    <input type="email" id="email" name="email" required>

    <label for="mdp">Mot de passe :</label>
    <input type="password" id="mdp" name="mdp" required>

    <label>
        <input type="checkbox" name="newsletter">
        Je m'inscris à la newsletter
    </label>

    <button type="submit">S'inscrire</button>
</form>
```

💡 L'attribut `required` empêche l'envoi du formulaire tant que le champ n'est pas rempli — encore
une validation gratuite fournie par le navigateur.

---

## 🎓 Points clés à retenir

✅ `<form action="..." method="...">` englobe tous les champs
✅ `<input type="...">` change de comportement selon son `type`
✅ `<label for="id-du-champ">` doit toujours correspondre à `id` du champ associé
✅ `<button type="submit">` (ou `<input type="submit">`) envoie le formulaire

---

## 🚀 À vous de jouer !
""",
    13, 10,
)

upsert_mini_exercise(
    chapter, 'exercice-les-formulaires', 'Exercice rapide : un formulaire', 14,
    """# 🎯 Exercice rapide : un formulaire

## Objectif

Créer un petit formulaire de contact avec un champ texte correctement associé à son label.

---

## 📋 Instructions

- [ ] Un `<form>`
- [ ] Un `<label>` avec un attribut `for`
- [ ] Un `<input type="text">` avec un `id` qui correspond exactement au `for` du label
- [ ] Un bouton `<button type="submit">` (ou `<input type="submit">`)

---

## ✅ Critères de validation

1. ✅ `<form>` présent
2. ✅ `<label>` avec attribut `for`
3. ✅ `<input>` avec un `id` correspondant au `for` du label
4. ✅ Un bouton de soumission présent

---

## 🚀 C'est parti !
""",
    """<!-- Construisez votre formulaire ici -->
""",
    """<form action="/contact" method="POST">
    <label for="nom">Votre nom :</label>
    <input type="text" id="nom" name="nom">

    <button type="submit">Envoyer</button>
</form>
""",
    [
        {"name": "<form> présent", "code": "assert '<form' in solution", "points": 2, "error_message": "Ajoutez une balise <form>"},
        {"name": "<label> avec attribut for", "code": "import re\nassert re.search(r'<label[^>]*for=[\\'\"]([^\\'\"]+)[\\'\"]', solution)", "points": 3, "error_message": "Ajoutez un <label for=\"...\">"},
        {"name": "id du champ correspond au for du label", "code": "import re\nlabel = re.search(r'for=\"([^\"]+)\"', solution) or re.search(r\"for='([^']+)'\", solution)\ninput_tag = re.search(r'id=\"([^\"]+)\"', solution) or re.search(r\"id='([^']+)'\", solution)\nassert label and input_tag and label.group(1) == input_tag.group(1)", "points": 3, "error_message": "L'attribut id de <input> doit être identique à l'attribut for de <label>"},
        {"name": "Bouton de soumission présent", "code": "assert ('type=\"submit\"' in solution or \"type='submit'\" in solution)", "points": 2, "error_message": "Ajoutez un bouton <button type=\"submit\"> pour envoyer le formulaire"},
    ],
    [
        "💡 Astuce 1 : <label for=\"nom\">...</label> puis <input id=\"nom\" ...>",
        "💡 Astuce 2 : le for et le id doivent être écrits exactement pareil, lettre pour lettre",
    ],
)

# ==========================================================================
# RÉORDONNER LES LEÇONS EXISTANTES (à la fin, après tout le vocabulaire vu)
# ==========================================================================

print("\nRéorganisation des leçons existantes...")
reorder = {
    'exercice-premiere-page-html': 15,
    'exercice-page-seo': 16,
    'quiz-html-fondamentaux': 17,
}
for slug, new_index in reorder.items():
    lesson = Lesson.objects.get(slug=slug)
    lesson.order_index = new_index
    lesson.save(update_fields=['order_index'])
    print(f"  ♻️  {lesson.title} -> position {new_index}")

# ==========================================================================
# METTRE À JOUR LA DURÉE ESTIMÉE DU CHAPITRE
# ==========================================================================

total_duration = sum(
    Lesson.objects.filter(chapter=chapter).values_list('estimated_duration', flat=True)
)
chapter.estimated_duration = total_duration
chapter.save(update_fields=['estimated_duration'])

# ==========================================================================
# RÉCAPITULATIF
# ==========================================================================

print("\n" + "=" * 70)
lessons = Lesson.objects.filter(chapter=chapter).order_by('order_index')
print(f"✨ Chapitre '{chapter.title}' : {lessons.count()} leçons, {total_duration} min estimées\n")
for lesson in lessons:
    print(f"  {lesson.order_index:>2}. [{lesson.lesson_type:<8}] {lesson.title}")

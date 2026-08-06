"""
Étoffe le chapitre 2 (Introduction au CSS) avec 6 nouvelles leçons
théoriques (une par famille de propriétés) suivies chacune d'un petit
exercice de mise en pratique, pensées pour un public débutant.

Réordonne les leçons existantes (2 gros exercices + quiz) à la fin du
chapitre, et corrige/enrichit le quiz existant qui utilisait un format de
données incompatible avec le moteur de quiz (correct_answer par lettre au
lieu d'un index, questions enveloppées dans un dict) — ce qui provoquait une
erreur serveur (total_points/question_count) dès qu'on ouvrait la leçon.

Usage: docker-compose exec backend python expand_section_2_css.py
"""

from apps.courses.models import Chapter, Lesson, Exercise, Quiz


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


def build():
    """Construit ou met a jour ce bloc de contenu. Idempotent."""
    chapter = Chapter.objects.get(slug='introduction-css')
    print(f"Chapitre : {chapter.title}\n")

    # ==========================================================================
    # 1. LES COULEURS
    # ==========================================================================

    upsert_theory(
        chapter, 'css-les-couleurs', 'Les couleurs en CSS', 3,
        """# Les couleurs en CSS

## 🎯 Objectifs de cette leçon

À la fin de cette leçon, vous serez capable de :
- ✅ Colorer du texte avec `color` et un fond avec `background-color`
- ✅ Utiliser les 4 façons d'écrire une couleur en CSS
- ✅ Ajouter de la transparence avec `rgba()`

---

## 🎨 Les deux propriétés de base

```css
h1 {
    color: blue;              /* couleur du texte */
    background-color: yellow; /* couleur de fond */
}
```

- `color` : couleur du **texte**
- `background-color` : couleur de **l'arrière-plan** de l'élément

---

## 1️⃣ Les mots-clés

```css
p {
    color: red;
}
```

✅ Simple et lisible, mais seulement ~150 couleurs nommées disponibles (red, blue, tomato, coral...).

## 2️⃣ L'hexadécimal

```css
p {
    color: #ff0000; /* rouge */
    color: #333;    /* gris foncé, forme courte (équivaut à #333333) */
}
```

- Commence par `#`, suivi de 6 (ou 3) chiffres hexadécimaux : **R**ouge **V**ert **B**leu
- `#000000` = noir, `#ffffff` = blanc
- La forme courte à 3 caractères double chaque chiffre (`#333` = `#333333`)

## 3️⃣ RGB : Rouge, Vert, Bleu

```css
p {
    color: rgb(255, 0, 0); /* rouge */
}
```

Chaque composante va de 0 à 255. `rgb(255, 0, 0)` équivaut exactement à `#ff0000`.

## 4️⃣ HSL : Teinte, Saturation, Luminosité

```css
p {
    color: hsl(0, 100%, 50%); /* rouge */
}
```

- **H**ue (teinte, 0-360° sur le cercle chromatique)
- **S**aturation (0% = gris, 100% = couleur vive)
- **L**ightness (0% = noir, 50% = couleur normale, 100% = blanc)

> 💡 **Pourquoi HSL est pratique** : pour obtenir une variante plus sombre d'une couleur, il suffit de
> baisser la luminosité (`hsl(210, 80%, 30%)` au lieu de `hsl(210, 80%, 50%)`), sans avoir à recalculer
> un code hexadécimal.

---

## 🫥 La transparence avec `rgba()`

```css
.overlay {
    background-color: rgba(0, 0, 0, 0.5); /* noir à 50% de transparence */
}
```

Le 4ᵉ paramètre (`alpha`) va de `0` (invisible) à `1` (opaque). Très utilisé pour des fonds
semi-transparents (bannières, modales).

> 💡 Il existe aussi `hsla()`, équivalent transparent de `hsl()`.

---

## 🆚 Comparatif rapide

| Format | Exemple | Transparence possible ? |
|--------|---------|--------------------------|
| Mot-clé | `red` | ❌ |
| Hexadécimal | `#ff0000` | ❌ (sauf forme à 8 chiffres) |
| RGB | `rgb(255, 0, 0)` | ❌ (utiliser `rgba()`) |
| HSL | `hsl(0, 100%, 50%)` | ❌ (utiliser `hsla()`) |

---

## 🎓 Points clés à retenir

✅ `color` colore le texte, `background-color` colore le fond
✅ 4 formats possibles : mot-clé, hexadécimal, `rgb()`, `hsl()`
✅ `rgba()`/`hsla()` ajoutent un canal de transparence (0 à 1)
✅ HSL facilite la création de variantes plus claires/sombres d'une même teinte

---

## 🚀 À vous de jouer !
""",
        10, 10,
    )

    upsert_mini_exercise(
        chapter, 'exercice-les-couleurs', 'Exercice rapide : les couleurs', 4,
        """# 🎯 Exercice rapide : les couleurs

## Objectif

Coloriser un titre et un fond, avec un fond semi-transparent.

---

## 📋 Instructions

- [ ] La règle `h1` doit avoir `color: #2563eb;` (bleu)
- [ ] La règle `.banniere` doit avoir `background-color: rgba(0, 0, 0, 0.6);`

---

## ✅ Critères de validation

1. ✅ `h1` a une propriété `color` en hexadécimal
2. ✅ `.banniere` a un `background-color` utilisant `rgba(`

---

## 🚀 C'est parti !
""",
        """h1 {
    /* Ajoutez une couleur de texte en hexadécimal */
}

.banniere {
    /* Ajoutez un fond noir semi-transparent avec rgba() */
}
""",
        """h1 {
    color: #2563eb;
}

.banniere {
    background-color: rgba(0, 0, 0, 0.6);
}
""",
        [
            {"name": "h1 a une couleur hexadécimale", "code": "import re\nassert re.search(r'h1\\s*\\{[^}]*color\\s*:\\s*#[0-9a-fA-F]{3,6}', solution)", "points": 5, "error_message": "Ajoutez 'color: #......;' dans la règle h1"},
            {"name": ".banniere utilise rgba()", "code": "import re\nassert re.search(r'\\.banniere\\s*\\{[^}]*background-color\\s*:\\s*rgba\\(', solution)", "points": 5, "error_message": "Ajoutez 'background-color: rgba(...);' dans .banniere"},
        ],
        [
            "💡 Astuce 1 : un code hexadécimal commence toujours par #",
            "💡 Astuce 2 : rgba(0, 0, 0, 0.6) = noir à 60% d'opacité",
        ],
    )

    # ==========================================================================
    # 2. LA TYPOGRAPHIE
    # ==========================================================================

    upsert_theory(
        chapter, 'css-la-typographie', 'La typographie', 5,
        """# La typographie

## 🎯 Objectifs de cette leçon

À la fin de cette leçon, vous serez capable de :
- ✅ Choisir une police avec `font-family` (et une police de secours)
- ✅ Définir taille, graisse et style avec `font-size`, `font-weight`, `font-style`
- ✅ Aligner du texte et gérer l'espacement des lignes

---

## 🔤 `font-family` : choisir une police

```css
body {
    font-family: Arial, Helvetica, sans-serif;
}
```

⚠️ Une police n'est pas forcément installée sur l'ordinateur du visiteur ! C'est pourquoi on donne une
**liste de secours** (*fallback stack*) : le navigateur essaie chaque police dans l'ordre, jusqu'à en
trouver une d'installée.

### Les familles génériques

| Famille | Exemple | Style |
|---------|---------|-------|
| `serif` | Times New Roman | Avec empattements (petits traits en bout de lettre) |
| `sans-serif` | Arial | Sans empattements, plus moderne |
| `monospace` | Courier New | Chasse fixe (toutes les lettres ont la même largeur) |

✅ **Toujours terminer sa liste par une famille générique** : si aucune police précise n'est trouvée,
le navigateur utilise au moins une police du bon style.

> 💡 Pour utiliser une police personnalisée (Google Fonts, etc.), il faut l'importer avant de pouvoir
> la nommer dans `font-family` — on abordera ça dans un chapitre dédié.

---

## 📏 `font-size` : la taille du texte

```css
p {
    font-size: 16px;
}
```

16px est la taille par défaut du texte dans la plupart des navigateurs.

## 🏋️ `font-weight` : la graisse

```css
strong {
    font-weight: bold;   /* ou : 700 */
}
p {
    font-weight: normal;  /* ou : 400 */
}
```

Peut être un mot-clé (`normal`, `bold`) ou un nombre de 100 (très fin) à 900 (très gras).

## 🔀 `font-style` : italique

```css
em {
    font-style: italic;
}
```

---

## ↔️ Aligner le texte : `text-align`

```css
h1 {
    text-align: center;
}
```

Valeurs possibles : `left` (par défaut), `center`, `right`, `justify`.

## 📐 `line-height` : l'espacement des lignes

```css
p {
    line-height: 1.6;
}
```

✅ Une valeur **sans unité** (comme `1.6`) est relative à la taille de police de l'élément — c'est la
pratique recommandée : elle s'adapte automatiquement si `font-size` change.

> 🚫 Un `line-height` trop petit (proche de 1) rend un long paragraphe difficile à lire.
> Une valeur entre 1.4 et 1.8 est généralement confortable pour du texte courant.

## ✂️ `text-decoration` : souligner, barrer

```css
a {
    text-decoration: none; /* retire le soulignement par défaut des liens */
}
.promo {
    text-decoration: line-through; /* texte barré */
}
```

---

## ✅ Exemple complet

```css
body {
    font-family: 'Segoe UI', Arial, sans-serif;
    font-size: 16px;
    line-height: 1.6;
    color: #1f2937;
}

h1 {
    font-weight: bold;
    text-align: center;
}

a {
    text-decoration: none;
    color: #2563eb;
}
```

---

## 🎓 Points clés à retenir

✅ `font-family` avec une liste de secours se terminant par une famille générique
✅ `font-size`, `font-weight`, `font-style` contrôlent taille, graisse et style
✅ `text-align` aligne le texte, `line-height` (sans unité) espace les lignes
✅ `text-decoration: none` retire le soulignement par défaut des liens

---

## 🚀 À vous de jouer !
""",
        12, 10,
    )

    upsert_mini_exercise(
        chapter, 'exercice-la-typographie', 'Exercice rapide : la typographie', 6,
        """# 🎯 Exercice rapide : la typographie

## Objectif

Styliser un paragraphe avec une police, une taille, un alignement et un espacement de ligne confortable.

---

## 📋 Instructions

Complétez la règle `.article` avec :

- [ ] `font-family` avec au moins 2 polices, se terminant par `sans-serif`
- [ ] `font-size: 18px;`
- [ ] `text-align: justify;`
- [ ] `line-height: 1.6;`

---

## ✅ Critères de validation

1. ✅ `font-family` se termine par une famille générique
2. ✅ `font-size: 18px` présent
3. ✅ `text-align: justify` présent
4. ✅ `line-height: 1.6` présent

---

## 🚀 C'est parti !
""",
        """.article {
    /* Ajoutez font-family, font-size, text-align et line-height */
}
""",
        """.article {
    font-family: Arial, sans-serif;
    font-size: 18px;
    text-align: justify;
    line-height: 1.6;
}
""",
        [
            {"name": "font-family avec famille générique", "code": "import re\nm = re.search(r'\\.article\\s*\\{[^}]*font-family\\s*:\\s*([^;]+);', solution)\nassert m and ('sans-serif' in m.group(1) or 'serif' in m.group(1) or 'monospace' in m.group(1))", "points": 3, "error_message": "Terminez votre font-family par sans-serif, serif ou monospace"},
            {"name": "font-size: 18px", "code": "import re\nassert re.search(r'\\.article\\s*\\{[^}]*font-size\\s*:\\s*18px', solution)", "points": 2, "error_message": "Ajoutez 'font-size: 18px;'"},
            {"name": "text-align: justify", "code": "import re\nassert re.search(r'\\.article\\s*\\{[^}]*text-align\\s*:\\s*justify', solution)", "points": 2, "error_message": "Ajoutez 'text-align: justify;'"},
            {"name": "line-height: 1.6", "code": "import re\nassert re.search(r'\\.article\\s*\\{[^}]*line-height\\s*:\\s*1\\.6', solution)", "points": 3, "error_message": "Ajoutez 'line-height: 1.6;'"},
        ],
        [
            "💡 Astuce 1 : font-family: Arial, sans-serif;",
            "💡 Astuce 2 : line-height sans unité (1.6, pas 1.6px)",
        ],
    )

    # ==========================================================================
    # 3. LES UNITÉS DE MESURE
    # ==========================================================================

    upsert_theory(
        chapter, 'css-les-unites-de-mesure', 'Les unités de mesure', 7,
        """# Les unités de mesure

## 🎯 Objectifs de cette leçon

À la fin de cette leçon, vous serez capable de :
- ✅ Différencier unités absolues (`px`) et relatives (`%`, `em`, `rem`)
- ✅ Comprendre à quoi `em` et `rem` sont relatifs
- ✅ Utiliser les unités de viewport `vw`/`vh`

---

## 📏 `px` : le pixel, une unité absolue

```css
p {
    font-size: 16px;
    width: 300px;
}
```

✅ Une taille en `px` reste **fixe**, quel que soit le contexte.
⚠️ Peu flexible : si vous voulez que tout s'agrandisse proportionnellement (accessibilité, zoom), il
faut changer chaque valeur une par une.

---

## 📐 `%` : relatif au parent

```css
.enfant {
    width: 50%; /* la moitié de la largeur du parent */
}
```

Si l'élément parent fait 600px de large, `.enfant` fera 300px. Si le parent change de taille,
`.enfant` s'adapte automatiquement.

---

## 🔤 `em` : relatif à la taille de police du **parent**

```css
.parent {
    font-size: 20px;
}
.enfant {
    font-size: 1.5em; /* 1.5 × 20px = 30px */
}
```

⚠️ **Piège classique** : les `em` s'accumulent en cascade. Si un enfant a lui-même un enfant en `em`,
la taille se calcule par rapport à SON parent direct (donc à répétition), ce qui peut vite devenir
imprévisible dans une page complexe.

---

## 🌱 `rem` : relatif à la taille de police de la **racine**

```css
html {
    font-size: 16px; /* la racine */
}
.titre {
    font-size: 2rem;  /* 2 × 16px = 32px, TOUJOURS, peu importe le parent */
}
```

✅ `rem` (*root em*) est toujours relatif au `<html>`, jamais au parent direct : pas d'effet
d'accumulation, beaucoup plus prévisible que `em`.

> 🎓 **Bonne pratique largement adoptée** : utiliser `rem` pour les tailles de police et les
> espacements, `%` pour les largeurs fluides, et `px` pour les détails qui ne doivent jamais changer
> (bordures fines, par exemple).

---

## 🖥️ `vw` et `vh` : relatif à la fenêtre du navigateur

```css
.hero {
    width: 100vw;   /* 100% de la largeur de la fenêtre (viewport) */
    height: 100vh;  /* 100% de la hauteur de la fenêtre */
}
```

- `vw` = *viewport width*, 1vw = 1% de la largeur visible de la fenêtre
- `vh` = *viewport height*, 1vh = 1% de la hauteur visible de la fenêtre

Très utilisé pour des sections "plein écran" (un grand titre d'accueil qui occupe tout l'écran, par exemple).

---

## 🆚 Récapitulatif

| Unité | Relative à... | Cas d'usage typique |
|-------|----------------|----------------------|
| `px` | Rien (absolu) | Bordures fines, détails précis |
| `%` | L'élément parent | Largeurs fluides |
| `em` | La police du parent direct | Espacements liés au texte local |
| `rem` | La police de `<html>` | Tailles de police, espacements généraux |
| `vw` / `vh` | La fenêtre du navigateur | Sections plein écran |

---

## 🎓 Points clés à retenir

✅ `px` est fixe, `%`/`em`/`rem`/`vw`/`vh` sont relatifs à quelque chose
✅ `em` dépend du parent direct (peut s'accumuler), `rem` dépend toujours de `<html>`
✅ `rem` est généralement préférable à `em` pour des tailles prévisibles
✅ `vw`/`vh` sont relatifs à la taille de la fenêtre du navigateur

---

## 🚀 À vous de jouer !
""",
        12, 10,
    )

    upsert_mini_exercise(
        chapter, 'exercice-les-unites-de-mesure', 'Exercice rapide : les unités', 8,
        """# 🎯 Exercice rapide : les unités de mesure

## Objectif

Utiliser une unité relative au parent et une unité relative à la racine dans une même feuille de style.

---

## 📋 Instructions

- [ ] La règle `.conteneur` doit avoir `width: 80%;`
- [ ] La règle `.titre` doit avoir `font-size: 2rem;`
- [ ] La règle `.titre` doit aussi avoir `margin-bottom: 1rem;`

---

## ✅ Critères de validation

1. ✅ `.conteneur` utilise une largeur en `%`
2. ✅ `.titre` a un `font-size` en `rem`
3. ✅ `.titre` a un `margin-bottom` en `rem`

---

## 🚀 C'est parti !
""",
        """.conteneur {
    /* Ajoutez une largeur relative en % */
}

.titre {
    /* Ajoutez font-size et margin-bottom en rem */
}
""",
        """.conteneur {
    width: 80%;
}

.titre {
    font-size: 2rem;
    margin-bottom: 1rem;
}
""",
        [
            {"name": ".conteneur a une largeur en %", "code": "import re\nassert re.search(r'\\.conteneur\\s*\\{[^}]*width\\s*:\\s*\\d+%', solution)", "points": 4, "error_message": "Ajoutez 'width: 80%;' dans .conteneur"},
            {"name": ".titre a un font-size en rem", "code": "import re\nassert re.search(r'\\.titre\\s*\\{[^}]*font-size\\s*:\\s*[\\d.]+rem', solution)", "points": 3, "error_message": "Ajoutez 'font-size: 2rem;' dans .titre"},
            {"name": ".titre a un margin-bottom en rem", "code": "import re\nassert re.search(r'\\.titre\\s*\\{[^}]*margin-bottom\\s*:\\s*[\\d.]+rem', solution)", "points": 3, "error_message": "Ajoutez 'margin-bottom: 1rem;' dans .titre"},
        ],
        [
            "💡 Astuce 1 : une unité en % s'écrit collée au nombre, ex: 80%",
            "💡 Astuce 2 : rem s'écrit aussi collé, ex: 2rem",
        ],
    )

    # ==========================================================================
    # 4. DISPLAY : BLOCK, INLINE ET INLINE-BLOCK
    # ==========================================================================

    upsert_theory(
        chapter, 'css-display-block-inline', 'Display : block, inline et inline-block', 9,
        """# Display : block, inline et inline-block

## 🎯 Objectifs de cette leçon

À la fin de cette leçon, vous serez capable de :
- ✅ Comprendre le comportement par défaut `block` et `inline`
- ✅ Changer ce comportement avec la propriété `display`
- ✅ Choisir `inline-block` quand vous avez besoin des deux à la fois

---

## 📦 `display: block` — l'élément "bloc"

```css
div {
    display: block; /* comportement par défaut de <div>, <p>, <h1>... */
}
```

Caractéristiques :
- Prend **toute la largeur disponible**
- Commence **toujours sur une nouvelle ligne**
- Accepte `width`, `height`, `margin` et `padding` sur les 4 côtés

`<div>`, `<p>`, `<h1>`-`<h6>`, `<ul>`, `<li>`, `<section>`... sont des éléments `block` par défaut.

---

## ✏️ `display: inline` — l'élément "en ligne"

```css
span {
    display: inline; /* comportement par défaut de <span>, <a>, <strong>... */
}
```

Caractéristiques :
- Ne prend **que l'espace nécessaire** à son contenu
- Reste **sur la même ligne** que ce qui l'entoure
- ⚠️ `width` et `height` sont **ignorés**
- ⚠️ `margin-top`/`margin-bottom` sont **ignorés** (seuls les côtés gauche/droite fonctionnent)

`<span>`, `<a>`, `<strong>`, `<em>`, `<img>` sont des éléments `inline` par défaut (`<img>` fait
exception pour `width`/`height`, qui fonctionnent bien sur les images).

---

## 🤝 `display: inline-block` — le meilleur des deux mondes

```css
.bouton {
    display: inline-block;
    width: 150px;
    padding: 10px;
}
```

Caractéristiques :
- Reste **sur la même ligne** que ses voisins (comme `inline`)
- Accepte `width`, `height`, et `margin` sur les 4 côtés (comme `block`)

> 💡 **Cas d'usage classique** : des liens de menu affichés côte à côte, mais avec un `padding`
> confortable comme des boutons — impossible avec `inline` seul, inutilement complexe avec `block`
> seul (il faudrait flotter ou repositionner chaque élément).

---

## 🆚 Comparatif visuel

| | `block` | `inline` | `inline-block` |
|---|---------|----------|-----------------|
| Nouvelle ligne | ✅ Oui | ❌ Non | ❌ Non |
| `width` / `height` | ✅ Fonctionne | ❌ Ignoré | ✅ Fonctionne |
| `margin` (haut/bas) | ✅ Fonctionne | ❌ Ignoré | ✅ Fonctionne |

---

## ✅ Exemple concret : une navigation

```css
nav a {
    display: inline-block;
    padding: 10px 16px;
    margin-right: 8px;
}
```

Sans `display: inline-block`, les `<a>` (naturellement `inline`) ignoreraient le `padding` vertical
et donneraient une zone cliquable trop petite et mal espacée.

---

## 🎓 Points clés à retenir

✅ `block` = toute la largeur + saut de ligne, `inline` = juste ce qu'il faut + reste sur la ligne
✅ `inline` ignore `width`, `height` et les marges verticales
✅ `inline-block` combine "reste sur la ligne" et "accepte les dimensions"
✅ La propriété `display` permet de changer le comportement par défaut de n'importe quel élément

---

## 🚀 À vous de jouer !
""",
        12, 10,
    )

    upsert_mini_exercise(
        chapter, 'exercice-display-block-inline', 'Exercice rapide : display', 10,
        """# 🎯 Exercice rapide : display

## Objectif

Transformer des liens de navigation (naturellement `inline`) pour qu'ils acceptent largeur et espacement.

---

## 📋 Instructions

Complétez la règle `.nav-lien` avec :

- [ ] `display: inline-block;`
- [ ] `width: 100px;`
- [ ] `padding: 10px;`

---

## ✅ Critères de validation

1. ✅ `display: inline-block` présent
2. ✅ `width: 100px` présent
3. ✅ `padding: 10px` présent

---

## 🚀 C'est parti !
""",
        """.nav-lien {
    /* Ajoutez display, width et padding */
}
""",
        """.nav-lien {
    display: inline-block;
    width: 100px;
    padding: 10px;
}
""",
        [
            {"name": "display: inline-block présent", "code": "import re\nassert re.search(r'\\.nav-lien\\s*\\{[^}]*display\\s*:\\s*inline-block', solution)", "points": 4, "error_message": "Ajoutez 'display: inline-block;'"},
            {"name": "width: 100px présent", "code": "import re\nassert re.search(r'\\.nav-lien\\s*\\{[^}]*width\\s*:\\s*100px', solution)", "points": 3, "error_message": "Ajoutez 'width: 100px;'"},
            {"name": "padding: 10px présent", "code": "import re\nassert re.search(r'\\.nav-lien\\s*\\{[^}]*padding\\s*:\\s*10px', solution)", "points": 3, "error_message": "Ajoutez 'padding: 10px;'"},
        ],
        [
            "💡 Astuce 1 : sans inline-block, un lien <a> ignore width et le padding vertical",
            "💡 Astuce 2 : toutes les propriétés vont dans le même bloc .nav-lien { ... }",
        ],
    )

    # ==========================================================================
    # 5. BORDURES, ARRONDIS ET OMBRES
    # ==========================================================================

    upsert_theory(
        chapter, 'css-bordures-arrondis-ombres', 'Bordures, arrondis et ombres', 11,
        """# Bordures, arrondis et ombres

## 🎯 Objectifs de cette leçon

À la fin de cette leçon, vous serez capable de :
- ✅ Personnaliser une bordure avec `border` (épaisseur, style, couleur)
- ✅ Arrondir des coins avec `border-radius`, jusqu'au cercle parfait
- ✅ Ajouter de la profondeur avec `box-shadow`

---

## 🖊️ La bordure : `border`

```css
.carte {
    border: 2px solid #2563eb;
}
```

`border` est un raccourci pour 3 valeurs, dans n'importe quel ordre :
- **Épaisseur** : `2px`
- **Style** : `solid` (pleine), `dashed` (tirets), `dotted` (pointillés), `double`
- **Couleur** : `#2563eb`

```css
.attention {
    border: 3px dashed orange;
}
```

💡 On peut aussi cibler un seul côté : `border-top`, `border-right`, `border-bottom`, `border-left`.

---

## ⭕ Arrondir les coins : `border-radius`

```css
.carte {
    border-radius: 8px; /* coins légèrement arrondis */
}

.avatar {
    border-radius: 50%; /* cercle parfait, si width = height */
}

.pilule {
    border-radius: 9999px; /* forme de "pilule" tout arrondie */
}
```

> 💡 **Astuce cercle parfait** : sur un élément **carré** (`width` = `height`), `border-radius: 50%`
> donne un cercle exact. C'est la technique classique pour un avatar rond.

On peut aussi arrondir chaque coin séparément :

```css
.notification {
    border-radius: 12px 12px 0 0; /* haut-gauche haut-droit bas-droit bas-gauche */
}
```

---

## 🌑 L'ombre portée : `box-shadow`

```css
.carte {
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}
```

`box-shadow` prend, dans l'ordre :

| Valeur | Rôle |
|--------|------|
| `0` | Décalage horizontal (0 = centré) |
| `4px` | Décalage vertical (l'ombre "tombe" vers le bas) |
| `6px` | Flou (plus grand = ombre plus diffuse) |
| `rgba(0,0,0,0.1)` | Couleur de l'ombre, souvent noire et semi-transparente |

```css
.carte:hover {
    box-shadow: 0 8px 16px rgba(0, 0, 0, 0.2);
}
```

> 💡 Combiner une ombre légère par défaut et une ombre plus marquée au survol (`:hover`) est une
> technique très courante pour donner une impression de profondeur et de réactivité aux cartes/boutons.

---

## ✅ Exemple complet : une carte

```css
.carte {
    border: 1px solid #e5e7eb;
    border-radius: 12px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
    padding: 20px;
}
```

---

## 🎓 Points clés à retenir

✅ `border: épaisseur style couleur;` en un seul raccourci
✅ `border-radius: 50%` sur un carré donne un cercle parfait
✅ `box-shadow: décalage-x décalage-y flou couleur;`
✅ Une ombre légère + `padding` confortable = l'effet "carte" le plus courant du web actuel

---

## 🚀 À vous de jouer !
""",
        12, 10,
    )

    upsert_mini_exercise(
        chapter, 'exercice-bordures-arrondis-ombres', 'Exercice rapide : bordures et ombres', 12,
        """# 🎯 Exercice rapide : bordures et ombres

## Objectif

Habiller une carte avec une bordure, des coins arrondis et une ombre légère.

---

## 📋 Instructions

Complétez la règle `.carte` avec :

- [ ] `border: 1px solid #e5e7eb;`
- [ ] `border-radius: 12px;`
- [ ] `box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);`

---

## ✅ Critères de validation

1. ✅ `border` présent avec une couleur
2. ✅ `border-radius` présent
3. ✅ `box-shadow` présent

---

## 🚀 C'est parti !
""",
        """.carte {
    /* Ajoutez border, border-radius et box-shadow */
}
""",
        """.carte {
    border: 1px solid #e5e7eb;
    border-radius: 12px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}
""",
        [
            {"name": "border présent", "code": "import re\nassert re.search(r'\\.carte\\s*\\{[^}]*border\\s*:\\s*\\d', solution)", "points": 3, "error_message": "Ajoutez une propriété 'border:' dans .carte"},
            {"name": "border-radius présent", "code": "import re\nassert re.search(r'\\.carte\\s*\\{[^}]*border-radius\\s*:', solution)", "points": 3, "error_message": "Ajoutez 'border-radius:' dans .carte"},
            {"name": "box-shadow présent", "code": "import re\nassert re.search(r'\\.carte\\s*\\{[^}]*box-shadow\\s*:', solution)", "points": 4, "error_message": "Ajoutez 'box-shadow:' dans .carte"},
        ],
        [
            "💡 Astuce 1 : border: 1px solid #e5e7eb; combine épaisseur, style et couleur",
            "💡 Astuce 2 : box-shadow: décalage-x décalage-y flou couleur;",
        ],
    )

    # ==========================================================================
    # 6. LES PSEUDO-CLASSES
    # ==========================================================================

    upsert_theory(
        chapter, 'css-les-pseudo-classes', "Les pseudo-classes : réagir aux interactions", 13,
        """# Les pseudo-classes : réagir aux interactions

## 🎯 Objectifs de cette leçon

À la fin de cette leçon, vous serez capable de :
- ✅ Styliser un élément survolé avec `:hover`
- ✅ Styliser un champ actif avec `:focus`
- ✅ Utiliser `:first-child` et `:last-child`
- ✅ Adoucir les changements avec `transition`

---

## 🖱️ `:hover` — au survol de la souris

```css
a:hover {
    color: orange;
}
```

Le style ne s'applique que **pendant que la souris survole** l'élément. Dès que la souris s'en va, le
style d'origine revient.

```css
.bouton {
    background-color: #2563eb;
}
.bouton:hover {
    background-color: #1e40af; /* plus foncé au survol */
}
```

---

## 🎯 `:focus` — quand un champ est actif

```css
input:focus {
    border-color: #2563eb;
    outline: none;
}
```

`:focus` s'applique quand un élément **reçoit le focus** (clic dans un champ, ou navigation au
clavier avec Tab). C'est essentiel pour donner un retour visuel clair à l'utilisateur qui remplit
un formulaire.

> ⚠️ **Attention à l'accessibilité** : ne retirez `outline: none` (qui supprime le contour par défaut
> du navigateur) que si vous le remplacez par un autre style visible (comme `border-color` ici).
> Sans aucun indicateur, les utilisateurs au clavier ne savent plus où ils se trouvent sur la page.

---

## 👆 `:active` — pendant le clic

```css
.bouton:active {
    transform: scale(0.98); /* légèrement rétréci pendant le clic */
}
```

S'applique uniquement pendant l'instant où l'élément est cliqué (bouton de souris enfoncé).

---

## 👶 `:first-child` et `:last-child`

```css
li:first-child {
    font-weight: bold;
}
li:last-child {
    border-bottom: none;
}
```

- `:first-child` cible un élément qui est le **premier enfant** de son parent
- `:last-child` cible le **dernier enfant**

> 💡 **Cas d'usage fréquent** : retirer la bordure du dernier élément d'une liste, pour éviter un
> double-trait avec la bordure du conteneur qui l'englobe.

---

## 🌊 Adoucir le changement avec `transition`

```css
.bouton {
    background-color: #2563eb;
    transition: background-color 0.3s ease;
}
.bouton:hover {
    background-color: #1e40af;
}
```

Sans `transition`, le changement de couleur au survol est **instantané** (un peu brutal). Avec
`transition`, il devient progressif sur la durée indiquée (`0.3s` = 300 millisecondes).

- `transition: propriété durée fonction-de-timing;`
- `all` peut remplacer le nom de propriété pour transitionner tous les changements à la fois

---

## ✅ Exemple complet

```css
.carte {
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
    transition: box-shadow 0.2s ease, transform 0.2s ease;
}

.carte:hover {
    box-shadow: 0 8px 20px rgba(0, 0, 0, 0.15);
    transform: translateY(-4px);
}
```

---

## 🎓 Points clés à retenir

✅ `:hover` (survol), `:focus` (élément actif), `:active` (pendant le clic)
✅ `:first-child`/`:last-child` ciblent le premier/dernier enfant d'un parent
✅ `transition` rend un changement progressif au lieu d'instantané
✅ Ne jamais retirer `outline` en `:focus` sans le remplacer par un autre indicateur visuel

---

## 🚀 À vous de jouer !
""",
        13, 10,
    )

    upsert_mini_exercise(
        chapter, 'exercice-les-pseudo-classes', 'Exercice rapide : les pseudo-classes', 14,
        """# 🎯 Exercice rapide : les pseudo-classes

## Objectif

Ajouter un effet de survol doux sur un bouton.

---

## 📋 Instructions

- [ ] La règle `.bouton` doit avoir une `transition` sur `background-color`
- [ ] La règle `.bouton:hover` doit changer `background-color`

---

## ✅ Critères de validation

1. ✅ `.bouton` a une propriété `transition`
2. ✅ `.bouton:hover` existe avec un `background-color`

---

## 🚀 C'est parti !
""",
        """.bouton {
    background-color: #2563eb;
    /* Ajoutez une transition sur background-color */
}

/* Ajoutez la règle :hover ici */
""",
        """.bouton {
    background-color: #2563eb;
    transition: background-color 0.3s ease;
}

.bouton:hover {
    background-color: #1e40af;
}
""",
        [
            {"name": ".bouton a une transition", "code": "import re\nassert re.search(r'\\.bouton\\s*\\{[^}]*transition\\s*:', solution)", "points": 5, "error_message": "Ajoutez une propriété 'transition:' dans .bouton"},
            {"name": ".bouton:hover change le fond", "code": "import re\nassert re.search(r'\\.bouton:hover\\s*\\{[^}]*background-color\\s*:', solution)", "points": 5, "error_message": "Ajoutez '.bouton:hover { background-color: ...; }'"},
        ],
        [
            "💡 Astuce 1 : transition: background-color 0.3s ease;",
            "💡 Astuce 2 : la règle :hover s'écrit collée au sélecteur, sans espace : .bouton:hover",
        ],
    )

    # ==========================================================================
    # RÉORDONNER LES LEÇONS EXISTANTES
    # ==========================================================================

    print("\nRéorganisation des leçons existantes...")
    reorder = {
        'exercice-styliser-premiere-page': 15,
        'exercice-box-model': 16,
    }
    for slug, new_index in reorder.items():
        lesson = Lesson.objects.get(slug=slug)
        lesson.order_index = new_index
        lesson.save(update_fields=['order_index'])
        print(f"  ♻️  {lesson.title} -> position {new_index}")

    # ==========================================================================
    # CORRIGER ET ENRICHIR LE QUIZ (format cassé -> format valide, + nouveaux sujets)
    # ==========================================================================

    print("\nReconstruction du quiz (format + contenu enrichi)...")

    quiz_lesson = Lesson.objects.get(slug='quiz-selecteurs-box-model')
    quiz_lesson.order_index = 17
    quiz_lesson.title = 'Quiz : Les Fondamentaux du CSS'
    quiz_lesson.slug = 'quiz-css-fondamentaux'
    quiz_lesson.points = 100
    quiz_lesson.save()

    quiz_questions = [
        {
            "id": 1,
            "question": "Que signifie l'acronyme CSS ?",
            "options": ["Computer Style System", "Cascading Style Sheets", "Creative Style Syntax", "Colorful Style Sheets"],
            "correct_answer": 1,
            "type": "single",
            "explanation": "CSS signifie Cascading Style Sheets, les feuilles de style en cascade.",
        },
        {
            "id": 2,
            "question": "Quel symbole précède un sélecteur de classe en CSS ?",
            "options": ["# (dièse)", "@ (arobase)", ". (point)", "% (pourcentage)"],
            "correct_answer": 2,
            "type": "single",
            "explanation": "Un point précède les sélecteurs de classe, un dièse précède les sélecteurs d'ID.",
        },
        {
            "id": 3,
            "question": "Quelle est la méthode recommandée pour appliquer du CSS en production ?",
            "options": ["CSS en ligne (attribut style)", "CSS externe (fichier .css lié)", "CSS interne (balise <style>)", "Toutes se valent"],
            "correct_answer": 1,
            "type": "single",
            "explanation": "Le CSS externe permet la réutilisation, la mise en cache et sépare contenu et présentation.",
        },
        {
            "id": 4,
            "question": "Dans le box model, quel est l'ordre des couches de l'intérieur vers l'extérieur ?",
            "options": ["margin, padding, border, content", "content, padding, border, margin", "content, border, padding, margin", "padding, content, margin, border"],
            "correct_answer": 1,
            "type": "single",
            "explanation": "L'ordre est : content (contenu) → padding (espace intérieur) → border (bordure) → margin (espace extérieur).",
        },
        {
            "id": 5,
            "question": "Comment centrer horizontalement un bloc avec une largeur définie ?",
            "options": ["text-align: center;", "margin: auto 0;", "padding: 0 auto;", "margin: 0 auto;"],
            "correct_answer": 3,
            "type": "single",
            "explanation": "margin: 0 auto; répartit l'espace horizontal restant également des deux côtés, centrant le bloc.",
        },
        {
            "id": 6,
            "question": "Quel sélecteur cible tous les <li> qui sont enfants directs d'un <ul> ?",
            "options": ["ul li", "ul ~ li", "ul > li", "ul + li"],
            "correct_answer": 2,
            "type": "single",
            "explanation": "Le combinateur > sélectionne uniquement les enfants directs, contrairement à l'espace qui cible tous les descendants.",
        },
        {
            "id": 7,
            "question": "Entre une classe et un ID, lequel doit être unique dans la page ?",
            "options": ["La classe", "Les deux", "Aucun des deux", "L'ID"],
            "correct_answer": 3,
            "type": "single",
            "explanation": "Un ID doit être unique dans la page, tandis qu'une classe peut être réutilisée sur plusieurs éléments.",
        },
        {
            "id": 8,
            "question": "Lequel de ces formats de couleur permet d'ajouter de la transparence ?",
            "options": ["rgba(0, 0, 0, 0.5)", "#000000", "rgb(0, 0, 0)", "black"],
            "correct_answer": 0,
            "type": "single",
            "explanation": "rgba() ajoute un 4ᵉ paramètre (alpha) de 0 à 1 pour la transparence. Il existe aussi hsla().",
        },
        {
            "id": 9,
            "question": "Que représente le H dans HSL ?",
            "options": ["Height (hauteur)", "Highlight (surbrillance)", "Hexadecimal", "Hue (teinte)"],
            "correct_answer": 3,
            "type": "single",
            "explanation": "H = Hue (teinte), un angle de 0 à 360° sur le cercle chromatique.",
        },
        {
            "id": 10,
            "question": "Pourquoi terminer une liste font-family par une famille générique (sans-serif, serif...) ?",
            "options": [
                "Pour que ça marche uniquement sur mobile",
                "C'est obligatoire, sinon le CSS ne compile pas",
                "En cas d'échec de toutes les polices demandées, le navigateur utilise au moins le bon style",
                "Pour accélérer le chargement de la page",
            ],
            "correct_answer": 2,
            "type": "single",
            "explanation": "La famille générique est une police de secours ultime si aucune des polices précédentes n'est disponible.",
        },
        {
            "id": 11,
            "question": "Quelle unité est TOUJOURS relative à la taille de police de <html>, sans effet d'accumulation ?",
            "options": ["em", "px", "rem", "%"],
            "correct_answer": 2,
            "type": "single",
            "explanation": "rem (root em) est toujours relatif à <html>, contrairement à em qui dépend du parent direct et peut s'accumuler.",
        },
        {
            "id": 12,
            "question": "À quoi servent vw et vh ?",
            "options": [
                "Ce sont des unités relatives à la fenêtre du navigateur (viewport)",
                "Ce sont des raccourcis pour vertical et horizontal",
                "Ce sont des unités relatives au parent",
                "Ce sont des propriétés de couleur",
            ],
            "correct_answer": 0,
            "type": "single",
            "explanation": "1vw = 1% de la largeur du viewport, 1vh = 1% de sa hauteur.",
        },
        {
            "id": 13,
            "question": "Quel est le comportement par défaut d'un élément <div> ?",
            "options": ["inline", "inline-block", "block", "none"],
            "correct_answer": 2,
            "type": "single",
            "explanation": "<div>, <p>, <h1>... sont des éléments block par défaut : toute la largeur, saut de ligne automatique.",
        },
        {
            "id": 14,
            "question": "Quelles propriétés sont ignorées sur un élément display: inline ? (plusieurs réponses)",
            "options": ["width et height", "color", "margin-top et margin-bottom", "background-color"],
            "correct_answer": [0, 2],
            "type": "multiple",
            "explanation": "Un élément inline ignore width, height, ainsi que les marges verticales (haut/bas).",
        },
        {
            "id": 15,
            "question": "Quelle valeur de display combine \"reste sur la ligne\" ET \"accepte width/height\" ?",
            "options": ["block", "flex", "inline", "inline-block"],
            "correct_answer": 3,
            "type": "single",
            "explanation": "inline-block cumule les deux comportements, très utile pour des liens de menu par exemple.",
        },
        {
            "id": 16,
            "question": "Sur un élément carré (width = height), quelle valeur de border-radius donne un cercle parfait ?",
            "options": ["100%", "circle", "50%", "999px"],
            "correct_answer": 2,
            "type": "single",
            "explanation": "border-radius: 50% sur un élément carré donne un cercle exact.",
        },
        {
            "id": 17,
            "question": "Dans 'box-shadow: 0 4px 6px rgba(0,0,0,0.1);', que représente le 6px ?",
            "options": ["Le décalage horizontal", "Le flou de l'ombre", "Le décalage vertical", "L'épaisseur de la bordure"],
            "correct_answer": 1,
            "type": "single",
            "explanation": "L'ordre est : décalage horizontal, décalage vertical, flou, couleur.",
        },
        {
            "id": 18,
            "question": "Quelle pseudo-classe s'applique pendant qu'un champ de formulaire est actif (cliqué ou navigué au clavier) ?",
            "options": [":active", ":hover", ":checked", ":focus"],
            "correct_answer": 3,
            "type": "single",
            "explanation": ":focus s'applique quand un élément reçoit le focus, essentiel pour l'accessibilité des formulaires.",
        },
        {
            "id": 19,
            "question": "À quoi sert la propriété transition ?",
            "options": [
                "Elle rend un changement de style progressif au lieu d'instantané",
                "Elle change la couleur d'un élément au clic",
                "Elle centre un élément horizontalement",
                "Elle crée une bordure animée en pointillés",
            ],
            "correct_answer": 0,
            "type": "single",
            "explanation": "transition: propriété durée timing; adoucit un changement (ex: couleur au survol) sur une durée donnée.",
        },
        {
            "id": 20,
            "question": "Que fait le sélecteur li:last-child ?",
            "options": [
                "Il cible tous les <li> sauf le premier",
                "Il cible le dernier <li>, enfant de son parent",
                "Il cible le <li> le plus long",
                "Il cible tous les <li> d'une page",
            ],
            "correct_answer": 1,
            "type": "single",
            "explanation": ":last-child cible un élément qui est le dernier enfant de son parent — utile par exemple pour retirer une bordure en trop.",
        },
    ]

    quiz, _ = Quiz.objects.update_or_create(
        lesson=quiz_lesson,
        defaults={
            'instructions': "Testez vos connaissances sur les fondamentaux du CSS : sélecteurs, box model, couleurs, typographie, unités, display, bordures/ombres et pseudo-classes.",
            'questions': quiz_questions,
            'passing_score': 70,
            'time_limit': 20,
            'randomize_questions': False,
            'randomize_options': True,
            'max_attempts': 0,
        }
    )
    print(f"  ✅ Quiz reconstruit : {quiz.question_count} questions, {quiz.total_points} points de contenu")

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

# Plan Détaillé : Chapitre HTML Complet

## 🎯 Objectifs Pédagogiques

À la fin de ce chapitre, l'apprenant sera capable de :
- ✅ Comprendre la structure et le rôle du HTML dans le web
- ✅ Créer des pages HTML valides et sémantiques
- ✅ Utiliser les balises HTML5 modernes
- ✅ Structurer du contenu de manière accessible
- ✅ Créer des formulaires interactifs
- ✅ Intégrer des médias (images, vidéos, audio)

---

## 📚 Structure du Chapitre

**Durée totale estimée :** 6-8 heures
**Points totaux :** 500 points
**Nombre de leçons :** 15-20 leçons

---

## 📖 Section 1 : Introduction au HTML (60 min - 60 points)

### Leçon 1.1 : Qu'est-ce que le HTML ? (15 min - 10 pts)
**Type :** Théorie

**Contenu :**
- Définition du HTML (HyperText Markup Language)
- Historique rapide : HTML → HTML5
- Rôle du HTML dans la triade web (HTML/CSS/JS)
- Différence entre HTML et XHTML

**Illustrations à créer :**
- 📊 Schéma : Architecture web (Client ↔ Serveur)
- 🎨 Infographie : HTML vs CSS vs JavaScript
- 📈 Timeline : Évolution HTML 1.0 → HTML5

**Exemples :**
```html
<!-- Exemple simple -->
<!DOCTYPE html>
<html>
  <head>
    <title>Ma première page</title>
  </head>
  <body>
    <h1>Bonjour le monde !</h1>
  </body>
</html>
```

---

### Leçon 1.2 : Structure de base d'une page HTML (20 min - 10 pts)
**Type :** Théorie

**Contenu :**
- Le DOCTYPE : pourquoi et comment
- Les balises `<html>`, `<head>`, `<body>`
- Métadonnées essentielles (`<meta>`, `<title>`, `<link>`)
- Attribut `lang` pour l'accessibilité
- Encodage UTF-8

**Illustrations :**
- 🏗️ Diagramme : Anatomie d'une page HTML
- 🔍 Zoom sur les balises meta importantes

**Exemples :**
```html
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="description" content="Ma page web professionnelle">
    <title>Titre de la page - Mon site</title>
</head>
<body>
    <!-- Contenu ici -->
</body>
</html>
```

---

### Exercice 1.1 : Créer sa première page HTML (15 min - 25 pts)
**Type :** Exercice
**Difficulté :** Facile

**Instructions :**
Créez une page HTML valide avec :
1. DOCTYPE HTML5
2. Langue française
3. Charset UTF-8
4. Viewport pour responsive
5. Titre "Ma première page web"
6. Un titre h1 avec votre nom
7. Un paragraphe de présentation

**Tests automatisés :**
- ✅ DOCTYPE présent
- ✅ Attribut lang="fr"
- ✅ Meta charset UTF-8
- ✅ Meta viewport présent
- ✅ Balise title avec contenu
- ✅ Balise h1 présente
- ✅ Balise p présente

---

### Exercice 1.2 : Structure complète d'un site (10 min - 15 pts)
**Type :** Exercice
**Difficulté :** Facile

**Instructions :**
Ajoutez les métadonnées pour le SEO :
- Meta description (max 160 caractères)
- Meta keywords
- Meta author
- Lien vers une feuille de style externe

---

### Quiz 1 : Validation Structure HTML (10 min - 20 pts)
**Type :** Quiz

**Questions (5) :**
1. Que signifie HTML ? (QCM)
2. Quelle balise contient les métadonnées ? (QCM)
3. Quel DOCTYPE utiliser pour HTML5 ? (QCM)
4. Pourquoi utiliser l'attribut lang ? (QCM)
5. Quelle balise définit le titre affiché dans l'onglet ? (QCM)

---

## 📖 Section 2 : Balises de Texte et Sémantique (90 min - 100 points)

### Leçon 2.1 : Titres et Paragraphes (15 min - 10 pts)
**Type :** Théorie

**Contenu :**
- Hiérarchie des titres h1 → h6
- Règles d'utilisation (un seul h1 par page)
- Balise `<p>` pour les paragraphes
- Balises `<br>` et `<hr>` pour les séparations

**Illustrations :**
- 📊 Diagramme : Hiérarchie des titres
- ⚠️ Bonnes pratiques vs Erreurs courantes

**Exemples :**
```html
<h1>Titre Principal (un seul par page)</h1>

<h2>Section 1</h2>
<p>Ceci est un paragraphe. Le texte se retourne automatiquement.</p>

<h3>Sous-section 1.1</h3>
<p>Autre paragraphe avec du contenu.</p>

<hr> <!-- Ligne de séparation -->

<h2>Section 2</h2>
```

---

### Leçon 2.2 : Mise en forme du texte (20 min - 10 pts)
**Type :** Théorie

**Contenu :**
- Balises de style : `<strong>`, `<em>`, `<mark>`, `<small>`
- Différence sémantique vs visuelle (strong vs b, em vs i)
- Balises de citation : `<blockquote>`, `<cite>`, `<q>`
- Balises de code : `<code>`, `<pre>`, `<kbd>`, `<samp>`

**Illustrations :**
- 🎨 Tableau comparatif : Balises sémantiques vs visuelles
- 💡 Exemples visuels de rendu

**Exemples :**
```html
<!-- Emphase sémantique -->
<p>C'est <strong>très important</strong> de comprendre.</p>
<p>Le mot <em>emphase</em> signifie importance.</p>

<!-- Citations -->
<blockquote cite="https://source.com">
    Citation longue sur plusieurs lignes.
</blockquote>

<!-- Code -->
<p>Tapez <kbd>Ctrl+C</kbd> pour copier.</p>
<code>console.log('Hello')</code>
```

---

### Leçon 2.3 : Listes (15 min - 10 pts)
**Type :** Théorie

**Contenu :**
- Listes non ordonnées `<ul>` + `<li>`
- Listes ordonnées `<ol>` + `<li>`
- Listes de définitions `<dl>`, `<dt>`, `<dd>`
- Listes imbriquées

**Illustrations :**
- 📋 Exemples visuels des 3 types de listes
- 🔗 Cas d'usage : quand utiliser chaque type

**Exemples :**
```html
<!-- Liste non ordonnée -->
<ul>
    <li>Premier élément</li>
    <li>Deuxième élément</li>
    <li>Troisième élément</li>
</ul>

<!-- Liste ordonnée -->
<ol>
    <li>Étape 1</li>
    <li>Étape 2</li>
    <li>Étape 3</li>
</ol>

<!-- Liste de définitions -->
<dl>
    <dt>HTML</dt>
    <dd>HyperText Markup Language</dd>
    <dt>CSS</dt>
    <dd>Cascading Style Sheets</dd>
</dl>
```

---

### Exercice 2.1 : Créer un article de blog (20 min - 30 pts)
**Type :** Exercice
**Difficulté :** Facile

**Instructions :**
Créez un article de blog sur un sujet de votre choix avec :
- Un titre h1
- Au moins 2 sections h2
- 3 paragraphes minimum
- Utilisation de strong et em
- Une citation avec blockquote
- Une liste à puces de 5 éléments

**Tests :**
- Présence de h1, h2 (x2), p (x3)
- Utilisation de strong et em
- Blockquote présent
- Liste ul avec 5 li

---

### Exercice 2.2 : Tutoriel pas à pas (15 min - 25 pts)
**Type :** Exercice
**Difficulté :** Moyen

**Instructions :**
Créez un tutoriel "Comment faire un café" avec :
- Titre principal
- Liste ordonnée des étapes (minimum 7)
- Chaque étape avec un paragraphe d'explication
- Utilisation de kbd pour les actions (ex: "Appuyez sur START")
- Une note importante avec mark

---

### Exercice 2.3 : Page de glossaire (15 min - 25 pts)
**Type :** Exercice
**Difficulté :** Moyen

**Instructions :**
Créez un glossaire de termes web avec :
- Liste de définitions (dl, dt, dd)
- Minimum 8 termes définis
- Utilisation de code pour les exemples techniques
- Balises abbr pour les acronymes

---

### Quiz 2 : Balises de texte (10 min - 20 pts)
**Type :** Quiz

**Questions (6) :**
1. Combien de h1 peut-on avoir par page ? (QCM)
2. Quelle balise pour un texte important ? (QCM)
3. Différence entre strong et b ? (QCM)
4. Quelle balise pour une liste ordonnée ? (QCM)
5. Balise pour une citation longue ? (QCM)
6. Balise pour afficher du code ? (QCM)

---

## 📖 Section 3 : Liens et Navigation (60 min - 80 points)

### Leçon 3.1 : Les liens hypertexte (20 min - 10 pts)
**Type :** Théorie

**Contenu :**
- Balise `<a>` et attribut href
- Liens absolus vs relatifs
- Liens internes (ancres)
- Attributs : target, rel, title
- Bonnes pratiques d'accessibilité

**Illustrations :**
- 🔗 Schéma : Types de liens (absolu, relatif, ancre)
- 🎯 Tableau : Valeurs de target et rel

**Exemples :**
```html
<!-- Lien externe -->
<a href="https://google.com" target="_blank" rel="noopener">Google</a>

<!-- Lien relatif -->
<a href="/about.html">À propos</a>
<a href="../index.html">Retour accueil</a>

<!-- Ancre interne -->
<a href="#section2">Aller à la section 2</a>
<h2 id="section2">Section 2</h2>

<!-- Lien email -->
<a href="mailto:contact@example.com">Nous contacter</a>

<!-- Lien téléphone -->
<a href="tel:+33123456789">Appeler</a>
```

---

### Leçon 3.2 : Navigation et menus (20 min - 10 pts)
**Type :** Théorie

**Contenu :**
- Balise `<nav>` pour la navigation
- Structure d'un menu avec liste
- Fil d'Ariane (breadcrumb)
- Navigation secondaire

**Illustrations :**
- 🧭 Exemples de structures de navigation
- 📱 Navigation responsive

**Exemples :**
```html
<nav>
    <ul>
        <li><a href="/">Accueil</a></li>
        <li><a href="/about">À propos</a></li>
        <li><a href="/services">Services</a></li>
        <li><a href="/contact">Contact</a></li>
    </ul>
</nav>

<!-- Fil d'Ariane -->
<nav aria-label="Breadcrumb">
    <ol>
        <li><a href="/">Accueil</a></li>
        <li><a href="/category">Catégorie</a></li>
        <li aria-current="page">Page actuelle</li>
    </ol>
</nav>
```

---

### Exercice 3.1 : Menu de navigation (15 min - 30 pts)
**Type :** Exercice
**Difficulté :** Facile

**Instructions :**
Créez un menu de navigation pour un site e-commerce :
- Balise nav
- 6 liens : Accueil, Produits, Promotions, À propos, Blog, Contact
- Logo cliquable vers accueil
- Liens accessibles (title)

---

### Exercice 3.2 : Page avec ancres (15 min - 30 pts)
**Type :** Exercice
**Difficulté :** Moyen

**Instructions :**
Créez une page "FAQ" avec :
- Menu de navigation des questions (ancres)
- 5 sections avec id
- Liens pour revenir en haut
- Table des matières cliquable

---

### Quiz 3 : Liens et Navigation (10 min - 20 pts)

---

## 📖 Section 4 : Images et Médias (90 min - 100 points)

### Leçon 4.1 : Intégrer des images (25 min - 10 pts)
**Type :** Théorie

**Contenu :**
- Balise `<img>` et attributs (src, alt, width, height)
- Formats d'images (JPEG, PNG, SVG, WebP)
- Images responsives avec srcset
- Balise `<figure>` et `<figcaption>`
- Accessibilité : texte alternatif

**Illustrations :**
- 🖼️ Comparaison des formats d'images
- 📏 Responsive images avec srcset
- ♿ Importance du texte alt

**Exemples :**
```html
<!-- Image simple -->
<img src="photo.jpg" alt="Description de la photo" width="600" height="400">

<!-- Image responsive -->
<img
    src="photo-800.jpg"
    srcset="photo-400.jpg 400w, photo-800.jpg 800w, photo-1200.jpg 1200w"
    sizes="(max-width: 600px) 100vw, 50vw"
    alt="Photo responsive">

<!-- Figure avec légende -->
<figure>
    <img src="graphique.png" alt="Graphique des ventes 2024">
    <figcaption>Fig. 1 - Évolution des ventes en 2024</figcaption>
</figure>
```

---

### Leçon 4.2 : Audio et Vidéo (25 min - 10 pts)
**Type :** Théorie

**Contenu :**
- Balise `<video>` avec controls, autoplay, loop
- Balise `<audio>`
- Formats supportés
- Balise `<source>` pour compatibilité
- Sous-titres avec `<track>`

**Exemples :**
```html
<!-- Vidéo -->
<video width="640" height="360" controls poster="thumbnail.jpg">
    <source src="video.mp4" type="video/mp4">
    <source src="video.webm" type="video/webm">
    <track src="subtitles-fr.vtt" kind="subtitles" srclang="fr" label="Français">
    Votre navigateur ne supporte pas la vidéo.
</video>

<!-- Audio -->
<audio controls>
    <source src="audio.mp3" type="audio/mpeg">
    <source src="audio.ogg" type="audio/ogg">
    Votre navigateur ne supporte pas l'audio.
</audio>
```

---

### Leçon 4.3 : SVG et Canvas (20 min - 10 pts)
**Type :** Théorie

**Contenu :**
- Balise `<svg>` pour graphiques vectoriels
- Formes de base SVG
- Balise `<canvas>` pour graphiques dynamiques
- Quand utiliser SVG vs Canvas

---

### Exercices 4.1 à 4.3 : Galerie photo, Player vidéo, etc. (40 min - 70 pts)

---

## 📖 Section 5 : Tableaux (60 min - 80 points)

### Leçon 5.1 : Tableaux de base (20 min - 10 pts)
### Leçon 5.2 : Tableaux avancés (20 min - 10 pts)
### Exercices + Quiz (40 min - 60 pts)

---

## 📖 Section 6 : Formulaires (120 min - 150 points)

### Leçon 6.1 : Structure d'un formulaire (25 min - 10 pts)
### Leçon 6.2 : Types d'input (30 min - 10 pts)
### Leçon 6.3 : Validation HTML5 (25 min - 10 pts)
### Exercices + Quiz (40 min - 120 pts)

---

## 📖 Section 7 : HTML5 Sémantique (60 min - 80 points)

### Leçon 7.1 : Balises structurelles (20 min - 10 pts)
**Contenu :**
- `<header>`, `<main>`, `<footer>`
- `<article>`, `<section>`, `<aside>`
- `<nav>`, `<figure>`, `<details>`

### Leçon 7.2 : Accessibilité (20 min - 10 pts)
### Exercices + Quiz (20 min - 60 pts)

---

## 📖 Projet Final : Site Web Complet (120 min - 150 points)

**Instructions :**
Créez un site web complet sur 3-5 pages avec :
- Page d'accueil avec hero section
- Page "À propos" avec timeline
- Page "Services" avec grille de cartes
- Page "Contact" avec formulaire complet
- Navigation cohérente
- Images optimisées
- Structure sémantique HTML5
- Accessible (ARIA, alt, etc.)

**Critères d'évaluation :**
- HTML valide (W3C)
- Sémantique correcte
- Accessibilité
- Navigation fonctionnelle
- Formulaire complet
- Images avec alt
- Code propre et indenté

---

## 📊 Récapitulatif

| Section | Leçons | Exercices | Quiz | Durée | Points |
|---------|--------|-----------|------|-------|--------|
| 1. Introduction | 2 | 2 | 1 | 60 min | 60 pts |
| 2. Texte & Sémantique | 3 | 3 | 1 | 90 min | 100 pts |
| 3. Liens & Navigation | 2 | 2 | 1 | 60 min | 80 pts |
| 4. Images & Médias | 3 | 3 | 1 | 90 min | 100 pts |
| 5. Tableaux | 2 | 2 | 1 | 60 min | 80 pts |
| 6. Formulaires | 3 | 3 | 1 | 120 min | 150 pts |
| 7. HTML5 Sémantique | 2 | 2 | 1 | 60 min | 80 pts |
| 8. Projet Final | - | 1 | - | 120 min | 150 pts |
| **TOTAL** | **17** | **18** | **7** | **660 min** | **800 pts** |

---

## 🎨 Médias à Créer

### Illustrations/Diagrammes :
1. Architecture Client-Serveur
2. HTML vs CSS vs JavaScript
3. Timeline évolution HTML
4. Anatomie d'une page HTML
5. Hiérarchie des titres
6. Types de liens (schéma)
7. Formats d'images (comparaison)
8. Structure HTML5 sémantique

### Images d'exemple :
- Photos pour exercices galerie
- Icônes pour navigation
- Graphiques pour figures
- Diagrammes pour tableaux

---

## 💡 Notes pour l'Implémentation

1. **Markdown enrichi** : Utiliser des blocs de code avec coloration syntaxique
2. **Interactivité** : Prévoir des exemples "Try it yourself" (futur)
3. **Progression** : Chaque section s'appuie sur la précédente
4. **Validation** : Tests automatisés pour chaque exercice
5. **Feedback** : Messages d'encouragement et hints progressifs
6. **Accessibilité** : Exemples conformes WCAG 2.1

---

## 🚀 Prochaines Étapes

1. Valider ce plan avec vous
2. Commencer par la Section 1 complète (théorie + exercices + quiz)
3. Créer les illustrations nécessaires
4. Implémenter section par section
5. Tester avec des vrais utilisateurs
6. Ajuster selon les retours

---

**Qu'en pensez-vous ? Souhaitez-vous qu'on commence par développer la Section 1 en détail ?**

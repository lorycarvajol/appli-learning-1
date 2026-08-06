"""
Rattachement des illustrations au contenu des leçons.

## Pourquoi ce module existe

Les illustrations étaient posées par cinq scripts à la racine de `backend/`
(`update_lessons_with_images.py`, `update_css_lessons2_with_images.py`, …) qui
faisaient un `str.replace()` **sur les leçons déjà enregistrées en base**. Trois
conséquences, toutes constatées :

1. **Rejouer un `load_section_*` effaçait les images**, puisqu'il réécrivait le
   contenu depuis la source — sans que rien ne le signale. C'est ce qui a laissé
   le cours sans une seule illustration (32 PNG orphelins sur le disque, zéro
   référence en base).
2. **L'ordre d'exécution était implicite** : il fallait savoir qu'un script de
   contenu devait passer avant tel script d'images, et le savoir n'était écrit
   nulle part.
3. Deux des cinq scripts utilisaient `content.replace()` sans vérifier que
   l'ancre existait : un texte source modifié d'un caractère faisait échouer le
   remplacement **en silence**.

Ici, les règles sont **déclaratives** et appliquées par le chargeur du chapitre
lui-même, juste avant l'enregistrement. Recharger un chapitre le reconstruit
donc toujours complet, illustrations comprises.

## Deux garanties

- **Idempotent** : si l'image est déjà présente dans le contenu, la règle ne
  fait rien. On peut appliquer deux fois sans dupliquer une figure.
- **Bruyant** : si l'ancre est introuvable *et* que l'image n'est pas déjà là,
  on lève `IllustrationError`. Une illustration qui disparaît casse le
  chargement au lieu de produire une leçon silencieusement amputée.

## Ajouter une illustration

1. Dessiner le PNG (voir `content/images/`) et le déposer sous
   `media/courses/<techno>/<section>/`
2. Ajouter une règle dans `ILLUSTRATIONS`, sous le slug de la leçon
3. Recharger le chapitre — `python manage.py load_section_N_xxx --force`

Le test `test_illustrations.py` vérifie que toute image citée ici existe sur le
disque et qu'aucun fichier n'est orphelin.
"""
from dataclasses import dataclass

HTML_1 = '/media/courses/html/section1'
CSS_2 = '/media/courses/css/section2'
JS_3 = '/media/courses/javascript/section3'


class IllustrationError(RuntimeError):
    """Une ancre attendue est introuvable dans le contenu d'une leçon."""


@dataclass(frozen=True)
class Rule:
    """Une substitution unique dans le contenu d'une leçon.

    `image` n'est pas décoratif : c'est lui qui rend la règle idempotente, en
    servant de témoin de « déjà appliquée ».
    """

    anchor: str
    replacement: str
    image: str

    def apply_to(self, content, lesson_slug):
        if self.image in content:
            return content, False
        if self.anchor not in content:
            raise IllustrationError(
                f"Leçon {lesson_slug!r} : ancre introuvable pour {self.image!r}.\n"
                f"  Ancre attendue : {self.anchor[:120]!r}\n"
                f"  Le texte source de la leçon a probablement changé — "
                f"mettre à jour la règle dans content/illustrations.py."
            )
        return content.replace(self.anchor, self.replacement, 1), True


def _figure(image, caption):
    return f"![{caption}]({image})\n\n*{caption}*"


def after(anchor, image, caption):
    """Insère une figure juste après l'ancre, qui est conservée."""
    return Rule(
        anchor=anchor,
        replacement=f"{anchor}\n\n{_figure(image, caption)}",
        image=image,
    )


def instead_of(anchor, image, caption):
    """Remplace l'ancre par la figure.

    Sert pour les marqueurs « 📊 Illustration à voir » laissés dans le texte
    source, et pour les schémas ASCII que le PNG remplace avantageusement.
    """
    return Rule(anchor=anchor, replacement=_figure(image, caption), image=image)


def raw(anchor, replacement, image):
    """Règle libre, quand la substitution apporte aussi de la prose.

    Trois règles en ont besoin : elles n'ajoutent pas qu'une figure mais aussi
    un encadré ou une section entière. Le texte est conservé mot pour mot tel
    qu'il était produit par les anciens scripts.
    """
    return Rule(anchor=anchor, replacement=replacement, image=image)


# ---------------------------------------------------------------------------
# Chapitre 1 — HTML
# ---------------------------------------------------------------------------

_HTML_TIMELINE_ANCHOR = """| **Aujourd'hui** | HTML Living Standard | Évolution continue |

### 🚀 HTML5 : La révolution moderne"""

_HTML_XHTML_ANCHOR = """✅ Syntaxe plus rigoureuse

> 💡 **Aujourd'hui** : On utilise HTML5 avec de bonnes pratiques (fermer les balises, indenter, etc.) sans la rigueur excessive de XHTML."""

_HTML_SEO_SECTION = f"""{_HTML_XHTML_ANCHOR}

---

## 🔍 Comment les moteurs de recherche interprètent le HTML

Les moteurs de recherche comme Google lisent et analysent votre code HTML pour comprendre et classer vos pages.

![Anatomie d'un résultat de recherche Google]({HTML_1}/google-search-anatomy.png)

*Figure 4: Anatomie d'un résultat de recherche Google - Chaque élément provient d'une balise HTML spécifique*

**Correspondances HTML → Google :**
- `<title>` → Titre cliquable bleu
- `<meta name="description">` → Texte descriptif sous le titre
- URL de la page → Adresse verte affichée
- Balises de structure (`<h1>`, `<h2>`) → Aide au classement

> 💡 **Bon à savoir** : Un HTML bien structuré améliore votre référencement (SEO) !"""

_HTML_META_ANCHOR = """### 📋 Métadonnées essentielles

#### A. Charset (encodage des caractères)"""

_HTML_META_REPLACEMENT = f"""### 📋 Métadonnées essentielles

![Carte mentale des balises meta]({HTML_1}/html-meta-tags-mindmap.png)

*Figure 2: Les principales balises meta et leur utilité*

#### A. Charset (encodage des caractères)"""

_HTML_VIEWPORT_ANCHOR = """**Avec viewport sur mobile :**
```
📱 [Page adaptée à l'écran] ← Parfait !
```

#### C. Description (SEO)"""

_HTML_VIEWPORT_REPLACEMENT = f"""**Avec viewport sur mobile :**
```
📱 [Page adaptée à l'écran] ← Parfait !
```

![Comparaison avec et sans viewport]({HTML_1}/viewport-mobile-comparison.png)

*Figure 3: Différence d'affichage sur mobile avec et sans la balise meta viewport*

> 💡 **Impact du viewport** : Sans cette balise, les sites sont illisibles sur mobile car le navigateur affiche la version desktop rétrécie.

#### C. Description (SEO)"""


_SECTION_1_HTML = {
    'quest-ce-que-le-html': (
        Rule(
            anchor='> 📊 **Illustration à voir** : Schéma "HTML vs CSS vs JavaScript"',
            replacement=(
                f"![Comparaison HTML, CSS et JavaScript]({HTML_1}/html-css-js-comparison.png)\n\n"
                "*Figure 1: Les trois piliers du développement web - HTML structure le contenu, "
                "CSS le stylise, et JavaScript le rend interactif*"
            ),
            image=f'{HTML_1}/html-css-js-comparison.png',
        ),
        Rule(
            anchor=_HTML_TIMELINE_ANCHOR,
            replacement=(
                f"{_HTML_TIMELINE_ANCHOR}\n\n"
                f"![Chronologie de l'évolution HTML]({HTML_1}/html-evolution-timeline.png)\n\n"
                "*Figure 2: L'évolution du HTML depuis 1991 jusqu'à aujourd'hui*\n"
            ),
            image=f'{HTML_1}/html-evolution-timeline.png',
        ),
        Rule(
            anchor='> 📊 **Illustration à voir** : Schéma "Architecture Client-Serveur"',
            replacement=(
                f"![Architecture Client-Serveur]({HTML_1}/client-server-architecture.png)\n\n"
                "*Figure 3: Le cycle de communication entre le client (navigateur) et le serveur web*"
            ),
            image=f'{HTML_1}/client-server-architecture.png',
        ),
        raw(_HTML_XHTML_ANCHOR, _HTML_SEO_SECTION,
            f'{HTML_1}/google-search-anatomy.png'),
    ),
    'structure-base-page-html': (
        Rule(
            anchor='> 📊 **Illustration à voir** : Diagramme "Anatomie d\'une page HTML"',
            replacement=(
                f"![Anatomie d'une page HTML]({HTML_1}/html-document-anatomy.png)\n\n"
                "*Figure 1: Anatomie complète d'un document HTML5 - Chaque élément a un rôle spécifique*"
            ),
            image=f'{HTML_1}/html-document-anatomy.png',
        ),
        raw(_HTML_META_ANCHOR, _HTML_META_REPLACEMENT,
            f'{HTML_1}/html-meta-tags-mindmap.png'),
        raw(_HTML_VIEWPORT_ANCHOR, _HTML_VIEWPORT_REPLACEMENT,
            f'{HTML_1}/viewport-mobile-comparison.png'),
    ),
    'html-texte-titres-paragraphes': (
        after(
            """<h5>Encore plus petit</h5>
<h6>Le plus petit niveau</h6>
```""",
            f'{HTML_1}/html-heading-hierarchy.png',
            "Figure 1 : la hiérarchie des titres h1 à h6 — la taille diminue, mais c'est l'ordre qui compte",
        ),
    ),
    'html-les-listes': (
        after(
            "> 💡 **Analogie** : Une liste de courses griffonnée sur un post-it, c'est une `<ul>` (l'ordre n'a pas\n"
            "> d'importance). Une recette de cuisine avec des étapes à suivre dans l'ordre, c'est une `<ol>`.",
            f'{HTML_1}/html-lists-comparison.png',
            "Figure 1 : liste à puces (ordre indifférent) vs liste numérotée (ordre essentiel)",
        ),
    ),
    'html-liens-et-images': (
        after(
            """💡 Préciser `width`/`height` évite que la page "saute" pendant le chargement de l'image.""",
            f'{HTML_1}/html-link-image-anatomy.png',
            "Figure 1 : anatomie d'un lien et d'une image — chaque attribut a un rôle précis",
        ),
    ),
    'html-div-span-semantique': (
        after(
            """| `<footer>` | Pied de page ou de section |""",
            f'{HTML_1}/html-semantic-page-layout.png',
            "Figure 1 : plan sémantique d'une page HTML5 — header/nav, main (article + aside), footer",
        ),
    ),
    'html-les-tableaux': (
        after(
            """| `<td>` | *table data* — une cellule de donnée normale |""",
            f'{HTML_1}/html-table-anatomy.png',
            "Figure 1 : anatomie d'un tableau — table > tr (ligne) > th/td (cellules)",
        ),
    ),
    'html-les-formulaires': (
        after(
            "> 🚫 Un formulaire sans `<label>` associé est un des problèmes d'accessibilité les plus fréquents sur\n"
            "> le web — pourtant très simple à corriger.",
            f'{HTML_1}/html-form-label-anatomy.png',
            "Figure 1 : le for du label doit être identique à l'id du champ associé",
        ),
    ),
}


# ---------------------------------------------------------------------------
# Chapitre 2 — CSS
# ---------------------------------------------------------------------------

_CSS_METHODS_ANCHOR = """## 🔗 Les 3 façons d'appliquer du CSS

### 1️⃣ CSS en ligne (inline)"""

_CSS_METHODS_REPLACEMENT = f"""## 🔗 Les 3 façons d'appliquer du CSS

![Les 3 façons d'appliquer du CSS]({CSS_2}/css-application-methods.png)

*Figure 2: Comparaison des 3 méthodes pour lier du CSS à une page HTML*

### 1️⃣ CSS en ligne (inline)"""

_CSS_SELECTORS_REPLACEMENT = f"""![Récapitulatif des sélecteurs CSS]({CSS_2}/css-selectors-cheatsheet.png)

*Figure 1: Vue d'ensemble des principaux sélecteurs CSS et leur cible*

### 5️⃣ Pseudo-classes"""

# Le schéma ASCII du box model, remplacé par le PNG équivalent.
_CSS_BOX_MODEL_ASCII = """```
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
```"""

_CSS_BOX_SIZING_ANCHOR = (
    "> 🎓 **Bonne pratique universelle** : Appliquer `box-sizing: border-box` à tous les éléments "
    "via `*` en début de feuille de style. Cela simplifie énormément les calculs de mise en page."
)


_SECTION_2_CSS = {
    'quest-ce-que-le-css': (
        Rule(
            anchor=(
                "> ⚠️ **Règle importante** : Chaque déclaration se termine par un point-virgule `;`. "
                "L'oublier sur la dernière ligne fonctionne, mais c'est une mauvaise pratique."
            ),
            replacement=(
                "> ⚠️ **Règle importante** : Chaque déclaration se termine par un point-virgule `;`. "
                "L'oublier sur la dernière ligne fonctionne, mais c'est une mauvaise pratique."
                f"\n\n![Anatomie d'une règle CSS]({CSS_2}/css-rule-anatomy.png)\n\n"
                "*Figure 1: Décomposition visuelle d'une règle CSS - sélecteur, propriété et valeur*"
            ),
            image=f'{CSS_2}/css-rule-anatomy.png',
        ),
        raw(_CSS_METHODS_ANCHOR, _CSS_METHODS_REPLACEMENT,
            f'{CSS_2}/css-application-methods.png'),
    ),
    'selecteurs-et-box-model': (
        raw("### 5️⃣ Pseudo-classes", _CSS_SELECTORS_REPLACEMENT,
            f'{CSS_2}/css-selectors-cheatsheet.png'),
        Rule(
            anchor=_CSS_BOX_MODEL_ASCII,
            replacement=(
                f"![Le Box Model CSS]({CSS_2}/css-box-model.png)\n\n"
                "*Figure 2: Chaque élément HTML est une boîte composée de content, padding, "
                "border et margin*"
            ),
            image=f'{CSS_2}/css-box-model.png',
        ),
        Rule(
            anchor=_CSS_BOX_SIZING_ANCHOR,
            replacement=(
                f"{_CSS_BOX_SIZING_ANCHOR}"
                f"\n\n![content-box vs border-box]({CSS_2}/css-box-sizing-comparison.png)\n\n"
                "*Figure 3: Avec border-box, padding et border sont inclus dans la largeur définie, "
                "plus besoin de recalculer*"
            ),
            image=f'{CSS_2}/css-box-sizing-comparison.png',
        ),
    ),
    'css-les-couleurs': (
        after(
            """| HSL | `hsl(0, 100%, 50%)` | ❌ (utiliser `hsla()`) |""",
            f'{CSS_2}/css-color-formats.png',
            "Figure 1 : la même couleur écrite de 4 façons différentes",
        ),
    ),
    'css-la-typographie': (
        after(
            "> 🚫 Un `line-height` trop petit (proche de 1) rend un long paragraphe difficile à lire.\n"
            "> Une valeur entre 1.4 et 1.8 est généralement confortable pour du texte courant.",
            f'{CSS_2}/css-line-height-comparison.png',
            "Figure 1 : un line-height trop serré fatigue la lecture",
        ),
    ),
    'css-les-unites-de-mesure': (
        after(
            "> 🎓 **Bonne pratique largement adoptée** : utiliser `rem` pour les tailles de police et les\n"
            "> espacements, `%` pour les largeurs fluides, et `px` pour les détails qui ne doivent jamais changer\n"
            "> (bordures fines, par exemple).",
            f'{CSS_2}/css-units-comparison.png',
            "Figure 1 : em s'accumule à travers les imbrications, rem reste toujours stable",
        ),
    ),
    'css-display-block-inline': (
        after(
            "> 💡 **Cas d'usage classique** : des liens de menu affichés côte à côte, mais avec un `padding`\n"
            "> confortable comme des boutons — impossible avec `inline` seul, inutilement complexe avec `block`\n"
            "> seul (il faudrait flotter ou repositionner chaque élément).",
            f'{CSS_2}/css-display-comparison.png',
            "Figure 1 : block, inline et inline-block côte à côte",
        ),
    ),
    'css-bordures-arrondis-ombres': (
        after(
            "> 💡 Combiner une ombre légère par défaut et une ombre plus marquée au survol (`:hover`) est une\n"
            "> technique très courante pour donner une impression de profondeur et de réactivité aux cartes/boutons.",
            f'{CSS_2}/css-border-radius-shadow.png',
            "Figure 1 : progression de border-radius jusqu'au cercle, et intensité de box-shadow",
        ),
    ),
    'css-les-pseudo-classes': (
        after(
            "- `transition: propriété durée fonction-de-timing;`\n"
            "- `all` peut remplacer le nom de propriété pour transitionner tous les changements à la fois",
            f'{CSS_2}/css-pseudo-states.png',
            "Figure 1 : un bouton en état normal, survolé (:hover) et cliqué (:active)",
        ),
    ),
}


# ---------------------------------------------------------------------------
# Chapitre 3 — JavaScript
# ---------------------------------------------------------------------------

_SECTION_3_JS = {
    # Réutilise l'illustration du chapitre HTML : les trois piliers du web sont
    # le même schéma, inutile d'en dessiner une variante.
    'js-quest-ce-que-javascript': (
        after(
            "Sans JavaScript, une page web est **statique** : elle affiche toujours la même chose, quoi que fasse\n"
            "le visiteur.",
            f'{HTML_1}/html-css-js-comparison.png',
            "Figure 1 : HTML structure, CSS présente, JavaScript rend interactif",
        ),
    ),
    'js-variables-et-types': (
        after(
            "> 🚫 Vous verrez parfois `var` dans du code ancien : c'est l'ancienne façon de déclarer une variable,\n"
            "> avec un comportement plus difficile à prévoir. On ne l'utilise plus dans du code moderne.",
            f'{JS_3}/js-variables-types.png',
            "Figure 1 : des variables, des boîtes étiquetées avec un type et un statut",
        ),
    ),
    'js-les-conditions': (
        after(
            "Les conditions sont testées **dans l'ordre**, et dès qu'une est vraie, les suivantes sont ignorées.",
            f'{JS_3}/js-conditions-flowchart.png',
            "Figure 1 : if / else if / else, une cascade de conditions",
        ),
    ),
    'js-les-boucles': (
        after(
            """| Incrémentation | Exécutée après chaque tour | `i++` (équivaut à `i = i + 1`) |""",
            f'{JS_3}/js-boucles-anatomy.png',
            "Figure 1 : les 3 rouages d'une boucle for",
        ),
    ),
    'js-les-fonctions': (
        after(
            "> 💡 **Analogie** : une fonction est comme une recette de cuisine. Les paramètres sont les\n"
            "> ingrédients, le code à l'intérieur est la préparation, et `return` est le plat obtenu à la fin.",
            f'{JS_3}/js-fonctions-anatomy.png',
            "Figure 1 : une fonction transforme une entrée en sortie",
        ),
    ),
    'js-les-tableaux': (
        after(
            "> ⚠️ **Les index commencent à 0**, pas à 1 ! Le premier élément est `fruits[0]`, pas `fruits[1]`.\n"
            "> C'est l'une des sources de confusion les plus fréquentes chez les débutants.",
            f'{JS_3}/js-tableaux-index.png',
            "Figure 1 : un tableau et ses index, à partir de 0",
        ),
    ),
    'js-manipuler-le-dom': (
        after(
            "`document.querySelector(selecteur)` accepte **exactement la même syntaxe** que les sélecteurs CSS que\n"
            "vous connaissez déjà (`h1`, `.classe`, `#id`) — et renvoie le **premier** élément qui correspond.",
            f'{JS_3}/js-dom-tree.png',
            "Figure 1 : le DOM est un arbre, querySelector y trouve un nœud",
        ),
    ),
    'js-les-evenements': (
        after(
            "> 💡 La fonction callback n'est **pas appelée tout de suite** : elle est \"mise de côté\" et exécutée\n"
            "> **plus tard**, uniquement quand l'événement se produit réellement (le clic).",
            f'{JS_3}/js-evenements-flow.png',
            "Figure 1 : le cycle clic → événement → callback → mise à jour",
        ),
    ),
}


ILLUSTRATIONS = {**_SECTION_1_HTML, **_SECTION_2_CSS, **_SECTION_3_JS}


# ---------------------------------------------------------------------------
# API
# ---------------------------------------------------------------------------

def attach(lesson_slug, content):
    """Renvoie le contenu enrichi des illustrations prévues pour cette leçon.

    Sans règle pour ce slug, le contenu ressort inchangé — la majorité des
    leçons (exercices, quiz, chapitre 4) n'a pas d'illustration.
    """
    for rule in ILLUSTRATIONS.get(lesson_slug, ()):
        content, _ = rule.apply_to(content, lesson_slug)
    return content


def attach_to_chapter(chapter, stdout=None):
    """Applique les règles aux leçons **déjà enregistrées** d'un chapitre.

    Utile pour rattraper un contenu chargé avant l'existence de ce module ;
    les chargeurs, eux, appellent `attach()` avant d'écrire.
    """
    touched = 0
    for lesson in chapter.lessons.all():
        rules = ILLUSTRATIONS.get(lesson.slug)
        if not rules:
            continue
        content = lesson.content or ''
        changed = False
        for rule in rules:
            content, applied = rule.apply_to(content, lesson.slug)
            changed = changed or applied
        if changed:
            lesson.content = content
            lesson.save(update_fields=['content', 'updated_at'])
            touched += 1
            if stdout:
                stdout.write(f'    🖼️  illustrations : {lesson.title}')
    return touched


def referenced_images():
    """Chemins d'images cités par les règles, pour les tests de cohérence."""
    return {rule.image for rules in ILLUSTRATIONS.values() for rule in rules}

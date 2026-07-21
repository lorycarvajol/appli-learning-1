#!/usr/bin/env python
"""
Intègre les 7 illustrations dans le contenu des leçons JavaScript
correspondantes, et réutilise l'illustration HTML/CSS/JS existante pour la
leçon d'introduction.
"""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
django.setup()

from apps.courses.models import Lesson


def insert_after(content, anchor, insertion):
    if anchor not in content:
        raise ValueError(f"Anchor not found: {anchor[:80]!r}")
    return content.replace(anchor, anchor + insertion, 1)


def update(slug, anchor, image_path, caption):
    lesson = Lesson.objects.get(slug=slug)
    insertion = f"\n\n![{caption}]({image_path})\n\n*{caption}*"
    lesson.content = insert_after(lesson.content, anchor, insertion)
    lesson.save()
    print(f"✅ {lesson.title}")


# Réutilise l'illustration déjà créée pour le chapitre HTML (les 3 piliers)
update(
    'js-quest-ce-que-javascript',
    """Sans JavaScript, une page web est **statique** : elle affiche toujours la même chose, quoi que fasse
le visiteur.""",
    '/media/courses/html/section1/html-css-js-comparison.png',
    "Figure 1 : HTML structure, CSS présente, JavaScript rend interactif",
)

update(
    'js-variables-et-types',
    """> 🚫 Vous verrez parfois `var` dans du code ancien : c'est l'ancienne façon de déclarer une variable,
> avec un comportement plus difficile à prévoir. On ne l'utilise plus dans du code moderne.""",
    '/media/courses/javascript/section3/js-variables-types.png',
    "Figure 1 : des variables, des boîtes étiquetées avec un type et un statut",
)

update(
    'js-les-conditions',
    """Les conditions sont testées **dans l'ordre**, et dès qu'une est vraie, les suivantes sont ignorées.""",
    '/media/courses/javascript/section3/js-conditions-flowchart.png',
    "Figure 1 : if / else if / else, une cascade de conditions",
)

update(
    'js-les-boucles',
    """| Incrémentation | Exécutée après chaque tour | `i++` (équivaut à `i = i + 1`) |""",
    '/media/courses/javascript/section3/js-boucles-anatomy.png',
    "Figure 1 : les 3 rouages d'une boucle for",
)

update(
    'js-les-fonctions',
    """> 💡 **Analogie** : une fonction est comme une recette de cuisine. Les paramètres sont les
> ingrédients, le code à l'intérieur est la préparation, et `return` est le plat obtenu à la fin.""",
    '/media/courses/javascript/section3/js-fonctions-anatomy.png',
    "Figure 1 : une fonction transforme une entrée en sortie",
)

update(
    'js-les-tableaux',
    """> ⚠️ **Les index commencent à 0**, pas à 1 ! Le premier élément est `fruits[0]`, pas `fruits[1]`.
> C'est l'une des sources de confusion les plus fréquentes chez les débutants.""",
    '/media/courses/javascript/section3/js-tableaux-index.png',
    "Figure 1 : un tableau et ses index, à partir de 0",
)

update(
    'js-manipuler-le-dom',
    """`document.querySelector(selecteur)` accepte **exactement la même syntaxe** que les sélecteurs CSS que
vous connaissez déjà (`h1`, `.classe`, `#id`) — et renvoie le **premier** élément qui correspond.""",
    '/media/courses/javascript/section3/js-dom-tree.png',
    "Figure 1 : le DOM est un arbre, querySelector y trouve un nœud",
)

update(
    'js-les-evenements',
    """> 💡 La fonction callback n'est **pas appelée tout de suite** : elle est "mise de côté" et exécutée
> **plus tard**, uniquement quand l'événement se produit réellement (le clic).""",
    '/media/courses/javascript/section3/js-evenements-flow.png',
    "Figure 1 : le cycle clic → événement → callback → mise à jour",
)

print("\n✨ Toutes les illustrations sont intégrées.")

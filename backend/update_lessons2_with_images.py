#!/usr/bin/env python
"""
Intègre les 6 nouvelles illustrations dans le contenu des leçons
correspondantes du chapitre HTML.
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


def update(slug, anchor, image_file, caption):
    lesson = Lesson.objects.get(slug=slug)
    insertion = f"\n\n![{caption}](/media/courses/html/section1/{image_file})\n\n*{caption}*"
    lesson.content = insert_after(lesson.content, anchor, insertion)
    lesson.save()
    print(f"✅ {lesson.title}")


update(
    'html-texte-titres-paragraphes',
    """<h5>Encore plus petit</h5>
<h6>Le plus petit niveau</h6>
```""",
    'html-heading-hierarchy.png',
    "Figure 1 : la hiérarchie des titres h1 à h6 — la taille diminue, mais c'est l'ordre qui compte",
)

update(
    'html-les-listes',
    '> 💡 **Analogie** : Une liste de courses griffonnée sur un post-it, c\'est une `<ul>` (l\'ordre n\'a pas\n> d\'importance). Une recette de cuisine avec des étapes à suivre dans l\'ordre, c\'est une `<ol>`.',
    'html-lists-comparison.png',
    "Figure 1 : liste à puces (ordre indifférent) vs liste numérotée (ordre essentiel)",
)

update(
    'html-liens-et-images',
    """💡 Préciser `width`/`height` évite que la page "saute" pendant le chargement de l'image.""",
    'html-link-image-anatomy.png',
    "Figure 1 : anatomie d'un lien et d'une image — chaque attribut a un rôle précis",
)

update(
    'html-div-span-semantique',
    """| `<footer>` | Pied de page ou de section |""",
    'html-semantic-page-layout.png',
    "Figure 1 : plan sémantique d'une page HTML5 — header/nav, main (article + aside), footer",
)

update(
    'html-les-tableaux',
    """| `<td>` | *table data* — une cellule de donnée normale |""",
    'html-table-anatomy.png',
    "Figure 1 : anatomie d'un tableau — table > tr (ligne) > th/td (cellules)",
)

update(
    'html-les-formulaires',
    """> 🚫 Un formulaire sans `<label>` associé est un des problèmes d'accessibilité les plus fréquents sur
> le web — pourtant très simple à corriger.""",
    'html-form-label-anatomy.png',
    "Figure 1 : le for du label doit être identique à l'id du champ associé",
)

print("\n✨ Toutes les illustrations sont intégrées.")

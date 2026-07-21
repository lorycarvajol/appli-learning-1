#!/usr/bin/env python
"""
Intègre les 6 nouvelles illustrations dans le contenu des leçons CSS
correspondantes.
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
    insertion = f"\n\n![{caption}](/media/courses/css/section2/{image_file})\n\n*{caption}*"
    lesson.content = insert_after(lesson.content, anchor, insertion)
    lesson.save()
    print(f"✅ {lesson.title}")


update(
    'css-les-couleurs',
    """| HSL | `hsl(0, 100%, 50%)` | ❌ (utiliser `hsla()`) |""",
    'css-color-formats.png',
    "Figure 1 : la même couleur écrite de 4 façons différentes",
)

update(
    'css-la-typographie',
    """> 🚫 Un `line-height` trop petit (proche de 1) rend un long paragraphe difficile à lire.
> Une valeur entre 1.4 et 1.8 est généralement confortable pour du texte courant.""",
    'css-line-height-comparison.png',
    "Figure 1 : un line-height trop serré fatigue la lecture",
)

update(
    'css-les-unites-de-mesure',
    """> 🎓 **Bonne pratique largement adoptée** : utiliser `rem` pour les tailles de police et les
> espacements, `%` pour les largeurs fluides, et `px` pour les détails qui ne doivent jamais changer
> (bordures fines, par exemple).""",
    'css-units-comparison.png',
    "Figure 1 : em s'accumule à travers les imbrications, rem reste toujours stable",
)

update(
    'css-display-block-inline',
    """> 💡 **Cas d'usage classique** : des liens de menu affichés côte à côte, mais avec un `padding`
> confortable comme des boutons — impossible avec `inline` seul, inutilement complexe avec `block`
> seul (il faudrait flotter ou repositionner chaque élément).""",
    'css-display-comparison.png',
    "Figure 1 : block, inline et inline-block côte à côte",
)

update(
    'css-bordures-arrondis-ombres',
    """> 💡 Combiner une ombre légère par défaut et une ombre plus marquée au survol (`:hover`) est une
> technique très courante pour donner une impression de profondeur et de réactivité aux cartes/boutons.""",
    'css-border-radius-shadow.png',
    "Figure 1 : progression de border-radius jusqu'au cercle, et intensité de box-shadow",
)

update(
    'css-les-pseudo-classes',
    """- `transition: propriété durée fonction-de-timing;`
- `all` peut remplacer le nom de propriété pour transitionner tous les changements à la fois""",
    'css-pseudo-states.png',
    "Figure 1 : un bouton en état normal, survolé (:hover) et cliqué (:active)",
)

print("\n✨ Toutes les illustrations sont intégrées.")

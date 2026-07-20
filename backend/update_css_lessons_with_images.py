#!/usr/bin/env python
"""
Script pour intégrer les images dans les leçons CSS (section 2)
"""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
django.setup()

from apps.courses.models import Lesson


def update_lesson_1():
    """Intègre les images dans la leçon: Qu'est-ce que le CSS ?"""
    print("📝 Mise à jour de la leçon 2.1...")

    lesson = Lesson.objects.get(slug='quest-ce-que-le-css')
    content = lesson.content

    # 1. Image d'anatomie d'une règle CSS, juste après l'exemple concret de syntaxe
    anchor_1 = """> ⚠️ **Règle importante** : Chaque déclaration se termine par un point-virgule `;`. L'oublier sur la dernière ligne fonctionne, mais c'est une mauvaise pratique."""

    content = content.replace(
        anchor_1,
        anchor_1 + '\n\n![Anatomie d\'une règle CSS](/media/courses/css/section2/css-rule-anatomy.png)\n\n*Figure 1: Décomposition visuelle d\'une règle CSS - sélecteur, propriété et valeur*'
    )

    # 2. Image comparative des 3 méthodes, avant le détail de chaque méthode
    anchor_2 = """## 🔗 Les 3 façons d'appliquer du CSS

### 1️⃣ CSS en ligne (inline)"""

    content = content.replace(
        anchor_2,
        """## 🔗 Les 3 façons d'appliquer du CSS

![Les 3 façons d'appliquer du CSS](/media/courses/css/section2/css-application-methods.png)

*Figure 2: Comparaison des 3 méthodes pour lier du CSS à une page HTML*

### 1️⃣ CSS en ligne (inline)"""
    )

    lesson.content = content
    lesson.save()
    print("✅ Leçon 2.1 mise à jour avec succès!")
    print("   - css-rule-anatomy.png")
    print("   - css-application-methods.png")


def update_lesson_2():
    """Intègre les images dans la leçon: Sélecteurs et Box Model"""
    print("\n📝 Mise à jour de la leçon 2.2...")

    lesson = Lesson.objects.get(slug='selecteurs-et-box-model')
    content = lesson.content

    # 1. Cheatsheet des sélecteurs, juste avant les pseudo-classes (fin de la section sélecteurs)
    anchor_1 = """### 5️⃣ Pseudo-classes"""

    content = content.replace(
        anchor_1,
        """![Récapitulatif des sélecteurs CSS](/media/courses/css/section2/css-selectors-cheatsheet.png)

*Figure 1: Vue d'ensemble des principaux sélecteurs CSS et leur cible*

### 5️⃣ Pseudo-classes"""
    )

    # 2. Diagramme du box model, en remplacement du schéma ASCII existant
    anchor_2 = """```
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

    content = content.replace(
        anchor_2,
        """![Le Box Model CSS](/media/courses/css/section2/css-box-model.png)

*Figure 2: Chaque élément HTML est une boîte composée de content, padding, border et margin*"""
    )

    # 3. Comparaison content-box vs border-box, après l'explication de box-sizing
    anchor_3 = """> 🎓 **Bonne pratique universelle** : Appliquer `box-sizing: border-box` à tous les éléments via `*` en début de feuille de style. Cela simplifie énormément les calculs de mise en page."""

    content = content.replace(
        anchor_3,
        anchor_3 + '\n\n![content-box vs border-box](/media/courses/css/section2/css-box-sizing-comparison.png)\n\n*Figure 3: Avec border-box, padding et border sont inclus dans la largeur définie, plus besoin de recalculer*'
    )

    lesson.content = content
    lesson.save()
    print("✅ Leçon 2.2 mise à jour avec succès!")
    print("   - css-selectors-cheatsheet.png")
    print("   - css-box-model.png")
    print("   - css-box-sizing-comparison.png")


if __name__ == '__main__':
    print("🚀 Démarrage de l'intégration des images dans les leçons CSS\n")
    print("=" * 70)

    try:
        update_lesson_1()
        update_lesson_2()

        print("\n" + "=" * 70)
        print("✨ Toutes les images ont été intégrées avec succès!")
        print("\n📁 Images utilisées:")
        print("   Leçon 2.1: 2 images")
        print("   Leçon 2.2: 3 images")
        print("\n💡 Conseil: Vérifiez l'affichage dans le frontend à http://localhost:5173")

    except Exception as e:
        print(f"\n❌ Erreur: {e}")
        import traceback
        traceback.print_exc()

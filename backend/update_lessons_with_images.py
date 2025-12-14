#!/usr/bin/env python
"""
Script pour intégrer les images dans les leçons HTML
"""

import os
import django

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
django.setup()

from apps.courses.models import Lesson

def update_lesson_1():
    """Intègre les images dans la leçon 1: Qu'est-ce que le HTML ?"""
    print("📝 Mise à jour de la leçon 1...")

    lesson = Lesson.objects.get(slug='quest-ce-que-le-html')
    content = lesson.content

    # 1. Remplacer le commentaire pour HTML vs CSS vs JavaScript
    content = content.replace(
        '> 📊 **Illustration à voir** : Schéma "HTML vs CSS vs JavaScript"',
        '![Comparaison HTML, CSS et JavaScript](/media/courses/html/section1/html-css-js-comparison.png)\n\n*Figure 1: Les trois piliers du développement web - HTML structure le contenu, CSS le stylise, et JavaScript le rend interactif*'
    )

    # 2. Ajouter l'image de la timeline HTML juste après le tableau d'évolution
    timeline_section = """| **Aujourd'hui** | HTML Living Standard | Évolution continue |

### 🚀 HTML5 : La révolution moderne"""

    content = content.replace(
        timeline_section,
        timeline_section + '\n\n![Chronologie de l\'évolution HTML](/media/courses/html/section1/html-evolution-timeline.png)\n\n*Figure 2: L\'évolution du HTML depuis 1991 jusqu\'à aujourd\'hui*\n'
    )

    # 3. Remplacer le commentaire pour Architecture Client-Serveur
    content = content.replace(
        '> 📊 **Illustration à voir** : Schéma "Architecture Client-Serveur"',
        '![Architecture Client-Serveur](/media/courses/html/section1/client-server-architecture.png)\n\n*Figure 3: Le cycle de communication entre le client (navigateur) et le serveur web*'
    )

    # 4. Ajouter l'image de l'anatomie Google dans la section SEO (avant "### 🚀 HTML5")
    # Trouver un bon endroit pour cette image - après la section XHTML
    xhtml_end = """✅ Syntaxe plus rigoureuse

> 💡 **Aujourd'hui** : On utilise HTML5 avec de bonnes pratiques (fermer les balises, indenter, etc.) sans la rigueur excessive de XHTML."""

    content = content.replace(
        xhtml_end,
        xhtml_end + '\n\n---\n\n## 🔍 Comment les moteurs de recherche interprètent le HTML\n\nLes moteurs de recherche comme Google lisent et analysent votre code HTML pour comprendre et classer vos pages.\n\n![Anatomie d\'un résultat de recherche Google](/media/courses/html/section1/google-search-anatomy.png)\n\n*Figure 4: Anatomie d\'un résultat de recherche Google - Chaque élément provient d\'une balise HTML spécifique*\n\n**Correspondances HTML → Google :**\n- `<title>` → Titre cliquable bleu\n- `<meta name="description">` → Texte descriptif sous le titre\n- URL de la page → Adresse verte affichée\n- Balises de structure (`<h1>`, `<h2>`) → Aide au classement\n\n> 💡 **Bon à savoir** : Un HTML bien structuré améliore votre référencement (SEO) !'
    )

    lesson.content = content
    lesson.save()
    print("✅ Leçon 1 mise à jour avec succès!")
    print(f"   - html-css-js-comparison.png")
    print(f"   - html-evolution-timeline.png")
    print(f"   - client-server-architecture.png")
    print(f"   - google-search-anatomy.png")

def update_lesson_2():
    """Intègre les images dans la leçon 2: Structure de base d'une page HTML"""
    print("\n📝 Mise à jour de la leçon 2...")

    lesson = Lesson.objects.get(slug='structure-base-page-html')
    content = lesson.content

    # 1. Remplacer le commentaire pour l'anatomie d'une page HTML
    content = content.replace(
        '> 📊 **Illustration à voir** : Diagramme "Anatomie d\'une page HTML"',
        '![Anatomie d\'une page HTML](/media/courses/html/section1/html-document-anatomy.png)\n\n*Figure 1: Anatomie complète d\'un document HTML5 - Chaque élément a un rôle spécifique*'
    )

    # 2. Ajouter l'image du mindmap des meta tags après la section "📋 Métadonnées essentielles"
    meta_section = """### 📋 Métadonnées essentielles

#### A. Charset (encodage des caractères)"""

    content = content.replace(
        meta_section,
        """### 📋 Métadonnées essentielles

![Carte mentale des balises meta](/media/courses/html/section1/html-meta-tags-mindmap.png)

*Figure 2: Les principales balises meta et leur utilité*

#### A. Charset (encodage des caractères)"""
    )

    # 3. Ajouter l'image de comparaison viewport après l'explication du viewport
    viewport_explanation = """**Avec viewport sur mobile :**
```
📱 [Page adaptée à l'écran] ← Parfait !
```

#### C. Description (SEO)"""

    content = content.replace(
        viewport_explanation,
        """**Avec viewport sur mobile :**
```
📱 [Page adaptée à l'écran] ← Parfait !
```

![Comparaison avec et sans viewport](/media/courses/html/section1/viewport-mobile-comparison.png)

*Figure 3: Différence d'affichage sur mobile avec et sans la balise meta viewport*

> 💡 **Impact du viewport** : Sans cette balise, les sites sont illisibles sur mobile car le navigateur affiche la version desktop rétrécie.

#### C. Description (SEO)"""
    )

    lesson.content = content
    lesson.save()
    print("✅ Leçon 2 mise à jour avec succès!")
    print(f"   - html-document-anatomy.png")
    print(f"   - html-meta-tags-mindmap.png")
    print(f"   - viewport-mobile-comparison.png")

if __name__ == '__main__':
    print("🚀 Démarrage de l'intégration des images dans les leçons HTML\n")
    print("="*70)

    try:
        update_lesson_1()
        update_lesson_2()

        print("\n" + "="*70)
        print("✨ Toutes les images ont été intégrées avec succès!")
        print("\n📁 Images utilisées:")
        print("   Leçon 1: 4 images")
        print("   Leçon 2: 3 images")
        print("\n💡 Conseil: Vérifiez l'affichage dans le frontend à http://localhost:5173")

    except Exception as e:
        print(f"\n❌ Erreur: {e}")
        import traceback
        traceback.print_exc()

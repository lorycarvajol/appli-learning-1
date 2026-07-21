"""
Catalogue d'avatars.

### Pourquoi un catalogue plutôt qu'un téléversement

`Profile.avatar` (un `ImageField`) existe depuis l'origine mais n'a jamais été
alimenté. On ne l'active pas : sur une plateforme scolaire dépourvue d'outil de
modération, laisser un apprenant envoyer une image quelconque signifie que
n'importe quoi peut apparaître à côté de son nom dans le tableau de bord du
formateur, et que personne ne dispose du moyen de le retirer. S'ajoutent la
liste blanche de formats (un SVG téléversé est un vecteur de XSS), les bombes
de décompression, et le stockage à sauvegarder.

Un identifiant choisi dans une liste close supprime tout cela d'un coup : rien
n'est stocké, rien n'est servi, et le rendu se fait en SVG côté client.

### La forme de la clé

`<motif>-<palette>`, par exemple `orbit-violet`. Deux petites listes valent
mieux qu'une énumération de trente-six combinaisons : ajouter une palette
enrichit tous les motifs à la fois.

⚠️ Les deux listes sont **dupliquées côté client** dans
`frontend/src/features/profile/avatars.js`, qui fait le rendu. Ajouter un motif
ici sans l'ajouter là produit un avatar vide. Un test verrouille le format des
clés, pas cette correspondance — elle relève de la relecture.
"""

MOTIFS = ('orbit', 'prism', 'wave', 'bloom', 'spark', 'mesh')

PALETTES = ('violet', 'amber', 'teal', 'rose', 'indigo', 'lime')

#: Valeur signifiant « pas de choix » : on retombe sur les initiales colorées.
DEFAULT_AVATAR_KEY = ''


def avatar_choices():
    """Toutes les clés valides, dans un ordre stable."""
    return [f'{motif}-{palette}' for motif in MOTIFS for palette in PALETTES]


def is_valid_avatar_key(key):
    """Vrai si la clé est vide (initiales) ou présente au catalogue.

    La validation est **côté serveur** : sans elle, un `PATCH` pourrait poser
    une chaîne arbitraire, qui finirait interpolée dans le rendu du client.
    """
    if not key:
        return True
    return key in set(avatar_choices())

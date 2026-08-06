"""
Catalogue d'avatars.

### Pourquoi un catalogue plutôt qu'un téléversement

`Profile.avatar` (un `ImageField`) existait depuis l'origine mais n'a jamais été
alimenté ; il a été supprimé (migration `0007`). On ne réactive pas le
téléversement : sur une plateforme scolaire dépourvue d'outil de modération,
laisser un apprenant envoyer une image quelconque signifie que n'importe quoi
peut apparaître à côté de son nom dans le tableau de bord du formateur, et que
personne ne dispose du moyen de le retirer. S'ajoutent la liste blanche de
formats (un SVG téléversé est un vecteur de XSS), les bombes de décompression,
et le stockage à sauvegarder.

Un identifiant choisi dans une liste close supprime tout cela d'un coup : rien
n'est stocké, rien n'est servi, et le rendu se fait côté client.

### Des visages, et non plus des formes abstraites

Le catalogue a longtemps été **volontairement abstrait** (orbit, prism, wave…),
pour ne pas avoir à arbitrer des représentations — teintes de peau, genres,
cultures — qu'une poignée de dessins ne peut pas rendre justement.

Ce choix a été levé au profit de visages illustrés, ce qui répond mieux à
l'attente d'un avatar de profil. L'objection d'origine tient toujours, mais
elle est désormais traitée par le volume : le rendu s'appuie sur **Notionists**
(via DiceBear), dont chaque graine combine coiffure, traits, teint et
accessoires. Le choix reste à l'apprenant, dans une liste que personne d'autre
ne peut alimenter.

⚠️ Les visages sont générés **hors ligne, dans le navigateur**, par le paquet
npm `@dicebear/collection` — **jamais** par l'API HTTP de DiceBear. Appeler un
service tiers enverrait l'adresse IP de chaque apprenant à chaque affichage de
page, ce qui ferait tomber la raison même pour laquelle l'application n'a pas
de bannière de consentement (aucun traceur tiers, cf. la section RGPD de
`CLAUDE.md`). Ne pas « simplifier » en passant par une URL distante.

Licence du style : **CC0 1.0** (Notionists, par Zoish) — domaine public, aucune
obligation d'attribution. Si un jour un autre style est retenu, vérifier sa
licence dans `collection[style].meta.license` : plusieurs styles de la même
bibliothèque sont en CC BY 4.0 et imposeraient une mention.

### La forme de la clé

`<visage>-<palette>`, par exemple `nova-violet`. Deux petites listes valent
mieux qu'une énumération de trente-six combinaisons : ajouter une palette
enrichit tous les visages à la fois.

⚠️ Les deux listes sont **dupliquées côté client** dans
`frontend/src/features/profile/avatars.js`, qui fait le rendu. Ajouter un
visage ici sans l'ajouter là produit un avatar vide. Un test verrouille le
format des clés, pas cette correspondance — elle relève de la relecture.
"""

#: Graines DiceBear. La valeur *est* la graine : la changer change le visage
#: rendu chez tous ceux qui l'avaient choisi. Ne pas renommer à la légère.
VISAGES = ('nova', 'atlas', 'vega', 'orion', 'lyra', 'sol')

PALETTES = ('violet', 'amber', 'teal', 'rose', 'indigo', 'lime')

#: Valeur signifiant « pas de choix » : on retombe sur les initiales colorées.
DEFAULT_AVATAR_KEY = ''


def avatar_choices():
    """Toutes les clés valides, dans un ordre stable."""
    return [f'{visage}-{palette}' for visage in VISAGES for palette in PALETTES]


def is_valid_avatar_key(key):
    """Vrai si la clé est vide (initiales) ou présente au catalogue.

    La validation est **côté serveur** : sans elle, un `PATCH` pourrait poser
    une chaîne arbitraire, qui finirait interpolée dans le rendu du client.
    """
    if not key:
        return True
    return key in set(avatar_choices())

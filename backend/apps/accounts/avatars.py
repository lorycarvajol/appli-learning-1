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
elle est désormais traitée par le volume : le rendu s'appuie sur **sept
familles DiceBear** de six visages chacune, dont chaque graine combine
coiffure, traits, teint et accessoires. Le choix reste à l'apprenant, dans une
liste que personne d'autre ne peut alimenter.

⚠️ Les visages sont **pré-générés à la construction** par le paquet npm
`@dicebear/collection`, puis versionnés en SVG — **jamais** servis par l'API
HTTP de DiceBear. Appeler un service tiers enverrait l'adresse IP de chaque
apprenant à chaque affichage de page, ce qui ferait tomber la raison même pour
laquelle l'application n'a pas de bannière de consentement (aucun traceur
tiers, cf. la section RGPD de `CLAUDE.md`). Ne pas « simplifier » en passant
par une URL distante.

### Licences — la seule contrainte juridique du catalogue

Notionists est en **CC0 1.0** (domaine public, rien à faire). Les six familles
ajoutées ensuite ne le sont pas :

- **CC BY 4.0** — Adventurer et Adventurer Neutral (Lisa Wischofsky),
  Big Smile (Ashley Seo), ToonHead (Johan Melin). L'attribution est
  **obligatoire** : elle est portée sous chaque famille du sélecteur d'avatar
  et dans les mentions légales (`frontend/src/features/legal/LegalNotice.jsx`).
- **« Free for personal and commercial use »** — Avataaars et Bottts
  (Pablo Stanley). Rien n'est exigé ; on crédite pareil.

⚠️ Avant d'ajouter ou de changer une famille, vérifier
`collection[style].meta.license`. Le script `frontend/scripts/generate-avatars.mjs`
confronte automatiquement les crédits affichés à ces métadonnées et **échoue**
en cas d'écart : une attribution fausse est pire qu'une attribution absente.

### La forme de la clé

`<visage>-<palette>`, par exemple `nova-violet`. Deux petites listes valent
mieux qu'une énumération de deux cent cinquante-deux combinaisons : ajouter une
palette enrichit tous les visages à la fois.

⚠️ Un identifiant de visage **ne peut pas contenir de tiret** : le client
découpe la clé sur ce caractère. D'où `adventurerneutral1` plutôt que
`adventurer-neutral-1`.

⚠️ Les deux listes sont **dupliquées côté client** dans
`frontend/src/features/profile/avatarCatalog.js`, qui porte en plus les
graines, les réglages de cadrage et les crédits. Ajouter un visage ici sans
l'ajouter là produit un avatar vide. Un test verrouille le format des clés, pas
cette correspondance — elle relève de la relecture.
"""

#: Graines DiceBear, groupées par famille dans l'ordre du sélecteur. La valeur
#: *est* la graine **et** ce qui est stocké en base : la changer change le
#: visage rendu chez tous ceux qui l'avaient choisi, et invalide leur clé
#: enregistrée. Ajouter, oui ; renommer, jamais.
VISAGES = (
    # Notionists — Zoish, CC0 1.0
    'nova', 'atlas', 'vega', 'orion', 'lyra', 'sol',
    # Adventurer — Lisa Wischofsky, CC BY 4.0
    'adventurer1', 'adventurer2', 'adventurer3',
    'adventurer4', 'adventurer5', 'adventurer6',
    # Adventurer Neutral — Lisa Wischofsky, CC BY 4.0
    'adventurerneutral1', 'adventurerneutral2', 'adventurerneutral3',
    'adventurerneutral4', 'adventurerneutral5', 'adventurerneutral6',
    # Avataaars — Pablo Stanley, free for personal and commercial use
    'avataaars1', 'avataaars2', 'avataaars3',
    'avataaars4', 'avataaars5', 'avataaars6',
    # Big Smile — Ashley Seo, CC BY 4.0
    'bigsmile1', 'bigsmile2', 'bigsmile3',
    'bigsmile4', 'bigsmile5', 'bigsmile6',
    # Bottts — Pablo Stanley, free for personal and commercial use
    'bottts1', 'bottts2', 'bottts3',
    'bottts4', 'bottts5', 'bottts6',
    # ToonHead — Johan Melin, CC BY 4.0
    'toonhead1', 'toonhead2', 'toonhead3',
    'toonhead4', 'toonhead5', 'toonhead6',
)

PALETTES = ('violet', 'amber', 'teal', 'rose', 'indigo', 'lime')

#: Bordures possibles autour de la vignette.
#:
#: ⚠️ **Champ séparé, et non un troisième segment de la clé.** La clé
#: `<visage>-<palette>` est découpée sur le tiret côté client ; y ajouter une
#: bordure aurait invalidé d'un coup **toutes** les clés déjà enregistrées, et
#: interdit à jamais un tiret dans un nom de bordure. Un champ à part se
#: valide seul, se laisse vide, et n'a aucun effet sur l'existant.
#:
#: La chaîne vide signifie « aucune bordure » — c'est le défaut, et il doit le
#: rester : un avatar sans bordure est l'état neutre, pas un choix par défaut
#: imposé.
BORDURES = ('', 'clair', 'sombre', 'double', 'lueur')

#: Valeur signifiant « pas de choix » : on retombe sur les initiales colorées.
DEFAULT_AVATAR_KEY = ''

#: Idem pour la bordure.
DEFAULT_AVATAR_BORDER = ''


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


def is_valid_avatar_border(border):
    """Vrai si la bordure est vide (aucune) ou présente au catalogue.

    Même raison qu'`is_valid_avatar_key` : sans ce contrôle, un `PATCH`
    poserait une chaîne arbitraire que le client interpolerait dans un nom de
    classe ou un attribut SVG.
    """
    return (border or '') in set(BORDURES)

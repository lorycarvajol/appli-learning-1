/**
 * Catalogue des visages d'avatar : **données seules**, aucun import d'image.
 *
 * ### Pourquoi un fichier à part
 *
 * Trois consommateurs ont besoin de la même liste, et deux d'entre eux ne
 * peuvent pas charger les autres :
 *
 * | Consommateur | Ce qu'il en fait |
 * |---|---|
 * | `scripts/generate-avatars.mjs` | dessine les SVG (Node — ne sait pas importer un `.svg`) |
 * | `features/profile/avatars.js` | associe chaque visage à son fichier et le rend |
 * | `features/profile/ProfilePage.jsx` | groupe le sélecteur par famille, affiche les crédits |
 *
 * En gardant ce module **sans aucun import**, le script de génération peut le
 * lire tel quel. C'est ce qui évite une troisième recopie de la liste : il n'en
 * reste qu'une, côté serveur (`backend/apps/accounts/avatars.py`), qui est
 * l'autorité sur ce qui est acceptable et ne dessine rien.
 *
 * ### Les identifiants sont gravés
 *
 * ⚠️ L'identifiant d'un visage est **par défaut** la graine DiceBear, et c'est
 * la valeur stockée en base (`Profile.avatar_key` vaut `<visage>-<palette>`).
 * Le renommer invalide la clé enregistrée de tous ceux qui l'avaient choisi.
 * Ajouter, oui ; renommer, jamais.
 *
 * **Pour remplacer un visage jugé raté**, ne pas renommer : déclarer une
 * graine dans le `graines` de sa famille. L'identifiant — donc la clé en base —
 * ne bouge pas, seul le dessin change. C'est le seul moyen de corriger un
 * choix esthétique sans reverser les apprenants aux initiales.
 *
 * ⚠️ Un identifiant **ne peut pas contenir de tiret** : `parseAvatarKey`
 * découpe la clé sur ce caractère. D'où `adventurerneutral1` et non
 * `adventurer-neutral-1`.
 *
 * ### Licences — la seule contrainte juridique du lot
 *
 * Notionists est en CC0 (domaine public, rien à faire). Les six familles
 * ajoutées ne le sont pas :
 *
 * - **CC BY 4.0** (Adventurer, Adventurer Neutral, Big Smile, ToonHead) —
 *   l'attribution est **obligatoire**. Elle est portée à deux endroits : sous
 *   chaque famille du sélecteur d'avatar (là où l'œuvre est utilisée) et dans
 *   les mentions légales (là où on la retrouve).
 * - **« Free for personal and commercial use »** (Avataaars, Bottts) —
 *   n'exige rien, mais on crédite pareil : distinguer visuellement deux
 *   régimes n'apporterait rien au lecteur.
 *
 * `generate-avatars.mjs` **confronte** les champs `credit` ci-dessous à
 * `collection[style].meta` et échoue si l'un a bougé : une licence qui change
 * au fil d'une mise à jour de DiceBear ne doit pas passer inaperçue.
 */

/**
 * Familles de visages, dans l'ordre d'affichage du sélecteur.
 *
 * - `style` : clé d'export dans `@dicebear/collection`.
 * - `options` : réglages de cadrage, propres à chaque style — ils se règlent
 *   **à l'œil**, pas au calcul. Chaque style dessine son sujet à sa propre
 *   échelle dans le carré ; `Avatar` pose ensuite l'image dans une vignette à
 *   coins arrondis, où un sujet trop grand se fait rogner le haut du crâne.
 * - `visages` : identifiants, et graines par défaut (voir plus haut).
 * - `graines` : optionnel — graine explicite pour un identifiant donné, quand
 *   le dessin par défaut ne convient pas.
 */
export const FAMILLES = [
  {
    id: 'notionists',
    style: 'notionists',
    titre: 'Notionists',
    credit: {
      auteur: 'Zoish',
      licence: 'CC0 1.0',
      source: 'https://heyzoish.gumroad.com/l/notionists',
    },
    // Notionists dessine un buste haut dans son cadre : sans réduction, le
    // haut de la coiffure passe sous le rayon de bord de la vignette.
    options: { scale: 80, translateY: 8 },
    visages: ['nova', 'atlas', 'vega', 'orion', 'lyra', 'sol'],
  },
  {
    id: 'adventurer',
    style: 'adventurer',
    titre: 'Adventurer',
    credit: {
      auteur: 'Lisa Wischofsky',
      licence: 'CC BY 4.0',
      source: 'https://www.figma.com/community/file/1184595184137881796',
    },
    options: { scale: 90 },
    visages: [
      'adventurer1', 'adventurer2', 'adventurer3',
      'adventurer4', 'adventurer5', 'adventurer6',
    ],
  },
  {
    id: 'adventurerNeutral',
    style: 'adventurerNeutral',
    titre: 'Adventurer Neutral',
    credit: {
      auteur: 'Lisa Wischofsky',
      licence: 'CC BY 4.0',
      source: 'https://www.figma.com/community/file/1184595184137881796',
    },
    // La variante neutre ne dessine que les traits — ni crâne, ni cou, ni
    // buste. À l'échelle des autres familles, la bouche sortait par le bas de
    // la vignette. Réduite, elle se lit comme un visage posé sur la pastille.
    options: { scale: 62 },
    visages: [
      'adventurerneutral1', 'adventurerneutral2', 'adventurerneutral3',
      'adventurerneutral4', 'adventurerneutral5', 'adventurerneutral6',
    ],
  },
  {
    id: 'avataaars',
    style: 'avataaars',
    titre: 'Avataaars',
    credit: {
      auteur: 'Pablo Stanley',
      licence: 'Free for personal and commercial use',
      source: 'https://avataaars.com/',
    },
    options: { scale: 90 },
    visages: [
      'avataaars1', 'avataaars2', 'avataaars3',
      'avataaars4', 'avataaars5', 'avataaars6',
    ],
    // Le dessin rendu par la graine « avataaars2 » ne convenait pas. On change
    // la graine, pas l'identifiant : la clé `avataaars2-<palette>` reste
    // valide pour qui l'aurait déjà enregistrée.
    graines: { avataaars2: 'maya' },
  },
  {
    id: 'bigSmile',
    style: 'bigSmile',
    titre: 'Big Smile',
    credit: {
      auteur: 'Ashley Seo',
      licence: 'CC BY 4.0',
      source: 'https://www.figma.com/community/file/881358461963645496',
    },
    // Les coiffures volumineuses (bigsmile4, bigsmile6) débordaient par le
    // haut sous le rayon de bord de la vignette.
    options: { scale: 78 },
    visages: [
      'bigsmile1', 'bigsmile2', 'bigsmile3',
      'bigsmile4', 'bigsmile5', 'bigsmile6',
    ],
  },
  {
    id: 'bottts',
    style: 'bottts',
    titre: 'Bottts',
    credit: {
      auteur: 'Pablo Stanley',
      licence: 'Free for personal and commercial use',
      source: 'https://bottts.com/',
    },
    options: { scale: 85 },
    visages: [
      'bottts1', 'bottts2', 'bottts3',
      'bottts4', 'bottts5', 'bottts6',
    ],
  },
  {
    id: 'toonHead',
    style: 'toonHead',
    titre: 'ToonHead',
    credit: {
      auteur: 'Johan Melin',
      licence: 'CC BY 4.0',
      source: 'https://www.figma.com/community/file/1589627891082866389',
    },
    options: { scale: 90 },
    visages: [
      'toonhead1', 'toonhead2', 'toonhead3',
      'toonhead4', 'toonhead5', 'toonhead6',
    ],
  },
]

/**
 * Tous les visages, à plat et dans l'ordre des familles.
 *
 * ⚠️ Miroir de `VISAGES` dans `backend/apps/accounts/avatars.py`. Ajouter un
 * visage d'un seul côté donne soit un avatar vide (le serveur accepte une clé
 * que le client ne sait pas dessiner), soit un choix refusé à l'enregistrement.
 */
export const VISAGES = FAMILLES.flatMap((famille) => famille.visages)

/** Famille d'un visage, ou `null` s'il est hors catalogue. */
export function familleDuVisage(visage) {
  return FAMILLES.find((famille) => famille.visages.includes(visage)) || null
}

/**
 * Graine DiceBear à employer pour dessiner un visage.
 *
 * L'identifiant sert de graine par défaut ; `graines` permet de la remplacer
 * sans toucher à l'identifiant, donc sans invalider les clés déjà en base.
 */
export function graineDuVisage(famille, visage) {
  return famille.graines?.[visage] || visage
}

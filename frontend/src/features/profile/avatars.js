/**
 * Rendu des avatars du catalogue.
 *
 * Le choix se fait dans une liste close : rien n'est téléversé, rien n'est
 * stocké côté serveur. Voir `backend/apps/accounts/avatars.py` pour le
 * raisonnement complet (modération, formats, surface d'attaque).
 *
 * Les familles, leurs graines et leurs crédits vivent dans `avatarCatalog.js`,
 * volontairement dépourvu d'imports : le script de génération, qui tourne sous
 * Node et ne sait pas charger un `.svg`, lit le même fichier. Ce module-ci n'y
 * ajoute que le dessin.
 *
 * ⚠️ Les visages sont **pré-générés à la construction** (`npm run avatars`) et
 * servis par l'application elle-même — **jamais** par l'API HTTP de DiceBear.
 * Un appel distant enverrait l'IP de chaque apprenant à un tiers à chaque
 * affichage, et ferait tomber la raison pour laquelle l'application n'a pas de
 * bannière de consentement (aucun traceur tiers). Ne pas remplacer par une URL.
 *
 * ⚠️ Ne pas réintroduire `@dicebear/core` ici. Le catalogue est fermé :
 * quarante-deux visages connus d'avance. Embarquer le générateur pour les
 * recalculer à l'exécution ajoutait ~380 ko au morceau d'entrée — `Avatar` est
 * tiré par le `Header`, donc structurel et jamais différé — et faisait repasser
 * le bundle de 261 ko à 640 ko.
 *
 * Licences : Notionists est en CC0, mais **quatre des sept familles sont en
 * CC BY 4.0** et imposent une attribution. Elle est portée par le sélecteur
 * d'avatar (sous chaque titre de famille) et par les mentions légales. Les
 * crédits sont vérifiés contre `collection[style].meta` à chaque génération.
 */

import { FAMILLES, VISAGES, familleDuVisage } from './avatarCatalog'

export { FAMILLES, VISAGES, familleDuVisage }

/**
 * Visages **pré-générés**, chargés en bloc plutôt qu'un `import` par fichier.
 *
 * Vite résout ce glob à la compilation : le résultat est exactement ce que
 * donnaient les imports nominatifs — quarante-deux URL de fichiers statiques,
 * mis en cache et chargés à la demande. Aucun code de génération n'entre dans
 * le bundle.
 *
 * On préfère le glob à quarante-deux lignes d'import parce qu'une liste
 * manuelle de cette taille dérive en silence : un visage ajouté au catalogue
 * mais oublié ici produirait une vignette vide, sans erreur. Ici, le fichier
 * manque ou il est là.
 *
 * ⚠️ Ces fichiers sont **exclus de l'intégration en base64** par le
 * `assetsInlineLimit` de `vite.config.js`. Sans cette exclusion, les douze
 * visages pesant moins de 4 ko atterrissaient dans le morceau d'entrée —
 * `Avatar` est tiré par le `Header`, donc structurel — et chaque visiteur
 * téléchargeait douze visages qu'il ne verrait jamais. Ne pas retirer la règle
 * en croyant simplifier la configuration.
 */
const FICHIERS = import.meta.glob('../../assets/avatars/*.svg', {
  eager: true,
  import: 'default',
})

const FACE_URLS = Object.fromEntries(
  Object.entries(FICHIERS).map(([chemin, url]) => [
    chemin.slice(chemin.lastIndexOf('/') + 1, -'.svg'.length),
    url,
  ])
)

export const PALETTES = ['violet', 'amber', 'teal', 'rose', 'indigo', 'lime']

/** Étiquette lisible d'une palette, pour les libellés d'accessibilité. */
export const PALETTE_LABELS = {
  violet: 'violet',
  amber: 'ambre',
  teal: 'turquoise',
  rose: 'rose',
  indigo: 'indigo',
  lime: 'vert',
}

/** Fond dégradé et couleur de tracé, pour chaque palette. */
const PALETTE_COLORS = {
  violet: { from: '#7c5cff', to: '#b06bff', ink: '#ffffff' },
  amber: { from: '#f0932b', to: '#ffc84a', ink: '#3d2600' },
  teal: { from: '#0f9b8e', to: '#4fd1c5', ink: '#00312c' },
  rose: { from: '#e0518c', to: '#ff8fb1', ink: '#4a0022' },
  indigo: { from: '#3d5afe', to: '#7c93ff', ink: '#ffffff' },
  lime: { from: '#5aa02c', to: '#a3d94f', ink: '#1b3000' },
}

/** Palette retenue quand on quitte les initiales sans en avoir choisi une. */
export const PALETTE_PAR_DEFAUT = 'violet'

/**
 * URL du visage, à poser dans un `<image>`.
 *
 * On passe par une image plutôt que par une injection de balisage : le SVG
 * référencé par `<image>` est rendu en mode « image », sans script ni requête
 * vers un tiers. Aucun `dangerouslySetInnerHTML` n'est nécessaire.
 */
export function avatarFaceUri(visage) {
  return FACE_URLS[visage] || null
}

export const AVATAR_KEYS = VISAGES.flatMap((visage) =>
  PALETTES.map((palette) => `${visage}-${palette}`)
)

/**
 * Décompose une clé en visage et palette, ou `null` si elle est inconnue.
 *
 * ⚠️ Le découpage se fait sur le tiret : c'est pourquoi aucun identifiant de
 * visage ne peut en contenir (`adventurerneutral1`, et non
 * `adventurer-neutral-1`). Un test verrouille cette règle.
 */
export function parseAvatarKey(key) {
  if (!key) return null
  const [visage, palette] = String(key).split('-')
  if (!VISAGES.includes(visage) || !PALETTES.includes(palette)) return null
  return { visage, palette }
}

export function paletteColors(palette) {
  return PALETTE_COLORS[palette] || PALETTE_COLORS.violet
}

/**
 * Couleur de repli, dérivée du nom, pour l'avatar à initiales.
 *
 * Déterministe : le même utilisateur garde la même couleur d'une session à
 * l'autre et d'un poste à l'autre, ce qui en fait un repère visuel utilisable
 * plutôt qu'une décoration aléatoire.
 */
export function initialsPalette(seed = '') {
  let hash = 0
  for (let index = 0; index < seed.length; index += 1) {
    hash = (hash * 31 + seed.charCodeAt(index)) % 997
  }
  return PALETTES[hash % PALETTES.length]
}

export function initialsOf(user) {
  const first = user?.first_name?.trim()?.[0] || ''
  const last = user?.last_name?.trim()?.[0] || ''
  const initials = `${first}${last}`.toUpperCase()
  if (initials) return initials

  // Le classement ne transmet ni prénom ni nom séparés — et surtout aucun
  // email : uniquement un nom d'affichage déjà réduit (« Lory C. »). On en
  // tire les initiales plutôt que d'afficher un « ? » pour toute la liste.
  const fromDisplayName = String(user?.display_name || '')
    .split(/\s+/)
    .filter(Boolean)
    .slice(0, 2)
    .map((word) => word[0])
    .join('')
  if (fromDisplayName) return fromDisplayName.toUpperCase()

  return (user?.email?.[0] || '?').toUpperCase()
}

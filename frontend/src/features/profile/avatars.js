/**
 * Rendu des avatars du catalogue.
 *
 * Le choix se fait dans une liste close : rien n'est téléversé, rien n'est
 * stocké côté serveur. Voir `backend/apps/accounts/avatars.py` pour le
 * raisonnement complet (modération, formats, surface d'attaque).
 *
 * ⚠️ Les visages sont **pré-générés à la construction** (`npm run avatars`) et
 * servis par l'application elle-même — **jamais** par l'API HTTP de DiceBear.
 * Un appel distant enverrait l'IP de chaque apprenant à un tiers à chaque
 * affichage, et ferait tomber la raison pour laquelle l'application n'a pas de
 * bannière de consentement (aucun traceur tiers). Ne pas remplacer par une URL.
 *
 * Style : **Notionists**, licence **CC0 1.0** (Zoish) — domaine public, aucune
 * attribution obligatoire. Plusieurs autres styles de la même bibliothèque sont
 * en CC BY 4.0 : vérifier `meta.license` avant d'en changer.
 *
 * ⚠️ `VISAGES` et `PALETTES` **dupliquent** les listes du serveur. C'est
 * assumé : le serveur reste l'autorité sur ce qui est acceptable, le client
 * n'a besoin que de savoir dessiner. Mais ajouter un visage d'un seul côté
 * produit soit un avatar vide, soit un choix refusé à l'enregistrement —
 * toujours modifier les deux fichiers ensemble.
 */

// Visages **pré-générés** par `npm run avatars` (voir
// `scripts/generate-avatars.mjs`). Vite les transforme en URLs : le navigateur
// reçoit six SVG statiques, mis en cache, et **aucun code de génération**.
//
// ⚠️ Ne pas réintroduire `@dicebear/core` ici. Le catalogue est fermé : six
// visages connus d'avance. Embarquer le générateur pour les recalculer à
// l'exécution ajoutait ~380 ko au morceau d'entrée — `Avatar` est tiré par le
// `Header`, donc structurel et jamais différé — et faisait repasser le bundle
// de 261 ko à 640 ko.
import novaSvg from '@/assets/avatars/nova.svg'
import atlasSvg from '@/assets/avatars/atlas.svg'
import vegaSvg from '@/assets/avatars/vega.svg'
import orionSvg from '@/assets/avatars/orion.svg'
import lyraSvg from '@/assets/avatars/lyra.svg'
import solSvg from '@/assets/avatars/sol.svg'

/**
 * Chaque valeur **est** la graine DiceBear : la renommer change le visage de
 * tous ceux qui l'avaient choisi. Miroir de `VISAGES` dans `avatars.py`.
 */
export const VISAGES = ['nova', 'atlas', 'vega', 'orion', 'lyra', 'sol']

export const PALETTES = ['violet', 'amber', 'teal', 'rose', 'indigo', 'lime']

/** Fond dégradé et couleur de tracé, pour chaque palette. */
const PALETTE_COLORS = {
  violet: { from: '#7c5cff', to: '#b06bff', ink: '#ffffff' },
  amber: { from: '#f0932b', to: '#ffc84a', ink: '#3d2600' },
  teal: { from: '#0f9b8e', to: '#4fd1c5', ink: '#00312c' },
  rose: { from: '#e0518c', to: '#ff8fb1', ink: '#4a0022' },
  indigo: { from: '#3d5afe', to: '#7c93ff', ink: '#ffffff' },
  lime: { from: '#5aa02c', to: '#a3d94f', ink: '#1b3000' },
}

const FACE_URLS = {
  nova: novaSvg,
  atlas: atlasSvg,
  vega: vegaSvg,
  orion: orionSvg,
  lyra: lyraSvg,
  sol: solSvg,
}

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

/** Décompose une clé en visage et palette, ou `null` si elle est inconnue. */
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
  return (user?.email?.[0] || '?').toUpperCase()
}

/**
 * Rendu des avatars du catalogue.
 *
 * Les avatars sont dessinés en SVG à la volée : rien n'est téléversé, rien
 * n'est stocké, rien n'est servi depuis le disque. Voir
 * `backend/apps/accounts/avatars.py` pour le raisonnement complet (modération,
 * formats, surface d'attaque).
 *
 * ⚠️ `MOTIFS` et `PALETTES` **dupliquent** les listes du serveur. C'est
 * assumé : le serveur reste l'autorité sur ce qui est acceptable, le client
 * n'a besoin que de savoir dessiner. Mais ajouter un motif d'un seul côté
 * produit soit un avatar vide, soit un choix refusé à l'enregistrement —
 * toujours modifier les deux fichiers ensemble.
 */

export const MOTIFS = ['orbit', 'prism', 'wave', 'bloom', 'spark', 'mesh']

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

/**
 * Géométrie de chaque motif, dans un carré de 100×100.
 *
 * Volontairement abstrait : des formes plutôt que des visages ou des animaux.
 * Un catalogue figuratif oblige à arbitrer des représentations (teintes de
 * peau, genres, cultures) qu'une liste de douze images ne peut pas rendre
 * justement — l'abstrait n'exclut personne.
 */
const MOTIF_SHAPES = {
  orbit: [
    { type: 'circle', props: { cx: 50, cy: 50, r: 17 } },
    { type: 'ellipse', props: { cx: 50, cy: 50, rx: 34, ry: 15, fill: 'none', strokeWidth: 6 } },
  ],
  prism: [
    { type: 'path', props: { d: 'M50 22 L76 68 H24 Z' } },
    { type: 'path', props: { d: 'M50 42 L63 68 H37 Z', opacity: 0.45 } },
  ],
  wave: [
    {
      type: 'path',
      props: {
        d: 'M18 58 q16 -22 32 0 t32 0',
        fill: 'none',
        strokeWidth: 8,
        strokeLinecap: 'round',
      },
    },
    {
      type: 'path',
      props: {
        d: 'M18 40 q16 -22 32 0 t32 0',
        fill: 'none',
        strokeWidth: 8,
        strokeLinecap: 'round',
        opacity: 0.45,
      },
    },
  ],
  bloom: [
    { type: 'circle', props: { cx: 50, cy: 32, r: 13 } },
    { type: 'circle', props: { cx: 50, cy: 68, r: 13 } },
    { type: 'circle', props: { cx: 32, cy: 50, r: 13, opacity: 0.55 } },
    { type: 'circle', props: { cx: 68, cy: 50, r: 13, opacity: 0.55 } },
  ],
  spark: [
    { type: 'path', props: { d: 'M50 18 L58 42 L82 50 L58 58 L50 82 L42 58 L18 50 L42 42 Z' } },
  ],
  mesh: [
    { type: 'circle', props: { cx: 34, cy: 34, r: 8 } },
    { type: 'circle', props: { cx: 66, cy: 34, r: 8, opacity: 0.55 } },
    { type: 'circle', props: { cx: 34, cy: 66, r: 8, opacity: 0.55 } },
    { type: 'circle', props: { cx: 66, cy: 66, r: 8 } },
    {
      type: 'path',
      props: { d: 'M34 34 H66 M34 66 H66 M34 34 V66 M66 34 V66', fill: 'none', strokeWidth: 4, opacity: 0.4 },
    },
  ],
}

export const AVATAR_KEYS = MOTIFS.flatMap((motif) =>
  PALETTES.map((palette) => `${motif}-${palette}`)
)

/** Décompose une clé en motif et palette, ou `null` si elle est inconnue. */
export function parseAvatarKey(key) {
  if (!key) return null
  const [motif, palette] = String(key).split('-')
  if (!MOTIFS.includes(motif) || !PALETTES.includes(palette)) return null
  return { motif, palette }
}

export function paletteColors(palette) {
  return PALETTE_COLORS[palette] || PALETTE_COLORS.violet
}

export function motifShapes(motif) {
  return MOTIF_SHAPES[motif] || []
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

import html from '@/assets/chapters/html.svg'

/**
 * Illustration d'ouverture de chaque chapitre.
 *
 * Une série, une grammaire : même format 16/9, même fond dégradé clair, mêmes
 * teintes de marque et d'accent, et une composition en trois plans — un halo
 * coloré, un objet central, des signes flottants. Seuls le motif et la
 * dominante changent d'un chapitre à l'autre.
 *
 * Les fichiers sont du **SVG écrit à la main** (`src/assets/chapters/`) :
 * net à toute taille — le fond du tableau de bord fait quelques centaines de
 * pixels, l'en-tête de chapitre en fera plus de mille —, quelques kilo-octets,
 * et relisible en diff. Aucune dépendance, aucune question de licence.
 *
 * ⚠️ **Aucun texte dans les fichiers** : une illustration posée en
 * `background-image` n'hérite d'aucune police du document, et un `<text>`
 * rendrait donc n'importe quoi selon la machine. Tout est tracé en formes.
 *
 * ⚠️ **`--` est interdit dans un commentaire XML.** Citer une variable CSS
 * (`- -brand`) dans le cartouche d'un SVG rend le fichier entier mal formé :
 * le navigateur n'affiche alors *rien*, sans le moindre message d'erreur.
 * C'est arrivé au premier fichier de la série.
 */

/**
 * ⚠️ Les clés sont les **slugs de chapitre en base**, pas des identifiants
 * inventés ici. Renommer un slug côté contenu fait disparaître l'illustration
 * en silence — le repli est volontairement discret (aucun fond), donc rien ne
 * le signalera. Vérifier avec `load_course_content --list` en cas de doute.
 */
const ILLUSTRATIONS = {
  'introduction-html': html,
}

/** URL de l'illustration d'un chapitre, ou `null` s'il n'en a pas encore. */
export function chapterIllustration(slug) {
  if (!slug) return null
  return ILLUSTRATIONS[slug] || null
}

export default ILLUSTRATIONS

import questCeQueLeHtml from '@/assets/lessons/quest-ce-que-le-html.svg'
import structureBasePageHtml from '@/assets/lessons/structure-base-page-html.svg'
import htmlTexteTitresParagraphes from '@/assets/lessons/html-texte-titres-paragraphes.svg'

/**
 * Illustration d'ouverture de chaque **leçon**.
 *
 * Une série, une grammaire : même format 16/9, même fond dégradé clair, mêmes
 * teintes de marque et d'accent, et une composition en trois plans — un halo
 * coloré, un objet central, des signes flottants. Seuls le motif et la
 * dominante changent d'une leçon à l'autre, la dominante suivant le chapitre.
 *
 * Les fichiers sont du **SVG écrit à la main** (`src/assets/lessons/`) : net à
 * toute taille — quelques centaines de pixels en fond de carte, plus de mille
 * en tête de leçon —, quelques kilo-octets, et relisible en diff. Aucune
 * dépendance, aucune question de licence.
 *
 * ⚠️ **Aucun texte dans les fichiers** : une illustration posée en
 * `background-image` n'hérite d'aucune police du document, et un `<text>`
 * rendrait donc n'importe quoi selon la machine. Tout est tracé en formes.
 *
 * ⚠️ **`--` est interdit dans un commentaire XML.** Citer une variable CSS
 * avec son préfixe dans le cartouche d'un SVG rend le fichier entier mal
 * formé : le navigateur n'affiche alors *rien*, sans le moindre message
 * d'erreur. C'est arrivé au premier fichier de la série.
 */

/**
 * ⚠️ Les clés sont les **slugs de leçon en base**, pas des identifiants
 * inventés ici, et le nom de fichier reprend le slug. Renommer un slug côté
 * contenu fait disparaître l'illustration en silence — le repli est
 * volontairement discret (aucun fond), donc rien ne le signalera.
 *
 * Le parcours compte 68 leçons : cette table se remplit au fil des dessins,
 * une leçon sans entrée s'affiche simplement sans illustration.
 */
const ILLUSTRATIONS = {
  'quest-ce-que-le-html': questCeQueLeHtml,
  'structure-base-page-html': structureBasePageHtml,
  'html-texte-titres-paragraphes': htmlTexteTitresParagraphes,
}

/** URL de l'illustration d'une leçon, ou `null` si elle n'en a pas encore. */
export function lessonIllustration(slug) {
  if (!slug) return null
  return ILLUSTRATIONS[slug] || null
}

export default ILLUSTRATIONS

/**
 * Pré-génère les visages du catalogue d'avatars en fichiers SVG.
 *
 * ### Pourquoi une génération à la construction, et non à l'exécution
 *
 * Le catalogue est **fermé** : une liste de visages fixée côté serveur
 * (`backend/apps/accounts/avatars.py`). Embarquer le générateur DiceBear dans
 * le bundle pour recalculer des images connues d'avance coûtait **~380 ko**
 * dans le morceau d'entrée — `Avatar` est utilisé par le `Header`, donc
 * structurel, donc jamais différé. Le bundle passait de 261 ko à 640 ko et
 * refranchissait le seuil d'alerte de Vite.
 *
 * En pré-générant, `@dicebear/*` devient une dépendance de développement : le
 * navigateur ne reçoit que des SVG statiques, mis en cache et servis à la
 * demande — et **aucune requête ne part chez DiceBear**, ce qui est la
 * condition pour que l'application reste sans traceur tiers (cf. la section
 * RGPD de `CLAUDE.md`).
 *
 * ### Quand relancer
 *
 * Après toute modification de `FAMILLES` dans
 * `src/features/profile/avatarCatalog.js` — c'est la seule source, ce fichier
 * ne redéclare rien. Les SVG produits sont versionnés : la construction ne
 * dépend donc pas de DiceBear, seul le développeur qui touche au catalogue en
 * a besoin.
 *
 *     npm run avatars
 *
 * Un test front vérifie que chaque clé du catalogue sait se dessiner : il
 * rougira si un visage a été ajouté sans relancer la commande.
 *
 * ### La vérification des licences n'est pas décorative
 *
 * Quatre des sept familles sont en **CC BY 4.0**, qui impose une attribution.
 * Les crédits affichés dans l'application sont saisis à la main dans le
 * catalogue ; ce script les **confronte** à `collection[style].meta` et
 * échoue si l'un a bougé. Sans ce contrôle, une mise à jour de DiceBear
 * pourrait changer un auteur ou une licence sans que rien ne le signale — et
 * l'application afficherait une attribution fausse, ce qui est pire que pas
 * d'attribution du tout.
 */

import { mkdirSync, readdirSync, rmSync, writeFileSync } from 'node:fs'
import { dirname, join } from 'node:path'
import { fileURLToPath } from 'node:url'

import { createAvatar } from '@dicebear/core'
import * as collection from '@dicebear/collection'

import { FAMILLES, VISAGES, graineDuVisage } from '../src/features/profile/avatarCatalog.js'

const OUT_DIR = join(dirname(fileURLToPath(import.meta.url)), '..', 'src', 'assets', 'avatars')

/**
 * Confronte les crédits déclarés aux métadonnées de la bibliothèque.
 *
 * On ne compare pas le titre : `bigSmile` s'annonce « Custom Avatar » chez
 * DiceBear, ce qui ne dit rien à un apprenant. Le titre affiché est le nôtre ;
 * l'auteur, la licence et la source, eux, engagent juridiquement.
 */
function verifierCredit(famille) {
  const style = collection[famille.style]
  if (!style) {
    throw new Error(`Style DiceBear inconnu : « ${famille.style} » (famille ${famille.id}).`)
  }

  const meta = style.meta || {}
  const attendu = famille.credit
  const ecarts = []

  if (meta.creator !== attendu.auteur) {
    ecarts.push(`auteur : catalogue « ${attendu.auteur} », DiceBear « ${meta.creator} »`)
  }
  if (meta.license?.name !== attendu.licence) {
    ecarts.push(`licence : catalogue « ${attendu.licence} », DiceBear « ${meta.license?.name} »`)
  }
  if (meta.source !== attendu.source) {
    ecarts.push(`source : catalogue « ${attendu.source} », DiceBear « ${meta.source} »`)
  }

  if (ecarts.length) {
    throw new Error(
      `Crédit périmé pour « ${famille.titre} » :\n  - ${ecarts.join('\n  - ')}\n`
      + '  Mettre à jour avatarCatalog.js **et** les mentions légales avant de régénérer.'
    )
  }

  return style
}

mkdirSync(OUT_DIR, { recursive: true })

// Un visage retiré du catalogue doit voir son fichier disparaître : laissé sur
// le disque, il serait embarqué par Vite sans que rien n'y renvoie.
const attendus = new Set(VISAGES.map((visage) => `${visage}.svg`))
for (const fichier of readdirSync(OUT_DIR)) {
  if (fichier.endsWith('.svg') && !attendus.has(fichier)) {
    rmSync(join(OUT_DIR, fichier))
    console.log(`  ${fichier} retiré (hors catalogue)`)
  }
}

let total = 0

for (const famille of FAMILLES) {
  const style = verifierCredit(famille)
  console.log(`\n${famille.titre} — ${famille.credit.auteur}, ${famille.credit.licence}`)

  for (const visage of famille.visages) {
    const graine = graineDuVisage(famille, visage)
    const svg = createAvatar(style, {
      seed: graine,
      // Le fond vient du dégradé de palette rendu par `Avatar`, pas du style :
      // c'est la palette qui distingue deux apprenants ayant choisi le même
      // visage.
      backgroundColor: ['transparent'],
      ...famille.options,
    }).toString()

    writeFileSync(join(OUT_DIR, `${visage}.svg`), svg, 'utf8')
    total += svg.length
    const note = graine === visage ? '' : `  (graine « ${graine} »)`
    console.log(`  ${visage.padEnd(20)} → ${(svg.length / 1024).toFixed(1)} ko${note}`)
  }
}

console.log(
  `\n${VISAGES.length} visages écrits dans src/assets/avatars/`
  + ` (${(total / 1024).toFixed(0)} ko au total).`
)

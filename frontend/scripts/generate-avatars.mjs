/**
 * Pré-génère les visages du catalogue d'avatars en fichiers SVG.
 *
 * ### Pourquoi une génération à la construction, et non à l'exécution
 *
 * Le catalogue est **fermé** : six visages, fixés côté serveur
 * (`backend/apps/accounts/avatars.py`). Embarquer le générateur DiceBear dans
 * le bundle pour recalculer six images connues d'avance coûtait **~380 ko**
 * dans le morceau d'entrée — `Avatar` est utilisé par le `Header`, donc
 * structurel, donc jamais différé. Le bundle passait de 261 ko à 640 ko et
 * refranchissait le seuil d'alerte de Vite.
 *
 * En pré-générant, `@dicebear/*` devient une dépendance de développement : le
 * navigateur ne reçoit que six SVG statiques, mis en cache et servis à la
 * demande.
 *
 * ### Quand relancer
 *
 * Après toute modification de `VISAGES` (ajout d'un visage) ou du style. Les
 * fichiers produits sont versionnés — la construction ne dépend donc pas de
 * DiceBear, seul le développeur qui touche au catalogue en a besoin.
 *
 *     npm run avatars
 *
 * ⚠️ La liste ci-dessous doit rester le miroir de `VISAGES` dans
 * `src/features/profile/avatars.js` **et** dans `avatars.py`. Un test front
 * vérifie que chaque clé du catalogue sait se dessiner : il rougira si un
 * visage n'a pas été généré.
 */

import { mkdirSync, writeFileSync } from 'node:fs'
import { dirname, join } from 'node:path'
import { fileURLToPath } from 'node:url'

import { createAvatar } from '@dicebear/core'
import * as notionists from '@dicebear/notionists'

const VISAGES = ['nova', 'atlas', 'vega', 'orion', 'lyra', 'sol']

const OUT_DIR = join(dirname(fileURLToPath(import.meta.url)), '..', 'src', 'assets', 'avatars')

mkdirSync(OUT_DIR, { recursive: true })

for (const visage of VISAGES) {
  const svg = createAvatar(notionists, {
    seed: visage,
    // Le fond vient du dégradé de palette rendu par `Avatar`, pas du style.
    backgroundColor: ['transparent'],
    // Notionists dessine un buste haut dans son cadre : sans réduction, le
    // haut de la coiffure passe sous le rayon de bord de la vignette.
    scale: 80,
    translateY: 8,
  }).toString()

  const file = join(OUT_DIR, `${visage}.svg`)
  writeFileSync(file, svg, 'utf8')
  console.log(`${visage.padEnd(8)} → ${(svg.length / 1024).toFixed(1)} ko`)
}

console.log(`\n${VISAGES.length} visages écrits dans src/assets/avatars/`)

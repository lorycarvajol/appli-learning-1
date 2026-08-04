import { describe, it, expect } from 'vitest'

import { DEFAULT_REDIRECT, isSafeInternalPath, safeRedirectPath } from './safePath'

/**
 * Le `?next=` de la page de connexion vient de l'URL, donc de n'importe qui.
 * Le contrôle d'origine — « commence par `/` mais pas par `//` » — laissait
 * passer `/\evil.com`, que les navigateurs réinterprètent comme
 * protocole-relatif : c'est le contournement par antislash décrit par l'avis
 * de sécurité de React Router.
 *
 * Ces tests sont volontairement **indépendants de la version du routeur** :
 * ils protègent même si la bibliothèque régresse.
 */

describe('destinations acceptées', () => {
  it.each([
    '/dashboard',
    '/rejoindre/abc123',
    '/chapters/introduction-html',
    '/lessons/quest-ce-que-le-html?onglet=2',
  ])('accepte le chemin interne %s', (chemin) => {
    expect(isSafeInternalPath(chemin)).toBe(true)
    expect(safeRedirectPath(chemin)).toBe(chemin)
  })
})

describe('destinations refusées', () => {
  it.each([
    ['URL absolue', 'https://evil.example'],
    ['protocole-relatif', '//evil.example'],
    ['antislash (le contournement documenté)', '/\\evil.example'],
    ['double antislash', '\\\\evil.example'],
    ['antislash en milieu de chemin', '/dashboard\\@evil.example'],
    ['espace en tête', ' //evil.example'],
    ['tabulation en tête', '\t//evil.example'],
    ['retour chariot injecté', '/dash\nboard'],
    ['chemin relatif', 'dashboard'],
    ['javascript:', 'javascript:alert(1)'],
    ['chaîne vide', ''],
    ['valeur absente', null],
  ])('refuse %s', (_libelle, chemin) => {
    expect(isSafeInternalPath(chemin)).toBe(false)
    expect(safeRedirectPath(chemin)).toBe(DEFAULT_REDIRECT)
  })
})

describe('repli', () => {
  it('permet de choisir sa destination de repli', () => {
    expect(safeRedirectPath('https://evil.example', '/login')).toBe('/login')
  })
})

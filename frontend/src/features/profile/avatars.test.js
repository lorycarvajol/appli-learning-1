import { describe, it, expect } from 'vitest'
import {
  AVATAR_KEYS,
  MOTIFS,
  PALETTES,
  initialsOf,
  initialsPalette,
  motifShapes,
  parseAvatarKey,
} from './avatars'

/**
 * Le catalogue est dupliqué entre le serveur (autorité) et le client (rendu).
 * Ces tests verrouillent le contrat côté client : toute clé acceptée par le
 * serveur doit savoir se dessiner, et toute clé inconnue doit retomber
 * proprement sur les initiales plutôt que de produire un avatar vide.
 */

describe('catalogue d’avatars', () => {
  it('couvre toutes les combinaisons motif × palette', () => {
    expect(AVATAR_KEYS).toHaveLength(MOTIFS.length * PALETTES.length)
    expect(AVATAR_KEYS).toContain('orbit-violet')
  })

  it('sait dessiner chaque clé du catalogue', () => {
    // Une clé valide côté serveur mais sans géométrie ici produirait un
    // avatar vide, sans erreur visible.
    for (const key of AVATAR_KEYS) {
      const parsed = parseAvatarKey(key)
      expect(parsed, key).not.toBeNull()
      expect(motifShapes(parsed.motif).length, key).toBeGreaterThan(0)
    }
  })

  it('retombe sur les initiales pour une clé inconnue', () => {
    expect(parseAvatarKey('')).toBeNull()
    expect(parseAvatarKey(null)).toBeNull()
    expect(parseAvatarKey('licorne-or')).toBeNull()
    expect(parseAvatarKey('<script>')).toBeNull()
  })
})

describe('avatar de repli', () => {
  it('donne la même couleur au même utilisateur', () => {
    // Déterministe : l'avatar sert de repère visuel, il ne doit pas changer
    // de couleur d'une session à l'autre.
    expect(initialsPalette('eve@example.com')).toBe(initialsPalette('eve@example.com'))
  })

  it('produit une palette valide quelle que soit la graine', () => {
    for (const seed of ['', 'a', 'très-long-email@exemple.fr', '🙂']) {
      expect(PALETTES).toContain(initialsPalette(seed))
    }
  })

  it('compose les initiales à partir du nom, sinon de l’email', () => {
    expect(initialsOf({ first_name: 'Eve', last_name: 'Martin' })).toBe('EM')
    expect(initialsOf({ first_name: 'Eve' })).toBe('E')
    expect(initialsOf({ email: 'zoe@example.com' })).toBe('Z')
    expect(initialsOf({})).toBe('?')
    expect(initialsOf(null)).toBe('?')
  })

  it('ignore un nom fait uniquement d’espaces', () => {
    expect(initialsOf({ first_name: '   ', email: 'zoe@example.com' })).toBe('Z')
  })
})

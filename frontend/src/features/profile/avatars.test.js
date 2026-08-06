import { describe, it, expect } from 'vitest'
import {
  AVATAR_KEYS,
  VISAGES,
  PALETTES,
  avatarFaceUri,
  initialsOf,
  initialsPalette,
  parseAvatarKey,
} from './avatars'

/**
 * Le catalogue est dupliqué entre le serveur (autorité) et le client (rendu).
 * Ces tests verrouillent le contrat côté client : toute clé acceptée par le
 * serveur doit savoir se dessiner, et toute clé inconnue doit retomber
 * proprement sur les initiales plutôt que de produire un avatar vide.
 */

describe('catalogue d’avatars', () => {
  it('couvre toutes les combinaisons visage × palette', () => {
    expect(AVATAR_KEYS).toHaveLength(VISAGES.length * PALETTES.length)
    expect(AVATAR_KEYS).toContain('nova-violet')
  })

  it('sait dessiner chaque clé du catalogue', () => {
    // Une clé valide côté serveur mais sans visage pré-généré produirait un
    // avatar vide, sans erreur visible. C'est ce test qui rougit si
    // `npm run avatars` n'a pas été relancé après un ajout à `VISAGES`.
    for (const key of AVATAR_KEYS) {
      const parsed = parseAvatarKey(key)
      expect(parsed, key).not.toBeNull()
      expect(avatarFaceUri(parsed.visage), key).toBeTruthy()
    }
  })

  it('sert les visages depuis l’application, jamais depuis un tiers', () => {
    // Aucune IP d'apprenant ne doit partir chez un hébergeur externe : pointer
    // l'API HTTP de DiceBear imposerait une bannière de consentement (cf. la
    // section RGPD de CLAUDE.md).
    for (const visage of VISAGES) {
      expect(avatarFaceUri(visage), visage).not.toMatch(/^(https?:)?\/\//)
    }
  })

  it('refuse un visage hors catalogue', () => {
    expect(avatarFaceUri('licorne')).toBeNull()
    expect(avatarFaceUri('')).toBeNull()
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

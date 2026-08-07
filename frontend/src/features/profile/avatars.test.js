import { describe, it, expect } from 'vitest'
import {
  AVATAR_KEYS,
  BORDURES,
  BORDURE_LABELS,
  bordureTraits,
  FAMILLES,
  VISAGES,
  PALETTES,
  avatarFaceUri,
  familleDuVisage,
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

  it('n’admet aucun tiret dans un identifiant de visage', () => {
    // `parseAvatarKey` découpe la clé sur le tiret : un identifiant qui en
    // contient serait tronqué, et la clé rejetée en silence — l'apprenant
    // verrait son choix revenir aux initiales sans explication.
    for (const visage of VISAGES) {
      expect(visage, visage).not.toContain('-')
    }
  })

  it('rattache chaque visage à une famille créditée', () => {
    // L'attribution CC BY 4.0 est une obligation : une famille sans auteur ni
    // licence affichés mettrait l'exploitant en faute. Un visage orphelin de
    // famille, lui, ne serait crédité nulle part.
    for (const visage of VISAGES) {
      const famille = familleDuVisage(visage)
      expect(famille, visage).not.toBeNull()
      expect(famille.credit.auteur, visage).toBeTruthy()
      expect(famille.credit.licence, visage).toBeTruthy()
    }
  })

  it('ne déclare aucun visage en double entre familles', () => {
    // Le même identifiant dans deux familles rendrait le crédit ambigu et
    // ferait dessiner deux fois la même vignette dans le sélecteur.
    expect(new Set(VISAGES).size).toBe(VISAGES.length)
    expect(VISAGES).toHaveLength(FAMILLES.reduce((n, f) => n + f.visages.length, 0))
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

describe('bordures', () => {
  it('propose « aucune » comme premier choix', () => {
    // Un avatar nu est l'état neutre : il doit rester atteignable, et rester
    // le défaut. Le retirer imposerait une bordure à qui n'en veut pas.
    expect(BORDURES[0]).toBe('')
    expect(bordureTraits('')).toEqual([])
  })

  it('donne un libellé à chaque bordure', () => {
    // Sans libellé, le bouton n'a pas de nom accessible — cinq vignettes
    // indistinguables pour un lecteur d'écran.
    for (const bordure of BORDURES) {
      expect(BORDURE_LABELS[bordure], bordure).toBeTruthy()
    }
  })

  it('retombe sur aucun anneau pour une valeur inconnue', () => {
    // Une valeur périmée en base doit donner un avatar nu, jamais un avatar
    // cassé.
    expect(bordureTraits('licorne')).toEqual([])
    expect(bordureTraits(undefined)).toEqual([])
  })

  it('rentre chaque anneau et réduit son rayon d’autant', () => {
    // ⚠️ Un trait centré sur le bord déborderait de la moitié de son
    // épaisseur et se ferait rogner par le `rx` du fond ; un rayon laissé à
    // 28 rendrait les coins plus carrés que la vignette.
    for (const bordure of BORDURES.filter(Boolean)) {
      for (const trait of bordureTraits(bordure)) {
        expect(trait.inset, bordure).toBeGreaterThan(0)
        expect(trait.epaisseur, bordure).toBeGreaterThan(0)
        expect(28 - trait.inset, bordure).toBeGreaterThan(0)
      }
    }
  })

  it('n’emploie que du blanc ou du noir translucide', () => {
    // Les anneaux se superposent aux six palettes : une teinte fixe
    // disparaîtrait sur au moins l'une d'elles.
    for (const bordure of BORDURES.filter(Boolean)) {
      for (const trait of bordureTraits(bordure)) {
        expect(trait.couleur, `${bordure} ${trait.couleur}`)
          .toMatch(/^rgba\((255,255,255|23,19,42),/)
      }
    }
  })
})

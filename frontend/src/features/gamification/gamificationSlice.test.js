import { describe, it, expect } from 'vitest'
import reducer, {
  badgesEarned,
  dismissReveal,
  fetchGamificationSummary,
  syncGamification,
  selectPendingReveal,
} from './gamificationSlice'

/**
 * L'invariant côté front est le pendant de celui du backend : **une
 * célébration ne rejoue jamais**. Le serveur garantit qu'un badge n'est gagné
 * qu'une fois ; la file de révélation garantit qu'il n'est fêté qu'une fois,
 * même si `unseen_badges` et `new_badges` le mentionnent tous les deux.
 */

const badge = (id) => ({ id, name: `Badge ${id}` })

const etatInitial = () => reducer(undefined, { type: '@@INIT' })

describe('gamificationSlice — file de révélation', () => {
  it('met en file un badge nouvellement gagné', () => {
    const state = reducer(etatInitial(), badgesEarned([badge('a')]))
    expect(state.revealQueue).toHaveLength(1)
    expect(selectPendingReveal({ gamification: state })).toMatchObject({ id: 'a' })
  })

  it('ne célèbre jamais deux fois le même badge', () => {
    let state = reducer(etatInitial(), badgesEarned([badge('a')]))
    state = reducer(state, badgesEarned([badge('a'), badge('b')]))

    expect(state.revealQueue.map((b) => b.id)).toEqual(['a', 'b'])
  })

  it('ne rejoue pas un badge déjà célébré puis acquitté', () => {
    let state = reducer(etatInitial(), badgesEarned([badge('a')]))
    state = reducer(state, dismissReveal())
    expect(state.revealQueue).toHaveLength(0)

    // Le résumé serveur le renvoie encore (mark_seen pas encore arrivé) :
    // la file doit rester vide.
    state = reducer(state, {
      type: fetchGamificationSummary.fulfilled.type,
      payload: { unseen_badges: [badge('a')] },
    })
    expect(state.revealQueue).toHaveLength(0)
  })

  it('dédoublonne entre unseen_badges et newly_earned d’une même réponse', () => {
    const state = reducer(etatInitial(), {
      type: syncGamification.fulfilled.type,
      payload: { unseen_badges: [badge('a')], newly_earned: [badge('a'), badge('c')] },
    })

    expect(state.revealQueue.map((b) => b.id)).toEqual(['a', 'c'])
  })

  it('ignore une charge utile absente ou malformée', () => {
    let state = reducer(etatInitial(), badgesEarned(undefined))
    state = reducer(state, badgesEarned([null, {}, badge('a')]))

    expect(state.revealQueue.map((b) => b.id)).toEqual(['a'])
  })
})

import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest'
import { renderHook, act } from '@testing-library/react'
import useTimeTracker from './useTimeTracker'
import progressionApi from '@/services/api/progressionApi'

vi.mock('@/services/api/progressionApi', () => ({
  default: {
    trackTime: vi.fn(() => Promise.resolve({})),
    trackTimeBeacon: vi.fn(),
  },
}))

/**
 * Le compteur de temps alimente des badges. S'il crédite un onglet oublié, les
 * récompenses ne veulent plus rien dire — ces tests verrouillent les deux
 * garde-fous : onglet visible **et** interaction récente.
 */

/** Simule `document.visibilityState`, non modifiable directement en jsdom. */
function setVisibility(value) {
  Object.defineProperty(document, 'visibilityState', {
    value,
    configurable: true,
  })
  document.dispatchEvent(new Event('visibilitychange'))
}

/** Avance les timers de n secondes, tic par tic comme le fait le hook. */
function avancer(seconds) {
  act(() => {
    vi.advanceTimersByTime(seconds * 1000)
  })
}

describe('useTimeTracker', () => {
  beforeEach(() => {
    vi.useFakeTimers()
    setVisibility('visible')
  })

  afterEach(() => {
    vi.useRealTimers()
  })

  it('envoie le temps accumulé par incréments', () => {
    renderHook(() => useTimeTracker('lecon-1'))

    avancer(30)

    expect(progressionApi.trackTime).toHaveBeenCalledWith('lecon-1', 30)
  })

  it('ne compte rien quand l’onglet est en arrière-plan', () => {
    renderHook(() => useTimeTracker('lecon-1'))

    setVisibility('hidden')
    avancer(120)

    expect(progressionApi.trackTime).not.toHaveBeenCalled()
    // Rien à sauver non plus : le reliquat est sous le seuil de flush.
    expect(progressionApi.trackTimeBeacon).not.toHaveBeenCalled()
  })

  it('cesse de compter après 90 s sans interaction', () => {
    renderHook(() => useTimeTracker('lecon-1'))

    // Bien au-delà du seuil : seules les 90 premières secondes doivent compter.
    avancer(600)

    const total = progressionApi.trackTime.mock.calls.reduce(
      (sum, [, seconds]) => sum + seconds,
      0
    )
    expect(total).toBe(90)
  })

  it('repart quand l’apprenant interagit à nouveau', () => {
    renderHook(() => useTimeTracker('lecon-1'))

    avancer(120) // le compteur s'est arrêté en route
    progressionApi.trackTime.mockClear()

    act(() => {
      window.dispatchEvent(new Event('keydown'))
    })
    avancer(30)

    expect(progressionApi.trackTime).toHaveBeenCalledWith('lecon-1', 30)
  })

  it('sauve le reliquat via un beacon quand l’onglet se ferme', () => {
    renderHook(() => useTimeTracker('lecon-1'))

    avancer(10) // sous le seuil de flush périodique
    expect(progressionApi.trackTime).not.toHaveBeenCalled()

    act(() => {
      window.dispatchEvent(new Event('pagehide'))
    })

    expect(progressionApi.trackTimeBeacon).toHaveBeenCalledWith('lecon-1', 10)
  })

  it('ne fait rien sans leçon', () => {
    renderHook(() => useTimeTracker(null))
    avancer(120)

    expect(progressionApi.trackTime).not.toHaveBeenCalled()
  })
})

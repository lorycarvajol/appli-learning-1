import { describe, it, expect, vi, beforeEach } from 'vitest'

/**
 * Contrat unifié des services API : **toutes** les méthodes renvoient les
 * données déjà déballées (`response.data`), jamais la réponse axios brute.
 *
 * Cette incohérence a coûté une page blanche : `authApi`/`coursesApi`
 * renvoyaient la réponse brute quand les autres renvoyaient les données, et un
 * `.data` de trop (ou de moins) donnait `undefined`, vidant le state au rendu.
 * Ce test verrouille l'uniformité — un module qui régresserait vers la réponse
 * brute le ferait rougir.
 */

// Un seul module axios sous-jacent, importé par tous les services (parfois
// sous le nom `apiClient`, parfois `apiService` — c'est le même défaut).
const payload = { ok: true, id: 'x' }
const mockClient = {
  get: vi.fn().mockResolvedValue({ data: payload, status: 200 }),
  post: vi.fn().mockResolvedValue({ data: payload, status: 200 }),
  patch: vi.fn().mockResolvedValue({ data: payload, status: 200 }),
  put: vi.fn().mockResolvedValue({ data: payload, status: 200 }),
  delete: vi.fn().mockResolvedValue({ data: payload, status: 200 }),
}

vi.mock('./apiService', () => ({
  default: mockClient,
  // `isAuthEndpoint` est aussi exporté du module ; inutile ici mais gardé
  // pour ne pas casser un éventuel import.
  isAuthEndpoint: () => false,
}))

beforeEach(() => {
  vi.clearAllMocks()
  for (const fn of Object.values(mockClient)) {
    fn.mockResolvedValue({ data: payload, status: 200 })
  }
})

describe('Contrat des services API — données déballées', () => {
  it('authApi renvoie les données, pas la réponse axios', async () => {
    const { authApi } = await import('./authApi')
    await expect(authApi.getCurrentUser()).resolves.toEqual(payload)
    await expect(authApi.login('a@b.c', 'x')).resolves.toEqual(payload)
  })

  it('coursesApi renvoie les données, pas la réponse axios', async () => {
    const coursesApi = (await import('./coursesApi')).default
    await expect(coursesApi.getChapters()).resolves.toEqual(payload)
    await expect(coursesApi.getChapter('html')).resolves.toEqual(payload)
  })

  it('progressionApi renvoie les données', async () => {
    const progressionApi = (await import('./progressionApi')).default
    await expect(progressionApi.getMyProgress()).resolves.toEqual(payload)
  })

  it('gamificationApi renvoie les données', async () => {
    const gamificationApi = (await import('./gamificationApi')).default
    await expect(gamificationApi.getSummary()).resolves.toEqual(payload)
  })

  it('cohortsApi renvoie les données', async () => {
    const cohortsApi = (await import('./cohortsApi')).default
    await expect(cohortsApi.getInvite('tok')).resolves.toEqual(payload)
  })

  it('administrationApi renvoie les données', async () => {
    const administrationApi = (await import('./administrationApi')).default
    await expect(administrationApi.getOverview()).resolves.toEqual(payload)
  })

  it('validationApi renvoie les données', async () => {
    const validationApi = (await import('./validationApi')).default
    await expect(validationApi.submitCode('id', 'code')).resolves.toEqual(payload)
  })
})

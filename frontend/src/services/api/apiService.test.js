import { describe, it, expect } from 'vitest'
import { isAuthEndpoint } from './apiService'

/**
 * Verrouille la décision centrale de l'intercepteur : un 401 sur une route
 * d'authentification est une réponse métier (« identifiants refusés »), pas un
 * signal de jeton expiré. Il ne doit donc **pas** déclencher le rafraîchissement
 * de jeton ni la redirection vers `/login` — sinon un login raté recharge la
 * page et efface le message d'erreur avant tout affichage.
 */
describe('isAuthEndpoint', () => {
  it('reconnaît les routes d’authentification', () => {
    expect(isAuthEndpoint('/auth/login/')).toBe(true)
    expect(isAuthEndpoint('/auth/token/refresh/')).toBe(true)
    expect(isAuthEndpoint('/auth/register/')).toBe(true)
    // Peu importe une éventuelle base URL absolue devant.
    expect(isAuthEndpoint('http://localhost:8000/api/auth/login/')).toBe(true)
  })

  it('laisse les autres routes suivre le flux normal de rafraîchissement', () => {
    expect(isAuthEndpoint('/auth/me/')).toBe(false)
    expect(isAuthEndpoint('/courses/chapters/')).toBe(false)
    expect(isAuthEndpoint('/gamification/summary/')).toBe(false)
    expect(isAuthEndpoint('')).toBe(false)
    expect(isAuthEndpoint(undefined)).toBe(false)
  })
})

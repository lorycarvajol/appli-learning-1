import { describe, it, expect, beforeEach, vi } from 'vitest'
import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { Provider } from 'react-redux'
import { configureStore } from '@reduxjs/toolkit'
import ProfilePage from './ProfilePage'
import authReducer from '@/features/auth/authSlice'
import { authApi } from '@/services/api/authApi'

vi.mock('@/services/api/authApi', () => ({
  authApi: { updateProfile: vi.fn(), changePassword: vi.fn() },
}))
vi.mock('@/services/api/gamificationApi', () => ({
  default: { getSummary: vi.fn().mockResolvedValue({ streak: { current_streak: 4 } }) },
}))

const USER = {
  id: 'u1',
  email: 'eve@example.com',
  first_name: 'Eve',
  last_name: 'Martin',
  role: 'LEARNER',
  profile: {
    bio: '', github_username: '', avatar_key: '', theme: 'AUTO',
    total_points: 120, level: 2,
  },
}

function renderPage(user = USER) {
  const store = configureStore({
    reducer: {
      auth: authReducer,
      gamification: (state = { summary: null }) => state,
    },
    preloadedState: {
      auth: { user, isAuthenticated: true, initialized: true, loading: false, error: null },
    },
  })
  return { store, ...render(<Provider store={store}><ProfilePage /></Provider>) }
}

beforeEach(() => {
  // Contrat uniforme : les services renvoient les données déjà déballées,
  // pas la réponse axios (cf. services/api/contract.test.js).
  authApi.updateProfile.mockResolvedValue(USER)
  authApi.changePassword.mockResolvedValue({})
})

describe('ProfilePage', () => {
  it('affiche la progression sans permettre de la modifier', async () => {
    renderPage()

    // Les points sont un solde dérivé du grand livre : ils s'affichent, mais
    // aucun champ de saisie ne doit les exposer.
    expect(await screen.findByText('120')).toBeInTheDocument()
    expect(screen.queryByLabelText(/points/i)).not.toBeInTheDocument()
  })

  it('enregistre l’avatar choisi dans la galerie', async () => {
    const user = userEvent.setup()
    renderPage()

    await user.click(await screen.findByRole('radio', { name: 'Avatar orbit violet' }))
    await user.click(screen.getByRole('button', { name: 'Enregistrer' }))

    await waitFor(() => {
      expect(authApi.updateProfile).toHaveBeenCalledWith(
        expect.objectContaining({
          profile: expect.objectContaining({ avatar_key: 'orbit-violet' }),
        })
      )
    })
  })

  it('permet de revenir aux initiales', async () => {
    const user = userEvent.setup()
    renderPage({ ...USER, profile: { ...USER.profile, avatar_key: 'prism-amber' } })

    await user.click(await screen.findByRole('radio', { name: 'Mes initiales' }))
    await user.click(screen.getByRole('button', { name: 'Enregistrer' }))

    await waitFor(() => {
      expect(authApi.updateProfile).toHaveBeenCalledWith(
        expect.objectContaining({
          profile: expect.objectContaining({ avatar_key: '' }),
        })
      )
    })
  })

  it('n’envoie jamais les points ni le rôle au serveur', async () => {
    const user = userEvent.setup()
    renderPage()

    await user.click(await screen.findByRole('button', { name: 'Enregistrer' }))

    await waitFor(() => expect(authApi.updateProfile).toHaveBeenCalled())
    const payload = authApi.updateProfile.mock.calls[0][0]
    expect(payload.role).toBeUndefined()
    expect(payload.profile.total_points).toBeUndefined()
    expect(payload.profile.level).toBeUndefined()
  })

  it('refuse un changement de mot de passe mal confirmé sans appeler l’API', async () => {
    const user = userEvent.setup()
    renderPage()

    await user.type(await screen.findByLabelText('Mot de passe actuel'), 'ancien-mdp')
    await user.type(screen.getByLabelText('Nouveau mot de passe'), 'nouveau-mdp-solide')
    await user.type(screen.getByLabelText('Confirmer'), 'faute-de-frappe')
    await user.click(screen.getByRole('button', { name: 'Changer le mot de passe' }))

    expect(await screen.findByRole('alert')).toHaveTextContent(/ne correspondent pas/)
    expect(authApi.changePassword).not.toHaveBeenCalled()
  })

  it('affiche un message d’erreur lisible plutôt que l’objet brut de DRF', async () => {
    // DRF répond {profile: {avatar_key: ["…"]}} : rendu tel quel, l'utilisateur
    // lirait « [object Object] ».
    authApi.updateProfile.mockRejectedValue({
      response: { data: { profile: { avatar_key: ['Cet avatar ne fait pas partie du catalogue.'] } } },
    })
    const user = userEvent.setup()
    renderPage()

    await user.click(await screen.findByRole('button', { name: 'Enregistrer' }))

    expect(await screen.findByRole('alert')).toHaveTextContent(
      'Cet avatar ne fait pas partie du catalogue.'
    )
  })
})

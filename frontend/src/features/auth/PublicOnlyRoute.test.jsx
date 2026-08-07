import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import { Provider } from 'react-redux'
import { configureStore } from '@reduxjs/toolkit'
import { MemoryRouter, Route, Routes } from 'react-router-dom'
import PublicOnlyRoute from './PublicOnlyRoute'

/**
 * Cette garde n'est pas une sécurité : elle évite une impasse. `/login`
 * affichait son formulaire à quelqu'un dont la session était déjà ouverte.
 */

function renderGuard({ user = null, entree = '/login' } = {}) {
  const store = configureStore({
    reducer: {
      auth: (state = { user, isAuthenticated: Boolean(user), initialized: true }) => state,
    },
  })

  return render(
    <Provider store={store}>
      <MemoryRouter initialEntries={[entree]}>
        <Routes>
          <Route
            path="/login"
            element={<PublicOnlyRoute><p>formulaire de connexion</p></PublicOnlyRoute>}
          />
          <Route path="/dashboard" element={<p>tableau de bord</p>} />
          <Route path="/rejoindre/:token" element={<p>page d’invitation</p>} />
        </Routes>
      </MemoryRouter>
    </Provider>
  )
}

const CONNECTE = { id: 'u1', email: 'eve@example.com', role: 'LEARNER' }

describe('PublicOnlyRoute', () => {
  it('laisse passer un visiteur sans session', () => {
    renderGuard()

    expect(screen.getByText('formulaire de connexion')).toBeInTheDocument()
  })

  it('renvoie au tableau de bord un visiteur déjà connecté', () => {
    renderGuard({ user: CONNECTE })

    expect(screen.getByText('tableau de bord')).toBeInTheDocument()
    expect(screen.queryByText('formulaire de connexion')).not.toBeInTheDocument()
  })

  it('respecte `?next=` — sinon l’invitation ne rattache jamais à la classe', () => {
    // Quelqu'un qui a déjà un compte suit un lien d'invitation : il passe par
    // /login?next=/rejoindre/<jeton>. Le renvoyer au tableau de bord le
    // laisserait connecté mais sans classe, sans rien pour le lui dire.
    renderGuard({ user: CONNECTE, entree: '/login?next=%2Frejoindre%2Fjeton123' })

    expect(screen.getByText('page d’invitation')).toBeInTheDocument()
  })

  it('écarte une destination externe', () => {
    // `safeRedirectPath` refuse tout ce qui n'est pas un chemin interne —
    // y compris `/\evil.com`, que les navigateurs lisent comme
    // protocole-relatif.
    renderGuard({ user: CONNECTE, entree: '/login?next=https%3A%2F%2Fevil.example' })

    expect(screen.getByText('tableau de bord')).toBeInTheDocument()
  })

  it('affiche le formulaire quand le jeton est mort', () => {
    // Identité résolue, aucun utilisateur : il faut bien pouvoir se
    // reconnecter. C'est pourquoi la garde ne redirige que sur une présence.
    localStorage.setItem('accessToken', 'jeton-perime')
    renderGuard({ user: null })

    expect(screen.getByText('formulaire de connexion')).toBeInTheDocument()
  })
})

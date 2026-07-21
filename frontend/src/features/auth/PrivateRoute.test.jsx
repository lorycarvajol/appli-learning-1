import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import { Provider } from 'react-redux'
import { configureStore } from '@reduxjs/toolkit'
import { MemoryRouter, Route, Routes } from 'react-router-dom'
import PrivateRoute from './PrivateRoute'
import { ROLES, STAFF_ROLES } from '@/constants/roles'

/**
 * Ces tests verrouillent le comportement décrit dans CLAUDE.md : la garde doit
 * **attendre `initialized`** avant de trancher sur le rôle. Sans cette attente,
 * un formateur était renvoyé vers /dashboard à chaque rafraîchissement de page.
 */

function renderGuard(authState, { roles } = {}) {
  const store = configureStore({
    reducer: { auth: (state = authState) => state },
  })

  return render(
    <Provider store={store}>
      <MemoryRouter initialEntries={['/protegee']}>
        <Routes>
          <Route
            path="/protegee"
            element={
              <PrivateRoute roles={roles}>
                <div>contenu protégé</div>
              </PrivateRoute>
            }
          />
          <Route path="/login" element={<div>page de connexion</div>} />
          <Route path="/dashboard" element={<div>tableau de bord</div>} />
        </Routes>
      </MemoryRouter>
    </Provider>
  )
}

const AUTH = {
  anonyme: { user: null, isAuthenticated: false, initialized: true, loading: false },
  enCours: { user: null, isAuthenticated: false, initialized: false, loading: false },
  apprenant: {
    user: { id: '1', role: ROLES.LEARNER },
    isAuthenticated: true,
    initialized: true,
    loading: false,
  },
  formateur: {
    user: { id: '2', role: ROLES.TRAINER },
    isAuthenticated: true,
    initialized: true,
    loading: false,
  },
}

describe('PrivateRoute', () => {
  it('renvoie vers la connexion sans jeton', () => {
    renderGuard(AUTH.anonyme)
    expect(screen.getByText('page de connexion')).toBeInTheDocument()
  })

  it('laisse passer un utilisateur connecté quand aucun rôle n’est exigé', () => {
    localStorage.setItem('accessToken', 'jeton')
    renderGuard(AUTH.apprenant)
    expect(screen.getByText('contenu protégé')).toBeInTheDocument()
  })

  it('attend la résolution de l’identité au lieu de trancher sur le rôle', () => {
    // Le cas du rafraîchissement de page : le jeton est là, le profil non.
    localStorage.setItem('accessToken', 'jeton')
    renderGuard(AUTH.enCours, { roles: STAFF_ROLES })

    expect(screen.getByRole('status')).toHaveTextContent('Chargement...')
    // Surtout : pas de redirection prématurée.
    expect(screen.queryByText('tableau de bord')).not.toBeInTheDocument()
  })

  it('renvoie un apprenant vers son espace sur une route formateur', () => {
    localStorage.setItem('accessToken', 'jeton')
    renderGuard(AUTH.apprenant, { roles: STAFF_ROLES })
    expect(screen.getByText('tableau de bord')).toBeInTheDocument()
  })

  it('laisse passer un formateur sur une route formateur', () => {
    localStorage.setItem('accessToken', 'jeton')
    renderGuard(AUTH.formateur, { roles: STAFF_ROLES })
    expect(screen.getByText('contenu protégé')).toBeInTheDocument()
  })

  it('renvoie vers la connexion quand le jeton est périmé', () => {
    // Jeton présent, identité résolue, mais aucun utilisateur en retour.
    localStorage.setItem('accessToken', 'jeton-perime')
    renderGuard({ ...AUTH.anonyme, isAuthenticated: false })
    expect(screen.getByText('page de connexion')).toBeInTheDocument()
  })
})

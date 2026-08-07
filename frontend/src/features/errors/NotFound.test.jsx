import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import { Provider } from 'react-redux'
import { configureStore } from '@reduxjs/toolkit'
import { MemoryRouter } from 'react-router-dom'
import { ThemeProvider } from '@/contexts/ThemeProvider'
import NotFound from './NotFound'
import App from '@/App'

/**
 * Une URL inconnue rendait une **page blanche** : aucune route `*` n'existait.
 * C'est le pire des cas — indistinguable d'une panne du site alors qu'il
 * s'agit le plus souvent d'une faute de frappe.
 */

function renderNotFound({ user = null, token = null, path = '/nawak' } = {}) {
  if (token) localStorage.setItem('accessToken', token)

  const store = configureStore({
    reducer: {
      auth: (state = { user, isAuthenticated: Boolean(user), initialized: true }) => state,
      gamification: (state = { revealQueue: [] }) => state,
    },
  })

  // `ThemeProvider` est requis par `Header`, que `Layout` monte pour un
  // visiteur connecté. Dans l'application il enveloppe tout depuis `main.jsx`,
  // au-dessus même du magasin Redux.
  return render(
    <Provider store={store}>
      <ThemeProvider>
        <MemoryRouter initialEntries={[path]}>
          <NotFound />
        </MemoryRouter>
      </ThemeProvider>
    </Provider>
  )
}

describe('Page 404', () => {
  it('dit ce qui s’est passé plutôt que de rester vide', () => {
    renderNotFound()

    expect(screen.getByRole('heading', { level: 1, name: /n’existe pas/ }))
      .toBeInTheDocument()
  })

  it('affiche le chemin demandé, seul indice d’une coquille', () => {
    // Sans lui, un visiteur ne peut pas repérer sa propre faute de frappe.
    renderNotFound({ path: '/chapitres/htlm' })

    expect(screen.getByText('/chapitres/htlm')).toBeInTheDocument()
  })

  it('propose la connexion à un visiteur sans session', () => {
    renderNotFound()

    expect(screen.getByRole('link', { name: 'Se connecter' })).toBeInTheDocument()
    // Proposer le tableau de bord enverrait vers /login : une seconde erreur
    // en guise de porte de sortie.
    expect(screen.queryByRole('link', { name: /tableau de bord/i })).not.toBeInTheDocument()
  })

  it('propose le tableau de bord à un visiteur connecté', () => {
    renderNotFound({ user: { first_name: 'Eve', role: 'LEARNER', profile: {} } })

    expect(screen.getByRole('link', { name: 'Retour au tableau de bord' }))
      .toBeInTheDocument()
    expect(screen.queryByRole('link', { name: 'Se connecter' })).not.toBeInTheDocument()
  })

  it('garde la navigation dès qu’un jeton existe, sans attendre le profil', () => {
    // `localStorage` répond tout de suite et `Header` tolère `user` absent :
    // attendre `initialized` ferait clignoter la page, version sans en-tête
    // puis avec.
    renderNotFound({ user: null, token: 'jeton-de-test' })

    expect(screen.getByRole('banner')).toBeInTheDocument()
    expect(screen.getByRole('link', { name: 'Retour au tableau de bord' }))
      .toBeInTheDocument()
  })

  it('n’enveloppe pas de navigation un visiteur sans session', () => {
    renderNotFound()

    expect(screen.queryByRole('banner')).not.toBeInTheDocument()
  })
})

/**
 * ⚠️ Les tests ci-dessus montent `<NotFound />` **directement** : ils
 * n'auraient pas attrapé le bug d'origine, qui n'était pas un composant
 * manquant mais une **route manquante**. Celui-ci monte l'application entière
 * et lui demande une adresse inconnue — c'est le seul qui rougit si la route
 * `*` disparaît de `App.jsx`.
 */
describe('Routage — adresse inconnue', () => {
  it('sert la page 404 pour n’importe quelle adresse non déclarée', async () => {
    const store = configureStore({
      reducer: {
        auth: (state = {
          user: null, isAuthenticated: false, initialized: true, loading: false,
        }) => state,
        gamification: (state = { revealQueue: [] }) => state,
      },
    })

    render(
      <Provider store={store}>
        <ThemeProvider>
          <MemoryRouter initialEntries={['/une/adresse/qui/nexiste/pas']}>
            <App />
          </MemoryRouter>
        </ThemeProvider>
      </Provider>
    )

    // `findBy…` : les pages sont chargées par `lazy()`, derrière un `Suspense`.
    expect(await screen.findByRole('heading', { level: 1, name: /n’existe pas/ }))
      .toBeInTheDocument()
    expect(screen.getByText('/une/adresse/qui/nexiste/pas')).toBeInTheDocument()
  })
})

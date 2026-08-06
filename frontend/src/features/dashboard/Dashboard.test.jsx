import { describe, it, expect, beforeEach, vi } from 'vitest'
import { render, screen } from '@testing-library/react'
import { Provider } from 'react-redux'
import { configureStore } from '@reduxjs/toolkit'
import { MemoryRouter } from 'react-router-dom'
import Dashboard from './Dashboard'

/**
 * ⚠️ Le chiffre de « Vue d'ensemble » ne mesurait pas ce qu'il annonçait.
 *
 * Il valait `terminées / (terminées + en cours)`, calculé sur les seules
 * leçons déjà touchées : une première leçon terminée affichait **100 % de
 * progression globale**, et ouvrir une leçon *faisait redescendre* la barre.
 * Le dénominateur réel — le nombre de leçons publiées — n'existait pas côté
 * client ; il vient désormais du serveur (`/progress/overview/`).
 *
 * Ces tests montent le composant avec un magasin figé : ils décrivent un état,
 * ils n'ont pas à rejouer les thunks pour y arriver.
 */

vi.mock('@/services/api/progressionApi', () => ({
  default: {
    getMyProgress: vi.fn().mockResolvedValue([]),
    getNextLesson: vi.fn().mockResolvedValue({}),
    getOverview: vi.fn().mockResolvedValue({}),
  },
}))
vi.mock('@/services/api/gamificationApi', () => ({
  default: { sync: vi.fn().mockResolvedValue({}) },
}))

const OVERVIEW = {
  lessons: { total: 68, completed: 12, in_progress: 2, percent: 18 },
  chapters: [
    { title: 'HTML', slug: 'html', order_index: 1, is_accessible: true, total: 18, completed: 12, percent: 67 },
    { title: 'CSS', slug: 'css', order_index: 2, is_accessible: false, total: 17, completed: 0, percent: 0 },
  ],
  time_spent_seconds: 5400,
  average_score: 88,
  graded_count: 4,
}

function renderDashboard({ overview = OVERVIEW, summary = null } = {}) {
  const store = configureStore({
    reducer: {
      auth: (state = { user: { first_name: 'Lory', profile: {} } }) => state,
      progression: (state = {
        progressByLesson: {}, nextLesson: null, overview, loading: false, error: null,
      }) => state,
      // `badgeStats` fait partie de l'état initial du vrai slice : le fournir
      // ici n'est pas une commodité de test, c'est reproduire le magasin réel
      // (`NextObjectives` s'en sert comme repli quand le résumé n'est pas
      // encore chargé).
      gamification: (state = {
        summary,
        revealQueue: [],
        badges: [],
        badgeStats: { earned_count: 0, total_count: 0, secret_total: 0, secret_found: 0 },
      }) => state,
    },
  })

  return render(
    <Provider store={store}>
      <MemoryRouter><Dashboard /></MemoryRouter>
    </Provider>
  )
}

beforeEach(() => {
  vi.clearAllMocks()
})

describe('Dashboard — vue d’ensemble', () => {
  it('compte la progression sur tout le programme, pas sur les leçons touchées', () => {
    renderDashboard()

    const barre = screen.getByRole('progressbar', { name: /Progression globale/i })
    // L'ancien calcul aurait affiché 86 % (12 terminées sur 14 touchées).
    expect(barre).toHaveAttribute('aria-valuenow', '18')
    expect(screen.getByText('12 / 68 leçons')).toBeInTheDocument()
  })

  it('détaille chaque chapitre, y compris ceux qui restent verrouillés', () => {
    renderDashboard()

    expect(
      screen.getByRole('progressbar', { name: 'Avancement du chapitre HTML' })
    ).toHaveAttribute('aria-valuenow', '67')

    // Verrouillé mais listé : on montre la suite du parcours, on ne l'ouvre pas.
    expect(
      screen.getByRole('progressbar', { name: 'Avancement du chapitre CSS' })
    ).toHaveAttribute('aria-valuenow', '0')
    expect(screen.getByLabelText('Chapitre verrouillé')).toBeInTheDocument()
  })

  it('affiche un tiret plutôt qu’un zéro quand rien n’est encore noté', () => {
    // `0 %` se lit comme un échec ; l'absence de note n'en est pas un.
    renderDashboard({
      overview: { ...OVERVIEW, average_score: null, graded_count: 0 },
    })

    expect(screen.getByText('—')).toBeInTheDocument()
    expect(screen.queryByText('0%')).not.toBeInTheDocument()
  })

  it('survit à une vue d’ensemble encore absente', () => {
    renderDashboard({ overview: null })

    expect(
      screen.getByRole('progressbar', { name: /Progression globale/i })
    ).toHaveAttribute('aria-valuenow', '0')
  })
})

describe('Dashboard — conseil du jour', () => {
  it('adresse un conseil lié au comportement, jamais la phrase figée d’avant', () => {
    renderDashboard({
      overview: {
        ...OVERVIEW,
        lessons: { total: 68, completed: 5, in_progress: 4, percent: 7 },
      },
    })

    const conseil = screen.getByText(/4 leçons sont ouvertes en même temps/i)
    expect(conseil).toBeInTheDocument()
    expect(
      screen.queryByText(/Pratiquez régulièrement/i)
    ).not.toBeInTheDocument()
  })
})
